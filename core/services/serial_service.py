#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Servicio de comunicación serial"""

from typing import Optional, Dict, Tuple
from core.adapters.serial_adapter import SerialAdapter


class SerialService:
    """Gestiona la comunicación serial con AB y CB"""
    
    def __init__(self):
        self.ab_adapter = SerialAdapter()
        self.cb_adapter = SerialAdapter()
        self._is_ready = False
    
    def connect_cb(self, port: str) -> Tuple[bool, str]:
        """Conecta a CB"""
        if not self.cb_adapter.connect(port):
            return False, f"Error conectando CB en {port}"
        
        board = self.cb_adapter.identify_board()
        if board != "CB":
            self.cb_adapter.disconnect()
            return False, f"Dispositivo no es CB (identificado como: {board})"
        
        return True, f"CB conectado en {port}"
    
    def connect_ab(self, port: str) -> Tuple[bool, str]:
        """Conecta a AB"""
        if not self.ab_adapter.connect(port):
            return False, f"Error conectando AB en {port}"
        
        board = self.ab_adapter.identify_board()
        if board != "AB":
            self.ab_adapter.disconnect()
            return False, f"Dispositivo no es AB (identificado como: {board})"
        
        return True, f"AB conectado en {port}"
    
    def prepare_cb(self) -> bool:
        """Prepara CB para pruebas"""
        if not self.cb_adapter.is_connected():
            return False
        self.cb_adapter.execute_command("hotkey_wssc.sh 0")
        return True
    
    def prepare_ab(self) -> bool:
        """Prepara AB para pruebas"""
        if not self.ab_adapter.is_connected():
            return False
        self.ab_adapter.execute_command("hotkey_wssc.sh 0")
        return True
    
    def power_on_ab(self) -> bool:
        """Enciende AB"""
        if not self.cb_adapter.is_connected():
            return False
        self.cb_adapter.execute_command("pwr_on_intl.sh 1")
        return True
    
    def power_off_ab(self) -> bool:
        """Apaga AB"""
        if not self.ab_adapter.is_connected():
            return False
        self.ab_adapter.execute_command("websocket_test.sh powerswitch 0")
        return True
    
    def power_off_cb(self) -> bool:
        """Apaga CB"""
        if not self.cb_adapter.is_connected():
            return False
        self.cb_adapter.execute_command("websocket_test.sh powerswitch 0")
        return True
    
    def erase_did(self, timeout: int = 30) -> Tuple[bool, str]:
        """Borra DID de AB"""
        if not self.ab_adapter.is_connected():
            return False, "AB no conectado"
        
        response = self.ab_adapter.execute_command_until(
            "websocket_test.sh erasedid",
            "ERASE DID/PDR SUCCESS",
            timeout
        )
        
        if "ERASE DID/PDR SUCCESS" in response:
            return True, "DID borrado exitosamente"
        return False, f"Error borrando DID: {response[:200]}"
    
    def disconnect_all(self):
        """Desconecta todos los dispositivos"""
        self.ab_adapter.disconnect()
        self.cb_adapter.disconnect()
    
    @property
    def is_ready(self) -> bool:
        return self._is_ready
    
    def get_ports(self) -> list:
        """Obtiene puertos disponibles"""
        return SerialAdapter.get_available_ports()
    
    def find_ab(self, timeout: int = 60) -> Optional[str]:
        """Busca AB automáticamente"""
        import time
        start = time.time()
        while (time.time() - start) < timeout:
            ports = self.get_ports()
            for port in ports:
                if self.connect_ab(port)[0]:
                    return port
            time.sleep(2)
        return None
    
    def find_cb(self) -> Optional[str]:
        """Busca CB automáticamente"""
        ports = self.get_ports()
        for port in ports:
            ok, _ = self.connect_cb(port)
            if ok:
                return port
        return None