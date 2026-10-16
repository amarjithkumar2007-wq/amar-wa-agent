import hashlib
import hmac
import json
import threading

import pytest

import app as bot


@pytest.fixture(autouse=True)
def clean(tmp_path, monkeypatch):
    monkeypatch.setattr(bot, "TASK_FILE", str(tmp_path / "tasks.json"))
    monkeypatch.setattr(bot, "VERIFY_TOKEN", "secret")
    monkeypatch.setattr(bot, "APP_SECRET", "")
    monkeypatch.setattr(bot, "ALLOWED", {"911"})
    bot.HISTORY.clear()
    bot.SEEN.clear()
    yield


@pytest.fixture
def client():
    return bot.app.test_client()


def wa_payload(text, sender="911", mid="m1", mtype="text"):
    msg = {"from": sender, "id": mid, "type": mtype}
    if mtype == "text":
        msg["text"] = {"body": text}
    return {"entry": [{"changes": [{"value": {"messages": [msg]}}]}]}


def test_health(client):
    assert client.get("/health").data == b"ok"
    assert client.get("/").data == b"ok"


def test_verify_ok_and_wrong_token(client):
    ok = client.get("/webhook?hub.mode=subscribe&hub.verify_token=secret&hub.challenge=123")
    assert ok.status_code == 200 and ok.data == b"123"
    bad = client.get("/webhook?hub.mode=subscribe&hub.verify_token=nope&hub.challenge=123")
    assert bad.status_code == 403


def test_verify_rejects_when_token_unset(client, monkeypatch):
    monkeypatch.setattr(bot, "VERIFY_TOKEN", "")
    r = client.get("/webhook?hub.mode=subscribe&hub.verify_token=&hub.challenge=1")
    assert r.status_code == 403


def test_signature_checked_when_secret_set(client, monkeypatch):
    monkeypatch.setattr(bot, "APP_SECRET", "s3")
    body = json.dumps(wa_payload("hi")).encode()
    assert client.post("/webhook", data=body, content_type="application/json").status_code == 403
    sig = "sha256=" + hmac.new(b"s3", body, hashlib.sha256).hexdigest()
    ok = client.post("/webhook", data=body, content_type="application/json",
                     headers={"X-Hub-Signature-256": sig})
    assert ok.status_code == 200


def test_commands_add_list_done():
    assert "#1" in bot.handle_command("911", "/add buy milk")
    assert "buy milk" in bot.handle_command("911", "/list")
    assert "Done" in bot.handle_command("911", "/done 1")
    assert "✅" in bot.handle_command("911", "/list")
    assert "Aise likh" in bot.handle_command("911", "/done 9")
    assert "Aise likh" in bot.handle_command("911", "/add")


def test_clear_and_help_and_plain_text():
    bot.HISTORY["911"] = [{"role": "user", "parts": [{"text": "x"}]}]
    assert "clear" in bot.handle_command("911", "/clear").lower()
    assert "911" not in bot.HISTORY
    assert "/add" in bot.handle_command("911", "/help")
    assert bot.handle_command("911", "what is python") is None


def run_process(monkeypatch, msg):
    sent = []
    monkeypatch.setattr(bot, "send", lambda to, text: sent.append((to, text)))
    monkeypatch.setattr(bot, "ask_gemini", lambda n, t: "ai:" + t)
    bot.process(msg)
    return sent


def test_process_ignores_other_numbers(monkeypatch):
    msg = {"from": "999", "type": "text", "text": {"body": "hi"}}
    assert run_process(monkeypatch, msg) == []


def test_process_text_goes_to_ai(monkeypatch):
    msg = {"from": "911", "type": "text", "text": {"body": "hello"}}
    assert run_process(monkeypatch, msg) == [("911", "ai:hello")]


def test_process_command_skips_ai(monkeypatch):
    msg = {"from": "911", "type": "text", "text": {"body": "/add x"}}
    out = run_process(monkeypatch, msg)
    assert out[0][1].startswith("Add ho gaya")


def test_process_non_text(monkeypatch):
    out = run_process(monkeypatch, {"from": "911", "type": "image"})
    assert "text" in out[0][1]


def test_webhook_dedupes_message_ids(client, monkeypatch):
    calls = []
    done = threading.Event()

    def fake_process(msg):
        calls.append(msg["id"])
        done.set()

    monkeypatch.setattr(bot, "process", fake_process)
    payload = wa_payload("hi", mid="dup")
    client.post("/webhook", json=payload)
    done.wait(2)
    client.post("/webhook", json=payload)
    assert calls == ["dup"]


def test_gemini_failure_returns_friendly_message(monkeypatch):
    class R:
        status_code = 500
        text = "boom"

    monkeypatch.setattr(bot.requests, "post", lambda *a, **k: R())
    out = bot.ask_gemini("911", "hi")
    assert "busy" in out
    assert bot.HISTORY["911"] == []
