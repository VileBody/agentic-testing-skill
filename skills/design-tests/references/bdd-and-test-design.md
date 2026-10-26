# Discover behavior and select cases

Use this when rules interact, history matters, or the expected result is unclear. Do not turn every task into a specification workshop.

## Rules, examples, questions

Capture the rule, a concrete example, and any unresolved question separately. Given describes relevant context; When describes an event; Then describes observable outcomes and side effects. Unknown outcomes remain questions. A Scenario Outline only covers the rows actually selected.

Example: an order is committed, its response is lost, and the client retries. The outcome must specify both the response and whether another order exists. This does not cover two simultaneous first requests; that requires a different sequence and execution setup.

For each consequential ambiguity, give two possible outcomes on the same small input. This makes the decision reviewable without a long questionnaire. Explicit assumptions may support a provisional plan when the user permits them; do not present them as established requirements.

## Match the technique to the risk

| Risk | Design move |
|---|---|
| Broad input domain | Identify behaviorally different equivalence classes |
| Threshold or interval | Below / equal / above; both ends, including inclusivity |
| Interacting conditions | Decision table with reachable combinations and rule priority |
| State/history | State × event table, valid and invalid transitions, representative sequences |
| Many settings | Consider t-way combinations, plus known high-risk interactions |
| Hard oracle | Valid metamorphic relations plus independently known examples |
| Optimization | Simple reference comparison on varied small inputs |

Do not confuse absent data, an empty collection, and a nonempty collection with no valid members. For numeric boundaries choose meaningful adjacent values; floating-point tolerances require a reason.

For a decision table, mark infeasible combinations and unspecified outcomes. If multiple errors can occur at once, establish which error or set of errors is acceptable. Pairwise testing cannot guarantee coverage of higher-order interactions.

For stateful behavior, test both returned values and state changes. Separate safety (an invalid effect never occurs) from progress (the operation eventually completes under stated conditions). State coverage alone may miss important transitions and sequences.

## Choose distinguishing examples

Avoid data symmetry that hides errors: identical bitstreams hide swaps, one tenant hides incorrect scoping, ordered timestamps hide dependence on input order, and identical output values hide alignment errors.

Name the plausible mutant in words before writing a key test: inclusive instead of exclusive bound, grouping by an incomplete key, counting every revision, accepting a stale write, or retaining a side effect after failure. Keep these examples hypothetical until actually tested.

For properties, state the domain and compare the correct entities. A row permutation may preserve results by entity while changing output order. Sorting requires both ordering and preservation of the input multiset; returning an empty list satisfies ordering alone. Encoder/decoder round trips may share the same standards violation.

Sources: [Cucumber BDD](https://cucumber.io/docs/bdd/), [Example Mapping](https://cucumber.io/blog/bdd/example-mapping-introduction/), [Gherkin](https://cucumber.io/docs/gherkin/reference/), [ISTQB syllabus](https://istqb.org/?download_id=3345&sdm_process_download=1), [NIST combinations](https://csrc.nist.gov/Projects/automated-combinatorial-testing-for-software/combinatorial-methods-in-testing/interactions-involved-in-software-failures).
