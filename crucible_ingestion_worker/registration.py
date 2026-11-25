import logging
import socket
import threading
from importlib.metadata import version
from typing import Optional

import requests

logger = logging.getLogger(__name__)

DEFAULT_HEARTBEAT = 150
REQUEST_TIMEOUT = 15


def registration_body(config) -> dict:
    from crucible_ingestion.ingestors.registry import capabilities

    return {"kind": "ingestion",
            "capabilities": capabilities(),
            "buckets": sorted(set(config.storage_buckets) | set(config.storage_mounts)),
            "worker_version": version("crucible-ingestion-worker"),
            "package_version": version("crucible-ingestion")}


class Registration:
    """Registers this worker's ingestors with the API (PUT /workers/{worker_id}) and renews the
    registration every heartbeat_seconds the API asks for, until stopped. Ingestion never depends
    on it: a refused or failed call is logged and tried again at the next heartbeat."""

    def __init__(self, config, body: dict, worker_id: Optional[str] = None, session=None):
        self.url = f"{config.api_url.rstrip('/')}/workers/{worker_id or socket.gethostname()}"
        self.body = body
        self.session = session or requests.Session()
        self.session.headers["Authorization"] = f"Bearer {config.api_key}"
        self.stopped = threading.Event()
        self.thread: Optional[threading.Thread] = None
        self.last_status = None
        self.reported_ignored = False

    def register(self) -> float:
        """One registration call; returns the seconds until the next."""
        try:
            response = self.session.put(self.url, json=self.body, timeout=REQUEST_TIMEOUT)
            status = response.status_code
            if not response.ok:
                self._log_refusal(status, response.text[:200])
                return DEFAULT_HEARTBEAT
            data = response.json()
        except Exception as err:
            self._log_refusal(type(err).__name__, str(err)[:200])
            return DEFAULT_HEARTBEAT
        if self.last_status != status:
            logger.info(f"Registered with the API as {self.url.rsplit('/', 1)[1]} "
                        f"({len(self.body['capabilities'])} ingestors)")
        self.last_status = status
        if not self.reported_ignored:
            for item in data.get("ignored") or []:
                logger.warning(f"The API ignored {item.get('field')} of ingestor {item.get('name')}: {item.get('reason')}")
            self.reported_ignored = True
        return data.get("heartbeat_seconds") or DEFAULT_HEARTBEAT

    def _log_refusal(self, status, detail: str) -> None:
        if status == self.last_status:
            return
        self.last_status = status
        # 404 and 405 mean an API without worker registration; anything else is worth a look.
        level = logging.DEBUG if status in (404, 405) else logging.WARNING
        logger.log(level, f"Worker registration not accepted ({status}): {detail}")

    def _run(self) -> None:
        while not self.stopped.is_set():
            self.stopped.wait(self.register())

    def start(self) -> None:
        self.thread = threading.Thread(target=self._run, name="registration", daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self.stopped.set()
        if self.thread is not None:
            self.thread.join(timeout=5)
        try:
            self.session.delete(self.url, timeout=5)
        except Exception as err:
            logger.debug(f"Could not deregister: {err}")
