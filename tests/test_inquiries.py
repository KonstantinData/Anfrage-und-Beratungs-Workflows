"""Exercise the inquiry API through HTTP against a temporary Uvicorn server."""

import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class InquiryApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
        cls.base_url = f"http://127.0.0.1:{port}"
        cls.server_log = tempfile.TemporaryFile(mode="w+b")
        cls.addClassCleanup(cls.server_log.close)
        cls.server = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host",
             "127.0.0.1", "--port", str(port), "--log-level", "warning"],
            cwd=Path(__file__).resolve().parents[1],
            stdout=cls.server_log,
            stderr=subprocess.STDOUT,
        )
        cls.addClassCleanup(cls.stop_server)
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            if cls.server.poll() is not None:
                break
            try:
                with urlopen(cls.base_url + "/openapi.json", timeout=0.5) as response:
                    if response.status == 200:
                        return
            except (URLError, TimeoutError, OSError):
                time.sleep(0.05)
        cls.server_log.seek(0)
        raise RuntimeError(
            "Temporary API server did not start:\n"
            + cls.server_log.read().decode("utf-8", errors="replace")
        )

    @classmethod
    def stop_server(cls):
        if cls.server.poll() is None:
            cls.server.terminate()
            try:
                cls.server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                cls.server.kill()
                cls.server.wait(timeout=5)

    def setUp(self):
        self.created_ids = []

    def tearDown(self):
        for inquiry_id in self.created_ids:
            self.request("DELETE", f"/inquiries/{inquiry_id}")

    def request(self, method, path, payload=None):
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        request = Request(
            self.base_url + path, data=body, method=method,
            headers={"Content-Type": "application/json"},
        )
        try:
            response = urlopen(request, timeout=5)
        except HTTPError as error:
            response = error
        with response:
            raw = response.read()
            return response.status, json.loads(raw) if raw else None, raw

    @staticmethod
    def valid_payload():
        return {
            "customer_name": "Synthetic Test Customer",
            "postal_code": "70173",
            "kitchen_type": "l_form",
            "budget": 15000,
        }

    def create(self, **overrides):
        payload = self.valid_payload() | overrides
        code, record, _ = self.request("POST", "/inquiries", payload)
        self.assertEqual(code, 201, record)
        self.created_ids.append(record["id"])
        return record

    def assert_stored(self, expected):
        code, actual, _ = self.request("GET", f"/inquiries/{expected['id']}")
        self.assertEqual(code, 200, actual)
        self.assertEqual(actual, expected)

    def test_post_get_and_list_regression(self):
        record = self.create(id=999999, status="completed")
        self.assertIsInstance(record["id"], int)
        self.assertGreater(record["id"], 0)
        self.assertEqual(record["status"], "neu")
        self.assert_stored(record)
        for path in ["/inquiries", "/inquiries?postal_code=70",
                     "/inquiries?postal_code=70173"]:
            with self.subTest(path=path):
                code, records, _ = self.request("GET", path)
                self.assertEqual(code, 200)
                self.assertIn(record, records)
        code, records, _ = self.request("GET", "/inquiries?postal_code=99999")
        self.assertEqual(code, 200)
        self.assertNotIn(record, records)

    def test_post_rejects_invalid_inputs(self):
        for field, value in [
            ("customer_name", "X"), ("postal_code", "abcde"),
            ("kitchen_type", "unknown"), ("budget", 0),
        ]:
            with self.subTest(field=field):
                code, _, _ = self.request(
                    "POST", "/inquiries", self.valid_payload() | {field: value}
                )
                self.assertEqual(code, 422)

    def test_put_replaces_all_business_fields_and_preserves_server_fields(self):
        original = self.create()
        replacement = {
            "customer_name": "Replacement Test Customer", "postal_code": "10115",
            "kitchen_type": "insel", "budget": 22000,
        }
        code, record, _ = self.request(
            "PUT", f"/inquiries/{original['id']}",
            replacement | {"id": -1, "status": "completed"},
        )
        self.assertEqual(code, 200, record)
        self.assertEqual(record, replacement | {
            "id": original["id"], "status": original["status"],
        })
        self.assert_stored(record)

    def test_put_requires_every_business_field_without_mutation(self):
        for field in self.valid_payload():
            with self.subTest(field=field):
                original = self.create()
                payload = self.valid_payload()
                del payload[field]
                code, _, _ = self.request("PUT", f"/inquiries/{original['id']}", payload)
                self.assertEqual(code, 422)
                self.assert_stored(original)

    def test_patch_updates_only_supplied_fields(self):
        original = self.create()
        expected = original
        updates = {"customer_name": "Updated Test Customer", "postal_code": "10115",
                   "kitchen_type": "zeile", "budget": 23000}
        for field, value in updates.items():
            with self.subTest(field=field):
                code, record, _ = self.request(
                    "PATCH", f"/inquiries/{original['id']}", {field: value}
                )
                expected = expected | {field: value}
                self.assertEqual(code, 200, record)
                self.assertEqual(record, expected)
                self.assert_stored(expected)

    def test_patch_empty_and_protected_fields_leave_record_unchanged(self):
        original = self.create()
        for payload in [{}, {"id": -1, "status": "completed"}]:
            with self.subTest(payload=payload):
                code, record, _ = self.request("PATCH", f"/inquiries/{original['id']}", payload)
                self.assertEqual(code, 200, record)
                self.assertEqual(record, original)
                self.assert_stored(original)

    def test_put_and_patch_validation_failures_are_atomic(self):
        invalid_values = {
            "customer_name": ["X", "X" * 101, None],
            "postal_code": ["1234", "123456", "abcde", None],
            "kitchen_type": ["unknown", None],
            "budget": [0, -1, None],
        }
        for method in ["PUT", "PATCH"]:
            for field, values in invalid_values.items():
                for value in values:
                    with self.subTest(method=method, field=field, value=value):
                        original = self.create()
                        payload = self.valid_payload() if method == "PUT" else {}
                        # Include a valid change to prove invalid requests apply no changes.
                        payload = payload | {"budget": 25000, "customer_name": "Changed Test Customer"}
                        payload[field] = value
                        code, _, _ = self.request(method, f"/inquiries/{original['id']}", payload)
                        self.assertEqual(code, 422)
                        self.assert_stored(original)

    def test_delete_returns_empty_204_and_removes_record(self):
        record = self.create()
        path = f"/inquiries/{record['id']}"
        code, body, raw = self.request("DELETE", path)
        self.assertEqual(code, 204)
        self.assertIsNone(body)
        self.assertEqual(raw, b"")
        code, _, _ = self.request("GET", path)
        self.assertEqual(code, 404)
        code, _, _ = self.request("DELETE", path)
        self.assertEqual(code, 404)

    def test_item_endpoints_reject_invalid_ids_and_report_missing_records(self):
        for method in ["GET", "PUT", "PATCH", "DELETE"]:
            payload = self.valid_payload() if method == "PUT" else ({} if method == "PATCH" else None)
            for invalid_id in ["0", "-1", "not-a-number", "1.5"]:
                with self.subTest(method=method, inquiry_id=invalid_id):
                    code, _, _ = self.request(method, f"/inquiries/{invalid_id}", payload)
                    self.assertEqual(code, 422)
            with self.subTest(method=method, missing=True):
                code, _, _ = self.request(method, "/inquiries/4611686018427387904", payload)
                self.assertEqual(code, 404)

    def test_openapi_exposes_all_crud_methods(self):
        code, schema, _ = self.request("GET", "/openapi.json")
        self.assertEqual(code, 200)
        self.assertTrue({"get", "post"}.issubset(schema["paths"]["/inquiries"]))
        self.assertTrue({"get", "put", "patch", "delete"}.issubset(
            schema["paths"]["/inquiries/{inquiry_id}"]
        ))


if __name__ == "__main__":
    unittest.main()
