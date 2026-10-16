from datetime import datetime, timedelta, timezone

from reminders import parse_when
import store

NOW = datetime(2026, 10, 16, 5, 0, tzinfo=timezone.utc)  # 10:30 IST


def test_relative():
    due, text = parse_when(["30m", "call", "mom"], NOW)
    assert due == NOW + timedelta(minutes=30) and text == "call mom"
    assert parse_when(["2h", "x"], NOW)[0] == NOW + timedelta(hours=2)
    assert parse_when(["1d", "x"], NOW)[0] == NOW + timedelta(days=1)


def test_clock_today_and_tomorrow():
    due, _ = parse_when(["18:00", "gym"], NOW)  # 18:00 IST = 12:30 UTC same day
    assert due == datetime(2026, 10, 16, 12, 30, tzinfo=timezone.utc)
    due, _ = parse_when(["09:00", "gym"], NOW)  # already passed in IST, so tomorrow
    assert due == datetime(2026, 10, 17, 3, 30, tzinfo=timezone.utc)


def test_date_and_clock():
    due, text = parse_when(["2026-10-20", "09:00", "form"], NOW)
    assert due == datetime(2026, 10, 20, 3, 30, tzinfo=timezone.utc) and text == "form"


def test_bad_input():
    for bad in ([], ["soon"], ["25:00", "x"], ["2026-13-40", "09:00"], ["2026-10-20"], ["0x", "a"]):
        assert parse_when(bad, NOW) is None


def test_file_store_roundtrip(tmp_path):
    s = store.FileStore(str(tmp_path / "d.json"))
    assert s.get("k", "dflt") == "dflt"
    s.set("k", {"a": 1})
    assert s.get("k") == {"a": 1}


def test_upstash_store_uses_rest(monkeypatch):
    calls = []

    class R:
        def __init__(self, result):
            self.result = result

        def raise_for_status(self):
            pass

        def json(self):
            return {"result": self.result}

    def fake_post(url, headers, json, timeout):
        calls.append((url, headers["Authorization"], json))
        return R('{"a": 1}' if json[0] == "GET" else "OK")

    monkeypatch.setattr(store.requests, "post", fake_post)
    s = store.UpstashStore("https://x.upstash.io/", "tok")
    assert s.get("k") == {"a": 1}
    s.set("k", [1])
    assert calls[0] == ("https://x.upstash.io", "Bearer tok", ["GET", "k"])
    assert calls[1][2] == ["SET", "k", "[1]"]


def test_make_store_picks_backend(monkeypatch, tmp_path):
    monkeypatch.delenv("UPSTASH_REDIS_REST_URL", raising=False)
    monkeypatch.delenv("UPSTASH_REDIS_REST_TOKEN", raising=False)
    assert isinstance(store.make_store(str(tmp_path / "x.json")), store.FileStore)
    monkeypatch.setenv("UPSTASH_REDIS_REST_URL", "https://x")
    monkeypatch.setenv("UPSTASH_REDIS_REST_TOKEN", "t")
    assert isinstance(store.make_store(), store.UpstashStore)
