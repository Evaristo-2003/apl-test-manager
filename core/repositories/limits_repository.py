#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Repositorio para limits.json"""

import json
from typing import Dict, Any, Optional
from pathlib import Path
import logging

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
    
    def _get_default_limits(self) -> Dict:
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
    
    def get_limits(self, test_name: str) -> Optional[Dict[str, Any]]:
        """Obtiene los límites para una prueba específica"""
        return self._limits.get(test_name)
    
    def get_all(self) -> Dict[str, Any]:
        """Obtiene todos los límites"""
        return self._limits
    
    def has_limits(self, test_name: str) -> bool:
        """Verifica si existen límites para una prueba"""
        return test_name in self._limits
    
    def reload(self):
        """Recarga el archivo"""
        self._limits = {}
        self._load()