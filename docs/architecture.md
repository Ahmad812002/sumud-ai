# Sumud AI: Backend Architecture

> Audience: everyone who changes the backend (Ahmad, Omar, Rawand, and future contributors).
> Status: written after the error-handling and folder cleanup. If a file or folder moves, update this document in the same pull request.

---

## 1. The one rule that matters: layers and dependency direction

```
Frontend (src/services/api.js)
        |  HTTP
        v
 routers/            HTTP only
        |
        v
 business_logic/     rules and orchestration
        |
        v
 data_access/        reads and writes data
        |
        v
 clients/            outside providers (LLM, embeddings, Supabase)
```

**Calls only go downward, one layer at a time.** Routers call `business_logic`, `business_logic` calls `data_access`, and `data_access` calls `clients`. Routers never call Chroma, the LLM or Supabase directly. A lower layer never imports a higher one.

| Layer | Folder | Its job | It must NOT |
|---|---|---|---|
| Frontend | `frontend/src/services/api.js` | Send requests, turn error responses into one `ApiError` | Contain business rules |
| Router | `routers/` | Validate input shape and file basics, call ONE `business_logic` function, return the result and choose the success status (200/201) | Contain logic, call Chroma/LLM/Supabase, catch exceptions |
| Business logic | `business_logic/` | Business rules: dedupe, chunking, thresholds, building prompts, order of steps | Know about HTTP (`HTTPException`, `JSONResponse`, status codes) |
| Data access | `data_access/` | Read and write storage, reshape results into plain lists/dicts | Make business decisions (for example thresholds) or return HTTP objects |
| Clients | `clients/` | Talk to ONE outside provider each (LLM, embedding API, Supabase). Translate provider errors into our exceptions | Contain business rules |

Why this matters: each layer can be tested and changed alone. If `data_access` returned HTTP responses, it could never be reused from a script or a test.

---

## 2. Folder map: what each folder is for and which files go in it

### Root files

- `main.py`: creates the app, registers the routers, and holds the global exception handlers and `STATUS_MAP`.
- `exceptions.py`: ALL domain exceptions live here. It imports nothing from the app, so every layer can import it.

### `routers/`

HTTP layer. One router file per resource; each endpoint calls one `business_logic` function and returns its result.

- Current files: `chat.py`, `coverletter.py`, `documents.py`, `initialize_router.py`, `preferences.py`, `scorer.py`.
- Add a new file here when you add a new resource (name it after the resource).
- No logic, no `try/except`, no `HTTPException`.

### `business_logic/`

The rules of the product, and the order in which steps happen.

- Current files: `chat_logic.py`, `cover_letter_logic.py`, `embeddings_logic.py`, `preferences_logic.py`, `scorer_logic.py`.
- Add a new `<feature>_logic.py` here for each new feature.
- Raises our exceptions. Never touches HTTP.

### `data_access/`

Reads and writes data. Reshapes raw results into plain lists and dicts, with no decisions.

- Current files: `db.py`, `embeddings.py`, `document_reader.py` (file to text).
- Add a file here when a new kind of storage or file reading is needed.
- Wraps storage failures in our exceptions (`VectorStoreError`, `DocumentReadError`, ...) with `raise ... from e`.

### `clients/`

One file per outside provider. This is where provider errors are translated.

- Current files: `llm.py`, `embedding_client.py`, `client.py` (builds the LLM client), `supabase_client.py`.
- Add a new file here for each new outside provider.
- Wraps provider failures in our exceptions (`LLMServiceError`, `EmbeddingServiceError`, ...) with `raise ... from e`.

### `config/`

Configuration that is not code logic.

- Current files: `prompts.py`.
- Add prompt-building functions to `prompts.py`. Shared constants (thresholds, chunk sizes) belong in `config/` too.

### `utils/`

Small pure helpers with no outside calls.

- Current files: `fingerprint.py`.
- Add a helper here only if it has no side effects and is used by more than one place.

### `knowledge_base/` and `temporary/`

Runtime folders for uploaded documents.

- `temporary/`: where an upload is saved while it is being processed. Files here are removed after every request.
- `knowledge_base/`: where processed documents are kept.
- No source code goes here. Both hold users' private files and stay out of git.

### `frontend/`

The React app. All calls to the backend go through `src/services/api.js`, so errors are handled in one place.

### `docs/`

Project documentation, including this file.

---

## 3. Error handling

### 3.1 Principles

1. **Raise our own exceptions, never HTTP ones, below the router.** No `HTTPException`, no `JSONResponse` in `business_logic`, `data_access` or `clients`.
2. **Translate at the boundary.** Where code touches an outside system (Chroma, the LLM API, Supabase, a file parser), wrap its failures once in one of our exceptions, always with `raise ... from e`.
3. **Do not wrap twice.** A function that only calls already-wrapped code has no `try/except`. Extra `except Exception` blocks hide the real cause.
4. **Never return an error as a normal value.** No `{"error": ...}` dicts and no "Couldn't generate a response" sentence inside a 200. A function returns its result or raises.
5. **Users get a safe `message`; developers get `details` in the log.** Provider text, counts and reasons go in `details` and are never sent to the client.
6. **Real bugs stay plain exceptions.** A `KeyError` or `TypeError` from our own code is not wrapped. It reaches the catch-all handler, is logged with the full traceback, and the user gets a generic 500.

