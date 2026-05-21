from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from app.services.stale_jobs import stale_job_cutoff


def test_stale_job_cutoff_uses_configured_timeout(monkeypatch):
    monkeypatch.setattr(
        "app.services.stale_jobs.settings",
        SimpleNamespace(JOB_STALE_TIMEOUT_MINUTES=90),
    )
    now = datetime(2026, 5, 21, 12, 0, tzinfo=timezone.utc)

    assert stale_job_cutoff(now) == now - timedelta(minutes=90)


def test_stale_job_cutoff_normalizes_naive_datetime(monkeypatch):
    monkeypatch.setattr(
        "app.services.stale_jobs.settings",
        SimpleNamespace(JOB_STALE_TIMEOUT_MINUTES=60),
    )
    now = datetime(2026, 5, 21, 12, 0)

    cutoff = stale_job_cutoff(now)

    assert cutoff.tzinfo == timezone.utc
    assert cutoff == datetime(2026, 5, 21, 11, 0, tzinfo=timezone.utc)


def test_stale_job_cutoff_enforces_minimum_timeout(monkeypatch):
    monkeypatch.setattr(
        "app.services.stale_jobs.settings",
        SimpleNamespace(JOB_STALE_TIMEOUT_MINUTES=0),
    )
    now = datetime(2026, 5, 21, 12, 0, tzinfo=timezone.utc)

    assert stale_job_cutoff(now) == now - timedelta(minutes=1)
