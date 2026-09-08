#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Adaptador para control FPGA (simplificado)"""

import logging
from typing import Optional, Dict
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class FPGAPacket:
    """Paquete de comunicación FPGA"""
    id: int = 0xA5
    sequence: int = 0
    command: int = 0
    length: int = 0
    payload: bytes = b''
    checksum: int = 0
    
    def build(self) -> bytes:
        packet = bytearray()
        packet.append(self.id)
        packet.append(self.sequence & 0xFF)
        packet.append(self.command & 0xFF)
        packet.append(len(self.payload))
        packet.extend(self.payload)
        
        checksum = 0
        for b in packet:
            checksum ^= b
        packet.append(checksum)
        self.checksum = checksum
        
        return bytes(packet)


class FPGACommand:
    """Constantes de comandos FPGA"""
    ENABLE = 0x01
    DISABLE = 0x02
    VIDEO_OUTPUT = 0x10
    VIDEO_VERIFY = 0x11
    PWM = 0x20
    OSC = 0x21
    CSI = 0x30
    HDMI = 0x31
    IP_MAC = 0x40
    I2C_BYPASS = 0x50


class FPGAAdapter:
    """Adaptador para FPGA (simplificado)"""
    
    def __init__(self, i2c_bus: int = 3, address: int = 0x62, 
                 simulate: bool = True):
        self.i2c_bus = i2c_bus
        self.address = address
        self.simulate = simulate
        self._sequence = 0
    
    def send_command(self, command: int, payload: bytes = b'',
                     timeout_ms: int = 1000) -> Dict:
        """Envía comando al FPGA (simulado)"""
        logger.debug(f"FPGA CMD: {command} payload: {payload.hex()}")
        
        return {
            'status': 'OK',
            'command': command,
            'payload': b'\x01',
            'sequence': 1
        }
    
    def enable(self) -> bool:
        return self.send_command(FPGACommand.ENABLE).get('status') == 'OK'
    
    def disable(self) -> bool:
        return self.send_command(FPGACommand.DISABLE).get('status') == 'OK'
    
    def set_pwm(self, duty_cycle: int) -> bool:
        if not 0 <= duty_cycle <= 255:
            raise ValueError(f"Duty cycle fuera de rango: {duty_cycle}")
        return self.send_command(FPGACommand.PWM, bytes([duty_cycle])).get('status') == 'OK'