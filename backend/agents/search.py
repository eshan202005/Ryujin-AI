import logging

from ddgs.exceptions import DDGSException
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

# DDGS uses the language portion of the region for Wikipedia's hostname.
# The default wt-wt region can generate the invalid host wt.wikipedia.org.
_search = DuckDuckGoSearchAPIWrapper(region="us-en")


@tool("duckduckgo_search")
def search_tool(query: str) -> str:
    """Search the web for information using a search query."""
    try:
        return _search.run(query)
    except (DDGSException, TimeoutError, ConnectionError):
        logger.exception("Web search failed")
        return (
            "Web search is temporarily unavailable. No search results were retrieved. "
            "Tell the user that the search failed; do not invent results or sources."
        )
