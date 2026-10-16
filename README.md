# amar-wa-agent

Amar's personal WhatsApp AI assistant. A small Flask app: WhatsApp Cloud API webhook in, Gemini reply out, replies in Hinglish.

Only numbers listed in `ALLOWED_NUMBERS` get a reply. Everyone else is ignored.

## What it does today

- Chats with Gemini (keeps the last 20 turns per number, saved in the store).
- Task tracker: `/add <text>`, `/list`, `/done <no>`, `/clear` (clears chat memory), `/help`.
- Reminders: `/remind 30m text`, `/remind 2h text`, `/remind 18:00 text` (IST), `/remind 2026-10-20 09:00 text`, `/reminders`, `/unremind <no>`.
- `/tick` (send due reminders) and `/digest` (morning summary): call them from a free cron such as cron-job.org with `?key=CRON_SECRET` or an `X-Cron-Key` header.
- Webhook verification, optional `X-Hub-Signature-256` check (`META_APP_SECRET`), duplicate message de-dupe.
- `GET /health` for hosting health checks.

## Known limits

- Without Upstash configured, data is kept in a local file (`data.json`), which a free host wipes on restart. Set the Upstash variables to keep it.
- Text messages only. No Gmail, Calendar, browsing or form filling yet.
- Planned next: tools (Gmail/Calendar), RAG memory.

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
| `UPSTASH_REDIS_REST_URL` / `UPSTASH_REDIS_REST_TOKEN` | Optional. Free Upstash Redis REST credentials. Turns on persistence. |
| `CRON_SECRET` | Secret for `/tick` and `/digest`. Without it both return 403. |
| `TZ_OFFSET_MINUTES` | Optional. Default `330` (IST). |
| `DATA_FILE` | Optional. Local fallback file. Default `data.json`. |

Never commit secrets. Set them in the host's secret settings.

## Deploy

See [SETUP_GUIDE.md](SETUP_GUIDE.md). `render.yaml` and `Procfile` are included.
