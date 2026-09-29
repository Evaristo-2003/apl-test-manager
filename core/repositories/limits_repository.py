#!/usr/bin/env python3
"""Repositorio para limits.json"""

import json
import logging
from pathlib import Path
from typing import Any
from core.state.app_state import app_state

logger = logging.getLogger(__name__)


class LimitsRepository:
    """Carga y consulta límites de pruebas"""
    
    def __init__(self, config_path: str = "limits.json"):
        self.config_path = Path(config_path)
        self._limits = {}
        self._load()
    
    def _load(self):
        """Carga el archivo JSON"""
        if not self.config_path.exists():
            logger.warning(f"No se encuentra: {self.config_path}, usando límites por defecto")
            self._limits = self._get_default_limits()
            return
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._limits = json.load(f)
            logger.info(f"Límites cargados desde {self.config_path}")
        except Exception as e:
            logger.error(f"Error cargando límites: {e}")
            self._limits = self._get_default_limits()
    
    def _get_default_limits(self) -> dict:
        """Retorna límites por defecto si no hay archivo"""
        return {
            "Check PCB ID": {"type": "exists"},
            "Check ABL": {"type": "exists"},
            "Kernel Version": {"type": "exists"},
            "CPU info": {"type": "exists"},
            "Thermal Port 0": {
                "temperature_min": 15,
                "temperature_max": 60,
                "humidity_min": 5,
                "humidity_max": 95
            },
            "Thermal Port 4": {
                "temperature_min": 15,
                "temperature_max": 60,
                "humidity_min": 5,
                "humidity_max": 95
            },
            "cursens_12vtoj6": {
                "voltage_min": 11.0,
                "voltage_max": 12.5
            },
            "cursens_hsbridge": {
                "voltage_min": 11.0,
                "voltage_max": 12.5
            },
            "cursens_ab3v3": {
                "voltage_min": 3.2,
                "voltage_max": 3.4
            },
            "cursens_ab5v": {
                "voltage_min": 4.8,
                "voltage_max": 5.2
            },
            "cursens_12vtoab": {
                "voltage_min": 11.0,
                "voltage_max": 12.5
            },
            "DDR Get Result": {"result": "PASS"},
            "PCIe Iperf Test": {
                "required_ports": [1, 2, 3],
                "tx_min": 400,
                "rx_min": 200
            },
            "USB3_3 Iperf Test": {
                "ping": "PINGOK",
                "tx_min": 350,
                "tx_max": 1000,
                "rx_min": 200,
                "rx_max": 1000
            },
            "USB2 Iperf Test": {
                "ping": "PINGOK",
                "tx_min": 50,
                "tx_max": 100,
                "rx_min": 50,
                "rx_max": 100
            },
            "EMMC-8bit": {
                "bus_width": "3",
                "clock": "200000000",
                "timing": "10"
            },
            "EMMC-4bit": {
                "result": "PASS",
                "bus_width": "2",
                "clock": "200000000",
                "timing": "9"
            },
            "SDIO": {
                "result": "PASS",
                "bus_width": "2",
                "clock": "50000000",
                "timing": "2"
            },
            "UART": {
                "expected_ports": [
                    "PORT 0 CB -> AB",
                    "PORT 0 AB -> CB",
                    "PORT 1 CB -> AB",
                    "PORT 1 AB -> CB",
                    "PORT 3 CB -> AB",
                    "PORT 3 AB -> CB"
                ]
            },
            "GPIO": {
                "GROUP1_CB_ORDER HIGH_0-15": "1111111111111101",
                "GROUP1_CB_ORDER LOW_0-15": "0000000000000000",
                "GROUP1_AB_ORDER HIGH_0-15": "1111111111111101",
                "GROUP1_AB_ORDER LOW_0-15": "0000000000000000",
                "GROUP2_CB_ORDER HIGH_16-31": "0111111111111111",
                "GROUP2_CB_ORDER LOW_16-31": "0000000000000000",
                "GROUP2_AB_ORDER HIGH_16-31": "0111111111111111",
                "GROUP2_AB_ORDER LOW_16-31": "0000000000000000",
                "GROUP3_CB_ORDER HIGH_32-41": "1111111111",
                "GROUP3_CB_ORDER LOW_32-41": "0000010000",
                "GROUP3_AB_ORDER HIGH_32-41": "1111111111",
                "GROUP3_AB_ORDER LOW_32-41": "0000010000"
            },
            "I2S": {"result": "PASS", "score": "999"},
            "SPI": {"type": "exists"},
            "I2C": {"temperature_min": 15, "temperature_max": 60},
            "SMBus": {"result": "PASS"},
            "LPC": {"result": "PASS"},
            "AB Mrcthreshold": {"value": "0,2"},
            "CSI": {"result": "PASS"}
        }
    
    def get_limits(
        self,
        test_name: str
    ) -> dict[str, Any] | None:
        print(
            f"[LIMITS] Solicitando límites para: {test_name}"
        )
        #
        # SAPME primero
        #

        if (
            app_state.sapme_ready
            and
            app_state.sapme_limits
        ):

            sapme_limits = self._get_sapme_limits(
                test_name
            )

            if sapme_limits:
                return sapme_limits

        #
        # Fallback limits.json
        #

        return self._limits.get(
            test_name
        )
    
    def get_all(self) -> dict[str, Any]:
        """Obtiene todos los límites"""
        return self._limits
    
    def has_limits(self, test_name: str) -> bool:
        """Verifica si existen límites para una prueba"""
        return test_name in self._limits
    
    def reload(self):
        """Recarga el archivo"""
        self._limits = {}
        self._load()

    def get_limits(
        self,
        test_name: str
    ) -> dict[str, Any] | None:

        #
        # SAPME tiene prioridad
        #
        print(
            f"[SAPME] Solicitando límites para: {test_name}"
        )
        if (
            app_state.sapme_ready
            and
            app_state.sapme_limits
        ):

            sapme = app_state.sapme_limits

            #
            # ADC
            #
            if test_name == "ADC":

                adc = sapme.get(
                    "ADC",
                    {}
                )

                if adc:

                    print(
                        "[SAPME] ADC solicitado"
                    )

                    return adc
            #
            # Kernel Version
            #

            print(
                f"[SAPME] Solicitando límites para: {test_name}"
            )

            if test_name == "Kernel Version":

                cpu = sapme.get(
                    "CPU",
                    {}
                )

                data = cpu.get(
                    "CHECK KERNEL VERSION"
                )

                if data:

                    return {
                        "expected":
                            str(
                                data["high"]
                            ).replace(
                                ",",
                                "."
                            )
                    }

            #
            # CBHW Version
            #

            if test_name == "CBHW Version":

                print(
                    "[SAPME] CBHW Version solicitado"
                )

                version = sapme.get(
                    "VERSION",
                    {}
                )

                data = version.get(
                    "CHECK CB HW VERSION"
                )

                if data:

                    print(
                        f"[SAPME] Valor encontrado: {data['high']}"
                    )

                    return {
                        "expected":
                            str(
                                data["high"]
                            )
                            .replace(
                                "CB VER:",
                                ""
                            )
                            .strip()
                            .upper()
                    }

            #
            # CBSW Version
            #

            if test_name == "CBSW Version":

                print(
                    "[SAPME] CBSW Version solicitado"
                )

                version = sapme.get(
                    "VERSION",
                    {}
                )

                data = version.get(
                    "CHECK CB SW VERSION"
                )

                if data:

                    print(
                        f"[SAPME] Valor encontrado: {data['high']}"
                    )

                    return {
                        "expected":
                            str(
                                data["high"]
                            )
                            .replace(
                                ",",
                                "."
                            )
                            .strip()
                            .upper()
                    }

            #
            # ABHW Version
            #

            if test_name == "ABHW Version":

                print(
                    "[SAPME] ABHW Version solicitado"
                )

                version = sapme.get(
                    "VERSION",
                    {}
                )

                data = version.get(
                    "CHECK AB HW VERSION"
                )

                if data:

                    print(
                        f"[SAPME] Valor encontrado: {data['high']}"
                    )

                    return {
                        "expected":
                            str(
                                data["high"]
                            )
                            .replace(
                                "AB VER:",
                                ""
                            )
                            .strip()
                            .upper()
                    }

            #
            # ABSW Version
            #

            if test_name == "ABSW Version":

                print(
                    "[SAPME] ABSW Version solicitado"
                )

                version = sapme.get(
                    "VERSION",
                    {}
                )

                data = version.get(
                    "CHECK AB SW VERSION"
                )

                if data:

                    print(
                        f"[SAPME] Valor encontrado: {data['high']}"
                    )

                    return {
                        "expected":
                            str(
                                data["high"]
                            )
                            .replace(
                                ",",
                                "."
                            )
                            .strip()
                            .upper()
                    }

            #
            # cursens_12vtoj6
            #

            if test_name == "cursens_12vtoj6":

                power = sapme.get(
                    "POWER",
                    {}
                )

                data = power.get(
                    "CURSENS_12VTOJ6_VOLTAGE"
                )

                if data:

                    print(
                        "[SAPME] cursens_12vtoj6 solicitado"
                    )

                    return {
                        "voltage_min": float(
                            data["low"]
                        ),
                        "voltage_max": float(
                            data["high"]
                        )
                    }

            #
            # cursens_hsbridge
            #

            if test_name == "cursens_hsbridge":

                power = sapme.get(
                    "POWER",
                    {}
                )

                data = power.get(
                    "CURSENS_HSBRIDGE_VOLTAGE"
                )

                if data:

                    print(
                        "[SAPME] cursens_hsbridge solicitado"
                    )

                    return {
                        "voltage_min": float(
                            data["low"]
                        ),
                        "voltage_max": float(
                            data["high"]
                        )
                    }
            #
            # Thermal Port 0
            #

            if test_name == "Thermal Port 0":

                thermal = sapme.get(
                    "THERMAL",
                    {}
                )

                temp = thermal.get(
                    "CB_BOARD_TEMP"
                )

                hum = thermal.get(
                    "CB_BOARD_HUMIDITY"
                )

                if temp and hum:

                    print(
                        "[SAPME] Thermal Port 0 solicitado"
                    )

                    return {
                        "temperature_min": float(
                            temp["low"]
                        ),
                        "temperature_max": float(
                            temp["high"]
                        ),
                        "humidity_min": float(
                            hum["low"]
                        ),
                        "humidity_max": float(
                            hum["high"]
                        )
                    }

            #
            # Thermal Port 4
            #

            if test_name == "Thermal Port 4":

                thermal = sapme.get(
                    "THERMAL",
                    {}
                )

                temp = thermal.get(
                    "12C_TEMPERATURE_4"
                )

                if temp:

                    print(
                        "[SAPME] Thermal Port 4 solicitado"
                    )

                    return {
                        "temperature_min": float(
                            temp["low"]
                        ),
                        "temperature_max": float(
                            temp["high"]
                        ),
                        "humidity_min": 0,
                        "humidity_max": 100
                    }

            #
            # AB CPU TEMP
            #

            if test_name in [
                "AB CPU TEMP",
                "AB CPU Temp"
            ]:

                thermal = sapme.get(
                    "THERMAL",
                    {}
                )

                temp = thermal.get(
                    "CHECK AB CPU TEMPERATURE"
                )

                if temp:

                    print(
                        "[SAPME] AB CPU TEMP solicitado"
                    )

                    return {
                        "temperature_min": float(
                            temp["low"]
                        ),
                        "temperature_max": float(
                            temp["high"]
                        )
                    }

            #
            # PCIe Iperf Test
            #

            if test_name == "PCIe Iperf Test":

                pcie = sapme.get(
                    "PCIE",
                    {}
                )

                if pcie:

                    print(
                        "[SAPME] PCIe Iperf Test solicitado"
                    )

                    return {
                        "pcie_limits": pcie
                    }

            #
            # USB3_3 Iperf Test
            #

            if test_name == "USB3_3 Iperf Test":

                usb = sapme.get(
                    "USB3_3",
                    {}
                )

                if usb:

                    print(
                        "[SAPME] USB3_3 Iperf Test solicitado"
                    )

                    return {
                        "usb_limits": usb
                    }

            #
            # USB2 Iperf Test
            #

            if test_name == "USB2 Iperf Test":

                usb = sapme.get(
                    "USB2",
                    {}
                )

                if usb:

                    print(
                        "[SAPME] USB2 Iperf Test solicitado"
                    )

                    return {
                        "usb_limits": usb
                    }

            #
            # USB3_2 Iperf Test
            #

            if test_name == "USB3_2 Iperf Test":

                usb = sapme.get(
                    "USB3_2",
                    {}
                )

                if usb:

                    print(
                        "[SAPME] USB3_2 Iperf Test solicitado"
                    )

                    return {
                        "usb_limits": usb
                    }

            #
            # EMMC-8bit
            #

            if test_name == "EMMC-8bit":

                emmc = sapme.get(
                    "EMMC",
                    {}
                )

                bw = emmc.get(
                    "EMMC8BIT_BUS_WIDTH"
                )

                clk = emmc.get(
                    "EMMC8BIT_ACTUAL_CLOCK"
                )

                timing = emmc.get(
                    "EMMC8BIT_TIMING_SPEC"
                )

                if bw and clk and timing:

                    print(
                        "[SAPME] EMMC-8bit solicitado"
                    )

                    return {
                        "bus_width": str(
                            int(bw["low"])
                        ),
                        "clock": str(
                            int(clk["low"])
                        ),
                        "timing": str(
                            int(timing["low"])
                        )
                    }
            #
            # UART
            #
            if test_name == "UART":

                uart = sapme.get(
                    "UART",
                    {}
                )

                if uart:

                    print(
                        "[SAPME] UART solicitado"
                    )

                    return {
                        "expected_result": "PASS"
                    }
            #
            # SPI
            #
            if test_name == "SPI":

                spi = sapme.get(
                    "SPI",
                    {}
                )

                if spi:

                    print(
                        "[SAPME] SPI solicitado"
                    )

                    return {
                        "expected_result": "PASS"
                    }

            if test_name == "I2S":

                i2s = sapme.get(
                    "I2S",
                    {}
                )
            #
            # I2S
            #
            if test_name == "I2S":

                i2s = sapme.get(
                    "I2S",
                    {}
                )

                if i2s:

                    print(
                        "[SAPME] I2S solicitado"
                    )

                    return {
                        "score_min": 999,
                        "score_max": 1001,
                        "expected_result": "PASS"
                    }
            #
            # CSI
            #
            if test_name == "CSI":

                csi = sapme.get(
                    "CSI",
                    {}
                )

                if csi:

                    print(
                        "[SAPME] CSI solicitado"
                    )

                    return {
                        "expected_result": "PASS"
                    }
            #
            # GPIO
            #
            if test_name == "GPIO":

                gpio = sapme.get(
                    "GPIO",
                    {}
                )

                if gpio:

                    print(
                        "[SAPME] GPIO solicitado"
                    )

                    return gpio