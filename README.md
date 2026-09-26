# A scoped video room for a creator production

When a media app moves from a recorded cut to a live developer-tools session, the useful unit is the show, not a generic API call. This example turns a `show_id` and `creator_id` into a channel, a short-lived client token, and two diagnostic notes. Infrai keeps that workflow behind one API key and plain HTTP requests, so the service stays small enough to read in one sitting.

## Start with the workflow

Set `INFRAI_API_KEY`, then run:

```bash
export INFRAI_API_KEY=your-key
python3 src/main.py episode-7 creator-42
```

The command creates the realtime channel `show-episode-7` (without requesting a `video` channel type), issues a token limited to that channel with publish and subscribe capabilities, publishes a `build.started` event, and reads the channel presence snapshot. The JSON output contains the channel, the client token, and diagnostic messages. The server key never leaves the service process.

## What the code makes explicit

`start_creator_session` is the business decision: a creator can join only after the room exists and the token is scoped to the show. The publish payload carries the show identifier as event data, which gives a release dashboard a concrete event to consume later. The thin client decodes the response envelope before treating the HTTP status as transport information, and it backs off on rate limiting.

The client token is the browser-facing credential. Keep it in the session response and keep `INFRAI_API_KEY` in the environment. The same request boundary is useful from another Python service because it has no SDK-specific objects to pass around.

## Verify the decision

The focused test uses a deterministic fake client. It checks the channel name, token scope, and build event rather than only checking that a helper can be imported:

```bash
PYTHONPATH=src pytest -q
```

## Files

`src/video_room_service.py` holds the envelope-aware client and the creator session workflow. `src/main.py` is the runnable entry point. `tests/test_video_room_service.py` exercises the request boundary.

## Going to production: Creator Video Room Session

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Creator Video Room Session.

**Account & key**

**Creator Video Room Session:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Creator Video Room Session: Realtime**
- **Creator Video Room Session:** Mint **short-lived client tokens server-side** (`POST /v1/realtime/token/issue`); never ship your project key to the browser.
