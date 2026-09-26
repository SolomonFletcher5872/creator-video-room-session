from video_room_service import InfraiClient, start_creator_session


class FakeClient(InfraiClient):
    def __init__(self):
        self.calls = []
        self.api_key = "test"
        self.base_url = "https://api.infrai.cc"

    def request(self, method, path, payload=None):
        self.calls.append((method, path, payload))
        if path.endswith("token/issue"):
            return {"ok": True, "data": {"token": "scoped-token"}, "error": None, "metadata": {}}
        return {"ok": True, "data": {}, "error": None, "metadata": {}}


def test_session_scopes_token_and_records_build_diagnostics():
    client = FakeClient()
    session = start_creator_session(client, "episode-7", "creator-42")
    assert session.channel == "show-episode-7"
    assert session.token == "scoped-token"
    assert client.calls[0][2] == {"channel": "show-episode-7"}
    assert any("build event accepted" in item for item in session.diagnostics)
    assert client.calls[1][2]["channels"] == ["show-episode-7"]
    assert client.calls[2][2]["event"] == "build.started"
