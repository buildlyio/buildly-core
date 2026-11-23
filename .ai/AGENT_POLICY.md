# Buildly AI Agent Policy

> **Scope:** All AI-assisted development in this repository

---

## Purpose

This policy defines how AI coding assistants (GitHub Copilot, Claude, Cursor, ChatGPT, etc.) are used within Buildly development workflows. AI accelerates development—but humans own understanding, quality, and accountability.

---

## Core Principles

### AI Handles
- Scaffolding and boilerplate code
- Repetitive refactors and migrations
- Test generation and expansion
- Documentation drafts
- Code formatting and linting fixes
- Standard CRUD operations
- Pattern-based implementations

### Humans Own
- Architecture decisions
- Business logic design
- Security-sensitive code (auth, encryption, access control)
- Third-party integrations
- Creative and novel implementations
- Performance-critical algorithms
- Final review and approval

---

## Required Artifacts

Every feature, bugfix, or change must include:

| Artifact | Required | Description |
|----------|----------|-------------|
| Work Item ID | Yes | Labs feature, GitHub issue, or punchlist item |
| Implementation Summary | Yes | Clear description of what was done |
| AI Self-Review | Yes | AI's own assessment of the code |
| Human Understanding Confirmation | Yes | Engineer confirms they understand the code |
| Documentation Updates | If applicable | README, API docs, inline comments |
| Tests | Yes | Unit, integration, or e2e tests as appropriate |

---

## Prohibited Practices

1. **Blind Merging**: Never merge AI-generated code without understanding it
2. **Untraceable Changes**: Every change must link to a work item
3. **Broad Rewrites**: Avoid large-scale AI refactors without explicit approval
4. **Security Delegation**: Never let AI write auth, billing, or encryption logic without expert review
5. **Copy-Paste Development**: Don't accept AI suggestions without validation

---

## Code Standards

### Readability First
- Small, focused diffs
- Clear variable and function names
- Comments for non-obvious logic
- Consistent formatting

### Minimal Changes
- Only modify what's necessary
- Don't "improve" unrelated code
- Preserve existing patterns unless explicitly changing them

### Traceability Always
- Link to work items in commits and PRs
- Document AI assistance in PRs
- Explain non-obvious decisions

---

## Review Requirements

Before any PR can be merged:

1. **Human Can Explain**: The author must be able to explain every line of code
2. **Traceability Exists**: Work item ID is present and valid
3. **Risks Acknowledged**: Edge cases and potential issues are documented
4. **Tests Pass**: All automated tests are green
5. **Docs Updated**: Relevant documentation reflects the change

---

## Enforcement

This policy is enforced through:

- PR templates requiring disclosure and confirmation
- Code review checklists
- Automated checks where possible
- Team accountability

---

## Philosophy

> **The AI handles the boring parts. The engineer owns understanding and originality.**

AI is a force multiplier, not a replacement for engineering judgment. Use it to move faster on routine work so you can invest more thought in the work that matters.

---

*This policy is part of the [Buildly AI Engineering Standard](../ops/standards/ai-engineering-standard.md).*
