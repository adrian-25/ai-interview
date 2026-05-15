# Requirements Document

## Introduction

This feature introduces an Internal API Wrapper Layer for the AI Interview Coach backend. The layer provides a standardized, fault-tolerant interface for making async HTTP calls to internal microservice modules (Decision Engine, Question Bank, Scoring, and Session). Each wrapper validates inputs and outputs using Pydantic v2 schemas, handles all error conditions gracefully, and always returns a consistent response envelope — never raising raw exceptions to callers.

## Glossary

- **BaseAPIWrapper**: The abstract base class that all module wrappers extend. Manages an `httpx.AsyncClient` and exposes generic HTTP methods.
- **Module Wrapper**: A concrete wrapper class (e.g., `DecisionEngineWrapper`) that extends `BaseAPIWrapper` and exposes domain-specific async methods.
- **Response Envelope**: The standardized dict returned by every wrapper method: `{ "success": bool, "data": any, "error": str | None, "module": str, "status_code": int }`.
- **Schema**: A Pydantic v2 model used to validate request payloads before sending and response payloads after receiving.
- **Internal Module**: A separate backend service (Decision Engine, Question Bank, Scoring, Session) reachable via HTTP.
- **httpx**: The async HTTP client library used for all outbound calls.
- **Pydantic_v2**: The data validation library (version 2.x) used for all schema definitions.

---

## Requirements

### Requirement 1: Base Wrapper Infrastructure

**User Story:** As a backend developer, I want a reusable base wrapper class, so that all module wrappers share consistent HTTP behavior, timeout handling, and response formatting.

#### Acceptance Criteria

1. THE `BaseAPIWrapper` SHALL accept `base_url: str` and `module_name: str` as constructor parameters.
2. THE `BaseAPIWrapper` SHALL use `httpx.AsyncClient` for all outbound HTTP calls.
3. THE `BaseAPIWrapper` SHALL apply a default timeout of 5 seconds to every HTTP call.
4. WHEN an HTTP call completes successfully with a 2xx status code, THE `BaseAPIWrapper` SHALL return a Response Envelope with `"success": true`, the parsed response body in `"data"`, `"error": null`, the module name in `"module"`, and the HTTP status code in `"status_code"`.
5. WHEN an `httpx.TimeoutException` is raised, THE `BaseAPIWrapper` SHALL return a Response Envelope with `"success": false`, `"data": null`, `"error": "timeout"`, the module name in `"module"`, and `"status_code": 0`.
6. WHEN an `httpx.ConnectError` is raised, THE `BaseAPIWrapper` SHALL return a Response Envelope with `"success": false`, `"data": null`, `"error": "module_unavailable"`, the module name in `"module"`, and `"status_code": 0`.
7. WHEN any other unexpected exception is raised, THE `BaseAPIWrapper` SHALL return a Response Envelope with `"success": false`, `"data": null`, `"error"` containing the exception message, the module name in `"module"`, and `"status_code": 0`.
8. WHEN an HTTP response has a non-2xx status code, THE `BaseAPIWrapper` SHALL return a Response Envelope with `"success": false`, the response body in `"data"`, `"error"` containing the HTTP error description, the module name in `"module"`, and the actual HTTP status code in `"status_code"`.
9. THE `BaseAPIWrapper` SHALL expose async methods `get()`, `post()`, `put()`, and `delete()` corresponding to the HTTP verbs.
10. THE `BaseAPIWrapper` SHALL never raise a raw exception to its callers.

---

### Requirement 2: Pydantic v2 Schemas

**User Story:** As a backend developer, I want typed Pydantic v2 request and response schemas for each internal module, so that data contracts are enforced at the boundary of every wrapper call.

#### Acceptance Criteria

1. THE `decision_engine_schemas` module SHALL define `NextQuestionRequest`, `NextQuestionResponse`, `StopDecisionRequest`, and `StopDecisionResponse` as Pydantic v2 `BaseModel` subclasses.
2. THE `question_bank_schemas` module SHALL define `FetchQuestionRequest`, `FetchQuestionResponse`, `FetchByTopicRequest`, and `FetchByTopicResponse` as Pydantic v2 `BaseModel` subclasses.
3. THE `scoring_schemas` module SHALL define `ScoreAnswerRequest`, `ScoreAnswerResponse`, `SessionScoreRequest`, and `SessionScoreResponse` as Pydantic v2 `BaseModel` subclasses.
4. THE `session_schemas` module SHALL define `CreateSessionRequest`, `CreateSessionResponse`, `UpdateSessionRequest`, `UpdateSessionResponse`, `CloseSessionRequest`, and `CloseSessionResponse` as Pydantic v2 `BaseModel` subclasses.
5. THE Schema definitions SHALL represent all MongoDB document IDs as `str` fields, not as `ObjectId` or `bson` types.
6. THE Schema definitions SHALL use Pydantic v2 field declarations and validators (e.g., `model_validator`, `field_validator`) where appropriate.

