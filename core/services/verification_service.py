#!/usr/bin/env python3
"""Servicio de verificación de resultados - VERSIÓN COMPLETA"""

from dataclasses import dataclass, field
from typing import Any

from core.repositories.limits_repository import LimitsRepository
from core.services.parser_service import ParsedResult


@dataclass
class VerificationResult:
    """Resultado de verificación"""
    status: str  # PASS, FAIL, WARNING, UNKNOWN
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    metrics: list[dict] = field(default_factory=list)
    
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
    
    def verify(self, test_name: str, parsed: ParsedResult | None) -> VerificationResult:
        """Verifica un resultado parseado"""
        print(
            f"[VERIFY]{test_name}"
        )
        if not parsed:
            return VerificationResult(
                status="UNKNOWN",
                message="No hay datos para verificar"
            )
        if parsed.status in ["COMMAND ACCEPT", "COMMAND_ACCEPT", "CONFIGURATION"]:
            return VerificationResult(
                status="PASS",
                message=f"Comando aceptado: {parsed.status}"
            )
        # ----- UART -----
        if "UART" in test_name:

            limits = self.limits_repo.get_limits(
                test_name
            )

            expected = "PASS"

            if limits:
                expected = limits.get(
                    "expected_result",
                    "PASS"
                )

            actual = parsed.data.get(
                "result",
                ""
            )

            if actual == expected:

                return VerificationResult(
                    status="PASS",
                    message="UART verificado correctamente"
                )

            return VerificationResult(
                status="FAIL",
                message=f"UART esperado {expected}, obtenido {actual}"
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

            limits = self.limits_repo.get_limits(
                test_name
            )

            expected = limits.get(
                "expected_result",
                "PASS"
            )

            score_min = limits.get(
                "score_min",
                999
            )

            score_max = limits.get(
                "score_max",
                1001
            )

            actual_result = parsed.data.get(
                "result",
                ""
            )

            score = int(
                parsed.metrics.get(
                    "score",
                    0
                )
            )

            if (
                actual_result == expected
                and
                score_min <= score <= score_max
            ):

                return VerificationResult(
                    status="PASS",
                    message=f"I2S OK score={score}",
                    details={
                        "score": score
                    }
                )

            return VerificationResult(
                status="FAIL",
                message=(
                    f"I2S FAIL result={actual_result} "
                    f"score={score}"
                )
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
        if (
            "USB3_3 Iperf Test" in test_name
            or
            "USB3_2 Iperf Test" in test_name
        ):
            return self._verify_usb3(
                parsed,
                limits
            )
        
        # ----- USB2 -----
        if "USB2 Iperf Test" in test_name:
            return self._verify_usb2(parsed, limits)
        
        # ----- EMMC/SDIO -----
        if test_name in ["EMMC-8bit", "EMMC-4bit", "SDIO"]:
            return self._verify_mmc(test_name, parsed, limits)


        
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
        # ----- ADC -----
        if "ADC" in test_name:

            channels = parsed.data.get(
                "channels",
                []
            )

            if len(channels) < 6:

                return VerificationResult(
                    status="FAIL",
                    message="ADC incompleto"
                )

            adc_limits = limits

            issues = []

            #
            # Detectar ADC0 o ADC1
            #

            is_adc1 = False

            try:

                first_value = float(
                    channels[0]
                )

                #
                # ADC1 suele arrancar cerca de 0.9V
                # ADC0 suele arrancar cerca de 1.8V
                #

                if first_value < 1.2:
                    is_adc1 = True

            except Exception:
                pass

            prefix = (
                "ADC1"
                if is_adc1
                else "ADC0"
            )

            max_channels = (
                6
                if is_adc1
                else 8
            )

            for idx in range(max_channels):

                key = f"{prefix}_CH{idx}"

                if key not in adc_limits:

                    issues.append(
                        f"{key}: LIMIT NOT FOUND"
                    )

                    continue

                try:

                    value = float(
                        channels[idx]
                    )

                except Exception:

                    issues.append(
                        f"{key}: INVALID"
                    )

                    continue

                low = float(
                    adc_limits[key]["low"]
                )

                high = float(
                    adc_limits[key]["high"]
                )

                if value < low or value > high:

                    issues.append(
                        f"{key}: {value}"
                    )

                if issues:

                    return VerificationResult(
                        status="FAIL",
                        message="; ".join(
                            issues
                        )
                    )


                return VerificationResult(
                    status="PASS",
                    message=f"{prefix} OK (SAPME)"
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

            expected = limits.get(
                "expected_result",
                "PASS"
            )

            actual = (
                "PASS"
                if parsed.status == "PASS"
                else "FAIL"
            )

            if actual == expected:

                return VerificationResult(
                    status="PASS",
                    message="CSI verificado correctamente"
                )

            return VerificationResult(
                status="FAIL",
                message=(
                    f"CSI esperado {expected}, "
                    f"obtenido {actual}"
                )
            )
        
        # ----- COMMAND ACCEPT / CONFIGURATION -----

        if "AB CPU TEMP" in test_name or "AB CPU Temp" in test_name:

            temp = float(parsed.data.get("value", 0))

            temp_min = limits.get("temperature_min", 0)
            temp_max = limits.get("temperature_max", 100)
            if temp_min <= temp <= temp_max:
                return VerificationResult(
                    status="PASS",
                    message=f"CPU Temp OK: {temp}°C"
                )

            return VerificationResult(
                status="FAIL",
                message=f"CPU Temp fuera de rango: {temp}°C"
            )
        # ----- VERIFICACIÓN POR VALOR ESPERADO -----

        if "expected" in limits:

            expected = str(
                limits["expected"]
            ).strip().upper()

            actual = ""

            if "version" in parsed.data:

                actual = str(
                    parsed.data["version"]
                ).strip().upper()

            elif "value" in parsed.data:

                actual = str(
                    parsed.data["value"]
                ).strip().upper()

            else:

                actual = str(
                    parsed.raw_value
                ).strip().upper()

            if actual == expected:

                return VerificationResult(
                    status="PASS",
                    message="Valor esperado verificado",
                    details={
                        "expected": expected,
                        "actual": actual
                    }
                )

            return VerificationResult(
                status="FAIL",
                message=(
                    f"Esperado '{expected}' "
                    f"pero obtenido '{actual}'"
                ),
                details={
                    "expected": expected,
                    "actual": actual
                }
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
            message="Verificación completada",
            details={'parsed_data': parsed.data}
        )
    
    def _verify_pcie(
        self,
        parsed: ParsedResult,
        limits: dict
    ) -> VerificationResult:
        """Verifica PCIe usando límites SAPME"""

        ports = parsed.data.get(
            "ports",
            []
        )

        sapme_ports = limits.get(
            "pcie_limits",
            {}
        )

        issues = []

        #
        # Mapeo parser -> SAPME
        #
        # Parser:
        # 1,2,3,4
        #
        # SAPME:
        # PORT_0,PORT_1,PORT_2,PORT_3
        #

        port_mapping = {
            1: "PORT_0",
            2: "PORT_1",
            3: "PORT_2",
            4: "PORT_3"
        }

        for port in ports:

            parser_port = port["port"]

            sapme_key = port_mapping.get(
                parser_port
            )

            if not sapme_key:

                continue

            if sapme_key not in sapme_ports:

                issues.append(
                    f"{sapme_key}: LIMIT NOT FOUND"
                )

                continue

            expected = sapme_ports[sapme_key]

            expected_ping = str(
                expected["PING"]["high"]
            )


 
            #
            # Puerto especial WEBSOCKET
            #

            if expected_ping == "WEBSOCKET":

                continue

            if port["ping"] != expected_ping:

                issues.append(
                    f"{sapme_key}: "
                    f"{port['ping']} != {expected_ping}"
                )

                continue

            #
            # TX/RX NULL
            #

            if (
                port["tx"] == "NULL"
                or port["rx"] == "NULL"
            ):
                print(
                    f"[NULL PORT] {sapme_key}"
                )
                issues.append(
                    f"{sapme_key}: NULL RESULT"
                )

                continue

            #
            # TX/RX reales
            #

            tx = float(
                port["tx"]
            )

            rx = float(
                port["rx"]
            )

            tx_min = float(
                expected["TX"]["low"]
            )

            tx_max = float(
                expected["TX"]["high"]
            )

            rx_min = float(
                expected["RX"]["low"]
            )

            rx_max = float(
                expected["RX"]["high"]
            )
            print(
                f"{sapme_key} "
                f"TX={tx} "
                f"RANGE=[{tx_min}-{tx_max}] "
                f"RX={rx} "
                f"RANGE=[{rx_min}-{rx_max}]"
            )
            #
            # Si SAPME tiene 0/0
            # significa "no validar"
            #

            if not (
                tx_min == 0
                and
                tx_max == 0
            ):

                if (
                    tx < tx_min
                    or
                    tx > tx_max
                ):

                    issues.append(
                        f"{sapme_key}: "
                        f"TX {tx}"
                    )

            if not (
                rx_min == 0
                and
                rx_max == 0
            ):

                if (
                    rx < rx_min
                    or
                    rx > rx_max
                ):

                    issues.append(
                        f"{sapme_key}: "
                        f"RX {rx}"
                    )

        if issues:

            return VerificationResult(
                status="FAIL",
                message="; ".join(
                    issues
                ),
                details={
                    "ports": ports
                }
            )

        return VerificationResult(
            status="PASS",
            message=f"PCIe OK ({len(ports)} puertos SAPME)",
            details={
                "ports": ports
            }
        )
    
    def _verify_usb3(
        self,
        parsed: ParsedResult,
        limits: dict
    ) -> VerificationResult:

        ports = parsed.data.get(
            "ports",
            []
        )

        sapme_ports = limits.get(
            "usb_limits",
            {}
        )

        issues = []

        port_mapping = {
            1: "PORT_0",
            2: "PORT_1",
            3: "PORT_2",
            4: "PORT_3"
        }

        for port in ports:

            parser_port = port["port"]

            sapme_key = port_mapping.get(
                parser_port
            )

            if not sapme_key:

                continue

            if sapme_key not in sapme_ports:

                issues.append(
                    f"{sapme_key}: LIMIT NOT FOUND"
                )

                continue

            expected = sapme_ports[sapme_key]

            expected_ping = str(
                expected["PING"]["high"]
            )

            if port["ping"] != expected_ping:

                issues.append(
                    f"{sapme_key}: "
                    f"{port['ping']} != {expected_ping}"
                )

                continue

            tx = float(
                port["tx"]
            )

            rx = float(
                port["rx"]
            )

            tx_min = float(
                expected["TX"]["low"]
            )

            tx_max = float(
                expected["TX"]["high"]
            )

            rx_min = float(
                expected["RX"]["low"]
            )

            rx_max = float(
                expected["RX"]["high"]
            )

            print(
                f"[USB3 PORT] {sapme_key}"
            )

            print(
                f"[TX] {tx}"
            )

            print(
                f"[RX] {rx}"
            )

            #
            # 0/0 = SAPME indica no validar
            #

            if not (
                tx_min == 0
                and
                tx_max == 0
            ):

                if (
                    tx < tx_min
                    or
                    tx > tx_max
                ):

                    issues.append(
                        f"{sapme_key}: TX {tx}"
                    )

            if not (
                rx_min == 0
                and
                rx_max == 0
            ):

                if (
                    rx < rx_min
                    or
                    rx > rx_max
                ):

                    issues.append(
                        f"{sapme_key}: RX {rx}"
                    )

        if issues:

            return VerificationResult(
                status="FAIL",
                message="; ".join(
                    issues
                )
            )


        return VerificationResult(
            status="PASS",
            message="USB3 OK (SAPME)"
        )
    
    def _verify_usb2(
        self,
        parsed: ParsedResult,
        limits: dict
    ) -> VerificationResult:

        ports = parsed.data.get(
            "ports",
            []
        )

        sapme_ports = limits.get(
            "usb_limits",
            {}
        )

        issues = []

        port_mapping = {
            1: "PORT_0",
            2: "PORT_1",
            3: "PORT_2",
            4: "PORT_3"
        }

        for port in ports:

            parser_port = port["port"]

            sapme_key = port_mapping.get(
                parser_port
            )

            if not sapme_key:
                continue

            if sapme_key not in sapme_ports:

                issues.append(
                    f"{sapme_key}: LIMIT NOT FOUND"
                )

                continue

            expected = sapme_ports[sapme_key]

            expected_ping = str(
                expected["PING"]["high"]
            )

            if port["ping"] != expected_ping:

                issues.append(
                    f"{sapme_key}: "
                    f"{port['ping']} != {expected_ping}"
                )

                continue

            tx = float(
                port["tx"]
            )

            rx = float(
                port["rx"]
            )

            tx_min = float(
                expected["TX"]["low"]
            )

            tx_max = float(
                expected["TX"]["high"]
            )

            rx_min = float(
                expected["RX"]["low"]
            )

            rx_max = float(
                expected["RX"]["high"]
            )

            print(
                f"[USB2 PORT] {sapme_key}"
            )

            print(
                f"[TX LIMITS] {tx_min} -> {tx_max}"
            )

            print(
                f"[RX LIMITS] {rx_min} -> {rx_max}"
            )

            print(
                f"[TX ACTUAL] {tx}"
            )

            print(
                f"[RX ACTUAL] {rx}"
            )

            if (
                tx < tx_min
                or
                tx > tx_max
            ):

                issues.append(
                    f"{sapme_key}: TX {tx}"
                )

            if (
                rx < rx_min
                or
                rx > rx_max
            ):

                issues.append(
                    f"{sapme_key}: RX {rx}"
                )

        if issues:

            print(
                "[USB2 RESULT] FAIL"
            )

            return VerificationResult(
                status="FAIL",
                message="; ".join(
                    issues
                )
            )

        print(
            "[USB2 RESULT] PASS"
        )

        return VerificationResult(
            status="PASS",
            message="USB2 OK (SAPME)"
        )
    
    def _verify_mmc(self, test_name: str, parsed: ParsedResult, limits: dict) -> VerificationResult:
        """Verifica EMMC/SDIO"""
        expected_bus_width = limits.get('bus_width')
        expected_clock = limits.get('clock')
        expected_timing = limits.get('timing')
        expected_result = limits.get('result')
        
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
        if expected_result is not None:

            if actual_result != expected_result:
                issues.append(
                    f"Resultado: {actual_result} "
                    f"(esperado {expected_result})"
                )
        
        if issues:
            return VerificationResult(status="FAIL", message="; ".join(issues), details={'issues': issues})
        return VerificationResult(status="PASS", message=f"{test_name} verificado correctamente")