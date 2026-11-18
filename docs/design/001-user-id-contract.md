# 001: user_id contract between auth and the vector store

- **Status:** Draft
- **Owners:** Ahmad (Chroma layer), Rawand (database and auth)
- **Reviewer:** Malkawi
- **Date:** 2026-11-17

## Problem
Sumud AI is moving from one user to many. Every uploaded document, chunk,
and preference must belong to exactly one user, and no request may ever read
another user's data. Auth (Rawand) and the Chroma layer (Ahmad) are built by
different people, so the interface between them must be written down.

## Goals
- Every endpoint that touches user data knows the caller's `user_id`.
- Chroma reads and writes cannot happen without a `user_id`.
- A user can delete one document, or all their data, and nothing remains in
  the database or in Chroma.

## Non-goals (v0.1)
- Roles or teams, sharing documents between users, social login, billing.

## Proposed design
**Auth side (Rawand).** Login returns a signed token whose subject is the
`user_id` (string UUID). A FastAPI dependency `get_current_user()` validates
the token and returns the `user_id`. All other endpoints depend on it.
[002](002-database-and-hosting.md)


**Chroma side (Ahmad).** One class, `UserScopedStore(user_id)`, wraps
`chroma_db.py`.
Chunks store fingerprint in metadata.
- `delete_document(fingerprint)` removes the chunks, then the database row.
- `delete_all()` removes everything for the user.

**Interface between us.**
```python
user_id: str = Depends(get_current_user)
store = UserScopedStore(user_id)
```

## Alternatives considered
- **One Chroma collection per user (chosen).** Isolation by default, since
  there is no shared data to leak. Deleting a user's data means dropping their
  collections. Each user gets their own per-collection concurrency limits.
  Cost is usage-based, not per-collection, so the collection count adds no
  cost (checked 2026-11-17, https://docs.trychroma.com/cloud/pricing).
- **Shared collection with a `user_id` metadata filter (rejected).** Fewer
  collections, but one missing filter leaks data across users, and all users
  share one collection's concurrency limits.

## Open questions
- Token lifetime and refresh (Rawand).
- Does preferences storage move to the database or stay in Chroma?
- How do we test that user A can never see user B's chunks?
- Should we host it by ourselves or Chroma's cloud?

see [002](002-database-and-hosting.md) file


## Decision log
- 2026-11-17: Draft created.