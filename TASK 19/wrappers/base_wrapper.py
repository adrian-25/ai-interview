"""Base API Wrapper — shared async HTTP client for all module wrappers."""
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 5.0  # seconds


class BaseAPIWrapper:
    """
    Async HTTP wrapper built on httpx.AsyncClient.
    All module wrappers extend this class.

    Every method returns a standardised Response Envelope:
    {
        "success": bool,
        "data": Any,
        "error": str | None,
        "module": str,
        "status_code": int,
    }
    Raw exceptions are never propagated to callers.
    """

    def __init__(self, base_url: str, module_name: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.module_name = module_name

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _envelope(
        self,
        success: bool,
        data: Any = None,
        error: str | None = None,
        status_code: int = 0,
    ) -> dict:
        return {
            "success": success,
            "data": data,
            "error": error,
            "module": self.module_name,
            "status_code": status_code,
        }

    def _handle_response(self, response: httpx.Response) -> dict:
        """Convert an httpx.Response into a Response Envelope."""
        try:
            data = response.json()
        except Exception:
            data = response.text

        if response.is_success:
            return self._envelope(True, data=data, status_code=response.status_code)

        error_msg = f"HTTP {response.status_code}: {response.reason_phrase}"
        logger.error(
            "[%s] Non-2xx response — status=%s body=%s",
            self.module_name,
            response.status_code,
            data,
        )
        return self._envelope(
            False, data=data, error=error_msg, status_code=response.status_code
        )

    def _handle_exception(self, exc: Exception) -> dict:
        """Map known httpx exceptions to standardised error strings."""
        if isinstance(exc, httpx.TimeoutException):
            logger.error("[%s] Request timed out: %s", self.module_name, exc)
            return self._envelope(False, error="timeout")
        if isinstance(exc, httpx.ConnectError):
            logger.error("[%s] Module unreachable: %s", self.module_name, exc)
            return self._envelope(False, error="module_unavailable")
        logger.error("[%s] Unexpected error: %s", self.module_name, exc, exc_info=True)
        return self._envelope(False, error=str(exc))

    # ------------------------------------------------------------------
    # Public HTTP methods
    # ------------------------------------------------------------------

    async def get(self, path: str, params: dict | None = None) -> dict:
        """Async GET request."""
        url = f"{self.base_url}{path}"
        try:
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                response = await client.get(url, params=params)
            return self._handle_response(response)
        except Exception as exc:
            return self._handle_exception(exc)

    async def post(self, path: str, payload: dict | None = None) -> dict:
        """Async POST request."""
        url = f"{self.base_url}{path}"
        try:
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                response = await client.post(url, json=payload)
            return self._handle_response(response)
        except Exception as exc:
            return self._handle_exception(exc)

    async def put(self, path: str, payload: dict | None = None) -> dict:
        """Async PUT request."""
        url = f"{self.base_url}{path}"
        try:
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                response = await client.put(url, json=payload)
            return self._handle_response(response)
        except Exception as exc:
            return self._handle_exception(exc)

    async def delete(self, path: str, params: dict | None = None) -> dict:
        """Async DELETE request."""
        url = f"{self.base_url}{path}"
        try:
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                response = await client.delete(url, params=params)
            return self._handle_response(response)
        except Exception as exc:
            return self._handle_exception(exc)
