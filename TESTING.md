Testing notes (manual + automated)

Manual checklist:
- Register a user, login, create warehouses, add products, request export.
- Try accessing another user's warehouse (should be forbidden).
- Invalid inputs e.g., missing title on product should return 422.

Automated (pytest) planned tests:
- Successful login
- User isolation: User B cannot see User A's data
- Duplicate registration -> 409
- Export lifecycle: pending -> completed
