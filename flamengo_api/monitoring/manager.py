from __future__ import annotations

import threading
import uuid
from typing import Dict, List, Optional

from flamengo_api.core.errors import Conflict, NotFound, ApiError
from flamengo_api.monitoring.models import MonitorJob
from flamengo_api.monitoring.worker import MonitorWorker
from flamengo_api.services.notifier_service import NotifierService
from flamengo_api.services.session_manager import SessionManager

from flamengo_tickets.flamengo.services import FlamengoTicketService


class MonitorManager:
    def __init__(self, session_manager: SessionManager, notifier_service: NotifierService) -> None:
        self._sessions = session_manager
        self._notifier_service = notifier_service
        self._jobs: Dict[str, MonitorJob] = {}
        self._threads: Dict[str, threading.Thread] = {}
        self._stops: Dict[str, threading.Event] = {}
        self._lock = threading.RLock()

    def list_jobs(self) -> List[MonitorJob]:
        with self._lock:
            return list(self._jobs.values())

    def get_job(self, job_id: str) -> MonitorJob:
        with self._lock:
            job = self._jobs.get(job_id)
        if not job:
            raise NotFound("Job não encontrado", details={"job_id": job_id})
        return job

    def stop_job(self, job_id: str) -> MonitorJob:
        job = self.get_job(job_id)
        ev = self._stops.get(job_id)
        if ev:
            ev.set()
        return job

    def start_job(
        self,
        *,
        account_id: str,
        event_id: int,
        sector_ids: Optional[List[int]] = None,
        poll_interval_seconds: Optional[float] = None,
        max_cart_tickets: Optional[int] = None,
    ) -> MonitorJob:
        if not self._sessions.is_logged(account_id):
            raise ApiError("Conta não está logada. Faça login antes.", status=400, code="not_logged")

        # evita múltiplos jobs por conta (mais seguro com sessão compartilhada)
        with self._lock:
            for j in self._jobs.values():
                if j.account_id == account_id and j.status == "running":
                    raise Conflict("Já existe um monitoramento em execução para esta conta.")

        job_id = str(uuid.uuid4())
        job = MonitorJob(
            id=job_id,
            account_id=account_id,
            event_id=int(event_id),
            sector_ids=[int(x) for x in (sector_ids or [])],
        )
        if poll_interval_seconds is not None:
            job.poll_interval_seconds = float(poll_interval_seconds)
        if max_cart_tickets is not None:
            job.max_cart_tickets = int(max_cart_tickets)

        acc_sess = self._sessions.get(account_id)
        client = acc_sess.client  # wrapper thread-safe

        ticket_service = FlamengoTicketService(client)

        # carrega detalhes do evento e setores
        events = ticket_service.fetch_events()
        event = next((e for e in events if int(e.id) == int(event_id)), None)
        if not event:
            raise NotFound("Evento não encontrado para esta conta", details={"event_id": event_id})

        sectors_map = ticket_service.fetch_sectors_map(event.id)

        notifier = self._notifier_service.build()
        # anexa a sessão do app para reaproveitar session/log
        try:
            notifier.attach_http_client(client)
        except Exception:
            pass

        stop_event = threading.Event()
        worker = MonitorWorker(
            job=job,
            client=client,
            event=event,
            sectors_map=sectors_map,
            notifier=notifier,
            stop_event=stop_event,
        )

        thread = threading.Thread(target=worker.run, name=f"monitor-{job_id}", daemon=True)

        with self._lock:
            self._jobs[job_id] = job
            self._threads[job_id] = thread
            self._stops[job_id] = stop_event

        thread.start()
        return job
