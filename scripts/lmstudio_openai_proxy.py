#!/usr/bin/env python3
"""Minimal localhost OpenAI-compatible proxy for LM Studio.

LM Studio 0.4.x rejects OpenAI's legacy response_format {"type":"json_object"}
while accepting ordinary chat-completion requests. The Trojan Hippo harness uses
that response_format for semantic judges when the provider is OpenAI-compatible.

This proxy forwards requests to LM Studio and removes only that unsupported
response_format value. It does not log request bodies and does not call any
network target except the configured localhost upstream.
"""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen


UPSTREAM_BASE_URL = os.environ.get("UPSTREAM_OPENAI_BASE_URL", "http://127.0.0.1:1234/v1").rstrip("/")
HOST = os.environ.get("LOCAL_PROXY_HOST", "127.0.0.1")
PORT = int(os.environ.get("LOCAL_PROXY_PORT", "1235"))


def rewrite_payload(payload: bytes, content_type: str) -> bytes:
    if not payload or "application/json" not in content_type.lower():
        return payload

    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return payload

    response_format = data.get("response_format")
    if isinstance(response_format, dict) and response_format.get("type") == "json_object":
        data.pop("response_format", None)
        return json.dumps(data).encode("utf-8")

    return payload


class ProxyHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self) -> None:
        self.forward()

    def do_POST(self) -> None:
        self.forward()

    def log_message(self, fmt: str, *args: object) -> None:
        print("%s - %s" % (self.log_date_time_string(), fmt % args), flush=True)

    def forward(self) -> None:
        body = b""
        if "content-length" in self.headers:
            body = self.rfile.read(int(self.headers["content-length"]))

        content_type = self.headers.get("content-type", "")
        rewritten = rewrite_payload(body, content_type)
        target_url = UPSTREAM_BASE_URL + self.path.removeprefix("/v1")

        headers = {
            key: value
            for key, value in self.headers.items()
            if key.lower() not in {"host", "content-length", "connection", "accept-encoding"}
        }
        if rewritten != body:
            print(f"rewrote unsupported json_object response_format for {self.path}", flush=True)

        request = Request(target_url, data=rewritten if self.command != "GET" else None, headers=headers, method=self.command)

        try:
            with urlopen(request, timeout=900) as response:
                response_body = response.read()
                self.send_response(response.status)
                self.copy_headers(response.headers, len(response_body))
                self.end_headers()
                self.wfile.write(response_body)
        except HTTPError as error:
            error_body = error.read()
            self.send_response(error.code)
            self.copy_headers(error.headers, len(error_body))
            self.end_headers()
            self.wfile.write(error_body)

    def copy_headers(self, source_headers, body_length: int) -> None:
        skipped = {"transfer-encoding", "connection", "content-encoding", "content-length"}
        for key, value in source_headers.items():
            if key.lower() not in skipped:
                self.send_header(key, value)
        self.send_header("content-length", str(body_length))
        self.send_header("connection", "close")


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), ProxyHandler)
    print(f"LM Studio OpenAI proxy listening on http://{HOST}:{PORT}/v1 -> {UPSTREAM_BASE_URL}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
