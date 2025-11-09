from typing import Any, Dict


def success_response(message: str, data: Any = None) -> Dict:
    return {"status": "success", "message": message, "data": data}


def error_response(message: str, errors: Any = None) -> Dict:
    return {"status": "error", "message": message, "errors": errors}
