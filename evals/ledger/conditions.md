# Conditions used in the first comparison

One fresh agent context per condition. The contract and stub were identical. Workspace paths are replaced by `<workspace>` and `<skill-root>` below; other instructions are preserved.

## Baseline

```text
Work only in <workspace>. Read TASK.md and the stub ledger.py there.
Complete the task in TASK.md: write a focused, useful unittest suite from
the contract, run it, and report actual results. Do not implement ledger.py,
install dependencies, read adjacent evaluation folders or repository research,
use other skills, or delegate. This is a standalone test-authoring task with no
production access. Preserve the provided contract. Aim for a practical
interview-sized suite rather than an exhaustive framework. Return a concise
report with written files and observed test results.
```

## Skill

```text
Use $design-tests at <skill-root>/SKILL.md for this task. Work only in
<workspace>, except reading that skill and the references it routes to.
Read TASK.md and the stub ledger.py there. Complete TASK.md: write a focused,
useful unittest suite from the contract, run it, and report actual results.
Do not implement ledger.py, install dependencies, read adjacent evaluation
folders or repository research, or delegate. This is a standalone
test-authoring task with no production access. Preserve the provided contract.
Aim for a practical interview-sized suite rather than an exhaustive framework.
Return a concise report with written files and observed test results.
```

## Small edit

```text
Use $design-tests at <skill-root>/SKILL.md. The user's request is:
'Fix the typo Requsets to Requests in README.md.' Work only in <workspace>,
except reading the named skill and relevant references. Complete the request
and report what you actually checked. Do not access adjacent evaluation
folders, install dependencies, use network access, or delegate.
```

The input file contained:

```markdown
# Requests

Requsets are processed in arrival order.
```
