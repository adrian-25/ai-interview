# Task B10 — Negative Marking Engine

## 1. Task Overview

| Field | Value |
|-------|-------|
| **Difficulty** | Easy |
| **Duration** | 1 Week |
| **Objective** | Calculate penalties for incorrect answers |

Negative marking is a required backend feature: when a candidate answers
incorrectly, points are deducted from their score rather than simply not
being awarded. This module provides a small, deterministic, reusable
engine for that calculation, plus a thin FastAPI layer so it can be
called as a service from other modules (e.g. the Scoring module
described in the Internal API Wrapper Layer).

---

## 2. Formula

```
final_score = correct - (wrong * penalty_per_wrong)
```

Default `penalty_per_wrong = 0.25`.

### Worked example (from the spec)

```json
Input:  { "correct": 8, "wrong": 2 }
Output: { "final_score": 7.5 }
```

`8 - (2 * 0.25) = 8 - 0.5 = 7.5` ✅

---

## 3. API

### POST `/score`

**Request body**

```json
{
  "correct": 8,
  "wrong": 2
}
```

**Response body**

```json
{
  "final_score": 7.5
}
```

### GET `/config`

Returns the current penalty configuration, for transparency/debugging:

```json
{ "penalty_per_wrong": 0.25 }
```

### GET `/health`

```json
{ "status": "healthy" }
```

---

## 4. Constraints & Edge Cases

| Case | Behaviour |
|------|-----------|
| `wrong` is missing | Defaults to `0` |
| `correct` is missing | Defaults to `0` |
| Both missing | `final_score` = `0` |
| `correct` or `wrong` is negative | **Rejected** — you cannot have a negative count of answers. Returns `422` (Pydantic schema validation) or `400` (engine-level validation, if called directly without the schema) |
| Resulting `final_score` is negative | **Allowed.** This is the expected outcome of negative marking (e.g. many wrong answers, few/no correct ones) — it is not an error condition |
| Floating point artifacts (e.g. `7.499999999999999`) | Result is rounded to 4 decimal places |
| Non-numeric input (e.g. `"eight"`) | Rejected with a clear validation error |
| Custom penalty scheme (e.g. `-0.5` per wrong, or `0` for no negative marking) | Supported via `NegativeMarkingEngine(penalty_per_wrong=...)` constructor argument — no code changes needed |

---

## 5. File Structure

```
TASK B10/
├── negative_marking_engine.py        # Core calculation logic (pure, no FastAPI dependency)
├── main.py                           # Standalone FastAPI app
├── test_negative_marking_engine.py   # Unit tests (20 cases)
├── requirements.txt                  # fastapi, uvicorn, pydantic
├── routes/
│   ├── __init__.py
│   └── scoring.py                    # Mountable APIRouter blueprint (POST /score, GET /score/config)
└── TASKB10_NEGATIVE_MARKING.md        # This document
```

`negative_marking_engine.py` has **zero FastAPI/Pydantic dependencies** —
it's a plain Python module so it can be unit-tested in isolation, reused
by other internal modules (e.g. wrapped by `ScoringWrapper` from the
Internal API Wrapper Layer), or imported directly into a script.

---

## 6. Running Instructions

### Install dependencies

```bash
cd "TASK B10"
pip install -r requirements.txt
```

### Run the API

```bash
python main.py
# or
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000/docs` for interactive Swagger UI.

### Run the tests

```bash
python -m unittest test_negative_marking_engine -v
```

### Quick manual test

```bash
curl -X POST http://localhost:8000/score \
  -H "Content-Type: application/json" \
  -d '{"correct": 8, "wrong": 2}'
# -> {"final_score":7.5}
```

### Use as a standalone Python function (no server needed)

```python
from negative_marking_engine import calculate_score

calculate_score(correct=8, wrong=2)
# -> {"final_score": 7.5}
```

---

## 7. Integrating with the Existing Backend

To mount this as a router inside the main `backend/` FastAPI app
(alongside `auth`, `sessions`, `dashboard`):

```python
# backend/main.py
from routes.scoring import router as scoring_router
app.include_router(scoring_router)
```

Or, to call it from the Internal API Wrapper Layer's `ScoringWrapper`
as part of `score_answer` / `get_session_score`, the
`NegativeMarkingEngine` class can be used directly inside that service
rather than over HTTP, since it has no external dependencies.

---

## 8. Deliverables & Acceptance Criteria

- [x] `final_score = correct - (wrong * penalty_per_wrong)`, default penalty `0.25`
- [x] Matches the exact spec example: `{correct: 8, wrong: 2}` → `{final_score: 7.5}`
- [x] Missing `correct`/`wrong` handled gracefully (default to 0)
- [x] Negative `final_score` results are supported, not blocked
- [x] Negative *input counts* are rejected with a clear error
- [x] Deterministic: same input always produces the same output
- [x] Configurable penalty (no hardcoded values that require a code change to tune)
- [x] 20 unit tests covering the formula and all edge cases
- [x] Mountable FastAPI router for integration into the larger backend
