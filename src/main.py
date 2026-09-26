import argparse
import json

from video_room_service import InfraiClient, start_creator_session


def main() -> None:
    parser = argparse.ArgumentParser(description="Start a scoped creator video room")
    parser.add_argument("show_id")
    parser.add_argument("creator_id")
    args = parser.parse_args()
    session = start_creator_session(InfraiClient(), args.show_id, args.creator_id)
    print(json.dumps({"channel": session.channel, "token": session.token, "diagnostics": session.diagnostics}))


if __name__ == "__main__":
    main()

