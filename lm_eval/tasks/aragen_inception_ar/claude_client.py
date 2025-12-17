#!/usr/bin/env python
"""
claude_client.py
────────────────
Tiny helper around Anthropic Claude that

• rotates through a pool of API keys
• enforces a simple requests‑per‑minute rate‑limit
• retries on rate limit errors
• exposes ONE public function: `claude_generate(prompt, **kwargs)`

All heavy lifting is internal.  Import it once, use everywhere.

Environment variables
─────────────────────
CLAUDE_KEY_FILE   Path to a text file containing ONE key per line (required
                  unless `key_file` is passed explicitly).
CLAUDE_RPM        Max requests per minute (default = 10)

Typical use
────────────
from claude_client import claude_generate
arabic = claude_generate("hello", model="claude-3-7-sonnet-20250219")
"""

from __future__ import annotations

import os
import threading
import time
from collections import deque
from pathlib import Path
from typing import List

from anthropic import Anthropic, RateLimitError


# ─────────────────────────────────────────────────────────────────── Helpers
def _read_keys(key_file: Path | str | None) -> List[str]:
    if key_file is None:
        key_file = os.getenv("CLAUDE_KEY_FILE")
    if not key_file:
        raise ValueError("Path to key‑file must be provided "
                         "via arg or CLAUDE_KEY_FILE env‑var.")
    keys = [ln.strip() for ln in Path(key_file).read_text().splitlines() if ln.strip()]
    if not keys:
        raise ValueError(f"No keys found in {key_file}")
    return keys


class _KeyCycler:
    """Round‑robin API‑key pool."""
    def __init__(self, keys: List[str]):
        self._keys = deque(keys)
        self._lock = threading.Lock()
        self.current: str | None = None
        self._next()                    # set first key

    def _next(self) -> bool:            # return False when empty
        if not self._keys:
            self.current = None
            return False
        self.current = self._keys.popleft()
        return True

    def advance(self) -> bool:
        with self._lock:
            return self._next()


class _RateLimiter:
    """Token‑bucket‑ish limiter."""
    def __init__(self, rpm: int):
        self._rpm = max(1, rpm)
        self._calls = deque()
        self._lock = threading.Lock()

    def wait(self) -> None:
        while True:
            now = time.time()
            with self._lock:
                while self._calls and now - self._calls[0] > 60:
                    self._calls.popleft()
                if len(self._calls) < self._rpm:
                    self._calls.append(now)
                    return
                # sleep until the oldest call exits the 60 s window
                to_sleep = 60 - (now - self._calls[0])
            time.sleep(to_sleep)


# ────────────────────────────────────────────────────────── Core client class
class ClaudeClient:
    _DEFAULT_MODEL = "claude-3-7-sonnet-20250219"
    _DEFAULT_GENCFG = dict(
        temperature=0,
        max_tokens=8192,
    )

    def __init__(
        self,
        key_file: str | Path | None = None,
        rpm: int | None = None,
        model: str | None = None,
        gen_config: dict | None = None,
    ) -> None:
        self._keys = _KeyCycler(_read_keys(key_file))
        self._limiter = _RateLimiter(rpm or int(os.getenv("CLAUDE_RPM", 10)))
        self._model_name = model or self._DEFAULT_MODEL
        self._base_cfg = self._DEFAULT_GENCFG | (gen_config or {})
        self._lock = threading.Lock()      # client instance isn't thread‑safe
        self._client = self._build_client()

    # ───────────────────────────── internal helpers
    def _build_client(self) -> Anthropic:
        return Anthropic(api_key=self._keys.current)

    def _raw_generate(self, prompt: str, **kwargs) -> str:
        cfg = self._base_cfg | kwargs
        with self._lock:                   # protect the underlying client
            message = self._client.messages.create(
                model=self._model_name,
                messages=[{"role": "user", "content": prompt}],
                **cfg
            )
            return message.content[0].text

    # ───────────────────────────── public API
    def generate(self, prompt: str, **kwargs) -> str:
        while True:
            if self._keys.current is None:
                raise RuntimeError("No API keys available.")
            self._limiter.wait()
            try:
                return self._raw_generate(prompt, **kwargs)
            except RateLimitError:
                # quota‑hit → rotate key & rebuild client
                if not self._keys.advance():
                    raise
                with self._lock:
                    self._client = self._build_client()
            except Exception:
                # propagate other errors upward for visibility
                raise


# ────────────────────────────────────────────────── module‑level convenience
# Initialise ONE global client on first import; adjust via env‑vars.
_client: ClaudeClient | None = None


def _global_client() -> ClaudeClient:
    global _client
    if _client is None:
        _client = ClaudeClient()          # picks env‑vars internally
    return _client


def claude_generate(prompt: str, **kwargs) -> str:
    """
    Shorthand for: `_global_client().generate(prompt, **kwargs)`

    Parameters
    ----------
    prompt : str
        The text prompt to send to Claude.
    **kwargs
        Any generation config overrides (e.g. temperature=0.3, max_tokens=4096).

    Returns
    -------
    str
        Model's text response.
    """
    return _global_client().generate(prompt, **kwargs)


if __name__ == "__main__":
    print(claude_generate("hello"))
