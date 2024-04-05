"""
Sitemap tree widget.

This renders a tree of the sitemap and updates the node info widget when a node is highlighted.

When a new target is set from the SearchBar, the tree is updated with the new sitemap data.
"""

import webbrowser
from typing import ClassVar

from rich.color import Color
from rich.style import Style
from rich.text import Text
from textual import work
from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static, Tree
from textual.widgets.tree import TreeNode

from antur.utils.sitemap_parser import Entry, Error, SitemapParser

from .node_info import NodeInfo


def dict_to_tree(dictionary: dict, tree: Tree | TreeNode) -> None:
    """Move a dictionary into the provided tree structure in-place."""
    for key, value in dictionary.items():
        if isinstance(value, (Entry, Error)):
            tree.add_leaf(key, data=value)
        else:
            sub_tree = tree.add(key)
            dict_to_tree(value, sub_tree)


class CustomTree(Tree):
    """Custom tree widget to aid with formatting."""

    def render_label(
        self: "CustomTree", node: TreeNode, base_style: Style, additional_style: Style
    ) -> Text:
        """Render the label with a custom style."""
        if hasattr(node, "data"):  # noqa: SIM102
            if isinstance(node.data, Error):
                additional_style = Style.chain(
                    additional_style, Style.from_color(Color.parse("red"))
                )

        return super().render_label(node, base_style, additional_style)


class SitemapTree(Widget):
    """Sitemap tree widget."""

    target = reactive(None, recompose=True, always_update=True)
    tree_data = reactive({}, recompose=True, always_update=True)

    BINDINGS: ClassVar = [("o", "open", "Open the selected item in the browser.")]

    def __init__(
        self: "SitemapTree",
        url: str | None = None,
        max_concurrent_requests: int = 40,
        *args: tuple,
        **kwargs: dict,
    ) -> None:
        """Initialize the sitemap tree."""
        super().__init__(*args, **kwargs)

        self.target = url
        self.max_concurrent_requests = max_concurrent_requests

    def compose(self: "SitemapTree") -> ComposeResult:
        """Compose the sitemap tree."""
        with ScrollableContainer():
            if isinstance(self.tree_data, Error):
                yield Static(f"Error: {self.tree_data.message}")
                return

            if self.target:
                t = CustomTree(f"Sitemap {self.target}")
                dict_to_tree(self.tree_data, t.root)
                t.root.expand()
                yield t
            else:
                yield Static("Enter a URL above to start.")

    @work(exclusive=True)
    async def watch_target(self: "SitemapTree", value: str) -> None:
        """Watch the target for changes and update the tree."""
        if value:
            self.loading = True

            parser = SitemapParser(value, self.max_concurrent_requests)
            self.tree_data = await parser.parse()

            self.loading = False

            self.notify(
                f"Found {parser.found_urls} URLs and {parser.found_sitemaps} sitemaps.",
                title="Search Complete",
            )

            if parser.http_errors:
                self.notify(
                    f"Failed to fetch {parser.http_errors} URLs.",
                    title="HTTP Errors",
                    severity="error",
                )

            if parser.xml_errors:
                self.notify(
                    f"Failed to parse {parser.xml_errors} XML documents.",
                    title="XML Errors",
                    severity="error",
                )

    def on_tree_node_highlighted(self: "SitemapTree", message: Tree.NodeHighlighted) -> None:
        """Update the node info when a node is highlighted."""
        if hasattr(message.node, "data"):
            self.app.query_one(NodeInfo).node = message.node.data
        else:
            self.app.query_one(NodeInfo).node = None

    def action_open(self: "SitemapTree") -> None:
        """Open the selected item in the browser."""
        tree = self.query_one(Tree)
        node = tree.get_node_at_line(tree.cursor_line)

        if node:
            if node.data:
                webbrowser.open(node.data.url)
            else:
                webbrowser.open(str(node.label))
