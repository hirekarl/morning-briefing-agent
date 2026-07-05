"""Single patchable time source used for all hours_back/hours_ahead window math."""

from datetime import UTC, datetime


def utcnow() -> datetime:
    return datetime.now(UTC)
