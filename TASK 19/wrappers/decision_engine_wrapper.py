"""Decision Engine Wrapper — typed interface for the Decision Engine module."""
import logging

from pydantic import ValidationError

from .base_wrapper import BaseAPIWrapper
from .schemas.decision_engine_schemas import (
    NextQuestionRequest,
    NextQuestionResponse,
    StopDecisionRequest,
    StopDecisionResponse,
)

logger = logging.getLogger(__name__)


class DecisionEngineWrapper(BaseAPIWrapper):
    """
    Wrapper for the Decision Engine internal module.

    Endpoints (relative to base_url):
        POST /next-question   → get_next_question
        POST /stop-decision   → get_stop_decision
    """

    def __init__(self, base_url: str) -> None:
        super().__init__(base_url=base_url, module_name="decision_engine")

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    async def get_next_question(self, payload: NextQuestionRequest) -> dict:
        """Request the next interview question from the Decision Engine."""
        # 1. Validate input
        try:
            data = payload.model_dump()
        except ValidationError as exc:
            logger.error("[decision_engine] Invalid request schema: %s", exc)
            return self._envelope(
                False,
                data=exc.errors(),
                error="invalid_request_schema",
            )

        # 2. Call base wrapper
        result = await self.post("/next-question", payload=data)
        if not result["success"]:
            return result

        # 3. Validate response
        try:
            NextQuestionResponse(**result["data"])
        except (ValidationError, TypeError) as exc:
            logger.error("[decision_engine] Invalid response schema: %s", exc)
            return self._envelope(
                False,
                data=exc.errors() if isinstance(exc, ValidationError) else str(exc),
                error="invalid_response_schema",
            )

        return result

    async def get_stop_decision(self, payload: StopDecisionRequest) -> dict:
        """Ask the Decision Engine whether the session should stop."""
        # 1. Validate input
        try:
            data = payload.model_dump()
        except ValidationError as exc:
            logger.error("[decision_engine] Invalid request schema: %s", exc)
            return self._envelope(
                False,
                data=exc.errors(),
                error="invalid_request_schema",
            )

        # 2. Call base wrapper
        result = await self.post("/stop-decision", payload=data)
        if not result["success"]:
            return result

        # 3. Validate response
        try:
            StopDecisionResponse(**result["data"])
        except (ValidationError, TypeError) as exc:
            logger.error("[decision_engine] Invalid response schema: %s", exc)
            return self._envelope(
                False,
                data=exc.errors() if isinstance(exc, ValidationError) else str(exc),
                error="invalid_response_schema",
            )

        return result
