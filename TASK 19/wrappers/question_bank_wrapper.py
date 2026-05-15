"""Question Bank Wrapper — typed interface for the Question Bank module."""
import logging

from pydantic import ValidationError

from .base_wrapper import BaseAPIWrapper
from .schemas.question_bank_schemas import (
    FetchQuestionRequest,
    FetchQuestionResponse,
    FetchByTopicRequest,
    FetchByTopicResponse,
)

logger = logging.getLogger(__name__)


class QuestionBankWrapper(BaseAPIWrapper):
    """
    Wrapper for the Question Bank internal module.

    Endpoints (relative to base_url):
        GET /question          → fetch_question
        GET /question/by-topic → fetch_by_topic
    """

    def __init__(self, base_url: str) -> None:
        super().__init__(base_url=base_url, module_name="question_bank")

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    async def fetch_question(self, payload: FetchQuestionRequest) -> dict:
        """Fetch a single question by its ID."""
        # 1. Validate input
        try:
            params = payload.model_dump()
        except ValidationError as exc:
            logger.error("[question_bank] Invalid request schema: %s", exc)
            return self._envelope(
                False,
                data=exc.errors(),
                error="invalid_request_schema",
            )

        # 2. Call base wrapper
        result = await self.get("/question", params=params)
        if not result["success"]:
            return result

        # 3. Validate response
        try:
            FetchQuestionResponse(**result["data"])
        except (ValidationError, TypeError) as exc:
            logger.error("[question_bank] Invalid response schema: %s", exc)
            return self._envelope(
                False,
                data=exc.errors() if isinstance(exc, ValidationError) else str(exc),
                error="invalid_response_schema",
            )

        return result

    async def fetch_by_topic(self, payload: FetchByTopicRequest) -> dict:
        """Fetch questions filtered by topic (and optionally difficulty)."""
        # 1. Validate input
        try:
            params = payload.model_dump(exclude_none=True)
        except ValidationError as exc:
            logger.error("[question_bank] Invalid request schema: %s", exc)
            return self._envelope(
                False,
                data=exc.errors(),
                error="invalid_request_schema",
            )

        # 2. Call base wrapper
        result = await self.get("/question/by-topic", params=params)
        if not result["success"]:
            return result

        # 3. Validate response
        try:
            FetchByTopicResponse(**result["data"])
        except (ValidationError, TypeError) as exc:
            logger.error("[question_bank] Invalid response schema: %s", exc)
            return self._envelope(
                False,
                data=exc.errors() if isinstance(exc, ValidationError) else str(exc),
                error="invalid_response_schema",
            )

        return result
