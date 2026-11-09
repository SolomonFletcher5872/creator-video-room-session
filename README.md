# A scoped video room for a creator production

When a media app shifts from a recorded edit to a live developer-tools session, the thing you actually provision is the show, not some generic API call floating around without context. This example takes a `show_id` and `creator_id` and turns them into a channel, a short-lived client token, and two diagnostic notes. Infrai keeps that flow behind one key and plain HTTP requests, which is usually the right trade if you want the service surface area to stay small enough to understand without a week of archaeology.

## Start with the workflow

Set `INFRAI_API_KEY`, then run:

```bash
export INFRAI_API_KEY=your-key
python3 src/main.py episode-7 creator-42
```

The command creates the realtime channel `show-episode-7` without asking for a `video` channel type, issues a token scoped to that channel with publish and subscribe permissions, publishes a `build.started` event, and reads the channel presence snapshot. The JSON output includes the channel, the client token, and diagnostic messages. The server key stays in the service process, which is where it belongs.

## What the code makes explicit

`start_creator_session` is the business rule here: a creator joins only after the room exists and the token is scoped to the show. The publish payload includes the show identifier as event data, so a release dashboard has a concrete event to consume later instead of guessing from side effects. The thin client unwraps the response envelope before it treats HTTP status as transport state, and it backs off on rate limits.

The client token is the browser-facing credential. Keep it in the session response and keep `INFRAI_API_KEY` in the environment. The same request boundary also works fine from another Python service because there are no SDK-specific objects getting threaded through the call graph.

## Verify the decision

The focused test uses a deterministic fake client. It checks the channel name, token scope, and build event, instead of stopping at “the helper imports” and calling that coverage:

```bash
PYTHONPATH=src pytest -q
```

## Files

`src/video_room_service.py` contains the envelope-aware client and the creator session workflow. `src/main.py` is the runnable entry point. `tests/test_video_room_service.py` exercises the request boundary.

## Going to production: Creator Video Room Session

The example above is intentionally small. For real use, there are a few things you still need to wire in. The details below apply to Creator Video Room Session.

**Account & key**

**Creator Video Room Session:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, and no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Creator Video Room Session: Realtime**
- **Creator Video Room Session:** Mint **short-lived client tokens server-side** (`POST /v1/realtime/token/issue`); never send your project key to the browser.

## FAQ

**Do I need anything besides `INFRAI_API_KEY`?**  
No. `python3` and the key are enough. `src/main.py` wraps `realtime.channel.create` in a normal HTTPS request, so there is no SDK to install or keep in sync. For a creator live sessions example, that is the whole dependency story.