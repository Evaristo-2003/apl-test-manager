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


@dataclass
class TestSession:
    """Sesión completa de pruebas"""
    session_id: str
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    end_time: Optional[str] = None
    board_type: str = "AB"
    results: List[TestResult] = field(default_factory=list)
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    
    def add_result(self, result: TestResult):
        self.results.append(result)
        self.total_tests += 1
        if result.status == "PASS":
            self.passed += 1
        elif result.status == "FAIL":
            self.failed += 1
    
    def get_summary(self) -> Dict:
        return {
            'session_id': self.session_id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'board_type': self.board_type,
            'total_tests': self.total_tests,
            'passed': self.passed,
            'failed': self.failed,
            'pass_rate': f"{(self.passed/self.total_tests*100):.2f}%" if self.total_tests > 0 else "0%"
        }