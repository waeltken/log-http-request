#!/usr/bin/env python3
"""Tiny request-logging sink: replies 200 to everything, logs the full request to stdout."""
import os
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.environ.get("PORT", "8080"))
RESPONSE_BODY = b"OK"


class LoggingHandler(BaseHTTPRequestHandler):
    def _handle(self):
        body = self._read_body()
        self._log(body)
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(RESPONSE_BODY)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(RESPONSE_BODY)

    def _read_body(self) -> bytes:
        length = self.headers.get("Content-Length")
        if length is None:
            return b""
        try:
            n = int(length)
        except ValueError:
            return b""
        if n <= 0:
            return b""
        return self.rfile.read(n)

    def _log(self, body: bytes):
        ts = datetime.now(timezone.utc).isoformat()
        lines = [
            f"--- {ts} {self.command} {self.path} {self.request_version} "
            f"from {self.client_address[0]}:{self.client_address[1]}"
        ]
        for key, value in self.headers.items():
            lines.append(f"{key}: {value}")
        lines.append("")
        lines.append(body.decode("utf-8", errors="replace") if body else "(no body)")
        lines.append("")
        sys.stdout.write("\n".join(lines) + "\n")
        sys.stdout.flush()

    # Suppress the default per-request access line; we emit our own block.
    def log_message(self, format, *args):
        pass

    # Every standard verb routes to the same handler.
    do_GET = do_POST = do_PUT = do_DELETE = do_PATCH = do_HEAD = do_OPTIONS = _handle


def main():
    server = ThreadingHTTPServer(("0.0.0.0", PORT), LoggingHandler)
    print(f"listening on 0.0.0.0:{PORT}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
