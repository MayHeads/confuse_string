from __future__ import annotations

import argparse

from buness.profiles import PROFILES
from buness.runner import list_profiles, run_profile


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="buness 统一入口")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="列出所有可执行 profile")

    show_parser = subparsers.add_parser("show", help="查看 profile 详情")
    show_parser.add_argument("profile", choices=sorted(PROFILES))

    run_parser = subparsers.add_parser("run", help="执行指定 profile")
    run_parser.add_argument("profile", choices=sorted(PROFILES))

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "list":
        for profile in list_profiles():
            print(f"{profile.name}: {profile.description}")
        return

    if args.command == "show":
        profile = PROFILES[args.profile]
        print(f"name: {profile.name}")
        print(f"description: {profile.description}")
        print("overrides:")
        if not profile.overrides:
            print("  (none)")
        else:
            for key, value in profile.overrides.items():
                print(f"  - {key} = {value!r}")
        print("steps:")
        for step in profile.steps:
            print(f"  - {step}")
        return

    if args.command == "run":
        run_profile(args.profile)


if __name__ == "__main__":
    main()
