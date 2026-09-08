#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Core package para APL Test Manager"""

__version__ = "2.0.0"
__author__ = "Reverse Engineering Team"

# Exportar clases principales
from .models import TestResult, TestMetric, TestSession
from .repositories import ButtonRepository, LimitsRepository
from .services import (
    SerialService, TestService, 
    ParserService, ParsedResult,
    VerificationService, VerificationResult
)
from .adapters import (
    SerialAdapter, WebSocketAdapter, 
    WSMessage, WSResponse,
    FPGAAdapter, FPGACommand
)