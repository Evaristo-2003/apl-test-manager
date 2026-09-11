#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Modelo de resultado de prueba"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List
import json


@dataclass
class TestMetric:
    """Métrica individual de una prueba"""
    name: str
    value: Any
    unit: Optional[str] = None
    min_limit: Optional[float] = None
    max_limit: Optional[float] = None
    status: str = "UNKNOWN"  # PASS, FAIL, WARNING


@dataclass
class TestResult:
    """Resultado completo de una prueba"""
    test_name: str
    status: str  # PASS, FAIL, RUNNING, NOT_RUN, UNKNOWN
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    duration_ms: Optional[float] = None
    metrics: List[TestMetric] = field(default_factory=list)
    raw_response: str = ""
    parsed_data: Dict[str, Any] = field(default_factory=dict)
    verification: Dict[str, Any] = field(default_factory=dict)
    board_type: str = "UNKNOWN"  # AB, CB
    command: str = ""
    
    def to_dict(self) -> Dict:
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

