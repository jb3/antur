"""Main module for the Antur application."""

import argparse

from . import __version__
from .app import AnturApp


def parse_args() -> argparse.Namespace:
    """Parse the command line arguments."""
    parser = argparse.ArgumentParser(
        description="Antur allows you to browse sitemaps from your command line.",
        epilog=f"antur v{__version__}",
    )
    parser.add_argument("url", nargs="?", help="The URL of a sitemap to start with.")

    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    parser.add_argument(
        "-c",
        "--concurrent",
        type=int,
        help="The number of concurrent requests to make.",
        default=40,
    )
    return parser.parse_args()


def main() -> None:
    """Run the Antur application."""
    args = parse_args()

    app = AnturApp(args.url, max_concurrent_requests=args.concurrent)
    app.run()


if __name__ == "__main__":
    main()
