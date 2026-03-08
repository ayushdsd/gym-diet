from typing import Optional
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.security import decode_access_token


class GymIsolationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.gym_id = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            token = auth.split(" ", 1)[1]
            try:
                payload = decode_access_token(token)
                gym_id = payload.get("gym_id")
                if gym_id is not None:
                    request.state.gym_id = int(gym_id)
            except Exception:
                pass
        response = await call_next(request)
        return response

