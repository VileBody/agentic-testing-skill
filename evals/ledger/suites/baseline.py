"""Contract tests for ledger.aggregate; run with python3 -m unittest -v."""

import copy
import unittest

from ledger import aggregate


def event(**changes):
    record = {
        "tenant": "alpha",
        "event_id": "one",
        "at": 1,
        "kind": "sale",
        "amount": 100,
    }
    record.update(changes)
    return record


class AggregateTests(unittest.TestCase):
    def test_empty_input_and_empty_window(self):
        for start, end in [(-10, 10), (0, 0), (-5, -5)]:
            with self.subTest(start=start, end=end):
                self.assertEqual(aggregate([], start, end), {})
        self.assertEqual(aggregate([event()], 1, 1), {})

    def test_half_open_window_and_signed_totals(self):
        records = [
            event(event_id="before", at=-6, amount=999),
            event(event_id="start", at=-5, amount=150),
            event(event_id="refund", at=-4, kind="refund", amount=50),
            event(tenant="negative", at=0, kind="refund", amount=80),
            event(tenant="zero", event_id="sale", at=2, amount=25),
            event(tenant="zero", event_id="refund", at=2,
                  kind="refund", amount=25),
            event(tenant="end-only", at=5),
            event(tenant="before-only", at=-9),
            event(tenant="after-only", at=6),
        ]
        self.assertEqual(
            aggregate(records, -5, 5),
            {"alpha": 100, "negative": -80, "zero": 0},
        )

    def test_duplicates_extra_fields_and_tenant_scoped_identity(self):
        records = [
            event(source={"nested": [1, 2]}),
            event(tenant="beta", kind="refund", amount=40),
            event(event_id="two", amount=25),
            event(source={"nested": [3]}, ignored=False),
            event(),
            event(source={"nested": [1, 2]}),
        ]
        # Duplicates are deliberately separated by other events. Extra fields
        # may differ or be absent, and need not contain hashable values.
        for ordered in [records, list(reversed(records)), records[2:] + records[:2]]:
            with self.subTest(order=ordered):
                self.assertEqual(aggregate(ordered, 0, 3), {"alpha": 125, "beta": -40})

    def test_nonempty_identifiers_are_not_trimmed(self):
        records = [event(tenant=" ", event_id=" ", amount=1)]
        self.assertEqual(aggregate(records, 0, 2), {" ": 1})

    def test_invalid_window_values(self):
        for value in [True, False, 1.5, "1", None]:
            for start, end in [(value, 10), (-10, value)]:
                with self.subTest(start=start, end=end):
                    with self.assertRaises(ValueError):
                        aggregate([], start, end)
        with self.assertRaises(ValueError):
            aggregate([], 2, 1)

    def test_each_required_field_is_required(self):
        for field in ["tenant", "event_id", "at", "kind", "amount"]:
            record = event()
            del record[field]
            with self.subTest(missing=field):
                with self.assertRaises(ValueError):
                    aggregate([record], 0, 3)

    def test_invalid_required_field_values(self):
        invalid_values = {
            "tenant": ["", None, 7],
            "event_id": ["", None, 7],
            "at": [True, False, 1.5, "1", None],
            "kind": ["SALE", "", None, 7],
            "amount": [True, False, 0, -1, 1.5, "1", None],
        }
        for field, values in invalid_values.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    with self.assertRaises(ValueError):
                        aggregate([event(**{field: value})], 0, 3)

    def test_invalid_records_are_checked_outside_and_in_empty_window(self):
        missing_tenant = event(event_id="bad", at=9)
        del missing_tenant["tenant"]
        for invalid in [event(event_id="bad", at=9, amount=0), missing_tenant]:
            for start, end in [(0, 2), (1, 1)]:
                with self.subTest(record=invalid, window=(start, end)):
                    with self.assertRaises(ValueError):
                        aggregate([event(), invalid], start, end)

    def test_conflicts_are_checked_globally_in_either_order(self):
        # These are individually valid records sharing an event key.
        # Windows cover both included, one excluded (for changed at), both
        # excluded, and empty. Each required field that can vary for a key is
        # checked independently.
        for changes in [{"at": 2}, {"kind": "refund"}, {"amount": 101}]:
            for start, end in [(0, 3), (1, 2), (3, 4), (1, 1)]:
                for reverse in [False, True]:
                    records = [event(), event(event_id="unrelated"), event(**changes)]
                    if reverse:
                        records.reverse()
                    with self.subTest(changes=changes, window=(start, end), reverse=reverse):
                        with self.assertRaises(ValueError):
                            aggregate(records, start, end)

    def test_success_preserves_input_list_and_dictionaries(self):
        records = [
            event(event_id="later", at=2, extra={"tags": ["keep"]}),
            event(at=-1),
            event(at=-1),
        ]
        snapshot = copy.deepcopy(records)
        original_dicts = list(records)
        try:
            self.assertEqual(aggregate(records, -2, 3), {"alpha": 200})
        finally:
            self.assertEqual(records, snapshot)
            for current, original in zip(records, original_dicts):
                self.assertIs(current, original)

    def test_validation_failure_preserves_input(self):
        cases = [
            ([event(at=2), event(event_id="bad", amount=0)], 0, 3),
            ([event(), event(amount=101)], 0, 3),
            ([event()], 3, 0),
        ]
        for records, start, end in cases:
            snapshot = copy.deepcopy(records)
            original_dicts = list(records)
            with self.subTest(records=records, window=(start, end)):
                try:
                    with self.assertRaises(ValueError):
                        aggregate(records, start, end)
                finally:
                    self.assertEqual(records, snapshot)
                    for current, original in zip(records, original_dicts):
                        self.assertIs(current, original)

    def test_calls_are_independent_and_results_are_new_dictionaries(self):
        records = [event()]
        first = aggregate(records, 0, 3)
        self.assertIsInstance(first, dict)
        self.assertEqual(first, {"alpha": 100})
        first["alpha"] = 999
        first["injected"] = 1

        second = aggregate(records, 0, 3)
        self.assertIsNot(first, second)
        self.assertEqual(second, {"alpha": 100})
        # A different call may reuse an event key without creating a conflict.
        self.assertEqual(aggregate([event(amount=25)], 0, 3), {"alpha": 25})
        self.assertEqual(aggregate(records, 3, 4), {})
        empty = aggregate([], 0, 3)
        empty["injected"] = 1
        self.assertEqual(aggregate([], 0, 3), {})
        self.assertEqual(aggregate(records, 0, 3), {"alpha": 100})


if __name__ == "__main__":
    unittest.main()
