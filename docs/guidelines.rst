.. _guidelines:

Guidelines
==========

The idea of this document is to make a guide for software source code quality. The guidelines appearing in this apply
to any individual who create, alters, or reads the source code. This document is not a description of a complete
software process and can be updated in the future by the maintainers and/or community.

Code Style
----------

- Code is readable and maintainable. If you need to add too many comments to describe your code, then it is a sign of poor readability (this does not apply always). Code must be self-documenting.
- Should comply PEP8 with the following exceptions:
  - maximum line length is 120 characters (instead of 80 as in PEP 8 E501).
  - models.py, where it’s allowed to break the 120 characters rule for the properties of a model.
- Variable naming is good and constant everywhere (coupon vs. voucher).
- Length and complexity of functions should be reduced as much as possible but don't create silly functions.
- Avoid magic constants or numbers. Incorrect: if len(password) > 7: error Correct: if len(password) > MAX_PASSWORD_SIZE: error
- Don’t create a commit to undo anything from a previous commit, we should rebase the previous commit to undo the unneeded changes instead.

Design principles
-----------------

- `KISS <https://bit.ly/1RtTg5j>`_ - Simplicity should be a key goal in design, and unnecessary complexity should be avoided.
- `Yagni <https://bit.ly/1gerxtF>`_ - Don’t add functionality until deemed necessary. Yagni only applies to capabilities built into the software to support a presumptive feature, it does not apply to efforts to make the software easier to modify.
- `DRY <https://bit.ly/1hQ65ME>`_ - Remove duplication in logic via abstraction.

Pull Requests & Code Reviews
----------------------------

- Before merging, it’s responsibility of the author to see if the branch is up-to-date (rebased on top of the latest commit) and the reviewer to confirm this . This way we avoid to merge two branches at the same time that can clash themselves and may leave potentially a red CI status.
- The title of the pull request should be descriptive but short. For example: Add validators to API endpoint /projects
- Use the pull request template to better explain how and which kind of changes you have done. It also should have the issue number inside for feature/change tracking.
- Commit message <= 70 characters, meaningful and written in imperative. Incorrect: “Fixing property“. Correct: “Make User.email char type”.
- Keep the scope of the ticket to solve and leave extra commits for a separate pull requests. It’s fine to add small refactors but not the refactoring of an entire class, otherwise, you will be asked to create a task and another pull request for it.
- If the pull request is too big, consider to divide it in two or more parts. It’s not recommended and comfortable to review very long pull requests. Divide and conquer!
- It fully complies the Acceptance Criteria of the ticket.
- How to QA should be in the body if it’s not clear or detailed enough in the ticket.
- In case of DB and serializer changes, keep a special attention to migrations and backwards compatibility.
- Tested with unit and integration tests (test cover all possible cases).
- Check for efficiency, especially in database queries.
