#!/usr/bin/env python3
"""Adaptador para comunicación serial"""

import logging
import time

import serial
from serial.tools import list_ports

logger = logging.getLogger(__name__)


class SerialAdapter:
    """Adaptador para comunicación serial con AB/CB"""
    
    def __init__(self, baudrate: int = 115200, timeout: float = 1.0):
        self.baudrate = baudrate
        self.timeout = timeout
        self._serial = None
        self._port = None
    
    @staticmethod
    def get_available_ports() -> list:
        """Obtiene lista de puertos COM disponibles"""
        return [port.device for port in list_ports.comports()]
    
    def connect(self, port: str) -> bool:
        """Conecta a un puerto serial"""
        try:
            self._serial = serial.Serial(
                port,
                self.baudrate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            self._port = port
            logger.info(f"Conectado a {port}")
            return True
        except Exception as e:
            logger.error(f"Error conectando a {port}: {e}")
            return False
    
    def disconnect(self):
        """Desconecta el puerto serial"""
        if self._serial:
            self._serial.close()
            self._serial = None
            self._port = None
            logger.info("Desconectado")
    
    def is_connected(self) -> bool:
        """Verifica si está conectado"""
        return self._serial is not None and self._serial.is_open
    
    def send_command(self, command: str) -> bool:
        """Envía un comando al dispositivo"""
        if not self.is_connected():
            return False
        
        try:
            self._serial.write((command + "\r\n").encode("utf-8"))
            self._serial.flush()
            return True
        except Exception as e:
            logger.error(f"Error enviando comando: {e}")
            return False
    
    def read_data(self, timeout: float = None) -> str:
        """Lee datos del puerto serial"""
        if not self.is_connected():
            return ""
        
        timeout = timeout or self.timeout
        response = ""
        start_time = time.time()
        
        try:
            while self._serial.in_waiting or (time.time() - start_time) < timeout:
                if self._serial.in_waiting:
                    response += self._serial.readline().decode("utf-8", errors="ignore")
                time.sleep(0.01)
        except Exception as e:
            logger.error(f"Error leyendo datos: {e}")
        
        return response
    
    def execute_command(self, command: str, wait_time: float = 2.0) -> str:
        """Ejecuta comando y espera respuesta"""
        if not self.is_connected():
            return "NOT CONNECTED"
        
        try:
            self._serial.reset_input_buffer()
            self.send_command(command)
            time.sleep(wait_time)
            return self.read_data()
        except Exception as e:
            logger.error(f"Error ejecutando comando: {e}")
            return f"ERROR: {e}"
    
    def execute_command_until(self, command: str, end_marker: str, 
                              timeout: int = 60) -> str:
        """Ejecuta comando y espera hasta encontrar marcador"""
        if not self.is_connected():
            return "NOT CONNECTED"
        
        try:
            self._serial.reset_input_buffer()
            self.send_command(command)
            
            response = ""
            start_time = time.time()
            
            while (time.time() - start_time) < timeout:
                if self._serial.in_waiting:
                    response += self._serial.readline().decode("utf-8", errors="ignore")
                
                if end_marker in response:
                    # Esperar un poco más para capturar todo
                    time.sleep(0.5)
                    response += self.read_data()
                    break
                
                time.sleep(0.05)
            
            return response
        except Exception as e:
            logger.error(f"Error ejecutando comando: {e}")
            return f"ERROR: {e}"
    
    def identify_board(self) -> str:
        """Identifica si es AB o CB"""
        if not self.is_connected():
            return "NOT CONNECTED"
        
        try:
            self._serial.reset_input_buffer()
            self.send_command("hostname")
            time.sleep(2)
            response = self.read_data()
            
            if "dra7xx-evm" in response:
                return "CB"
            elif "harman-si-intel-plk" in response:
                return "AB"
            else:
                return response.strip()[:50]  # Primeros 50 caracteres
        except Exception as e:
            logger.error(f"Error identificando board: {e}")
            return f"ERROR: {e}"
    
    @property
    def port(self) -> str | None:
        return self._port