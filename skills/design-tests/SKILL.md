---
name: design-tests
description: "Design and run tests from requirements and plausible failure modes. Use for test strategy, TDD/BDD, regression coverage, or coding interviews with an AI agent."
---

# Design Tests

Build evidence that distinguishes correct behavior from plausible mistakes, within the user's scope and time budget. Respond in the user's language. Adapt to the project's test tools; this skill requires no particular runner or language.

## Establish the contract

Inspect the relevant task, interface, existing tests, and applicable project instructions. Separate intended behavior from observed legacy behavior and assumptions. Identify the entity key, ordering/time rules, error behavior, and side effects when relevant.

If an ambiguity changes the answer, show a small example with the alternative outcomes and ask the necessary question. Continue independent work. Make routine technical choices without asking; do not silently decide consequential business rules.

Use plain Given–When–Then or a few rules/examples when it clarifies behavior. Gherkin and a BDD framework are optional. For interacting conditions or state/history, read [BDD and test design](references/bdd-and-test-design.md).

## Choose discriminating checks

For the most important risks, identify:

| Rule / plausible mistake | Distinguishing input or sequence | Expected result and its basis | Cheapest adequate level |
|---|---|---|---|

Keep this short for small tasks. Do not impose a fixed number of tests or a coverage percentage. Prioritize impact, likelihood, and what current checks miss.

- Derive expected results from the agreed contract, a small manual calculation, or an independently justified oracle. Do not copy the implementation into the expectation.
- Use asymmetric data: distinct values, entities, timestamps and outcomes. Explain which plausible incorrect implementation a key test would reject.
- Choose boundaries for thresholds, decision tables for interacting rules, and action sequences for history. A sequential retry does not check concurrency.
- Use properties or metamorphic relations when their preconditions are valid. Ask what incorrect implementation would still satisfy them. Pair weak properties with known answers; generated inputs should reach meaningful valid behavior, not mostly rejection paths.
- Consider a simpler reference implementation or an external oracle for complex algorithms. Shared helpers and assumptions reduce independence; agreement alone is not proof.
- Test observable behavior at the cheapest level that can expose the failure. Use real integration boundaries when mocks would hide the relevant defect.

Read only the applicable profile:

- [Data and ML](references/data-ml.md): tabular transforms, time-based features, model evaluation.
- [Stateful APIs](references/stateful-api.md): retries, transactions, persistence, concurrency.
- [UI](references/ui.md): user journeys, visual states, accessibility.
- [Test quality](references/test-quality.md): weak assertions, suspicious green runs, mocks, mutation probes, or flaky checks.
- [Interviews](references/interviews.md): a constrained coding session or rehearsal.

## Implement and verify

For meaningful new behavior or a bug fix, use small Red → Green → Refactor cycles. Start with a focused failing check and inspect why it fails. An unavailable dependency is not evidence that the test detects the target defect. A missing API may be an initial scaffolding failure; distinguish it from a demonstrated behavioral regression.

If the user asked only for a plan, review, or tests, stop at that scope. If implementation is authorized, implement the behavior and run the relevant checks. Do not manufacture a retrospective RED by deleting working code when test-first sequencing is no longer applicable; use a justified regression/mutation comparison if valuable.

Never weaken expectations merely to pass. Correct an erroneous test when contract evidence warrants it, and explain the change. Preserve unrelated checks. Inspect skipped tests, swallowed exceptions, test selection, or the imported target when the result is suspicious.

For a material uncovered risk, consider one additional independent check: a property, reference comparison, real integration, or a plausible mutation in an isolated copy. Require behavioral detection, not a syntax/import crash. Mutation testing and a separate reviewer are optional, not mandatory ceremony.

Run checks proportionate to the change. Build/type/lint checks may be adequate for a small reversible edit. Once required checks pass, repeat or broaden only for new changes, failures, or unresolved concerns. Keep mutation artifacts and evaluation work separate from the user's implementation.

## Report evidence and stop

Report the contract decisions that matter, checks actually run, their results, and remaining risks. Tie evidence to the tested revision or file state; never count planned, skipped, blocked, or unrun checks as passed. If execution is unavailable, provide the exact runnable checks and say that results are unverified.

Finish when the agreed behavior has appropriate evidence and required checks pass, or clearly explain the blocker and missing evidence. A large test count, line coverage, or a model's approval is not a substitute for this assessment.
