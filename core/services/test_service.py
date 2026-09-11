#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Servicio de ejecución de pruebas"""

import time
from typing import Dict, Optional, Tuple, Callable
from core.models.test_result import TestResult, TestMetric
from core.services.parser_service import ParserService
from core.services.verification_service import VerificationService
from core.repositories.button_repository import ButtonRepository
from core.services.serial_service import SerialService


class TestService:
    """Orquesta la ejecución de pruebas"""
    
    def __init__(self, serial_service: SerialService):
        self.serial_service = serial_service
        self.button_repo = ButtonRepository()
        self.parser = ParserService()
        self.verifier = VerificationService()
        self.on_progress: Optional[Callable] = None
        self.on_log: Optional[Callable] = None
    
# En test_service.py, modificar para que on_log sea una señal, no una función directa

    def set_callbacks(self, on_progress=None, on_log=None, on_error=None):
        """Configura callbacks (que deben ser señales)"""
        self._on_log = on_log
        self._on_progress = on_progress
        self._on_error = on_error

    def _log(self, message: str):
        """Emite mensaje de log (usa la señal)"""
        if self._on_log:
            # ✅ Usar emit si es una señal, o llamar si es función
            try:
                self._on_log(message)
            except RuntimeError:
                # Si el objeto ya fue eliminado, ignorar
                pass
            
    def _progress(self, current: int, total: int):
        """Emite progreso"""
        if self.on_progress:
            self.on_progress(current, total)
    
    def execute_test(self, button: Dict) -> TestResult:
        """Ejecuta una prueba individual"""
        label = button['label']
        action = button['action']
        test_type = action.get('type', 'single')
        
        self._log(f"▶ INICIANDO: {label}")
        
        start_time = time.time()
        result = TestResult(
            test_name=label,
            status="RUNNING",
            board_type="AB" if action.get('target') == 2 else "CB"
        )
        
        try:
            if test_type == 'single':
                result = self._execute_single(button, result)
            elif test_type == 'sequence':
                result = self._execute_sequence(button, result)
            elif test_type == 'sequence_buttons':
                result = self._execute_sequence_buttons(button, result)
            else:
                result.status = "FAIL"
                result.parsed_data = {'error': f'Tipo desconocido: {test_type}'}
        except Exception as e:
            result.status = "FAIL"
            result.parsed_data = {'error': str(e)}
            self._log(f"❌ ERROR: {str(e)}")
        
        result.duration_ms = (time.time() - start_time) * 1000
        self._log(f"✓ FINALIZADO: {label} - {result.status}")
        
        return result
    
    def _execute_single(self, button: Dict, result: TestResult) -> TestResult:
        """Ejecuta prueba tipo single"""
        action = button['action']
        cmd = action['cmd']
        target = action.get('target', 1)
        end_marker = action.get('end_marker')
        
        result.command = cmd
        
        # Seleccionar adaptador
        adapter = self.serial_service.cb_adapter if target == 1 else self.serial_service.ab_adapter
        
        # Ejecutar comando
        if end_marker:
            response = adapter.execute_command_until(cmd, end_marker, timeout=120)
        else:
            response = adapter.execute_command(cmd)
        
        result.raw_response = response
        
        # Parsear
        parsed = self.parser.parse(response, button['label'])
        result.parsed_data = parsed.__dict__ if parsed else {}
        
        # Verificar

        if parsed:

            verification = self.verifier.verify(button['label'],parsed)
            result.verification = (verification.__dict__ if verification else {})

            result.status = (
                verification.status
                if verification
                else "UNKNOWN"
            )

            if hasattr(verification, "metrics"):
                result.metrics = verification.metrics

        else:

            # Comandos de configuración sin respuesta parseable
            result.status = "PASS"
        
        return result
    
    def _execute_sequence(self, button: Dict, result: TestResult) -> TestResult:
        """Ejecuta prueba tipo sequence"""

        action = button['action']
        steps = action.get('steps', [])

        results = []

        for step in steps:

            cmd = step.get('cmd')
            target = step.get('target', 1)
            end_marker = step.get('end_marker')
            delay = step.get('delay', 0)

            adapter = (
                self.serial_service.cb_adapter
                if target == 1
                else self.serial_service.ab_adapter
            )

            if end_marker:
                response = adapter.execute_command_until(
                    cmd,
                    end_marker,
                    timeout=120
                )
            else:
                response = adapter.execute_command(cmd)

            parsed = self.parser.parse(
                response,
                button['label']
            )

            results.append({
                'cmd': cmd,
                'response': response,
                'parsed': parsed
            })

            if delay > 0:
                time.sleep(delay)

        result.raw_response = '\n'.join(
            r['response'] for r in results
        )

        result.parsed_data = {
            'steps': results
        }

        # Estados válidos para secuencias
        valid_status = {
            "PASS",
            "UART",
            "I2C",
            "SPI",
            "I2S",
            "GPIO",
            "ADC",
            "SMBUS",
            "MMC",
            "DDR",
            "THERMAL",
            "CURRENT",
            "CONFIGURATION",
            "COMMAND ACCEPT",
            "COMMAND_ACCEPT"
        }

        sequence_ok = True

        for step in results:

            parsed = step.get("parsed")

            # Algunos pasos son sólo comandos de configuración
            if parsed is None:
                continue

            if parsed.status not in valid_status:
                sequence_ok = False
                break

        result.status = "PASS" if sequence_ok else "FAIL"

        return result
    
    def _execute_sequence_buttons(self, button: Dict, result: TestResult) -> TestResult:
        """Ejecuta secuencia de botones"""
        action = button['action']
        button_names = action.get('buttons', [])
        
        results = []
        total = len(button_names)
        
        for i, name in enumerate(button_names):
            self._progress(i + 1, total)
            self._log(f"📋 {i+1}/{total}: {name}")
            
            btn = self.button_repo.get_by_label(name)
            if not btn:
                self._log(f"⚠️ Botón no encontrado: {name}")
                continue
            
            # Ejecutar recursivamente (pero sin recursión infinita)
            sub_result = self.execute_test(btn)
            results.append(sub_result)
        
        result.parsed_data = {'sub_results': results}
        
        # Resumen
        passed = sum(1 for r in results if r.status == "PASS")
        failed = len(results) - passed
        
        result.status = "PASS" if failed == 0 else "FAIL"
        result.metrics.append(TestMetric(
            name="total_tests",
            value=len(results),
            unit="count"
        ))
        result.metrics.append(TestMetric(
            name="passed",
            value=passed,
            unit="count"
        ))
        result.metrics.append(TestMetric(
            name="failed",
            value=failed,
            unit="count"
        ))
        
        return result