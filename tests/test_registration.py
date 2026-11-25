import logging

import requests

from crucible_ingestion_worker.config import load_config
from crucible_ingestion_worker.registration import DEFAULT_HEARTBEAT, Registration

CONFIG = load_config({"CRUCIBLE_API_URL": "https://crucible.example/api/v4/", "CRUCIBLE_API_KEY": "k",
                      "RABBITMQ_HOST": "h", "RABBITMQ_PASSWORD": "pw", "QUEUE": "q"})
BODY = {"kind": "ingestion", "capabilities": [{"name": "AFMIngestor"}], "buckets": ["b"],
        "worker_version": "1", "package_version": "2"}


class Response:
    def __init__(self, status, data=None):
        self.status_code, self.ok, self.data, self.text = status, 200 <= status < 300, data, str(data)

    def json(self):
        return self.data


class Session:
    def __init__(self, *responses):
        self.headers, self.responses, self.calls = {}, list(responses), []

    def put(self, url, json, timeout):
        self.calls.append(("PUT", url, json))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response

    def delete(self, url, timeout):
        self.calls.append(("DELETE", url, None))


def test_registers_follows_the_heartbeat_and_reports_ignored_metadata_once(caplog):
    ignored = {"heartbeat_seconds": 90, "ignored": [{"name": "AFMIngestor", "field": "file_extensions", "reason": "bad"}]}
    session = Session(Response(200, ignored), Response(200, ignored))
    registration = Registration(CONFIG, BODY, worker_id="pod-1", session=session)
    with caplog.at_level(logging.WARNING):
        assert registration.register() == 90
        assert registration.register() == 90
    assert session.calls[0] == ("PUT", "https://crucible.example/api/v4/workers/pod-1", BODY)
    assert session.headers["Authorization"] == "Bearer k"
    assert len([r for r in caplog.records if "ignored file_extensions" in r.message]) == 1


def test_a_refused_or_failed_registration_is_retried_at_the_default_heartbeat():
    session = Session(Response(404, {"detail": "Not Found"}), requests.exceptions.ConnectionError("down"))
    registration = Registration(CONFIG, BODY, worker_id="pod-1", session=session)
    assert registration.register() == DEFAULT_HEARTBEAT
    assert registration.register() == DEFAULT_HEARTBEAT


def test_stop_deregisters():
    session = Session(Response(200, {"heartbeat_seconds": 3600}))
    registration = Registration(CONFIG, BODY, worker_id="pod-1", session=session)
    registration.start()
    registration.stop()
    assert [c[0] for c in session.calls] == ["PUT", "DELETE"]
