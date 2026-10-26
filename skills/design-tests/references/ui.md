# User interfaces

Start from a user outcome and the relevant states: ready, loading, empty, validation error, server failure, retry, and success. Select those applicable to the change.

- Use observable behavior and stable accessible roles/names where possible. Avoid binding tests to incidental DOM nesting or CSS classes.
- Assert the meaningful result and side effects. A success banner alone does not prove that data was saved.
- Isolate test data and browser state. Use the framework's condition-based waiting rather than arbitrary sleeps.
- Check keyboard navigation, labels and focus for affected interactions. Automated accessibility checks cover only part of accessibility.
- Use screenshots or direct visual inspection for layout, overflow, readable states and relevant viewports. DOM assertions and visual checks answer different questions.
- Keep most pure business logic below browser level; retain the integration journeys that exercise meaningful wiring.
- Review visual baseline updates. Do not automatically accept a new screenshot because it differs.

Report what was actually exercised, including browser/device limits. Do not present an unvisited screen or a generated screenshot as a successful interaction test.

Source: [Playwright best practices](https://playwright.dev/docs/best-practices).
