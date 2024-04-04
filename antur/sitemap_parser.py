"""Parse a sitemap file and return a dict of URLs and their metadata."""

from dataclasses import dataclass

import aiohttp
from lxml.etree import Element, fromstring, tostring


@dataclass
class Entry:
    """Dataclass for a sitemap entry."""

    url: str
    lastmod: str
    changefreq: str
    priority: str
    other: str


@dataclass
class Error:
    """Dataclass for an error."""

    url: str
    message: str


HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; AnturSitemap/2.1; +http://github.com/jb3/antur)"
}

IGNORE_TAGS = ["lastmod", "changefreq", "priority", "loc"]


class SitemapParser:
    """Parse a sitemap file and return a dict of URLs and their metadata."""

    def __init__(self: "SitemapParser", url: str) -> None:
        """Initialize the parser."""
        self.url = url
        self.data = {}
        self.found_urls = 0
        self.found_sitemaps = 0
        self.http_errors = 0
        self.xml_errors = 0

    async def get_data(self: "SitemapParser", url: str) -> bytes:
        """Fetch the data from the URL."""
        async with aiohttp.ClientSession() as session, session.get(
            url, headers=HEADERS
        ) as response:
            return await response.read()

    def _filter_out_children(self: "SitemapParser", element: Element) -> Element:
        """Return an XML Element with matching children removed."""
        for tag in IGNORE_TAGS:
            found = element.findall(f"{{*}}{tag}")
            for c in found:
                c.getparent().remove(c)

        return element

    def _maybe_child(self: "SitemapParser", element: Element, tag: str) -> str | None:
        """Return the text of a child element if it exists."""
        child = element.find(tag)
        return child.text if child is not None else None

    async def parse(
        self: "SitemapParser", url: str | None = None
    ) -> dict[str, Entry | Error]:
        """Parse the sitemap at the given URL."""
        if not url:
            url = self.url

        level = {}

        try:
            data = await self.get_data(url)
        except aiohttp.ClientError as e:
            self.http_errors += 1
            return Error(url, str(e))

        try:
            parsed = fromstring(data)  # noqa: S320
        except Exception as e:
            self.xml_errors += 1
            return Error(url, str(e))

        if parsed.tag.endswith("sitemapindex"):
            for child in parsed:
                if child.tag.endswith("sitemap"):
                    loc = child.find("{*}loc").text
                    self.found_sitemaps += 1
                    level[loc] = await self.parse(loc)

        if parsed.tag.endswith("urlset"):
            for child in parsed:
                loc = child.find("{*}loc").text
                self.found_urls += 1
                level[loc] = Entry(
                    loc,
                    self._maybe_child(child, "{*}lastmod"),
                    self._maybe_child(child, "{*}changefreq"),
                    self._maybe_child(child, "{*}priority"),
                    tostring(
                        self._filter_out_children(child), pretty_print=True
                    ).decode(),
                )

        return level
