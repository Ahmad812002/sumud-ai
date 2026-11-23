- **Status:** Draft
- **Owners:** Rawand (database and hosting)
- **Reviewer:** Ahmad, Malkawi
- **Date:** 2026-11-17

## Problem
Sumud AI only has a vector database today. It needs a place for user
accounts, credentials, and document metadata, plus a decision on where
everything runs.

## Goals
- Store users and documents with enforced uniqueness and relationships.
- Deploy by Dec 7 with a setup the team can run.
- Keep user data deletable and hosted in an acceptable region.

## Non-goals (v0.1)
- Multi-region, read replicas, analytics.


## Options
**Relational/document database:** PostgreSQL (SQL) · MongoDB (Non-SQL)
**Hosting:** managed service · self-hosted (for the database and for Chroma)

## Criteria and comparison
| Criterion | PostgreSQL | MongoDB | Supabase
|---|---|---|
| Fit for users→documents data | | |
| Team familiarity and speed to Dec 7 | | |
| Cost / hosting options | | |
| Data location (GDPR) | | |


## Decision
<Rawand: choice, hosting, and the reasons>

## Proposed design (if PostgreSQL)

*Proposal by Ahmad. Rawand to confirm or change.*

**Schema**
```sql
users (
  id             UUID PRIMARY KEY,
  email          TEXT UNIQUE NOT NULL,   -- store lowercased
  password_hash  TEXT NOT NULL,          -- Argon2id/bcrypt hash, never the password itself 
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
)

documents (
  id            UUID PRIMARY KEY, 
  user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  fingerprint   TEXT NOT NULL,           -- hash of file content; shared key with Chroma chunks
  file_name      TEXT NOT NULL,
  status        TEXT NOT NULL,           -- uploaded | processing | ready | failed | deleting
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (user_id, fingerprint)
)
-- index on documents(user_id)
```

**Link to Chroma:** `user_id` and `doc_id` are soft references. The database
cannot enforce them across systems. Collection names and chunk metadata are
defined in [001](001-user-id-contract.md).

**Delete order (every step safe to repeat)**
- Delete one document: set `status = deleting`, delete its chunks from Chroma
  by `doc_id`, then delete the row.
- Delete a user: drop their Chroma collections first, then delete the user
  row. `ON DELETE CASCADE` removes the document rows but does not touch Chroma,
  which is why Chroma goes first.
- If a step fails, retry. A failed run leaves a visible `deleting` row.

**Passwords:** store only a salted hash from a maintained library, using
Argon2id (OWASP minimum: 19 MiB memory, 2 iterations, parallelism 1) or
bcrypt. Never store plaintext or encrypted passwords.

## Open questions
- <question>: <owner>, <date>


## Decision log
- 2026-11-17: Draft created.