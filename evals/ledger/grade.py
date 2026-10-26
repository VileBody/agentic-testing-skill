"""Evaluate an authored unittest suite against correct variants and seeded defects.

Usage: python3 evals/ledger/grade.py path/to/test_ledger.py --output results.json
All implementations run in temporary directories. No third-party dependencies.
This is a small diagnostic benchmark, not a general measure of test quality.
"""

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile


REFERENCE = '''
def aggregate(records, start, end):
    plain_int = lambda x: isinstance(x, int) and not isinstance(x, bool)
    if FAULT != "invalid_window" and (
        not plain_int(start) or not plain_int(end) or start > end
    ):
        raise ValueError("invalid window")
    if FAULT == "mutate_input":
        records.reverse()
    seen = {}
    totals = {}
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("invalid record")
        if FAULT == "ignore_invalid_outside" and plain_int(record.get("at")):
            if not (start <= record["at"] < end):
                continue
        try:
            tenant, event_id, at, kind, amount = (
                record[k] for k in ("tenant", "event_id", "at", "kind", "amount")
            )
        except KeyError as exc:
            raise ValueError("missing field") from exc
        valid_amount = plain_int(amount) and amount > 0
        if FAULT == "boolean_amount":
            valid_amount = isinstance(amount, int) and amount > 0
        if FAULT == "zero_amount":
            valid_amount = plain_int(amount) and amount >= 0
        if FAULT == "negative_amount":
            valid_amount = plain_int(amount) and amount != 0
        if (not isinstance(tenant, str) or not tenant
                or not isinstance(event_id, str) or not event_id
                or not plain_int(at) or kind not in ("sale", "refund")
                or not valid_amount):
            raise ValueError("invalid fields")
        key = event_id if FAULT == "global_identity" else (tenant, event_id)
        payload = (tenant, event_id, at, kind, amount)
        if FAULT == "extra_fields_identity":
            payload = repr(record)
        if key in seen and FAULT != "no_dedup":
            if seen[key] != payload and FAULT != "ignore_conflict":
                raise ValueError("conflicting event")
            continue
        seen[key] = payload
        left = start < at if FAULT == "exclusive_start" else start <= at
        right = at <= end if FAULT == "inclusive_end" else at < end
        if left and right:
            target = "all" if FAULT == "merge_tenants" else tenant
            signed = amount if kind == "sale" or FAULT == "refund_positive" else -amount
            totals[target] = totals.get(target, 0) + signed
    if FAULT == "drop_zero":
        totals = {k: v for k, v in totals.items() if v != 0}
    if FAULT == "absolute_total":
        totals = {k: abs(v) for k, v in totals.items()}
    if FAULT == "empty_result":
        return {}
    return totals
'''

# Deliberately different organization: validate and deduplicate first, reduce later.
ALTERNATIVE = '''
def aggregate(records, start, end):
    def is_integer(value):
        return isinstance(value, int) and not isinstance(value, bool)
    if not is_integer(start) or not is_integer(end) or start > end:
        raise ValueError("window")
    unique = {}
    for item in records:
        if not isinstance(item, dict):
            raise ValueError("record")
        try:
            values = tuple(item[name] for name in
                           ("tenant", "event_id", "at", "kind", "amount"))
        except KeyError as exc:
            raise ValueError("fields") from exc
        tenant, ident, timestamp, kind, cents = values
        if not all(isinstance(x, str) and len(x) > 0 for x in (tenant, ident)):
            raise ValueError("identity")
        if not is_integer(timestamp) or not is_integer(cents) or cents <= 0:
            raise ValueError("numbers")
        if kind not in ("sale", "refund"):
            raise ValueError("kind")
        identity = tenant, ident
        if identity in unique and unique[identity] != values:
            raise ValueError("conflict")
        unique[identity] = values
    answer = {}
    for tenant, ident, timestamp, kind, cents in reversed(list(unique.values())):
        if timestamp < start or timestamp >= end:
            continue
        answer.setdefault(tenant, 0)
        answer[tenant] += {"sale": cents, "refund": -cents}[kind]
    return answer
'''

FAULTS = (
    "exclusive_start", "inclusive_end", "no_dedup", "global_identity",
    "refund_positive", "drop_zero", "absolute_total", "ignore_conflict",
    "ignore_invalid_outside", "mutate_input", "boolean_amount", "zero_amount",
    "negative_amount", "invalid_window", "merge_tenants", "extra_fields_identity",
    "empty_result",
)

RUNNER = '''
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path.cwd()))
suite = unittest.defaultTestLoader.discover(str(Path.cwd()), pattern="test_ledger.py")
result = unittest.TextTestRunner(verbosity=2).run(suite)
summary = {
    "tests_run": result.testsRun,
    "failures": [str(test) for test, _ in result.failures],
    "errors": [str(test) for test, _ in result.errors],
    "skipped": [str(test) for test, _ in result.skipped],
    "expected_failures": [str(test) for test, _ in result.expectedFailures],
    "unexpected_successes": [str(test) for test in result.unexpectedSuccesses],
    "passed": result.wasSuccessful(),
}
Path("outcome.json").write_text(json.dumps(summary))
'''


def evaluate(test_source, implementation):
    with tempfile.TemporaryDirectory(prefix="design-tests-grader-") as directory:
        work = Path(directory)
        (work / "ledger.py").write_text(implementation)
        (work / "test_ledger.py").write_text(test_source)
        (work / "run_suite.py").write_text(RUNNER)
        try:
            process = subprocess.run(
                [sys.executable, "-I", "run_suite.py"], cwd=work,
                capture_output=True, text=True, timeout=30,
            )
        except subprocess.TimeoutExpired:
            return {"status": "timeout"}
        outcome = work / "outcome.json"
        if not outcome.exists():
            return {"status": "runner_error", "log": process.stderr[-4000:]}
        result = json.loads(outcome.read_text())
        result["status"] = "completed"
        result["log"] = (process.stdout + process.stderr)[-14000:]
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("suite", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = args.suite.read_text()
    outcomes = {
        "reference": evaluate(source, 'FAULT = None\n' + REFERENCE),
        "alternative": evaluate(source, ALTERNATIVE),
    }
    baseline_valid = all(
        result.get("passed") and result.get("tests_run", 0) > 0
        and not result.get("skipped") and not result.get("expected_failures")
        for result in outcomes.values()
    )
    mutations = {}
    if baseline_valid:
        for fault in FAULTS:
            outcome = evaluate(source, f"FAULT = {fault!r}\n" + REFERENCE)
            # Errors/timeouts need human review; they are not automatically counted.
            outcome["assertion_detected"] = bool(outcome.get("failures"))
            mutations[fault] = outcome
    report = {
        "baseline_valid": baseline_valid,
        "correct_implementations": outcomes,
        "mutation_count": len(FAULTS),
        "assertion_detected": sum(x["assertion_detected"] for x in mutations.values()),
        "mutations": mutations,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in
                      ("baseline_valid", "mutation_count", "assertion_detected")}))


if __name__ == "__main__":
    main()
