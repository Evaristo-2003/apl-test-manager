#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Modelo de sesión de pruebas"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional
from .test_result import TestResult


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