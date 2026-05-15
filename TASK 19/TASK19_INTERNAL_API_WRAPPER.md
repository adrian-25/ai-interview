# TASK 19 — Internal API Wrapper Layer

## Overview

This task implements a standardised, fault-tolerant **Internal API Wrapper Layer** for the AI Interview Coach backend. It provides a clean async HTTP interface between the FastAPI application and its internal microservice modules (Decision Engine, Question Bank, Scoring, Session).

---

## Folder Structure

```
TASK 19/
└── wrappers/
    ├── __init__.py                    ← Clean exports for all 4 wrappers
    ├── base_wrapper.py                ← BaseAPIWrapper (httpx.AsyncClient)
    ├── decision_engine_wrapper.py     ← DecisionEngineWrapper
    ├── question_bank_wrapper.py       ← QuestionBankWrapper
    ├── scoring_wrapper.py             ← ScoringWrapper
    ├── session_wrapper.py             ← SessionWrapper
    └── schemas/
        ├── __init__.py                ← Exports all schema classes
        ├── decision_engine_schemas.py ← NextQuestion*, StopDecision*
        ├── question_bank_schemas.py   ← FetchQuestion*, FetchByTopic*
        ├── scoring_schemas.py         ← ScoreAnswer*, SessionScore*
        └── session_schemas.py         ← CreateSession*, UpdateSession*, CloseSession*
```

---

## Stack

| Layer       | Technology              |
|-------------|-------------------------|
| HTTP Client | `httpx.AsyncClient`     |
| Validation  | Pydantic v2             |
| Logging     | Python built-in logging |
| Framework   | FastAPI (async)         |
| Database    | MongoDB via Motor       |

---

## Response Envelope

Every wrapper method returns this exact structure — never raises raw exceptions:

```python
{
    "success": bool,
    "data": Any,
    "error": str | None,   # None on success
    "module": str,         # e.g. "decision_engine"
    "status_code": int,    # 0 on connection/timeout errors
}
```

---

## Error Codes

| Scenario                        | `error` value              |
|---------------------------------|----------------------------|
| Module unreachable              | `"module_unavailable"`     |
| Request timed out (> 5s)        | `"timeout"`                |
| Invalid request Pydantic schema | `"invalid_request_schema"` |
| Invalid response Pydantic schema| `"invalid_response_schema"`|
| Non-2xx HTTP response           | `"HTTP {code}: {reason}"`  |

---

## Usage

```python
from wrappers import DecisionEngineWrapper, QuestionBankWrapper, ScoringWrapper, SessionWrapper
from wrappers.schemas import NextQuestionRequest

# Instantiate with the internal module's base URL
engine = DecisionEngineWrapper(base_url="http://decision-engine-service:8001")

# Call a typed method
result = await engine.get_next_question(
    NextQuestionRequest(
        session_id="64f1a2b3c4d5e6f7a8b9c0d1",
        topic="Python",
        difficulty="medium",
    )
)

if result["success"]:
    print(result["data"])   # validated NextQuestionResponse dict
else:
    print(result["error"])  # e.g. "timeout", "module_unavailable"
```

---

## Wrappers Summary

### DecisionEngineWrapper
| Method               | HTTP       | Endpoint          |
|----------------------|------------|-------------------|
| `get_next_question`  | POST       | `/next-question`  |
| `get_stop_decision`  | POST       | `/stop-decision`  |

### QuestionBankWrapper
| Method           | HTTP | Endpoint              |
|------------------|------|-----------------------|
| `fetch_question` | GET  | `/question`           |
| `fetch_by_topic` | GET  | `/question/by-topic`  |

### ScoringWrapper
| Method              | HTTP | Endpoint         |
|---------------------|------|------------------|
| `score_answer`      | POST | `/score/answer`  |
| `get_session_score` | GET  | `/score/session` |

### SessionWrapper
| Method           | HTTP | Endpoint                  |
|------------------|------|---------------------------|
| `create_session` | POST | `/session`                |
| `update_session` | PUT  | `/session/{id}`           |
| `close_session`  | POST | `/session/{id}/close`     |

---

## Integration with Existing Backend

Add `httpx` to `backend/requirements.txt`:
```
httpx==0.25.2
```

Copy the `wrappers/` folder into `backend/` and import directly:
```python
from wrappers import SessionWrapper
```
