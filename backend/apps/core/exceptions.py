"""
Centralized exception handler for DRF.
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Returns consistent error response format:
    {
        "success": false,
        "error": { "code": "...", "message": "..." }
    }
    """
    response = exception_handler(exc, context)

    if response is not None:
        custom_data = {
            'success': False,
            'error': {
                'code': response.status_code,
                'message': _extract_message(response.data),
            }
        }
        response.data = custom_data
        return response

    # Unhandled exceptions – return 500
    return Response(
        {
            'success': False,
            'error': {
                'code': 500,
                'message': 'An unexpected error occurred.',
            }
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def _extract_message(data):
    """Flatten DRF error dict into a readable string."""
    if isinstance(data, list):
        return ' '.join(str(item) for item in data)
    if isinstance(data, dict):
        messages = []
        for key, value in data.items():
            if isinstance(value, list):
                messages.append(f"{key}: {' '.join(str(v) for v in value)}")
            else:
                messages.append(f"{key}: {value}")
        return ' | '.join(messages)
    return str(data)
