#!/usr/bin/env python3
"""Servicio de parsing de resultados - VERSIÓN COMPLETA"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ParsedResult:
    """Resultado parseado de una prueba"""
    status: str  # PASS, FAIL, INFO, ERROR, etc.
    raw_value: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def is_pass(self) -> bool:
        return self.status == "PASS"
    
    @property
    def is_fail(self) -> bool:
        return self.status == "FAIL"


class ParserService:
    """Servicio de parsing de resultados de pruebas - VERSIÓN COMPLETA"""
    
    RESULT_PATTERN = re.compile(r"\*(.*?)&")
    
    def parse(self, text: str, test_name: str) -> ParsedResult | None:
        """
        Parsea el resultado de una prueba
        
        Args:
            text: Texto de respuesta del dispositivo
            test_name: Nombre de la prueba
        
        Returns:
            ParsedResult o None si no se pudo parsear
        """
        # Buscar patrón principal (*...&)
        result_match = self.RESULT_PATTERN.search(text)
        raw_value = result_match.group(1) if result_match else text[:200]
        
        # ============================================================
        # PARSEAR SEGÚN TIPO DE PRUEBA (MIGRADO DE TU APP.PY ORIGINAL)
        # ============================================================
        
        # ----- CBSW Version -----
        if "CBSW Version" in test_name:
            match = re.search(r"v\d+\.\d+\.\d+\.\d+\s+\d+", text)
            if match:
                return ParsedResult(
                    status="CBSW",
                    raw_value=raw_value,
                    data={'version': match.group(0)},
                    metrics={'version': match.group(0)}
                )
        
        # ----- ABHW Version -----
        if "ABHW Version" in test_name:
            match = re.search(r"ab ver:([A-Z])", text, re.IGNORECASE)
            if match:
                return ParsedResult(
                    status="ABHW",
                    raw_value=raw_value,
                    data={'version': match.group(1)},
                    metrics={'version': match.group(1)}
                )
        
        # ----- CBHW Version -----
        if "CBHW Version" in test_name:
            match = re.search(r"cb ver:([A-Z])", text, re.IGNORECASE)
            if match:
                return ParsedResult(
                    status="CBHW",
                    raw_value=raw_value,
                    data={'version': match.group(1)},
                    metrics={'version': match.group(1)}
                )
        
        # ----- ADC -----
        if "ADC" in test_name:
            return self._parse_adc(text)
        
        # ----- USB3_3 Iperf Test -----
        if "USB3_3 Iperf Test" in test_name:
            parsed = self._parse_pcie(text)
            if parsed:
                return ParsedResult(
                    status="USB3",
                    raw_value=raw_value,
                    data={'ports': parsed['ports']},
                    metrics={'ports': len(parsed['ports'])}
                )
        
        # ----- USB2 Iperf Test -----
        if "USB2 Iperf Test" in test_name:
            parsed = self._parse_pcie(text)
            if parsed:
                return ParsedResult(
                    status="USB2",
                    raw_value=raw_value,
                    data={'ports': parsed['ports']},
                    metrics={'ports': len(parsed['ports'])}
                )
        
        # ----- PCIe Iperf Test -----
        if "PCIe Iperf Test" in test_name:
            parsed = self._parse_pcie(text)
            if parsed:
                return ParsedResult(
                    status="PCIE",
                    raw_value=raw_value,
                    data={'ports': parsed['ports']},
                    metrics={'ports': len(parsed['ports'])}
                )
        
        # ----- USB number of port / PCIe number of port -----
        if test_name in [
            "USB3_3 number of port",
            "USB2 number of port",
            "PCIe number of port"
        ]:
            return ParsedResult(
                status="COMMAND ACCEPT",
                raw_value=raw_value,
                data={'message': 'COMMAND ACCEPT'}
            )
        
        # ----- UART -----
        if "UART" in test_name:
            uart_result = self._parse_uart(text)
            if uart_result:
                return uart_result
        
        # ----- DDR -----
        if "DDR" in test_name:
            match = self.RESULT_PATTERN.search(text)
            if match:
                values = match.group(1).strip().split("|")
                if len(values) == 2:
                    return ParsedResult(
                        status="DDR",
                        raw_value=raw_value,
                        data={'score': values[0], 'result': values[1]},
                        metrics={'score': values[0]}
                    )
        
        # ----- THERMAL -----
        if "Thermal" in test_name:
            match = self.RESULT_PATTERN.search(text)
            if match:
                values = match.group(1).strip().split("|")
                if len(values) == 2:
                    return ParsedResult(
                        status="THERMAL",
                        raw_value=raw_value,
                        data={'temperature': values[0], 'humidity': values[1]},
                        metrics={'temp_c': float(values[0]), 'humidity_pct': float(values[1])}
                    )
        
        # ----- CURRENT SENSOR -----
        if "cursens" in test_name:
            match = self.RESULT_PATTERN.search(text)
            if match:
                values = match.group(1).strip().split("|")
                if len(values) == 2:
                    return ParsedResult(
                        status="CURRENT",
                        raw_value=raw_value,
                        data={'current': values[0], 'voltage': values[1]},
                        metrics={'current_a': float(values[0]), 'voltage_v': float(values[1])}
                    )
        
        # ----- SMBus -----
        if "SMBus" in test_name:
            match = self.RESULT_PATTERN.search(text)
            if match:
                values = match.group(1).strip().split("|")
                if len(values) == 3:
                    return ParsedResult(
                        status="SMBUS",
                        raw_value=raw_value,
                        data={'result': values[0], 'temp_c': values[1], 'temp_f': values[2]},
                        metrics={'temp_c': float(values[1]), 'temp_f': float(values[2])}
                    )
        
        # ----- KERNEL VERSION -----
        if "Kernel Version" in test_name:
            match = self.RESULT_PATTERN.search(text)
            if match:
                values = match.group(1).strip().split("|")
                if len(values) == 2:
                    return ParsedResult(
                        status="KERNEL",
                        raw_value=raw_value,
                        data={'version': values[0], 'build_date': values[1]},
                        metrics={'version': values[0]}
                    )
        
        # ----- EMMC/SDIO -----
        if test_name in ["EMMC-8bit", "EMMC-4bit", "SDIO"]:
            match = self.RESULT_PATTERN.search(text)
            if match:
                values = match.group(1).strip().split("|")
                if len(values) == 4:
                    return ParsedResult(
                        status="MMC",
                        raw_value=raw_value,
                        data={
                            'result': values[0],
                            'bus_width': values[1],
                            'clock': values[2],
                            'timing': values[3]
                        },
                        metrics={
                            'bus_width': values[1],
                            'clock': values[2],
                            'timing': values[3]
                        }
                    )
        
        # ----- I2C -----
        if "I2C" in test_name:
            match = self.RESULT_PATTERN.search(text)
            if match:
                values = match.group(1).strip().split("|")
                if len(values) == 2:
                    return ParsedResult(
                        status="I2C",
                        raw_value=raw_value,
                        data={'temp_c': values[0], 'temp_f': values[1]},
                        metrics={'temp_c': float(values[0]), 'temp_f': float(values[1])}
                    )
        
        # ----- SPI -----
        if "SPI" in test_name:
            match = self.RESULT_PATTERN.search(text)
            if match:
                values = match.group(1).strip().split("|", 1)
                if len(values) == 2:
                    return ParsedResult(
                        status="SPI",
                        raw_value=raw_value,
                        data={'result': values[0], 'device_id': values[1]},
                        metrics={'result': values[0]}
                    )
        
        # ----- I2S -----
        if "I2S" in test_name:
            match = self.RESULT_PATTERN.search(text)
            if match:
                values = match.group(1).strip().split("|")
                if len(values) == 2:
                    return ParsedResult(
                        status="I2S",
                        raw_value=raw_value,
                        data={'result': values[0], 'score': values[1]},
                        metrics={'score': values[1]}
                    )
        
        # ----- PWM -----
        if test_name == "PWM":
            return ParsedResult(
                status="CONFIGURATION",
                raw_value=raw_value,
                data={'message': 'CONFIGURATION'}
            )
        
        # ----- AB Mrcthreshold -----
        if "AB Mrcthreshold" in test_name:
            match = self.RESULT_PATTERN.search(text)
            if match:
                return ParsedResult(
                    status="MRCTHRESHOLD",
                    raw_value=raw_value,
                    data={'value': match.group(1).strip()}
                )
        
        # ----- HDMI -----
        if test_name == "HDMI":
            return ParsedResult(
                status="COMMAND_ACCEPT",
                raw_value=raw_value,
                data={'message': 'COMMAND_ACCEPT'}
            )
        
        # ----- GPIO -----
        if "GPIO" in test_name:
            return self._parse_gpio(text)
        
        # ============================================================
        # PARSEO GENÉRICO (PASS/FAIL)
        # ============================================================
        
        # Buscar PASS/FAIL en el patrón
        if result_match:
            value = result_match.group(1).strip()
            
            if value == "PASS":
                return ParsedResult(status="PASS", raw_value=raw_value)
            
            if value == "NG":
                return ParsedResult(status="FAIL", raw_value=raw_value)
            
            # Si no es PASS/FAIL pero tiene valor, devolver INFO
            return ParsedResult(
                status="INFO",
                raw_value=raw_value,
                data={'value': value}
            )
        
        # Si no hay patrón *...&, intentar detectar PASS/FAIL en el texto
        if "*PASS&" in text:
            return ParsedResult(status="PASS", raw_value=raw_value)
        if "*NG&" in text:
            return ParsedResult(status="FAIL", raw_value=raw_value)
        if "ERASE DID/PDR SUCCESS" in text:
            return ParsedResult(
                status="PASS",
                raw_value=raw_value,
                data={'message': 'ERASE DID/PDR SUCCESS'}
            )
        
        # Si no se pudo parsear nada
        return None
    
    def _parse_adc(self, text: str) -> ParsedResult | None:
        """Parsea ADC"""
        channels = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                float(line)
                channels.append(line)
            except ValueError:
                if "DON'T CARE" in line:
                    channels.append(line)
        
        if channels:
            return ParsedResult(
                status="ADC",
                raw_value="|".join(channels),
                data={'channels': channels},
                metrics={'channels': len(channels)}
            )
        return None
    
    def _parse_pcie(self, text: str) -> dict | None:
        """Parsea PCIe/USB"""
        lines = []
        for line in text.splitlines():
            if "|PINGOK|" in line or "|PINGNG|" in line:
                lines.append(line)
        
        if not lines:
            return None
        
        compact = lines[0]
        fields = compact.split("|")
        ports = []
        idx = 1
        i = 1
        
        while i + 2 < len(fields):
            ping = fields[i].strip()
            tx = fields[i + 1].strip()
            rx = fields[i + 2].strip()
            
            if ping in ["PINGOK", "PINGNG"]:
                ports.append({
                    "port": idx,
                    "ping": ping,
                    "tx": tx,
                    "rx": rx
                })
                idx += 1
            
            i += 3
        
        return {"ports": ports} if ports else None
    
    def _parse_uart(self, text: str) -> ParsedResult | None:
        """Parsea UART"""
        if "are identical" not in text:
            return None
        
        match = re.search(r"UART_rx_(\d+)", text)
        port = match.group(1) if match else "?"
        
        return ParsedResult(
            status="UART",
            raw_value=text[:200],
            data={'port': port, 'result': 'PASS'},
            metrics={'port': port}
        )
    
    def _parse_gpio(self, text: str) -> ParsedResult | None:
        """Parsea GPIO"""
        match = self.RESULT_PATTERN.search(text)
        if not match:
            return None
        
        bits = match.group(1).replace("|", "")
        
        return ParsedResult(
            status="GPIO",
            raw_value=bits,
            data={'bits': bits},
            metrics={'bits': bits}
        )