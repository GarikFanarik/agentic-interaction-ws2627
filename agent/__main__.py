"""Answer a calendar question in one pass: model -> tool -> model."""

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

from .runlog import RunLog
from .tools import CALENDAR_TOOL, HTTP_TIMEOUT_SECONDS, parse_arguments, run_tool_call

REPO_ROOT = Path(__file__).resolve().parent.parent
REQUIRED_VARIABLES = ("OPENAI_BASE_URL", "MODEL", "OPENAI_API_KEY", "DATA_BASE_URL")


def load_config():
    missing = [name for name in REQUIRED_VARIABLES if not os.environ.get(name)]
    if missing:
        raise RuntimeError(f"Missing configuration: {', '.join(missing)} (see .env.example)")
    return {name: os.environ[name] for name in REQUIRED_VARIABLES}


def system_prompt(data_base_url):
    """The mock world has its own "now", which relative dates must resolve against."""
    prompt = (
        "You answer questions about the user's calendar. "
        "Always look up the days in question with the tool, never guess appointments. "
        "Answer only from the tool results, in the language of the question."
    )
    try:
        url = f"{data_base_url.rstrip('/')}/context.json"
        with urllib.request.urlopen(url, timeout=HTTP_TIMEOUT_SECONDS) as response:
            now = datetime.fromisoformat(json.load(response)["now"])
    except (urllib.error.URLError, TimeoutError, ValueError, KeyError, TypeError):
        return prompt
    return f"{prompt} Today is {now:%A, %Y-%m-%d}, the time is {now:%H:%M}."


def answer(question, config, log):
    client = OpenAI(base_url=config["OPENAI_BASE_URL"], api_key=config["OPENAI_API_KEY"])
    messages = [
        {"role": "system", "content": system_prompt(config["DATA_BASE_URL"])},
        {"role": "user", "content": question},
    ]
    request = {"model": config["MODEL"], "tools": [CALENDAR_TOOL]}

    # Pass 1: the model has to call the tool.
    response = client.chat.completions.create(
        messages=messages, tool_choice="required", **request
    )
    message = response.choices[0].message
    if not message.tool_calls:
        raise RuntimeError("The model did not call the tool.")

    messages.append(
        {
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments,
                    },
                }
                for call in message.tool_calls
            ],
        }
    )
    for call in message.tool_calls:
        name = call.function.name
        arguments = parse_arguments(call.function.arguments)
        log.write("tool_call", ok=True, tool=name, args=arguments)
        result = run_tool_call(config["DATA_BASE_URL"], name, arguments)
        log.write(
            "tool_result", ok="error" not in result, tool=name, args=arguments, result=result
        )
        messages.append(
            {
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(result, ensure_ascii=False),
            }
        )

    # Pass 2: the model turns the tool results into the answer.
    response = client.chat.completions.create(messages=messages, tool_choice="none", **request)
    if not response.choices[0].message.content:
        raise RuntimeError("The model returned no answer.")
    return response.choices[0].message.content


def main():
    # override=False: variables already set in the environment take precedence.
    load_dotenv(REPO_ROOT / ".env", override=False)
    log = RunLog(REPO_ROOT / "logs", model=os.environ.get("MODEL"))

    if len(sys.argv) != 2 or not sys.argv[1].strip():
        message = 'Usage: python -m agent "<question>"'
        log.write("error", ok=False, text=message)
        print(message, file=sys.stderr)
        return 2

    question = sys.argv[1]
    log.write("user_task", ok=True, text=question)
    try:
        text = answer(question, load_config(), log)
    except (OpenAIError, RuntimeError) as error:
        log.write("error", ok=False, text=str(error))
        print(f"Error: {error}", file=sys.stderr)
        return 1

    log.write("final", ok=True, text=text)
    # Windows consoles and pipes may not default to UTF-8.
    sys.stdout.reconfigure(encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
