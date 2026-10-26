# Check whether the tests deserve trust

Use for suspicious green results, test review, independent oracles, or a high-impact gap. Investigate concrete concerns rather than auditing the entire harness for every edit.

## False-green checks

- Did the runner collect and select the intended tests? Distinguish zero tests, skips, expected failures, and passes.
- Did execution import the edited implementation rather than an installed copy or mock of the target?
- Does each relevant path reach a meaningful assertion? Look for early returns, empty loops, swallowed exceptions and vacuous generators.
- Was expected computed independently? Calling the SUT twice or copying its branch logic proves little.
- Does a mock hide the boundary whose correctness matters? Verify important adapters against reality at an appropriate level.
- Is the log from the final tested state? An old green result does not cover later edits.
- Were snapshots, tolerances, skips or test selection changed to conceal a failure?

## Oracles and generated cases

Use explicit manually checked answers for small examples. A simple reference may be suitable for complex code, but avoid sharing the production algorithm or helpers. When both implementations are untrusted, a difference identifies an investigation, not which one is correct.

Generate meaningful valid structures and target rare states, not just random primitives. Treat invalid inputs as their own class. Inspect excessive filtering, unreachable assertions, and weak properties. Save a minimized failing example as a readable regression; retain reproduction information when necessary.

Snapshot updates need a semantic reason. LLM judges can help with subjective quality, but exact state or arithmetic should use deterministic checks. Do not require an internal call order unless the order itself is contractual.

## Mutation probes

Choose a plausible mistake tied to a requirement. Use a disposable copy or a tool's isolated mutation environment; preserve uncommitted user work. Establish a passing baseline, apply the mutation, run the relevant check, inspect its failure, and discard or restore the isolated artifact.

A kill caused by a syntax error, broken import or setup exception does not demonstrate behavioral sensitivity. A surviving mutation may be equivalent on the valid domain or outside scope. Investigate rather than adding assertions merely to raise a score. Do not leave a mutation in the implementation.

## Flakiness and cost

Control clocks, random sources, shared state, network behavior and concurrency schedules when applicable. Test cleanup and resource release for relevant failures. Repeated successful retries do not explain an intermittent failure.

For performance, distinguish resource growth and operation counts from noisy wall-clock thresholds. Record the workload and environment. Do not weaken a contractual limit to make a benchmark pass; explain measurement limitations.

Sources: [Google on behavior](https://testing.googleblog.com/2013/08/testing-on-toilet-test-behavior-not.html), [Hypothesis](https://hypothesis.readthedocs.io/en/latest/reference/integrations.html), [mutmut](https://mutmut.readthedocs.io/en/latest/), [pytest flakiness](https://docs.pytest.org/en/stable/explanation/flaky.html).
