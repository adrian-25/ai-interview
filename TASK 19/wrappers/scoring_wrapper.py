"""Scoring Wrapper — typed interface for the Scoring module."""
import logging

from pydantic import ValidationError

from .base_wrapper import BaseAPIWrapper
from .schemas.scoring_schemas import (
    ScoreAnswerRequest,
    ScoreAnswerResponse,
    SessionScoreRequest,
    SessionScoreResponse,
)

logger = logging.getLogger(__name__)


class ScoringWrapper(BaseAPIWrapper):
    """
    Wrapper for the Scoring internal module.

    Endpoints (relative to base_url):
        POST /score/answer   → score_answer
        GET  /score/session  → get_session_score
    """

    def __init__(self, base_url: str) -> None:
        super().__init__(base_url=base_url, module_name="scoring")

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    async def score_answer(self, payload: ScoreAnswerRequest) -> dict:
        """Score a single candidate answer."""
        # 1. Validate input
        try:
            data = payload.model_dump(exclude_none=True)
        except ValidationError as exc:
            logger.error("[scoring] Invalid request schema: %s", exc)
            return self._envelope(
                False,
                data=exc.errors(),
                error="invalid_request_schema",
            )

        # 2. Call base wrapper
        result = await self.post("/score/answer", payload=data)
        if not result["success"]:
            return result

        # 3. Validate response
        try:
            ScoreAnswerResponse(**result["data"])
        except (ValidationError, TypeError) as exc:
            logger.error("[scoring] Invalid response schema: %s", exc)
            return self._envelope(
                False,
                data=exc.errors() if isinstance(exc, ValidationError) else str(exc),
                error="invalid_response_schema",
            )

        return result

    async def get_session_score(self, payload: SessionScoreRequest) -> dict:
        """Retrieve the aggregate score for an entire session."""
        # 1. Validate input
        try:
            params = payload.model_dump()
        except ValidationError as exc:
            logger.error("[scoring] Invalid request schema: %s", exc)
            return self._envelope(
                False,
                data=exc.errors(),
                error="invalid_request_schema",
            )

        # 2. Call base wrapper
        result = await self.get("/score/session", params=params)
        if not result["success"]:
            return result

        # 3. Validate response
        try:
            SessionScoreResponse(**result["data"])
        except (ValidationError, TypeError) as exc:
            logger.error("[scoring] Invalid response schema: %s", exc)
            return self._envelope(
                False,
                data=exc.errors() if isinstance(exc, ValidationError) else str(exc),
                error="invalid_response_schema",
            )

        return result
