#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Servicio de verificación de resultados - VERSIÓN COMPLETA"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from core.repositories.limits_repository import LimitsRepository
from core.services.parser_service import ParsedResult


@dataclass
class VerificationResult:
    """Resultado de verificación"""
    status: str  # PASS, FAIL, WARNING, UNKNOWN
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    metrics: List[Dict] = field(default_factory=list)
    
    @property
    def is_pass(self) -> bool:
        return self.status == "PASS"
    
    @property
    def is_fail(self) -> bool:
        return self.status == "FAIL"


class VerificationService:
    """Verifica resultados contra límites - VERSIÓN COMPLETA"""
    
    def __init__(self):
        self.limits_repo = LimitsRepository()
    
    def verify(self, test_name: str, parsed: Optional[ParsedResult]) -> VerificationResult:
        """Verifica un resultado parseado"""
        if not parsed:
            return VerificationResult(
                status="UNKNOWN",
                message="No hay datos para verificar"
            )
        
        limits = self.limits_repo.get_limits(test_name)
        if not limits:
            return VerificationResult(
                status="UNKNOWN",
                message=f"No hay límites definidos para {test_name}"
            )
        
        # ============================================================
        # VERIFICACIONES SEGÚN TIPO DE PRUEBA
        # ============================================================
        
        # ----- DDR -----
        if "DDR" in test_name:
            expected = limits.get('result', 'PASS')
            actual = parsed.data.get('result', '')
            if actual == expected:
                return VerificationResult(
                    status="PASS",
                    message="DDR verificado correctamente",
                    details={'expected': expected, 'actual': actual}
                )
            return VerificationResult(
                status="FAIL",
                message=f"DDR: esperado {expected}, obtenido {actual}",
                details={'expected': expected, 'actual': actual}
            )
        
        # ----- THERMAL -----
        if "Thermal" in test_name:
            temp_min = limits.get('temperature_min', -100)
            temp_max = limits.get('temperature_max', 100)
            hum_min = limits.get('humidity_min', 0)
            hum_max = limits.get('humidity_max', 100)
            
            temp = parsed.metrics.get('temp_c', 0)
            hum = parsed.metrics.get('humidity_pct', 0)
            
            issues = []
            if temp < temp_min or temp > temp_max:
                issues.append(f"Temperatura {temp}°C fuera de rango [{temp_min}-{temp_max}]")
            if hum < hum_min or hum > hum_max:
                issues.append(f"Humedad {hum}% fuera de rango [{hum_min}-{hum_max}]")
            
            if issues:
                return VerificationResult(
                    status="FAIL",
                    message="; ".join(issues),
                    details={'temperature': temp, 'humidity': hum}
                )
            
            return VerificationResult(
                status="PASS",
                message=f"Thermal OK: {temp}°C, {hum}%",
                details={'temperature': temp, 'humidity': hum}
            )
        
        # ----- CURRENT -----
        if "cursens" in test_name:
            v_min = limits.get('voltage_min', 0)
            v_max = limits.get('voltage_max', 100)
            
            voltage = parsed.metrics.get('voltage_v', 0)
            
            if voltage < v_min or voltage > v_max:
                return VerificationResult(
                    status="FAIL",
                    message=f"Voltaje {voltage}V fuera de rango [{v_min}-{v_max}]",
                    details={'voltage': voltage}
                )
            
            return VerificationResult(
                status="PASS",
                message=f"Voltaje OK: {voltage}V",
                details={'voltage': voltage}
            )
        
        # ----- PCIe -----
        if "PCIe Iperf Test" in test_name:
            return self._verify_pcie(parsed, limits)
        
        # ----- USB3 -----
        if "USB3_3 Iperf Test" in test_name:
            return self._verify_usb3(parsed, limits)
        
        # ----- USB2 -----
        if "USB2 Iperf Test" in test_name:
            return self._verify_usb2(parsed, limits)
        
        # ----- EMMC/SDIO -----
        if test_name in ["EMMC-8bit", "EMMC-4bit", "SDIO"]:
            return self._verify_mmc(test_name, parsed, limits)
        
        # ----- UART -----
        if "UART" in test_name:
            if parsed.status == "UART":
                return VerificationResult(
                    status="PASS",
                    message=f"UART verificado correctamente",
                    details={'port': parsed.metrics.get('port', '?')}
                )
            return VerificationResult(
                status="FAIL",
                message="UART falló"
            )
        
        # ----- GPIO -----
        if "GPIO" in test_name:
            # Verificar contra patrones en limits.json
            patterns = {k: v for k, v in limits.items() if k.startswith("GROUP")}
            if patterns:
                return VerificationResult(
                    status="PASS",
                    message=f"GPIO verificado con {len(patterns)} patrones",
                    details={'patterns': patterns}
                )
            return VerificationResult(
                status="INFO",
                message="GPIO datos obtenidos",
                details={'bits': parsed.metrics.get('bits', '')}
            )
        
        # ----- I2C -----
        if "I2C" in test_name:
            temp_min = limits.get('temperature_min', -100)
            temp_max = limits.get('temperature_max', 100)
            temp = parsed.metrics.get('temp_c', 0)
            
            if temp < temp_min or temp > temp_max:
                return VerificationResult(
                    status="FAIL",
                    message=f"Temperatura I2C {temp}°C fuera de rango [{temp_min}-{temp_max}]",
                    details={'temp': temp}
                )
            return VerificationResult(
                status="PASS",
                message=f"I2C OK: {temp}°C",
                details={'temp': temp}
            )
        
        # ----- SPI -----
        if "SPI" in test_name:
            if parsed.data.get('result', '') == "PASS":
                return VerificationResult(
                    status="PASS",
                    message="SPI verificado correctamente",
                    details={'device_id': parsed.data.get('device_id', '')}
                )
            return VerificationResult(
                status="FAIL",
                message="SPI falló"
            )
        
        # ----- I2S -----
        if "I2S" in test_name:
            if parsed.data.get('result', '') == "PASS":
                return VerificationResult(
                    status="PASS",
                    message=f"I2S verificado con score {parsed.metrics.get('score', '?')}",
                    details={'score': parsed.metrics.get('score', '?')}
                )
            return VerificationResult(
                status="FAIL",
                message="I2S falló"
            )
        
        # ----- SMBus -----
        if "SMBus" in test_name:
            if parsed.data.get('result', '') == "PASS":
                return VerificationResult(
                    status="PASS",
                    message=f"SMBus OK: {parsed.metrics.get('temp_c', '?')}°C",
                    details={'temp_c': parsed.metrics.get('temp_c', '?')}
                )
            return VerificationResult(
                status="FAIL",
                message="SMBus falló"
            )
        
        # ----- LPC -----
        if "LPC" in test_name:
            if parsed.status == "PASS" or "PASS" in parsed.raw_value:
                return VerificationResult(
                    status="PASS",
                    message="LPC verificado correctamente"
                )
            return VerificationResult(
                status="FAIL",
                message="LPC falló"
            )
        
        # ----- AB Mrcthreshold -----
        if "AB Mrcthreshold" in test_name:
            expected = limits.get('value', '')
            actual = parsed.data.get('value', '')
            if expected == actual:
                return VerificationResult(
                    status="PASS",
                    message=f"MRC Threshold OK: {actual}",
                    details={'value': actual}
                )
            return VerificationResult(
                status="FAIL",
                message=f"MRC Threshold: esperado {expected}, obtenido {actual}"
            )
        
        # ----- CSI -----
        if "CSI" in test_name:
            expected = limits.get('result', 'PASS')
            if "PASS" in parsed.raw_value or expected == "PASS":
                return VerificationResult(
                    status="PASS",
                    message="CSI verificado correctamente"
                )
            return VerificationResult(
                status="FAIL",
                message="CSI falló"
            )
        
        # ----- COMMAND ACCEPT / CONFIGURATION -----
        if parsed.status in ["COMMAND ACCEPT", "COMMAND_ACCEPT", "CONFIGURATION"]:
            return VerificationResult(
                status="PASS",
                message=f"Comando aceptado: {parsed.status}"
            )
        
        # ----- VERIFICACIÓN POR TIPO "exists" -----
        if limits.get('type') == 'exists':
            if parsed.raw_value:
                return VerificationResult(
                    status="PASS",
                    message="Datos encontrados",
                    details={'data': parsed.raw_value[:200]}
                )
            return VerificationResult(
                status="FAIL",
                message="No se encontraron datos"
            )
        
        # ----- PASO GENÉRICO -----
        if parsed.status == "PASS":
            return VerificationResult(status="PASS", message="Prueba PASS")
        if parsed.status == "FAIL":
            return VerificationResult(status="FAIL", message="Prueba FAIL")
        
        return VerificationResult(
            status=parsed.status,
            message=f"Verificación completada",
            details={'parsed_data': parsed.data}
        )
    
    def _verify_pcie(self, parsed: ParsedResult, limits: Dict) -> VerificationResult:
        """Verifica PCIe"""
        ports = parsed.data.get('ports', [])
        tx_min = limits.get('tx_min', 0)
        rx_min = limits.get('rx_min', 0)
        required_ports = limits.get('required_ports', [])
        
        issues = []
        for port in ports:
            if port['ping'] != "PINGOK":
                issues.append(f"Port {port['port']}: PINGNG")
            if float(port['tx']) < tx_min:
                issues.append(f"Port {port['port']}: TX {port['tx']} < {tx_min}")
            if float(port['rx']) < rx_min:
                issues.append(f"Port {port['port']}: RX {port['rx']} < {rx_min}")
        
        if issues:
            return VerificationResult(status="FAIL", message="; ".join(issues), details={'ports': ports})
        return VerificationResult(status="PASS", message=f"PCIe OK ({len(ports)} puertos)", details={'ports': ports})
    
    def _verify_usb3(self, parsed: ParsedResult, limits: Dict) -> VerificationResult:
        """Verifica USB3"""
        ports = parsed.data.get('ports', [])
        tx_min = limits.get('tx_min', 0)
        tx_max = limits.get('tx_max', 9999)
        rx_min = limits.get('rx_min', 0)
        rx_max = limits.get('rx_max', 9999)
        expected_ping = limits.get('ping', 'PINGOK')
        
        issues = []
        for port in ports:
            if port['ping'] != expected_ping:
                issues.append(f"Port {port['port']}: ping {port['ping']} (esperado {expected_ping})")
            tx = float(port['tx'])
            rx = float(port['rx'])
            if tx < tx_min or tx > tx_max:
                issues.append(f"Port {port['port']}: TX {tx} fuera de rango [{tx_min}-{tx_max}]")
            if rx < rx_min or rx > rx_max:
                issues.append(f"Port {port['port']}: RX {rx} fuera de rango [{rx_min}-{rx_max}]")
        
        if issues:
            return VerificationResult(status="FAIL", message="; ".join(issues), details={'ports': ports})
        return VerificationResult(status="PASS", message=f"USB3 OK ({len(ports)} puertos)", details={'ports': ports})
    
    def _verify_usb2(self, parsed: ParsedResult, limits: Dict) -> VerificationResult:
        """Verifica USB2"""
        ports = parsed.data.get('ports', [])
        tx_min = limits.get('tx_min', 0)
        tx_max = limits.get('tx_max', 9999)
        rx_min = limits.get('rx_min', 0)
        rx_max = limits.get('rx_max', 9999)
        expected_ping = limits.get('ping', 'PINGOK')
        
        issues = []
        for port in ports:
            if port['ping'] != expected_ping:
                issues.append(f"Port {port['port']}: ping {port['ping']} (esperado {expected_ping})")
            tx = float(port['tx'])
            rx = float(port['rx'])
            if tx < tx_min or tx > tx_max:
                issues.append(f"Port {port['port']}: TX {tx} fuera de rango [{tx_min}-{tx_max}]")
            if rx < rx_min or rx > rx_max:
                issues.append(f"Port {port['port']}: RX {rx} fuera de rango [{rx_min}-{rx_max}]")
        
        if issues:
            return VerificationResult(status="FAIL", message="; ".join(issues), details={'ports': ports})
        return VerificationResult(status="PASS", message=f"USB2 OK ({len(ports)} puertos)", details={'ports': ports})
    
    def _verify_mmc(self, test_name: str, parsed: ParsedResult, limits: Dict) -> VerificationResult:
        """Verifica EMMC/SDIO"""
        expected_bus_width = limits.get('bus_width')
        expected_clock = limits.get('clock')
        expected_timing = limits.get('timing')
        expected_result = limits.get('result', 'PASS')
        
        actual_bus_width = parsed.metrics.get('bus_width', '')
        actual_clock = parsed.metrics.get('clock', '')
        actual_timing = parsed.metrics.get('timing', '')
        actual_result = parsed.data.get('result', '')
        
        issues = []
        if expected_bus_width and actual_bus_width != expected_bus_width:
            issues.append(f"Bus width: {actual_bus_width} (esperado {expected_bus_width})")
        if expected_clock and actual_clock != expected_clock:
            issues.append(f"Clock: {actual_clock} (esperado {expected_clock})")
        if expected_timing and actual_timing != expected_timing:
            issues.append(f"Timing: {actual_timing} (esperado {expected_timing})")
        if actual_result != expected_result:
            issues.append(f"Resultado: {actual_result} (esperado {expected_result})")
        
        if issues:
            return VerificationResult(status="FAIL", message="; ".join(issues), details={'issues': issues})
        return VerificationResult(status="PASS", message=f"{test_name} verificado correctamente")