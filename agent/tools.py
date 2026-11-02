"""The calendar tool: its description for the model and its implementation."""

import json
import urllib.error
import urllib.request
from datetime import datetime

HTTP_TIMEOUT_SECONDS = 15

CALENDAR_TOOL = {
    "type": "function",
    "function": {
        "name": "get_calendar_day",
        "description": (
            "Returns all appointments of one calendar day. "
            "An empty 'events' list means the day is free. "
            "'found: false' means there is no calendar data for that date."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "The day to look up, formatted as YYYY-MM-DD.",
                },
            },
            "required": ["date"],
            "additionalProperties": False,
        },
    },
}


def get_calendar_day(data_base_url, date):
    """Read one day. Every failure becomes a result the model can report on."""
    try:
        normalized = datetime.strptime(date, "%Y-%m-%d").date().isoformat()
    except (TypeError, ValueError):
        return {"error": f"Invalid date {date!r}, expected YYYY-MM-DD."}

    url = f"{data_base_url.rstrip('/')}/calendar/{normalized}.json"
    try:
        with urllib.request.urlopen(url, timeout=HTTP_TIMEOUT_SECONDS) as response:
            return {"found": True, **json.load(response)}
    except urllib.error.HTTPError as error:
        # The data repository defines 404 as "no data", not as a failure.
        if error.code == 404:
            return {"found": False, "date": normalized, "events": []}
        return {"error": f"Calendar request failed with HTTP {error.code}."}
    except (urllib.error.URLError, TimeoutError, ValueError) as error:
        return {"error": f"Calendar request failed: {error}"}


def parse_arguments(raw_arguments):
    """Models can emit malformed JSON; keep the raw text so it can be logged and reported."""
    try:
        return json.loads(raw_arguments)
    except json.JSONDecodeError:
        return raw_arguments


def run_tool_call(data_base_url, name, arguments):
    """Execute one tool call as requested by the model."""
    if name != CALENDAR_TOOL["function"]["name"]:
        return {"error": f"Unknown tool {name!r}."}
    try:
        return get_calendar_day(data_base_url, arguments["date"])
    except (KeyError, TypeError):
        return {"error": f"Invalid tool arguments: {arguments!r}"}
