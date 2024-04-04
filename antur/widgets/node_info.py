"""
Node info widget.

Shows information on the selected node including the last modified date, change frequency,
and priority.

Optionally shows the markdown preview of the XML content.
"""

from datetime import datetime

from humanize import naturaldelta
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Markdown

from antur.utils.sitemap_parser import Error

URL_TEMPLATE = """
# {node.url}

- Last Modified: {node.lastmod} {delta}
- Change Frequency: {node.changefreq}
- Priority: {node.priority}

{opt_md}
"""

ERROR_TEMPLATE = """
# Error: {node.message}

Open this URL in your browser to see the error, it is possible that the URL is not a sitemap.
"""


class NodeInfo(Widget):
    """Node info widget."""

    node = reactive(None, recompose=True, always_update=True)

    def compose(self: "NodeInfo") -> ComposeResult:
        """Compose the node info."""
        if self.node:
            if isinstance(self.node, Error):
                yield Markdown(ERROR_TEMPLATE.format(node=self.node), id="node-info")
                return

            try:
                lastmod = datetime.fromisoformat(self.node.lastmod)

                delta = naturaldelta(datetime.now(tz=lastmod.tzinfo) - lastmod)
                delta = f"**({delta} ago)**"
            except (TypeError, ValueError):
                delta = ""

            opt_md = ("```xml\n" + self.node.other + "\n```") if self.app.show_markdown else ""

            yield Markdown(
                URL_TEMPLATE.format(node=self.node, delta=delta, opt_md=opt_md),
                id="node-info",
            )
        else:
            yield Markdown("# No node selected.")
