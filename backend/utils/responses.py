"""Standardized API response utilities."""
from typing import Any, Optional


def success_response(data: Any, message: Optional[str] = None) -> dict:
    """Create a standardized success response."""
    response = {
        "success": True,
        "data": data
    }
    if message:
        response["message"] = message
    return response


def error_response(error: str, code: Optional[str] = None, details: Optional[dict] = None) -> dict:
    """Create a standardized error response."""
    response = {
        "success": False,
        "error": {
            "message": error
        }
    }
    if code:
        response["error"]["code"] = code
    if details:
        response["error"]["details"] = details
    return response
