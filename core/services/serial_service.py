#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Servicio de comunicación serial"""

import logging
import time

from core.adapters.serial_adapter import SerialAdapter

logger = logging.getLogger(__name__)


class SerialService:
    """Gestiona la comunicación serial con AB y CB"""

    def __init__(self):
        self.ab_adapter = SerialAdapter()
        self.cb_adapter = SerialAdapter()
        self._is_ready = False

    # ============================================================
    # CONEXIÓN DIRECTA
    # ============================================================

    def connect_cb(self, port: str) -> tuple[bool, str]:
        """Conecta a CB"""
        if not self.cb_adapter.connect(port):
            return False, f"Error conectando CB en {port}"

        board = self.cb_adapter.identify_board()
        if board != "CB":
            self.cb_adapter.disconnect()
            return False, f"Dispositivo no es CB (identificado como: {board})"

        return True, f"CB conectado en {port}"

    def connect_ab(self, port: str) -> tuple[bool, str]:
        """Conecta a AB"""
        if not self.ab_adapter.connect(port):
            return False, f"Error conectando AB en {port}"

        board = self.ab_adapter.identify_board()
        if board != "AB":
            self.ab_adapter.disconnect()
            return False, f"Dispositivo no es AB (identificado como: {board})"

        return True, f"AB conectado en {port}"

    # ============================================================
    # PREPARACIÓN
    # ============================================================

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

    # ============================================================
    # ENERGÍA
    # ============================================================

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

    # ============================================================
    # ERASE DID
    # ============================================================

    def erase_did(self, timeout: int = 30) -> tuple[bool, str]:
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

    # ============================================================
    # DESCONEXIÓN
    # ============================================================

    def disconnect_all(self):
        """Desconecta todos los dispositivos"""
        self.ab_adapter.disconnect()
        self.cb_adapter.disconnect()

    # ============================================================
    # PROPIEDADES
    # ============================================================

    @property
    def is_ready(self) -> bool:
        return self._is_ready

    def get_ports(self) -> list:
        """Obtiene TODOS los puertos disponibles (sin filtrar)"""
        return SerialAdapter.get_available_ports()

    def get_usb_serial_ports(self) -> list:
        """Obtiene solo puertos USB Serial (filtrados)"""
        return SerialAdapter.get_usb_serial_ports()

    # ============================================================
    # AUTO-DETECCIÓN
    # ============================================================

    def find_cb(self) -> str | None:
        """
        Busca CB automáticamente y CONECTA el adapter real.
        
        Itera sobre puertos USB Serial, prueba identificarlo como CB,
        y si lo encuentra, deja self.cb_adapter conectado a ese puerto.
        """
        ports = self.get_usb_serial_ports()

        print(f"[find_cb] Puertos USB Serial disponibles: {ports}")

        if not ports:
            print("[find_cb] ⚠️  No hay puertos USB Serial detectados")
            return None

        for port in ports:
            if (self.ab_adapter.is_connected()
                    and self.ab_adapter.port == port):
                continue

            if (self.cb_adapter.is_connected()
                    and self.cb_adapter.port == port):
                return port

            temp = SerialAdapter()

            try:
                if not temp.connect(port):
                    continue

                board = temp.identify_board()
                temp.disconnect()

                if board == "CB":
                    # ✅ CONECTAR EL ADAPTER REAL, no solo identificar
                    print(f"[find_cb] Identificado CB en {port}, conectando adapter...")
                    self.cb_adapter.connect(port)
                    print(f"[find_cb] ✅ CB encontrado en {port}")
                    return port

                print(f"[find_cb] {port} no es CB (detectado: {board})")

            except Exception as e:
                print(f"[find_cb] Skip {port}: {e}")
                try:
                    temp.disconnect()
                except Exception:
                    pass

        print("[find_cb] ❌ CB no encontrado")
        return None


    def find_ab(self, timeout: int = 60) -> str | None:
        """
        Busca AB automáticamente y CONECTA el adapter real.
        """
        start = time.time()

        while (time.time() - start) < timeout:

            ports = self.get_usb_serial_ports()

            if ports:
                print(f"[find_ab] Puertos USB Serial disponibles: {ports}")

            for port in ports:
                if (self.cb_adapter.is_connected()
                        and self.cb_adapter.port == port):
                    continue

                if (self.ab_adapter.is_connected()
                        and self.ab_adapter.port == port):
                    return port

                temp = SerialAdapter()

                try:
                    if not temp.connect(port):
                        continue

                    board = temp.identify_board()
                    temp.disconnect()

                    if board == "AB":
                        # ✅ CONECTAR EL ADAPTER REAL
                        print(f"[find_ab] Identificado AB en {port}, conectando adapter...")
                        self.ab_adapter.connect(port)
                        print(f"[find_ab] ✅ AB encontrado en {port}")
                        return port

                    print(f"[find_ab] {port} no es AB (detectado: {board})")

                except Exception as e:
                    print(f"[find_ab] Skip {port}: {e}")
                    try:
                        temp.disconnect()
                    except Exception:
                        pass

            time.sleep(2)

        print("[find_ab] ❌ AB no encontrado")
        return None

    # ============================================================
    # LOGS
    # ============================================================

    def get_fixture_raw_log(self):
        """Obtiene logs crudos de ambos adaptadores"""
        log = []
        log.extend(self.cb_adapter.get_raw_log())
        log.extend(self.ab_adapter.get_raw_log())
        return log