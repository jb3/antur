"""Main application for Antur."""

import typing

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.reactive import reactive
from textual.widgets import Footer, Header

from antur import __version__

from .widgets.node_info import NodeInfo
from .widgets.search_bar import SearchBar
from .widgets.sitemap_tree import SitemapTree


class AnturApp(App):
    """Antur allows you to browse sitemaps from your command line."""

    BINDINGS: typing.ClassVar = [
        ("q", "quit", "Quit the application."),
        ("d", "toggle_dark", "Toggle between light and dark mode."),
        (
            "m",
            "toggle_markdown",
            "Show the markdown preview of unrecognised properties.",
        ),
    ]

    CSS_PATH = "antur.tcss"

    ENABLE_COMMAND_PALETTE = False

    TITLE = "Antur"

    SUB_TITLE = f"v{__version__}"

    show_markdown = reactive(False)

    def __init__(self: "AnturApp", url: str | None = None, *, max_concurrent_requests: int) -> None:
        """Initialize the Antur application."""
        super().__init__()

        self.url = url
        self.max_concurrent_requests = max_concurrent_requests

    def compose(self: "AnturApp") -> ComposeResult:
        """Compose the layout of the app."""
        yield Header(False)
        yield SearchBar(self.url)
        with Vertical(id="contents"):
            with Vertical(id="main"):
                yield SitemapTree(self.url, max_concurrent_requests=self.max_concurrent_requests)
                yield NodeInfo()
            yield Footer()

    def action_toggle_dark(self: "AnturApp") -> None:
        """Toggle between light and dark mode."""
        self.dark = not self.dark

    def action_toggle_markdown(self: "AnturApp") -> None:
        """Toggle the markdown preview."""
        self.show_markdown = not self.show_markdown
        self.query_one(NodeInfo).node = self.query_one(NodeInfo).node
