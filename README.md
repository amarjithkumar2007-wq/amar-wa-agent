# amar-wa-agent

Amar's personal WhatsApp AI assistant. A small Flask app: WhatsApp Cloud API webhook in, Gemini reply out, replies in Hinglish.

Only numbers listed in `ALLOWED_NUMBERS` get a reply. Everyone else is ignored.

## What it does today

- Chats with Gemini (keeps the last 20 turns per number, in memory).
- Task tracker: `/add <text>`, `/list`, `/done <no>`, `/clear` (clears chat memory), `/help`.
- Webhook verification, optional `X-Hub-Signature-256` check (`META_APP_SECRET`), duplicate message de-dupe.
- `GET /health` for hosting health checks.

## Known limits

- Chat history and `tasks.json` live on local disk or memory. On a free host they are lost on restart.
- Text messages only. No Gmail, Calendar, browsing or form filling yet.
- Planned next: persistence + reminders, then tools.

## Run locally

```
pip install -r requirements-dev.txt
cp .env.example .env   # fill in values, then export them
pytest
python app.py
```

## Environment variables

| Name | What |
|---|---|
| `VERIFY_TOKEN` | Any secret word. Same value goes in the Meta webhook setup. |
| `WHATSAPP_TOKEN` | Meta access token. The temporary one lasts 24 hours. |
| `PHONE_NUMBER_ID` | From Meta, WhatsApp, API Setup. |
| `GEMINI_API_KEY` | From aistudio.google.com/apikey. |
| `GEMINI_MODEL` | Optional. Default `gemini-2.0-flash`. |
| `ALLOWED_NUMBERS` | Comma-separated numbers with country code, no `+`. |
| `META_APP_SECRET` | Optional. Turns on webhook signature checking. |
| `TASK_FILE` | Optional. Path of the task file. Default `tasks.json`. |

Never commit secrets. Set them in the host's secret settings.

## Deploy

See [SETUP_GUIDE.md](SETUP_GUIDE.md). `render.yaml` and `Procfile` are included.
