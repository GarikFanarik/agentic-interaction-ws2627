# agentic-interaction-ws2627

Exercises for *Agentic Interaction* (winter term 2026/27, Ulm University).

Exercise 1 is an agent that answers calendar questions in one pass: model → tool → model.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then put your API key into .env
```

The agent reads `OPENAI_BASE_URL`, `MODEL`, `OPENAI_API_KEY` and `DATA_BASE_URL` from `.env` at
startup. Variables already set in the environment take precedence. It works with any
OpenAI-compatible endpoint.

## Usage

```bash
python -m agent "Was steht am 29.10.2026 im Kalender?"
```

The answer goes to standard output and the exit code is 0. Errors go to standard error with a
non-zero exit code.

## How it works

1. The model receives the question and the description of the tool `get_calendar_day`
   (`agent/tools.py`) and has to call it.
2. The tool reads `{DATA_BASE_URL}/calendar/{YYYY-MM-DD}.json`. A 404 means "no data" and is
   returned to the model as a result.
3. The model receives the result and writes the answer.

Relative dates such as "morgen" resolve against `now` from `{DATA_BASE_URL}/context.json`, the
current time of the mock data.

## Logs

Each run writes its own file `logs/<UTC time>_<run id>.jsonl` (`agent/runlog.py`). Every line is one
step and always has these fields; those that do not apply to a step are `null`:

| Field | Content |
|---|---|
| `ts` | Time stamp, ISO 8601 |
| `run_id` | One ID per run |
| `event` | `user_task`, `tool_call`, `tool_result`, `final` or `error` |
| `tool`, `args` | Tool name and arguments |
| `ok` | Whether the step succeeded; a day without data counts as success |
| `model` | Model name as sent to the endpoint |
| `duration_ms` | Time since the previous step ended, so `tool_call` covers the model request that produced the call |

In addition, `user_task`, `final` and `error` carry `text`, and `tool_result` carries `result`.