---

### Requirement 3: Decision Engine Wrapper

**User Story:** As a backend developer, I want a `DecisionEngineWrapper` that exposes typed methods for the decision engine module, so that callers can request the next interview question or a stop decision with validated inputs and outputs.

#### Acceptance Criteria

1. THE `DecisionEngineWrapper` SHALL extend `BaseAPIWrapper`.
2. THE `DecisionEngineWrapper` SHALL expose an async method `get_next_question(payload: NextQuestionRequest) -> dict`.
3. THE `DecisionEngineWrapper` SHALL expose an async method `get_stop_decision(payload: StopDecisionRequest) -> dict`.
4. WHEN `get_next_question` is called with a valid `NextQuestionRequest`, THE `DecisionEngineWrapper` SHALL call the base wrapper's `post()` method with the serialized payload and validate the response against `NextQuestionResponse`.
5. WHEN `get_stop_decision` is called with a valid `StopDecisionRequest`, THE `DecisionEngineWrapper` SHALL call the base wrapper's `post()` method with the serialized payload and validate the response against `StopDecisionResponse`.
6. WHEN the input payload fails Pydantic validation specifically, THE `DecisionEngineWrapper` SHALL return a Response Envelope with `"success": false`, `"error": "invalid_request_schema"`, and Pydantic validation details in `"data"`; input validation errors SHALL take precedence over response validation errors.
7. WHEN the response body fails Pydantic validation against the expected response schema, THE `DecisionEngineWrapper` SHALL return a Response Envelope with `"success": false`, `"error": "invalid_response_schema"`, and Pydantic validation details in `"data"`.
8. WHEN an internal error occurs during the base wrapper `post()` call, THE `DecisionEngineWrapper` SHALL return a Response Envelope with `"success": false` and `"error"` containing a description of the internal failure.

---

### Requirement 4: Question Bank Wrapper

**User Story:** As a backend developer, I want a `QuestionBankWrapper` that exposes typed methods for the question bank module, so that callers can fetch individual questions or questions by topic with validated inputs and outputs.

#### Acceptance Criteria

1. THE `QuestionBankWrapper` SHALL extend `BaseAPIWrapper`.
2. THE `QuestionBankWrapper` SHALL expose an async method `fetch_question(payload: FetchQuestionRequest) -> dict`.
3. THE `QuestionBankWrapper` SHALL expose an async method `fetch_by_topic(payload: FetchByTopicRequest) -> dict`.
4. WHEN `fetch_question` is called with a valid `FetchQuestionRequest`, THE `QuestionBankWrapper` SHALL call the base wrapper's `get()` method with the serialized payload and validate the response against `FetchQuestionResponse`.
5. WHEN `fetch_by_topic` is called with a valid `FetchByTopicRequest`, THE `QuestionBankWrapper` SHALL call the base wrapper's `get()` method with the serialized payload and validate the response against `FetchByTopicResponse`.
6. WHEN the input payload fails Pydantic validation specifically, THE `QuestionBankWrapper` SHALL return a Response Envelope with `"success": false`, `"error": "invalid_request_schema"`, and Pydantic validation details in `"data"`; input validation errors SHALL take precedence over response validation errors.
7. WHEN the response body fails Pydantic validation against the expected response schema, THE `QuestionBankWrapper` SHALL return a Response Envelope with `"success": false`, `"error": "invalid_response_schema"`, and Pydantic validation details in `"data"`.

---

### Requirement 5: Scoring Wrapper

**User Story:** As a backend developer, I want a `ScoringWrapper` that exposes typed methods for the scoring module, so that callers can score individual answers or retrieve session-level scores with validated inputs and outputs.

#### Acceptance Criteria

