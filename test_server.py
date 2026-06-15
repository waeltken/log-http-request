import http.client
import threading
import unittest

from server import LoggingHandler, ThreadingHTTPServer


class ServerBehaviorTests(unittest.TestCase):
    def setUp(self):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), LoggingHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.server.server_port

    def tearDown(self):
        self.server.shutdown()
        self.thread.join()
        self.server.server_close()

    def test_root_request_returns_ok(self):
        conn = http.client.HTTPConnection("127.0.0.1", self.port)
        conn.request("GET", "/", headers={"User-Agent": "Mozilla/5.0"})
        response = conn.getresponse()
        self.assertEqual(response.status, 200)
        self.assertEqual(response.read(), b"OK")
        conn.close()

    def test_any_path_returns_ok(self):
        conn = http.client.HTTPConnection("127.0.0.1", self.port)
        conn.request("GET", "/not-found", headers={"User-Agent": "Mozilla/5.0"})
        response = conn.getresponse()
        self.assertEqual(response.status, 200)
        self.assertEqual(response.read(), b"OK")
        conn.close()
