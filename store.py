"""Tiny key-value store for the bot.

Uses Upstash Redis (REST API, free tier) when UPSTASH_REDIS_REST_URL and
UPSTASH_REDIS_REST_TOKEN are set. Otherwise falls back to a local JSON file,
which is wiped on restart on most free hosts.
"""
import json
import os
import threading

import requests


class FileStore:
    def __init__(self, path):
        self.path = path
        self.lock = threading.Lock()

    def _load(self):
        try:
            with open(self.path) as f:
                return json.load(f)
        except Exception:
            return {}

    def get(self, key, default=None):
        with self.lock:
            return self._load().get(key, default)

    def set(self, key, value):
        with self.lock:
            data = self._load()
            data[key] = value
            with open(self.path, "w") as f:
                json.dump(data, f)


class UpstashStore:
    def __init__(self, url, token):
        self.url = url.rstrip("/")
        self.token = token

    def _cmd(self, *args):
        r = requests.post(self.url, headers={"Authorization": f"Bearer {self.token}"},
                          json=list(args), timeout=10)
        r.raise_for_status()
        return r.json().get("result")

    def get(self, key, default=None):
        raw = self._cmd("GET", key)
        if raw is None:
            return default
        try:
            return json.loads(raw)
        except ValueError:
            return default

    def set(self, key, value):
        self._cmd("SET", key, json.dumps(value))


def make_store(file_path="data.json"):
    url = os.environ.get("UPSTASH_REDIS_REST_URL", "")
    token = os.environ.get("UPSTASH_REDIS_REST_TOKEN", "")
    if url and token:
        return UpstashStore(url, token)
    return FileStore(file_path)