1. THE `ScoringWrapper` SHALL extend `BaseAPIWrapper`.
2. THE `ScoringWrapper` SHALL expose an async method `score_answer(payload: ScoreAnswerRequest) -> dict`.
3. THE `ScoringWrapper` SHALL expose an async method `get_session_score(payload: SessionScoreRequest) -> dict`.
4. WHEN `score_answer` is called with a valid `ScoreAnswerRequest`, THE `ScoringWrapper` SHALL call the base wrapper's `post()` method with the serialized payload and validate the response against `ScoreAnswerResponse`.
5. WHEN `get_session_score` is called with a valid `SessionScoreRequest`, THE `ScoringWrapper` SHALL call the base wrapper's `get()` method with the serialized payload and validate the response against `SessionScoreResponse`.
6. WHEN the input payload fails Pydantic validation specifically, THE `ScoringWrapper` SHALL return a Response Envelope with `"success": false`, `"error": "invalid_request_schema"`, and Pydantic validation details in `"data"`; input validation errors SHALL take precedence over response validation errors.
7. WHEN the response body fails Pydantic validation against the expected response schema, THE `ScoringWrapper` SHALL return a Response Envelope with `"success": false`, `"error": "invalid_response_schema"`, and Pydantic validation details in `"data"`.

---

### Requirement 6: Session Wrapper

**User Story:** As a backend developer, I want a `SessionWrapper` that exposes typed methods for the session module, so that callers can create, update, and close interview sessions with validated inputs and outputs.

#### Acceptance Criteria

1. THE `SessionWrapper` SHALL extend `BaseAPIWrapper`.
2. THE `SessionWrapper` SHALL expose an async method `create_session(payload: CreateSessionRequest) -> dict`.
3. THE `SessionWrapper` SHALL expose an async method `update_session(payload: UpdateSessionRequest) -> dict`.
4. THE `SessionWrapper` SHALL expose an async method `close_session(payload: CloseSessionRequest) -> dict`.
5. WHEN `create_session` is called with a valid `CreateSessionRequest`, THE `SessionWrapper` SHALL call the base wrapper's `post()` method with the serialized payload and validate the response against `CreateSessionResponse`.
6. WHEN `update_session` is called with a valid `UpdateSessionRequest`, THE `SessionWrapper` SHALL call the base wrapper's `put()` method with the serialized payload and validate the response against `UpdateSessionResponse`.
7. WHEN `close_session` is called with a valid `CloseSessionRequest`, THE `SessionWrapper` SHALL call the base wrapper's `post()` method with the serialized payload and validate the response against `CloseSessionResponse`.
8. WHEN the input payload fails Pydantic validation specifically, THE `SessionWrapper` SHALL return a Response Envelope with `"success": false`, `"error": "invalid_request_schema"`, and Pydantic validation details in `"data"`; input validation errors SHALL take precedence over response validation errors.
9. WHEN the response body fails Pydantic validation against the expected response schema, THE `SessionWrapper` SHALL return a Response Envelope with `"success": false`, `"error": "invalid_response_schema"`, and Pydantic validation details in `"data"`.

---

### Requirement 7: Error Handling and Logging

**User Story:** As a backend developer, I want all wrapper errors to be logged and returned in a standardized format, so that I can diagnose failures without the wrapper layer crashing the application.

#### Acceptance Criteria

1. WHEN any error condition occurs (timeout, connection failure, schema mismatch, non-2xx response), THE Wrapper Layer SHALL log the error using Python's built-in `logging` module at the `ERROR` level before returning the Response Envelope.
2. WHEN a non-2xx HTTP response is received from an internal module, THE Wrapper Layer SHALL log the status code and response body at the `ERROR` level.
3. THE Wrapper Layer SHALL never propagate raw exceptions to callers; all exceptions SHALL be caught and converted to a Response Envelope.

---

### Requirement 8: Package Exports

**User Story:** As a backend developer, I want to import all four wrappers from a single `wrappers` package, so that integration is straightforward and consistent.

#### Acceptance Criteria

1. THE `wrappers/__init__.py` SHALL export `DecisionEngineWrapper`, `QuestionBankWrapper`, `ScoringWrapper`, and `SessionWrapper`.
2. WHEN a caller writes `from wrappers import DecisionEngineWrapper`, THE import SHALL resolve without error.
3. THE `wrappers/schemas/__init__.py` SHALL export all schema classes from all four schema modules.
