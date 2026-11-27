"""Errores tipados del motor de scheduling (contrato I3 v0.2, pendiente de revision)."""

from __future__ import annotations

from enum import Enum


class ErrorCode(str, Enum):
    UNKNOWN_COURSE = "UNKNOWN_COURSE"
    UNKNOWN_NRC = "UNKNOWN_NRC"
    DUPLICATE_NRC = "DUPLICATE_NRC"
    NOT_ELIGIBLE = "NOT_ELIGIBLE"
    INVALID_RANGE = "INVALID_RANGE"
    CAREER_NOT_SUPPORTED = "CAREER_NOT_SUPPORTED"


class ScheduleError(ValueError):
    """Error de validacion con codigo explicito."""

    def __init__(self, code: ErrorCode, message: str) -> None:
        super().__init__(f"{code.value}: {message}")
        self.code = code
        self.message = message
