# -*- coding: utf-8 -*-
"""Structured errors for consistent CLI exit codes."""

from __future__ import annotations


class GWTError(Exception):
    def __init__(self, message: str, exit_code: int = 1):
        super().__init__(message)
        self.exit_code = int(exit_code)

