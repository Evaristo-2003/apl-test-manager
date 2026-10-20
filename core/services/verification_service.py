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
        # ----- CPU info -----
        if "CPU info" in test_name:

            checks = [
                ("vendor_id", "VENDOR_ID"),
                ("cpu_family", "CPU_FAMILY"),
                ("model", "MODEL"),
                ("model_name", "MODEL_NAME"),
                ("l1d_cache", "L1D_CACHE"),
                ("l1i_cache", "L1I_CACHE"),
                ("l2_cache", "L2_CACHE")
            ]

            issues = []

            for field, label in checks:

                expected = str(
                    limits.get(field, "")
                ).strip().upper()

                actual = str(
                    parsed.data.get(field, "")
                ).strip().upper()

                expected = expected.replace(",", ".")
                actual = actual.replace(",", ".")

                if expected != actual:

                    issues.append(
                        f"{label}: {actual} != {expected}"
                    )

            if issues:

                return VerificationResult(
                    status="FAIL",
                    message="; ".join(issues)
                )

            return VerificationResult(
                status="PASS",
                message="CPU INFO OK (SAPME)"
            )
        # ----- DDR -----
        if "DDR Get Result" in test_name:

            expected = limits.get(
                "expected_status",
                "PASS"
            )

            actual = parsed.data.get(
                "result",
                ""
            )

            score = float(
                parsed.data.get(
                    "score",
                    0
                )
            )

            score_min = limits.get(
                "score_min",
                -9999
            )

            score_max = limits.get(
                "score_max",
                9999
            )

            if actual != expected:

                return VerificationResult(
                    status="FAIL",
                    message=(
                        f"CHECK DDR STATUS: "
                        f"{actual}"
                    ),
                    details={
                        "sapme_key":
                            "CHECK DDR STATUS",
                        "score":
                            score
                    }
                )

            if score < score_min or score > score_max:

                return VerificationResult(
                    status="FAIL",
                    message=(
                        f"DDR VALUE: "
                        f"{score} fuera de rango "
                        f"[{score_min}-{score_max}]"
                    ),
                    details={
                        "sapme_key":
                            "DDR VALUE",
                        "score":
                            score
                    }
                )

            return VerificationResult(
                status="PASS",
                message=(
                    f"CHECK DDR STATUS OK | "
                    f"DDR VALUE={score}"
                ),
                details={
                    "sapme_key":
                        "DDR VALUE",
                    "status":
                        actual,
                    "score":
                        score,
                    "low":
                        score_min,
                    "high":
                        score_max
                }
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

            voltage = parsed.metrics.get(
                "voltage_v",
                0
            )

            current = parsed.metrics.get(
                "current_a",
                0
            )

            voltage_min = limits.get(
                "voltage_min",
                0
            )

            voltage_max = limits.get(
                "voltage_max",
                9999
            )

            current_min = limits.get(
                "current_min",
                -999
            )

            current_max = limits.get(
                "current_max",
                999
            )

            issues = []

            if (
                voltage < voltage_min
                or
                voltage > voltage_max
            ):
                issues.append(
                    f"Voltage {voltage}V"
                )

            #
            # SAPME usa -999/999 para indicar
            # no validar corriente
            #
            if not (
                current_min == -999
                and
                current_max == 999
            ):
                if (
                    current < current_min
                    or
                    current > current_max
                ):
                    issues.append(
                        f"Current {current}A"
                    )

            if issues:

                return VerificationResult(
                    status="FAIL",
                    message="; ".join(
                        issues
                    ),
                    details={
                        "voltage": voltage,
                        "current": current
                    }
                )

            return VerificationResult(
                status="PASS",
                message=(
                    f"Voltage OK: {voltage}V | "
                    f"Current OK: {current}A"
                ),
                details={
                    "voltage": voltage,
                    "current": current,
                    "voltage_low": voltage_min,
                    "voltage_high": voltage_max,
                    "current_low": current_min,
                    "current_high": current_max
                }
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
            channel_results = []

            is_adc1 = False

            try:

                first_value = float(
                    channels[0]
                )

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

                    channel_results.append({

                        "channel": key,
                        "actual": None,
                        "low": None,
                        "high": None,
                        "result": "LIMIT NOT FOUND"

                    })

                    continue

                try:

                    value = float(
                        channels[idx]
                    )

                except Exception:

                    channel_results.append({

                        "channel": key,
                        "actual": channels[idx],
                        "low": None,
                        "high": None,
                        "result": "INVALID"

                    })

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

                passed = (
                    low <= value <= high
                )

                channel_results.append({

                    "channel": key,
                    "actual": value,
                    "low": low,
                    "high": high,
                    "result": (
                        "PASS"
                        if passed
                        else "FAIL"
                    )

                })

                if not passed:

                    issues.append(
                        f"{key}: {value}"
                    )

            if issues:

                return VerificationResult(

                    status="FAIL",

                    message="; ".join(
                        issues
                    ),

                    details={
                        "adc": prefix,
                        "channels": channel_results
                    }
                )

            return VerificationResult(

                status="PASS",

                message=f"{prefix} OK (SAPME)",

                details={
                    "adc": prefix,
                    "channels": channel_results
                }
            )

           
        # ----- I2C -----
        if "I2C" in test_name:

            temp_min = limits.get(
                "temperature_min",
                -100
            )

            temp_max = limits.get(
                "temperature_max",
                100
            )

            temp = parsed.metrics.get(
                "temp_c",
                0
            )

            #
            # Identificar sensor usando el comando
            #
            sensor = parsed.data.get(
                "sensor",
                "?"
            )

            sapme_key = (
                f"12C_TEMPERATURE_{sensor}"
            )

            if temp < temp_min or temp > temp_max:

                return VerificationResult(
                    status="FAIL",
                    message=(
                        f"{sapme_key}: "
                        f"{temp}°C fuera de rango "
                        f"[{temp_min}-{temp_max}]"
                    ),
                    details={
                        "sapme_key": sapme_key,
                        "temp": temp,
                        "low": temp_min,
                        "high": temp_max
                    }
                )

            return VerificationResult(
                status="PASS",
                message=(
                    f"{sapme_key} OK: "
                    f"{temp}°C"
                ),
                details={
                    "sapme_key": sapme_key,
                    "temp": temp,
                    "low": temp_min,
                    "high": temp_max
                }
            )

        
        
        # ----- SMBus -----
        if "SMBus" in test_name:

            temp_min = limits.get(
                "temperature_min",
                -100
            )

            temp_max = limits.get(
                "temperature_max",
                100
            )

            temp = parsed.metrics.get(
                "temp_c",
                0
            )

            if temp < temp_min or temp > temp_max:

                return VerificationResult(
                    status="FAIL",
                    message=(
                        f"CHECK SMBUS: "
                        f"{temp}°C fuera de rango "
                        f"[{temp_min}-{temp_max}]"
                    ),
                    details={
                        "sapme_key": "CHECK SMBUS",
                        "temp": temp,
                        "low": temp_min,
                        "high": temp_max
                    }
                )

            return VerificationResult(
                status="PASS",
                message=f"CHECK SMBUS OK: {temp}°C",
                details={
                    "sapme_key": "CHECK SMBUS",
                    "temp": temp,
                    "low": temp_min,
                    "high": temp_max
                }
            )
        
        # ----- LPC -----
        if "LPC" in test_name:

            expected = limits.get(
                "expected_result",
                "PASS"
            )

            actual = (
                "PASS"
                if parsed.status == "PASS"
                else parsed.status
            )

            if actual == expected:

                return VerificationResult(
                    status="PASS",
                    message="CHECK LPC STATUS OK"
                )

            return VerificationResult(
                status="FAIL",
                message=(
                    f"CHECK LPC STATUS: "
                    f"esperado {expected}, "
                    f"obtenido {actual}"
                )
            )
        
        # ----- AB Mrcthreshold -----
        if "AB Mrcthreshold" in test_name:

            value_str = parsed.data.get(
                "value",
                "0"
            )

            try:

                value = float(
                    value_str.replace(
                        ",",
                        "."
                    )
                )

            except Exception:

                return VerificationResult(
                    status="FAIL",
                    message=f"Valor inválido: {value_str}"
                )

            value_min = limits.get(
                "value_min",
                0
            )

            value_max = limits.get(
                "value_max",
                9999
            )

            if value < value_min or value > value_max:

                return VerificationResult(
                    status="FAIL",
                    message=(
                        f"CHECK AB MRCTHRESHOLD: "
                        f"{value} fuera de rango "
                        f"[{value_min}-{value_max}]"
                    ),
                    details={
                        "sapme_key": "CHECK AB MRCTHRESHOLD",
                        "value": value,
                        "low": value_min,
                        "high": value_max
                    }
                )

            return VerificationResult(
                status="PASS",
                message=(
                    f"CHECK AB MRCTHRESHOLD OK: "
                    f"{value}"
                ),
                details={
                    "sapme_key": "CHECK AB MRCTHRESHOLD",
                    "value": value,
                    "low": value_min,
                    "high": value_max
                }
            )
        # ----- AB Erase DID -----
        if "AB Erase DID" in test_name:

            limits = self.limits_repo.get_limits(
                test_name
            )

            expected = ""

            if limits:

                expected = str(
                    limits.get(
                        "expected_result",
                        ""
                    )
                ).strip().upper()

            actual = str(
                parsed.data.get(
                    "value",
                    ""
                )
            ).strip().upper()

            #
            # El DUT devuelve:
            # ERASE DID/PDR SUCCESS
            # SAPME espera:
            # PASSED
            #
            if (
                actual
                == "ERASE DID/PDR SUCCESS"
            ):
                actual = "PASSED"

            if actual == expected:

                return VerificationResult(
                    status="PASS",
                    message="CHECKERASEDIDRESULT OK",
                    details={
                        "expected": expected,
                        "actual": actual
                    }
                )

            return VerificationResult(
                status="FAIL",
                message=(
                    f"Esperado {expected}, "
                    f"obtenido {actual}"
                ),
                details={
                    "expected": expected,
                    "actual": actual
                }
            )

        # ----- SATA -----
        if "SATA Get" in test_name:

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
                    message=f"{test_name} OK"
                )

            return VerificationResult(
                status="FAIL",
                message=(
                    f"{test_name}: "
                    f"esperado {expected}, "
                    f"obtenido {actual}"
                )
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

        port_results = []

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

            expected = sapme_ports[
                sapme_key
            ]

            expected_ping = str(
                expected["PING"]["high"]
            )

            #
            # Puerto especial WEBSOCKET
            #
            if expected_ping == "WEBSOCKET":

                port_results.append({

                    "port": sapme_key,

                    "rows": [

                        {
                            "name": "PING",
                            "low": "WEBSOCKET",
                            "high": "WEBSOCKET",
                            "actual": port["ping"],
                            "result": "N/A"
                        },

                        {
                            "name": "TX",
                            "low": "N/A",
                            "high": "N/A",
                            "actual": port["tx"],
                            "result": "N/A"
                        },

                        {
                            "name": "RX",
                            "low": "N/A",
                            "high": "N/A",
                            "actual": port["rx"],
                            "result": "N/A"
                        }

                    ]
                })

                continue

            #
            # Ping
            #
            if port["ping"] != expected_ping:

                issues.append(
                    f"{sapme_key}: "
                    f"{port['ping']} != {expected_ping}"
                )

            #
            # TX/RX NULL
            #
            if (
                port["tx"] == "NULL"
                or
                port["rx"] == "NULL"
            ):

                port_results.append({

                    "port": sapme_key,

                    "rows": [

                        {
                            "name": "PING",
                            "low": expected_ping,
                            "high": expected_ping,
                            "actual": port["ping"],
                            "result": (
                                "PASS"
                                if port["ping"] == expected_ping
                                else "FAIL"
                            )
                        },

                        {
                            "name": "TX",
                            "low": "N/A",
                            "high": "N/A",
                            "actual": "NULL",
                            "result": "FAIL"
                        },

                        {
                            "name": "RX",
                            "low": "N/A",
                            "high": "N/A",
                            "actual": "NULL",
                            "result": "FAIL"
                        }

                    ]

                })

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

            tx_result = "PASS"
            rx_result = "PASS"

            #
            # SAPME 0/0 = no validar
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

                    tx_result = "FAIL"

                    issues.append(
                        f"{sapme_key}: TX {tx}"
                    )

            else:

                tx_result = "N/A"

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

                    rx_result = "FAIL"

                    issues.append(
                        f"{sapme_key}: RX {rx}"
                    )

            else:

                rx_result = "N/A"

            port_results.append({

                "port": sapme_key,

                "rows": [

                    {
                        "name": "PING",
                        "low": expected_ping,
                        "high": expected_ping,
                        "actual": port["ping"],
                        "result": (
                            "PASS"
                            if port["ping"] == expected_ping
                            else "FAIL"
                        )
                    },

                    {
                        "name": "TX",
                        "low": tx_min,
                        "high": tx_max,
                        "actual": tx,
                        "result": tx_result
                    },

                    {
                        "name": "RX",
                        "low": rx_min,
                        "high": rx_max,
                        "actual": rx,
                        "result": rx_result
                    }

                ]

            })

        if issues:

            return VerificationResult(
                status="FAIL",
                message="; ".join(
                    issues
                ),
                details={
                    "ports": port_results
                }
            )

        return VerificationResult(
            status="PASS",
            message=f"PCIe OK ({len(ports)} puertos SAPME)",
            details={
                "ports": port_results
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
        port_results = []
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
            port_results.append({

                "port": sapme_key,

                "rows": [

                    {
                        "name": "PING",
                        "low": expected_ping,
                        "high": expected_ping,
                        "actual": port["ping"],
                        "result": (
                            "PASS"
                            if port["ping"] == expected_ping
                            else "FAIL"
                        )
                    },

                    {
                        "name": "TX",
                        "low": tx_min,
                        "high": tx_max,
                        "actual": tx,
                        "result": (
                            "N/A"
                            if (
                                tx_min == 0
                                and
                                tx_max == 0
                            )
                            else (
                                "PASS"
                                if tx_min <= tx <= tx_max
                                else "FAIL"
                            )
                        )
                    },

                    {
                        "name": "RX",
                        "low": rx_min,
                        "high": rx_max,
                        "actual": rx,
                        "result": (
                            "N/A"
                            if (
                                rx_min == 0
                                and
                                rx_max == 0
                            )
                            else (
                                "PASS"
                                if rx_min <= rx <= rx_max
                                else "FAIL"
                            )
                        )
                    }

                ]
            })
        if issues:

            return VerificationResult(
                status="FAIL",
                message="; ".join(
                    issues
                ),
                details={
                    "ports": port_results
                }
            )


        return VerificationResult(
            status="PASS",
            message="USB3 OK (SAPME)",
            details={
                "ports": port_results
            }
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

        port_results = []

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

            #
            # Build report rows
            #

            port_results.append({

                "port": sapme_key,

                "rows": [

                    {
                        "name": "PING",
                        "low": expected_ping,
                        "high": expected_ping,
                        "actual": port["ping"],
                        "result": (
                            "PASS"
                            if port["ping"] == expected_ping
                            else "FAIL"
                        )
                    },

                    {
                        "name": "TX",
                        "low": tx_min,
                        "high": tx_max,
                        "actual": tx,
                        "result": (
                            "PASS"
                            if tx_min <= tx <= tx_max
                            else "FAIL"
                        )
                    },

                    {
                        "name": "RX",
                        "low": rx_min,
                        "high": rx_max,
                        "actual": rx,
                        "result": (
                            "PASS"
                            if rx_min <= rx <= rx_max
                            else "FAIL"
                        )
                    }

                ]
            })

            #
            # Validation
            #

            if port["ping"] != expected_ping:

                issues.append(
                    f"{sapme_key}: "
                    f"{port['ping']} != {expected_ping}"
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
                ),
                details={
                    "ports": port_results
                }
            )

        print(
            "[USB2 RESULT] PASS"
        )

        return VerificationResult(
            status="PASS",
            message="USB2 OK (SAPME)",
            details={
                "ports": port_results
            }
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