### 3.2 Errors travel up

```
clients / data_access raises  ->  business_logic lets it pass  ->  router lets it pass
                                                               ->  global handler in main.py
                                                               ->  JSON + status code
                                                               ->  api.js wraps it in ApiError
                                                               ->  UI shows the message
```

Only the global handler decides the status code.

### 3.3 Status codes (`STATUS_MAP` in `main.py`)

Pick the code by asking: who failed, and who can fix it?

| Exception | Status | Meaning |
|---|---|---|
| `SumudError` (fallback) | 400 | Unmapped domain error |
| `InvalidInputError` | 400 | Bad input |
| `DocumentError` | 422 | The request is valid but the file is unusable |
| `EmptyFileError`, `DocumentReadError` | 422 | Empty, corrupted or password-protected file |
| `DuplicateDocumentError`, `UserAlreadyExistsError` | 409 | Already exists |
| `UnsupportedFileTypeError` | 415 | File type not allowed |
| `VectorStoreError`, `DatabaseError` | 503 | Our own storage is unavailable |
| `ExternalServiceError`, `EmbeddingServiceError`, `LLMServiceError`, `LLMResponseError` | 502 | A provider failed or returned something unusable |
| `LLMUnavailableError` | 503 | Provider overloaded or rate limiting us, try again |
| `LLMTimeoutError` | 504 | Provider took too long |
| anything else (not a `SumudError`) | 500 | A bug: logged with full traceback |

Never use 401/403 for infrastructure problems (they mean "not logged in" and "not allowed"), 404 for an unreadable file, or 501 for a bad AI answer.

### 3.4 The global handler (`main.py`)

- Looks up the status in `STATUS_MAP`.
- Logs the traceback (`exc_info=exc`) for 5xx errors or when the error wraps a cause, together with `exc.details`.
- Returns `{"detail": exc.message}`. `details` is never sent to the client.
- A second catch-all handler for plain `Exception` logs the traceback and returns a generic 500.

### 3.5 Library errors we translate (examples)

- **Chroma**: `store_embeddings`, `search_embedding`, `document_exists` wrap every failure in `VectorStoreError(..., details={...}) from e`.
- **Embedding API**: `get_embeddings` raises `EmbeddingServiceError` and checks that the number of vectors equals the number of texts.
- **LLM API**: `_call_llm` in `clients/llm.py` (see section 5).
- **File parsers**: `read_document` wraps parser failures in `DocumentReadError`.
- **Supabase auth**: use a small lookup from Supabase's `e.code` to our exception, with the provider text kept in `details`:

```python
SIGNUP_ERRORS = {
    "email_exists":  (UserAlreadyExistsError, "An account with this email already exists"),
    "weak_password": (InvalidInputError,      "The password does not meet the requirements"),
}
error_class, message = SIGNUP_ERRORS.get(e.code, (ExternalServiceError, "Sign up failed"))
raise error_class(message, details={"supabase_code": e.code, "reason": e.message}) from e
```

- **Multi-step writes need rollback.** If step 2 fails after step 1 succeeded (profile insert after user creation), undo step 1 in its own `try/except`. If the rollback fails, log it at `critical` with the ids needed for manual cleanup.

### 3.6 Validate where the data enters

Check the cheap things first: duplicate, empty, extension, length. Do the expensive things (parsing, embedding, LLM) after.

---

## 4. RAG conventions

- **Documents and queries use different embedding modes.** Stored chunks use `task_type="search_document"`. Search queries use `task_type="search_query"`. Do not mix them without a measured reason, and write the reason down.
- **Chunk ids**: `"<fingerprint>_<chunk number>"`. The fingerprint is a hash of the whole file and is the same for every chunk of that file.
- **Batch everything**: one embedding call for all chunks of a document, one `collection.add` for all of them. `ids`, `documents`, `embeddings`, `metadatas` must all have the same length (one metadata dict per chunk).
- **Shapes**: `get_embeddings([text])` returns `[[...vector...]]`. A single query vector is `...[0]`. Check the shape at every handoff.
- **Duplicates**: the fingerprint is checked once per document, before any embedding work.
- **Distance, not similarity**: Chroma returns distances. Lower is closer. The default metric is squared L2, not cosine. Thresholds depend on the metric and the embedding mode, so re-tune them after changing either.
- **Chunks that are too short or blank** are skipped. Very large documents may exceed Chroma's batch limit (`client.get_max_batch_size()`); split the `add` into batches if that happens.
- **Empty retrieval is a real case.** Prompts must handle "no relevant context" (for example, tell the user the information is not in their documents) and must not invent facts.

---

## 5. LLM conventions (`clients/llm.py`)

