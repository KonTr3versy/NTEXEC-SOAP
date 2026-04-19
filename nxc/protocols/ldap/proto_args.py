from __future__ import annotations

import argparse


def register_ldap_proto_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--directory-transport",
        choices=("ldap", "adws"),
        default="ldap",
        help="Directory query transport backend",
    )
    parser.add_argument(
        "--adws",
        action="store_true",
        help="Alias for --directory-transport adws",
    )
    parser.add_argument(
        "--adws-endpoint",
        default=None,
        help="Custom ADWS endpoint (used only when transport is adws)",
    )
    parser.add_argument(
        "--adws-page-size",
        type=int,
        default=256,
        help="Page size hint for ADWS enumerate/pull",
    )
    parser.add_argument(
        "--adws-scope",
        choices=("base", "onelevel", "subtree"),
        default="subtree",
        help="Search scope for ADWS requests",
    )


def normalize_ldap_args(args: argparse.Namespace) -> argparse.Namespace:
    if getattr(args, "adws", False):
        args.directory_transport = "adws"

    if args.directory_transport != "adws":
        # Leave adws args present but inert for compatibility.
        return args

    if args.adws_page_size <= 0:
        raise ValueError("--adws-page-size must be positive")
    return args
