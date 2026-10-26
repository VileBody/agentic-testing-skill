"""Contract tests for ledger.aggregate; run with python3 -m unittest -v."""

from copy import deepcopy
import unittest

import ledger


def event(tenant="alpha", event_id="e1", at=4, kind="sale", amount=11, **extra):
    return dict(tenant=tenant, event_id=event_id, at=at,
                kind=kind, amount=amount, **extra)


class AggregateTests(unittest.TestCase):
    def aggregate_unchanged(self, records, start, end):
        before = deepcopy(records)
        try:
            return ledger.aggregate(records, start, end)
        finally:
            # Also checked if aggregation raises, including expected ValueErrors.
            self.assertEqual(records, before, "aggregate mutated its input")

    def test_sales_refunds_and_tenant_identity_keep_zero_and_negative_totals(self):
        records = [
            event("alpha", "shared", at=8, amount=19),
            event("beta", "shared", at=3, kind="refund", amount=7),
            event("zero", "sale", at=1, amount=5),
            event("alpha", "return", at=2, kind="refund", amount=6),
            event("zero", "return", at=7, kind="refund", amount=5),
            event("beta", "other", at=6, amount=2),
            # Nonempty strings need not be stripped, and one cent is valid.
            event(" ", " ", at=5, amount=1),
        ]
        expected = {"alpha": 13, "beta": -5, "zero": 0, " ": 1}
        for ordered in (records, list(reversed(records))):
            with self.subTest(order=[row["at"] for row in ordered]):
                result = self.aggregate_unchanged(ordered, 0, 10)
                self.assertIsInstance(result, dict)
                self.assertEqual(result, expected)

    def test_half_open_window_with_negative_timestamps(self):
        records = [
            event("at_end", at=5, amount=101),
            event("inside", "start", at=-5, amount=17),
            event("before", at=-6, amount=103),
            event("inside", "last", at=4, kind="refund", amount=3),
            event("after", at=6, amount=107),
        ]
        self.assertEqual(self.aggregate_unchanged(records, -5, 5), {"inside": 14})

    def test_empty_input_empty_window_and_no_matching_events(self):
        cases = [([], -3, 7), ([], 0, 0),
                 ([event(at=4)], 4, 4), ([event(at=-1)], 0, 10)]
        for records, start, end in cases:
            with self.subTest(records=records, start=start, end=end):
                result = self.aggregate_unchanged(records, start, end)
                self.assertIsInstance(result, dict)
                self.assertEqual(result, {})

    def test_duplicates_ignore_extra_fields_and_do_not_require_adjacency(self):
        first = event("alpha", "shared", amount=11, metadata={"tags": [1]})
        records = [
            first,
            event("beta", "shared", kind="refund", amount=7),
            event("alpha", "other", amount=3),
            dict(first),
            event("alpha", "shared", amount=11, metadata=["different"]),
        ]
        for ordered in (records, list(reversed(records))):
            with self.subTest(order=[row["tenant"] for row in ordered]):
                self.assertEqual(self.aggregate_unchanged(ordered, 0, 10),
                                 {"alpha": 14, "beta": -7})

    def test_conflicts_are_global_and_order_independent(self):
        pairs = [
            ("amount inside", event(), event(amount=12)),
            ("kind inside", event(), event(kind="refund")),
            ("timestamp inside", event(), event(at=5)),
            ("one outside", event(), event(at=-1)),
            ("both outside timestamp", event(at=-2), event(at=12)),
            ("both outside amount", event(at=-2), event(at=-2, amount=12)),
            ("both outside kind", event(at=12), event(at=12, kind="refund")),
        ]
        for name, first, second in pairs:
            for ordered in ([first, second], [second, first]):
                with self.subTest(case=name, first=ordered[0]):
                    with self.assertRaises(ValueError):
                        self.aggregate_unchanged(ordered, 0, 10)

    def test_missing_required_fields_are_rejected_even_outside_window(self):
        for field in ("tenant", "event_id", "at", "kind", "amount"):
            bad = event(at=-1)
            del bad[field]
            with self.subTest(missing=field):
                with self.assertRaises(ValueError):
                    self.aggregate_unchanged([event(event_id="valid"), bad], 0, 10)

    def test_invalid_field_values_are_rejected_even_outside_window(self):
        invalid = {
            "tenant": ("", None, 7),
            "event_id": ("", None, 7),
            "at": (True, False, 4.0, "4", None),
            "kind": ("SALE", "other", "", None, 1),
            "amount": (0, -1, True, False, 11.0, "11", None),
        }
        for field, values in invalid.items():
            for value in values:
                bad = event(at=-1)
                bad[field] = value
                with self.subTest(field=field, value=value):
                    with self.assertRaises(ValueError):
                        self.aggregate_unchanged([event(event_id="valid"), bad], 20, 30)

    def test_boolean_duplicate_is_validated_before_deduplication(self):
        # Python equates True with 1, but the contract rejects boolean values.
        for field in ("at", "amount"):
            valid = event(at=1, amount=1)
            bad = dict(valid, **{field: True})
            for ordered in ([valid, bad], [bad, valid]):
                with self.subTest(field=field, first=ordered[0]):
                    with self.assertRaises(ValueError):
                        self.aggregate_unchanged(ordered, 0, 10)

    def test_empty_window_still_validates_records_and_conflicts(self):
        for records in ([event(amount=0)], [event(), event(amount=12)]):
            with self.subTest(records=records):
                with self.assertRaises(ValueError):
                    self.aggregate_unchanged(records, 4, 4)

    def test_invalid_windows_are_rejected_even_for_empty_input(self):
        windows = [(2, 1)]
        for invalid in (True, False, 0.0, "0", None):
            windows.extend([(invalid, 10), (-10, invalid)])
        for start, end in windows:
            with self.subTest(start=start, end=end):
                with self.assertRaises(ValueError):
                    self.aggregate_unchanged([], start, end)

    def test_calls_have_no_shared_state_and_return_new_dictionaries(self):
        records = [event(amount=7)]
        first = self.aggregate_unchanged(records, 0, 10)
        self.assertEqual(first, {"alpha": 7})
        first["alpha"] = 999
        first["injected"] = 1
        second = self.aggregate_unchanged(records, 0, 10)
        self.assertEqual(second, {"alpha": 7})
        self.assertIsNot(first, second)
        self.assertIsNot(second, records[0])
        self.assertEqual(self.aggregate_unchanged(
            [event(kind="refund", amount=3)], 0, 10), {"alpha": -3})
        empty = self.aggregate_unchanged([], 0, 10)
        self.assertEqual(empty, {})
        self.assertIsNot(empty, self.aggregate_unchanged([], 0, 10))


if __name__ == "__main__":
    unittest.main()