- **All LLM calls go through `_call_llm(feature, timeout, **kwargs)`.** It is the only place that talks to the provider and the only place that translates provider errors.
- `except` order: **child classes before parent classes.** `openai.APIError` is the parent of all SDK errors and must be last:
  `APITimeoutError` -> `RateLimitError` -> `InternalServerError` -> `AuthenticationError` -> `APIError`.
- The public functions (`llm_scorer`, `llm_chat`, `llm_cover_letter`) return a **non-empty string or raise**. Callers never check for `None` or error dicts.
- Truncated output (`finish_reason == "length"`), empty output and "no choices" raise `LLMResponseError`.
- JSON replies are parsed in `business_logic` with `json.loads`; a `JSONDecodeError` becomes `LLMResponseError`.
- **Timeouts and retries**: total wait is roughly `timeout x (1 + retries)`, because the SDK also retries timeouts and 5xx errors. Set timeouts per feature (scorer short, cover letter longer) and keep retries low for slow calls.
- **`reasoning_effort="high"` is slow and capacity-hungry.** Use it only where quality needs it.
- A 503 from the provider (`UNAVAILABLE`, "high demand") is temporary and not our bug. It maps to `LLMUnavailableError`.

---

## 6. Logging and privacy

- Use `logging`, not `print`. Configure it once at startup (`logging.basicConfig(level=logging.INFO)`), or info-level lines will not appear.
- **Never log user content**: no document text, CV content, prompts or model replies. Log metadata only (feature name, counts, lengths, token usage, ids).
- `details` may contain reasons, counts and names. It must not contain secrets or user text.
- Running in Docker: set `PYTHONUNBUFFERED=1`, and read logs with `docker compose logs -f`.
- Files in `knowledge_base/` and `temporary/`, and the Chroma database files, are private user data. Keep them out of git (`.gitignore`).

---

## 7. How to add a feature (checklist)

1. **Schema**: define request and response models.
2. **Router** (`routers/`): one function that calls one `business_logic` function and returns its result. No `try/except`, no logic.
3. **Business logic** (`business_logic/`): validate input (raise `InvalidInputError`), apply the rules, build the prompt, return a dict.
4. **Data access and clients** (`data_access/`, `clients/`): only if a new storage or outside provider is needed. Wrap its errors, raise our exceptions with `from e`.
5. **Exceptions**: reuse an existing class if it describes the cause. If a new one is truly needed, add it to `exceptions.py` and to `STATUS_MAP`.
6. **Frontend**: call it through `api.js` so errors become `ApiError`; show a loading state for slow AI calls.
7. **Test** the happy path and at least one failure path.

---

## 8. Pull request checklist

- [ ] Layers respected: router calls only `business_logic`, `business_logic` calls only `data_access`, `data_access` calls `clients`.
- [ ] No `HTTPException` or `JSONResponse` below the router (success responses in routers are fine).
- [ ] No `except Exception` that re-labels an already-typed error. Broad `except` only at a boundary with an outside library, always with `from e`.
- [ ] Every raised exception exists in `exceptions.py` and has a line in `STATUS_MAP`.
- [ ] No function returns an error value (`None`, `{"error": ...}`) where it should raise.
- [ ] No `print`, and nothing logs user content.
- [ ] No mutable default arguments (`def f(x=[])`). Use `None`.
- [ ] Shapes are checked where lists of vectors or chunks move between functions.
- [ ] Type hints tell the truth (`list[list[float]]`, not `str`).
- [ ] No uploaded or private files are committed.
- [ ] The three upload tests still pass (see section 9).

---

## 9. Testing

Manual smoke test after any change to ingestion or errors:

1. Upload a new valid file: expect **201**.
2. Upload the same file again: expect **409**.
3. Upload an empty file: expect **422**.

Recommended next step: automated tests with `pytest` and FastAPI's `TestClient` for those three cases, plus a mocked LLM failure (expect 502) and a stopped vector store (expect 503). Error-handling code runs rarely, so it is the least-tested code; test it on purpose.

---

## 10. Known gaps and backlog

| Priority | Item |
|---|---|
| High | Re-tune the distance threshold with real English and German queries (log distances for related and unrelated texts). |
| High | Check German retrieval quality; `nomic-embed-text-v1.5` may be weak for German. Evaluate a multilingual embedding model. |
| High | Make "nothing relevant found" an explicit, visible result in the scorer instead of an OK response with an empty value. |
| Medium | Automated tests for the failure paths. |
| Medium | Frontend: show errors by status and message, loading states for 60-90 second AI calls. |
| Medium | Per-feature LLM timeouts and reasoning effort. |
| Medium | The cover-letter request currently carries scorer output from the client. For multi-user, store results server-side and send an id. |
| Medium | Standard error body with a stable machine-readable `code` (for example `DUPLICATE_DOCUMENT`) so the frontend does not depend on message text. |
| Low | Chat has no conversation history; each message is answered alone. |
| Low | Decide what to do when two different files share a name in `knowledge_base/`. |