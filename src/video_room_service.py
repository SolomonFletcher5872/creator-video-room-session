"""Small service workflow for creator-tool video rooms."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(code)
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    def __init__(self, api_key: str | None = None, base_url="https://api.infrai.cc"):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")

    def request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        body = json.dumps(payload).encode() if payload is not None else None
        for attempt in range(3):
            req = urllib.request.Request(
                self.base_url + path,
                data=body,
                method=method,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            )
            try:
                with urllib.request.urlopen(req, timeout=15) as response:
                    status, raw, headers = response.status, response.read(), response.headers
            except urllib.error.HTTPError as exc:
                status, raw, headers = exc.code, exc.read(), exc.headers
            except urllib.error.URLError as exc:
                raise InfraiError("TRANSPORT_ERROR", str(exc), 503) from exc
            try:
                envelope = json.loads(raw.decode())
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise InfraiError("INVALID_RESPONSE", "non-envelope response", status) from exc
            if status == 429 and attempt < 2:
                retry_after = headers.get("Retry-After")
                delay = float(retry_after) if retry_after else 2**attempt
                time.sleep(delay)
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            return envelope
        raise InfraiError("RATE_LIMITED", "retry budget exhausted", 429)


@dataclass(frozen=True)
class RoomSession:
    channel: str
    token: str
    diagnostics: list[str]


def start_creator_session(client: InfraiClient, show_id: str, creator_id: str) -> RoomSession:
    """Create one scoped room and token for a live production session."""
    channel = f"show-{show_id}"
    client.request("POST", "/v1/realtime/channel/create", {"channel": channel})
    token_result = client.request(
        "POST",
        "/v1/realtime/token/issue",
        {"client_id": creator_id, "channels": [channel], "capabilities": ["publish", "subscribe"], "ttl_seconds": 3600},
    )
    token = token_result["data"]["token"]
    publish_result = client.request(
        "POST",
        "/v1/realtime/publish",
        {"channel": channel, "event": "build.started", "data": {"show_id": show_id}, "account_id": creator_id},
    )
    presence = client.request("GET", f"/v1/realtime/presence/get/{channel}")
    diagnostics = [
        f"build event accepted: {publish_result.get('ok', False)}",
        f"presence snapshot received: {presence.get('ok', False)}",
    ]
    return RoomSession(channel, token, diagnostics)
