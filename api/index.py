"""Vercel ASGI entrypoint for the Intervals.icu MCP server.

The MCP endpoint is exposed at /api (the Vercel function route).
Set INTERVALS_ICU_API_KEY, INTERVALS_ICU_ATHLETE_ID and MCP_AUTH_TOKEN
in the Vercel project environment variables before enabling the deployment.
"""
import hmac
import json
import os
import sys
from pathlib import Path
from typing import Any

# The project uses a src/ layout and is imported directly from the repository.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from intervals_icu_mcp.server import mcp  # noqa: E402

_token = os.environ.get("MCP_AUTH_TOKEN", "")
if not _token:
    raise RuntimeError("MCP_AUTH_TOKEN must be configured in the Vercel project.")

_mcp_app = mcp.http_app(path="/", stateless_http=True)


class BearerTokenMiddleware:
    """Require a private bearer token before forwarding requests to MCP."""

    def __init__(self, app: Any, token: str) -> None:
        self.app = app
        self.token = token.encode("utf-8")

    async def __call__(self, scope: dict, receive: Any, send: Any) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        authorization = headers.get(b"authorization", b"")
        expected = b"Bearer " + self.token
        if not hmac.compare_digest(authorization, expected):
            body = json.dumps({"error": "Unauthorized"}).encode("utf-8")
            await send({
                "type": "http.response.start",
                "status": 401,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"content-length", str(len(body)).encode("ascii")),
                    (b"www-authenticate", b'Bearer realm="Intervals.icu MCP"'),
                ],
            })
            await send({"type": "http.response.body", "body": body})
            return

        await self.app(scope, receive, send)


app = BearerTokenMiddleware(_mcp_app, _token)
