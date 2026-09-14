#!/usr/bin/env python3
"""Modelo de resultado de prueba"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class TestMetric:
    """Métrica individual de una prueba"""
    name: str
    value: Any
    unit: str | None = None
    min_limit: float | None = None
    max_limit: float | None = None
    status: str = "UNKNOWN"  # PASS, FAIL, WARNING


@dataclass
class TestResult:
    """Resultado completo de una prueba"""
    test_name: str
    status: str  # PASS, FAIL, RUNNING, NOT_RUN, UNKNOWN
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    duration_ms: float | None = None
    metrics: list[TestMetric] = field(default_factory=list)
    raw_response: str = ""
    parsed_data: dict[str, Any] = field(default_factory=dict)
    verification: dict[str, Any] = field(default_factory=dict)
    board_type: str = "UNKNOWN"  # AB, CB
    command: str = ""
    
    def to_dict(self) -> dict:
        return {
            'test_name': self.test_name,
            'status': self.status,
            'timestamp': self.timestamp,
            'duration_ms': self.duration_ms,
            'metrics': [m.__dict__ for m in self.metrics],
            'parsed_data': self.parsed_data,
            'verification': self.verification,
            'board_type': self.board_type,
            'command': self.command
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, default=str)

