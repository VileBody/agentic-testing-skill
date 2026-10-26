# Stateful APIs and integrations

Select checks that exercise the relevant boundary. Unit tests of an in-memory fake do not establish transaction isolation or real-provider compatibility.

## Establish the state contract

Identify actors, ownership scope, operation IDs, states, allowed transitions, side effects, persistence, and error behavior. Determine whether authorization must precede lookup or mutation. Separate business identity from a transport-level request ID.

For idempotency, establish key scope, payload comparison, retention/expiry, retry responses, and concurrent-first-request behavior. A repeated key with different payload or a delayed retry after deletion may need a specific policy; do not invent one silently.

## Select useful sequences

| Situation | Evidence to seek |
|---|---|
| Response lost after commit | Retry returns the promised result and does not repeat the effect |
| Failure before commit | No forbidden partial state; subsequent retry behaves correctly |
| Concurrent first requests | Real uniqueness/transaction mechanism prevents the defined duplicate effect |
| Restart between effect and retry | Persistence meets the promised recovery behavior |
| Same local key, another actor | Correct isolation and authorization |
| Cancellation or timeout | Defined resulting state and resource cleanup |

Use barriers, controlled scheduling or appropriate state-machine tooling rather than assuming a sleep will reliably expose a race. Check both safety and progress where required.

## Integration and compatibility

Choose a real adapter/database check when its behavior is material. Consumer/provider contract tests check shared messages; they do not prove the entire business workflow. Schema compatibility alone may miss semantic changes.

Test relevant old payloads, missing/unknown fields, failure responses and migration behavior according to the supported contract. Verify important external effects rather than only a status code. Keep fixtures disposable and within the environment authorized for the task.

Sources: [AWS idempotency](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/), [Pact](https://docs.pact.io/), [Hypothesis stateful tests](https://hypothesis.readthedocs.io/en/latest/stateful.html), [OWASP ASVS](https://asvs.owasp.org/).
