"""Main module for the Antur application."""

from .app import AnturApp


def main() -> None:
    """Run the Antur application."""
    app = AnturApp()
    app.run()


if __name__ == "__main__":
    main()
