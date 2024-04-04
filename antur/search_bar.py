"""Widget for containing the search bar and buttons."""

from urllib.parse import urlparse

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.validation import Function
from textual.widget import Widget
from textual.widgets import Button, Input

from .sitemap_tree import SitemapTree


def is_url(value: str) -> bool:
    """Check if the value is a URL."""
    try:
        result = urlparse(value)
        if result.scheme not in ["http", "https"]:
            return False

        return all([result.scheme, result.netloc])
    except Exception:
        return False


class SearchBar(Widget):
    """Search bar widget."""

    def __init__(self: "SearchBar", *args: tuple, **kwargs: dict) -> None:
        """Initialize the search bar."""
        super().__init__(*args, **kwargs)

    def compose(self: "SearchBar") -> ComposeResult:
        """Compose the search bar."""
        with Horizontal(id="buttons-container"):
            yield Input(
                None,
                "Sitemap URL",
                id="search-bar",
                validate_on=["changed", "submitted"],
                validators=[Function(is_url, "Value is not a URL.")],
            )
            yield Button("Clear", "error", id="clear-button")
            yield Button("Search", "success", id="search-button")

    def do_search(self: "SearchBar", url: str) -> None:
        """Perform a search."""
        self.notify(url, title="Search Called")
        self.app.query_one(SitemapTree).target = url

    def on_button_pressed(self: "SearchBar", message: Button.Pressed) -> None:
        """Handle button presses."""
        if message.button.id == "clear-button":
            self.query_one(Input).value = ""
        elif message.button.id == "search-button":
            inp = self.query_one(Input)
            if self.query_one(Input).validate(inp.value).is_valid:
                self.do_search(inp.value)
            else:
                self.notify("Invalid URL", title="Search Error", severity="error")

    def on_input_submitted(self: "SearchBar", message: Input.Submitted) -> None:
        """Handle input submission."""
        if message.validation_result.is_valid:
            self.notify(message.value, title="Search Called")
            self.app.query_one(SitemapTree).target = message.value
            self.app.query_one(SitemapTree).refresh()
        else:
            self.notify("Invalid URL", title="Search Error", severity="error")
