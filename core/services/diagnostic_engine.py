import re
 
 
class DiagnosticEngine:
    """
    Motor de reglas basado en el reporte oficial de Harman 
    (LGA Check AB Connection - Failure Analysis Report)
    """
 
    # Marcador de arranque exitoso (prompt de Linux)
    PROMPT_PATTERNS = [
        r"root@harman-si-intel-plk",
        r"root@.*:~#",
        r"login:",
    ]
 
    # Patrón de MRC exitoso: "MRC: [...] OK(0): 6GB"
    MRC_SUCCESS_PATTERN = r"MRC:.*OK\(\d+\):\s*\d+GB"
 
    # Patrones de falla crítica (prioridad máxima)
    CRITICAL_FAILURE_PATTERNS = [
        (r"KERNEL PANIC", "KERNEL_PANIC", "El kernel de Linux falló durante el arranque (Kernel Panic).", "Revisar el log completo para identificar el módulo o driver que causó el fallo."),
        (r"ACPI MEMORY OR I/O RESET_REG", "04", "Daño interno en el procesador Intel. Error de hardware o acceso a memoria Flash.", "Reemplazar el procesador Intel (IC10500)."),
        (r"MACHINE CHECK EXCEPTION", "04", "Daño interno en el procesador Intel. Error de hardware o acceso a memoria Flash.", "Reemplazar el procesador Intel (IC10500)."),
        (r"EXCEPTION\s*#\d+", "04", "Excepción de CPU detectada. El procesador Intel no puede continuar el arranque.", "Reemplazar el procesador Intel (IC10500)."),
        (r"NO/INCORRECT USB CONFIG FOUND", "USB_CONFIG_ERROR", "Falla de inicialización de hardware (USB/PCIe). El BIOS no pudo configurar los puertos USB.", "Revisar falso contacto en el socket LGA (pines USB/PCIe). Verificar el estado del chipset/HUB de la AB."),
    ]
 
    # Patrones de falla de SDRAM (solo si NO hay MRC OK)
    SDRAM_FAILURE_PATTERNS = [
        r"MRC.*(FAIL|FATAL|ABORT|HANG)",
        r"(FAIL|FATAL|ABORT).*MRC",
        r"MEMORY.*(FAIL|ERROR|ABORT)",
        r"SDRAM.*(FAIL|ERROR)",
        r"MRC.*EXCEPTION",
        r"NO MEMORY DETECTED",
        r"MEMORY INIT.*FAIL",
    ]
 
    @staticmethod
    def analyze_ab_log_only(log_text: str) -> dict:
        """
        FILTRO 1: Analiza SOLO el log. Si no encuentra nada, devuelve UNKNOWN.
        """
        log_upper = log_text.upper()
 
        # ============================================================
        # PRIORIDAD 1: Fallas críticas (Kernel Panic, Excepción, etc.)
        # Estas fallas anulan cualquier MRC OK o prompt.
        # ============================================================
        for pattern, mode, diagnosis, action in DiagnosticEngine.CRITICAL_FAILURE_PATTERNS:
            if re.search(pattern, log_upper):
                return {
                    "mode": mode,
                    "status": "FAIL",
                    "diagnosis": diagnosis,
                    "action": action
                }
 
        # ============================================================
        # PRIORIDAD 2: ¿El sistema llegó al prompt de Linux?
        # Si llegó, es un PASS sin importar los warnings.
        # ============================================================
        for pattern in DiagnosticEngine.PROMPT_PATTERNS:
            if re.search(pattern, log_text, re.IGNORECASE):
                return {
                    "mode": "NONE",
                    "status": "PASS",
                    "diagnosis": "Arranque de la AB exitoso. Sistema de memoria y alimentación OK.",
                    "action": "Ninguna."
                }
 
        # ============================================================
        # PRIORIDAD 3: ¿El MRC terminó con éxito?
        # (solo si no hay fallas críticas ni prompt)
        # ============================================================
        if re.search(DiagnosticEngine.MRC_SUCCESS_PATTERN, log_upper):
            return {
                "mode": "NONE",
                "status": "PASS",
                "diagnosis": "Inicialización de memoria (MRC) exitosa. El sistema no llegó al prompt pero la RAM está OK.",
                "action": "Revisar por qué el sistema no llegó al prompt de Linux."
            }
 
        # ============================================================
        # PRIORIDAD 4: Falla de SDRAM (solo si NO hay MRC OK)
        # ============================================================
        for pattern in DiagnosticEngine.SDRAM_FAILURE_PATTERNS:
            if re.search(pattern, log_upper):
                return {
                    "mode": "03",
                    "status": "FAIL",
                    "diagnosis": "Falla en el sistema SDRAM. El procesador no puede comunicarse con las memorias.",
                    "action": "Revisar corto en el procesador Intel (IC10500) o reemplazar memorias SDRAM (IC10651)."
                }
 
        # ============================================================
        # Si llegamos aquí, el log NO es concluyente.
        # ============================================================
        return {
            "mode": "UNKNOWN",
            "status": "UNKNOWN",
            "diagnosis": "El log no contiene información suficiente para diagnosticar la falla.",
            "action": "Requiere análisis con LEDs."
        }
 
    @staticmethod
    def analyze_with_leds(log_text: str, led_d62: str, led_d65: str) -> dict:
        """
        FILTRO 2: Se usa solo si el log no fue concluyente. Analiza los LEDs.
        """
        # Modo 04 por LEDs (Se apagaron por completo)
        if led_d62 == "LOW" and led_d65 == "LOW":
            return {
                "mode": "04",
                "status": "FAIL",
                "diagnosis": "Daño en el procesador Intel (D62 LOW, D65 LOW). El sistema se apagó después del DID.",
                "action": "Reemplazar el procesador Intel (IC10500)."
            }
 
        # Modo 01: Falla de PMIC (D62 High, D65 Low)
        if led_d62 == "HIGH" and led_d65 == "LOW":
            return {
                "mode": "01",
                "status": "FAIL",
                "diagnosis": "Falla de alimentación (PMIC). D62 HIGH, D65 LOW. La placa enciende pero no hay comunicación RH850.",
                "action": "Revisar voltajes (VDDQ, VCC). Reemplazar PMIC (IC10750)."
            }
 
        # Modo 02: Falla de Regulador (D62 High, D65 High)
        elif led_d62 == "HIGH" and led_d65 == "HIGH":
            return {
                "mode": "02",
                "status": "FAIL",
                "diagnosis": "Falla de comunicación con RH850. D62 HIGH, D65 HIGH.",
                "action": "Revisar Regulador (IC10851) y líneas de comunicación del procesador."
            }
 
        # Si el operador seleccionó cosas que no tienen sentido
        return {
            "mode": "UNKNOWN",
            "status": "UNKNOWN",
            "diagnosis": "No se pudo identificar el error con los datos actuales.",
            "action": "Requiere análisis manual."
        }
 