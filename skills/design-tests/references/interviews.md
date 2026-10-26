# Interviews and short sessions

Respect the provided time budget; if absent, keep a focused approach without inventing a hard deadline. Discuss essential semantics early and keep producing a reviewable solution.

Start with a short contract and a few high-impact risks. Choose small examples that distinguish those risks. Use a decision table for interacting conditions and a sequence for history only when helpful.

For a typical 45-minute exercise, an adjustable allocation is roughly five minutes for understanding, seven for initial checks, eighteen for implementation with further checks, eight for the largest remaining risk, and seven for final verification and explanation. This is a heuristic, not a gate or a required timer.

Prefer tools already available. Hand-picked cases may be enough; adding a generator, Gherkin runner, mutation framework or reviewer must earn its cost. Do not require a property test just to satisfy a checklist.

Keep a tiny matrix if useful:

| Rule / plausible mistake | Input | Expected and basis | Check | Observed status |
|---|---|---|---|---|

Before finishing, explain the solution, actual checks and the most important untested risk. If a requirement remains ambiguous, describe both interpretations and what was implemented or left provisional. Do not claim completeness from the number of tests.

Example request:

> Use $design-tests for this 45-minute exercise. Identify the main failure modes, choose discriminating checks, then implement and verify the solution. Keep the setup small and explain unresolved business rules.
