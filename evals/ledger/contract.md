# Ledger aggregation task

Write standard-library unittest tests for `ledger.aggregate(records, start, end)`. Do not implement the function. The provided stub is intentionally unimplemented. Use explicit expected results derived from this contract. Keep the suite suitable for a coding interview.

`records` is a list of dictionaries. Each record requires these five fields:

- `tenant`: a nonempty string.
- `event_id`: a nonempty string.
- `at`: an integer timestamp; negative timestamps are valid. Booleans are not valid timestamps.
- `kind`: exactly `"sale"` or `"refund"`.
- `amount`: a strictly positive integer number of cents. Booleans are not valid amounts.

Additional fields may be present and do not affect validation, identity, or aggregation. Missing required fields or invalid values raise `ValueError`.

`start` and `end` must be integer timestamps, excluding booleans, with `start <= end`. Otherwise raise `ValueError`. An equal start and end defines an empty window.

Validate all records, including records outside the time window. Identify events by `(tenant, event_id)` across the entire input. Repeated occurrences with equal values of the five required fields are one event. If the same event key has conflicting required-field values, raise `ValueError`, even when one or both occurrences are outside the window. Extra fields do not create a conflict.

Include each unique event whose timestamp satisfies `start <= at < end`. A sale adds its amount; a refund subtracts its amount. Return a new dictionary mapping each tenant with at least one included event to its net cents. Keep zero and negative totals. Omit tenants with no included events. Output dictionary iteration order is not specified.

An empty input returns `{}` for a valid window. Do not mutate the input list or its dictionaries, including when validation fails. Input order must not change the outcome or conflict detection. There is no persistent state across calls.

Write `test_ledger.py`. Run the tests against the stub and report the observed result honestly. Do not install dependencies or change `ledger.py`. A short note may explain the most important cases and remaining limitations.
