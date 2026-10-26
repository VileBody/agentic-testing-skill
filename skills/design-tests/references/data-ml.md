# Data transformations and ML

Read only the relevant part. A deterministic data function does not need model evaluation machinery.

## Tabular transformations

Establish the complete entity key, uniqueness rules, time semantics, missing-value policy, output cardinality, ordering/index behavior and mutation policy. Do not infer these from a convenient pandas expression.

Choose asymmetric examples: the same local ID in different groups, groups with different results, out-of-order timestamps, revisions that change the winner, and nontrivial indices. If duplicate index labels are allowed, test positional alignment as well as label preservation. Check joins for unintended row multiplication or dropping.

Distinguish an empty table, a group with no valid values, zero, and missing. Establish allowed types and coercions: booleans can behave as integers in Python. Error handling should not silently remove invalid records unless that is the contract.

For optimized operations, a small loop-based oracle can help. Derive it from the rules, not by translating each vectorized step. Properties need preconditions: row-order invariance is invalid when order is meaningful or tie handling is unspecified.

## ML: separate four kinds of evidence

| Layer | Appropriate checks |
|---|---|
| Program correctness | Metrics on hand-calculated examples; feature transforms; threshold boundaries |
| Data/pipeline correctness | Keys, missingness, fit on permitted data, as-of joins, feature availability |
| Statistical quality | Baselines, suitable splits, uncertainty, relevant slices, calibration |
| Operation | Training/serving consistency, versioned artifacts, drift and resource behavior |

Choose temporal/group/random splitting according to the generalization claim. For historical features distinguish event time from availability time. Disjoint row IDs do not prevent leakage through related entities. A Pipeline helps with preprocessing but does not exclude every leakage mechanism.

Specify the metric and threshold-selection protocol; do not equate average precision with every definition of PR-AUC. Keep final test data out of tuning. Use seeds for reproducibility and repeated runs when assessing variation; a reproducible run is not evidence of robustness.

Do not require an arbitrary score or statistical cutoff absent a task requirement. A green metric-unit-test proves the calculation on its inputs, not future predictive quality.

Sources: [scikit-learn pitfalls](https://scikit-learn.org/stable/common_pitfalls.html), [ML Test Score](https://research.google/pubs/the-ml-test-score-a-rubric-for-ml-production-readiness-and-technical-debt-reduction/).
