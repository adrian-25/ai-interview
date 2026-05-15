"""Session Wrapper — typed interface for the Session module."""
import logging

from pydantic import ValidationError

from .base_wrapper import BaseAPIWrapper
from .schemas.session_schemas import (
    CreateSessionRequest,
    CreateSessionResponse,
    UpdateSessionRequest,
    UpdateSessionResponse,
    CloseSessionRequest,
    CloseSessionResponse,
)

logger = logging.getLogger(__name__)


class SessionWrapper(BaseAPIWrapper):
    """
    Wrapper for the Session internal module.

    Endpoints (relative to base_url):
        POST /session          → create_session
        PUT  /session/{id}     → update_session
        POST /session/{id}/close → close_session
    """

    def __init__(self, base_url: str) -> None:
        super().__init__(base_url=base_url, module_name="session")

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    async def create_session(self, payload: CreateSessionRequest) -> dict:
        """Create a new interview session."""
        # 1. Validate input
        try:
            data = payload.model_dump(exclude_none=True)
        except ValidationError as exc:
            logger.error("[session] Invalid request schema: %s", exc)
            return self._envelope(
                False,
                data=exc.errors(),
                error="invalid_request_schema",
            )

        # 2. Call base wrapper
        result = await self.post("/session", payload=data)
        if not result["success"]:
            return result

        # 3. Validate response
        try:
            CreateSessionResponse(**result["data"])
        except (ValidationError, TypeError) as exc:
            logger.error("[session] Invalid response schema: %s", exc)
            return self._envelope(
                False,
                data=exc.errors() if isinstance(exc, ValidationError) else str(exc),
                error="invalid_response_schema",
            )

        return result

    async def update_session(self, payload: UpdateSessionRequest) -> dict:
        """Update an existing session's state."""
        # 1. Validate input
        try:
            data = payload.model_dump(exclude_none=True)
        except ValidationError as exc:
            logger.error("[session] Invalid request schema: %s", exc)
            return self._envelope(
                False,
                data=exc.errors(),
                error="invalid_request_schema",
            )

        session_id = data.pop("session_id")

        # 2. Call base wrapper
        result = await self.put(f"/session/{session_id}", payload=data)
        if not result["success"]:
            return result

        # 3. Validate response
        try:
            UpdateSessionResponse(**result["data"])
        except (ValidationError, TypeError) as exc:
            logger.error("[session] Invalid response schema: %s", exc)
            return self._envelope(
                False,
                data=exc.errors() if isinstance(exc, ValidationError) else str(exc),
                error="invalid_response_schema",
            )

        return result

    async def close_session(self, payload: CloseSessionRequest) -> dict:
        """Close a session and record the final score."""
        # 1. Validate input
        try:
            data = payload.model_dump(exclude_none=True)
        except ValidationError as exc:
            logger.error("[session] Invalid request schema: %s", exc)
            return self._envelope(
                False,
                data=exc.errors(),
                error="invalid_request_schema",
            )

        session_id = data.pop("session_id")

        # 2. Call base wrapper
        result = await self.post(f"/session/{session_id}/close", payload=data)
        if not result["success"]:
            return result

        # 3. Validate response
        try:
            CloseSessionResponse(**result["data"])
        except (ValidationError, TypeError) as exc:
            logger.error("[session] Invalid response schema: %s", exc)
            return self._envelope(
                False,
                data=exc.errors() if isinstance(exc, ValidationError) else str(exc),
                error="invalid_response_schema",
            )

        return result
