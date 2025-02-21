import json
from urllib.parse import quote_plus

from app.log import log


def get_search_query(attribute: str, start: int = 0, limit: int = 1000) -> str:
    """Helper method to create a url encoded string for Search API."""
    log.debug(f"Creating search query string with these params: {attribute=}, {start=}, {limit=}")
    params = {
        "query": {
            "type": "terminal",
            "service": "text",
            "parameters": {
                "attribute": attribute,
                "operator": "range",
                "value": {"from": "now-1w", "include_lower": True},
            },
        },
        "request_options": {"paginate": {"start": start, "rows": limit}},
        "return_type": "entry",
    }

    json_params = json.dumps(params)
    encoded = quote_plus(json_params)
    log.debug(f"Query string created. {encoded}")
    return encoded
