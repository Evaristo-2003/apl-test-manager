import re


class DiagnosticEngine:
    """
    Motor de reglas basado en el reporte oficial de Harman 
    (LGA Check AB Connection - Failure Analysis Report)
    """

    # Marcador de arranque exitoso (prompt de Linux)
    PROMPT_MARKER = "root@harman-si-intel-plk"

    # Patrón de MRC exitoso: "MRC: [...] OK(0): 6GB"
    MRC_SUCCESS_PATTERN = r"MRC:.*OK\(\d+\):\s*\d+GB"

    # Errores de drivers que son BENIGNOS (no indican falla de hardware)
    BENIGN_ERROR_PATTERNS = [
        r"\[drm:.*\] \*ERROR\*",           # Errores de DRM/i915
        r"Failed to fetch uC firmware",     # Firmware i915
        r"Requesting EDID firmware",         # EDID
        r"uvesafb: .* failed",              # Framebuffer
        r"kvm: disabled by bios",            # KVM
        r"snd_soc_.*: no .* found",         # Audio
        r"ASoC: no .* widget found",        # Audio
        r"ASoC: Failed to add route",       # Audio
        r"Error opening /dev/fb0",           # Framebuffer
        r"mmcblk1: error -110",             # MMC (puede ser benigno si arranca)
        r"Dev mmcblk1: unable to read",     # MMC (ídem)
        r"blk_update_request: I/O error",    # I/O (ídem)
        r"EXT[234]-fs.*error",               # FS (puede ser benigno si arranca)
        r"cp: .* No such file",              # Errores de initrd
        r"fsck: .* No such file",            # Errores de initrd
        r"mount: mount point .* does not exist",
        r"Error connecting to .* No route to host", # WSSC
        r"parameter error",                  # AB script
        r"umount: .* mountpoint not found",
        r"cat: .* No such file",             # Archivos faltantes
        r"rm: cannot remove",                # Archivos faltantes
        r"init_connection",                  # WSSC
        r"Re-init conn",                     # WSSC
    ]

    @staticmethod
    def _is_benign_error(line: str) -> bool:
        """Verifica si una línea de error es benigna (no indica falla de HW)."""
        for pattern in DiagnosticEngine.BENIGN_ERROR_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        return False

    @staticmethod
    def analyze_ab_log_only(log_text: str) -> dict:
        """
        FILTRO 1: Analiza SOLO el log. Si no encuentra nada, devuelve UNKNOWN.
        """
        log_upper = log_text.upper()

        # ============================================================
        # PRIMERO: ¿El sistema llegó al prompt de Linux?
        # Si llegó, es un PASS sin importar los warnings.
        # ============================================================
        if DiagnosticEngine.PROMPT_MARKER in log_text:
            return {
                "mode": "NONE",
                "status": "PASS",
                "diagnosis": "Arranque de la AB exitoso. Sistema de memoria y alimentación OK.",
                "action": "Ninguna."
            }

        # ============================================================
        # SEGUNDO: ¿El MRC terminó con éxito? (aunque no haya prompt)
        # Si el MRC dice "OK(0): 6GB", la memoria está bien.
        # ============================================================
        if re.search(DiagnosticEngine.MRC_SUCCESS_PATTERN, log_upper):
            return {
                "mode": "NONE",
                "status": "PASS",
                "diagnosis": "Inicialización de memoria (MRC) exitosa. El sistema no llegó al prompt pero la RAM está OK.",
                "action": "Revisar por qué el sistema no llegó al prompt de Linux."
            }

        # ============================================================
        # TERCERO: Filtrar errores benignos y buscar fallas reales
        # ============================================================
        # Separar las líneas del log y filtrar las benignas
        lines = log_text.splitlines()
        critical_lines = []
        for line in lines:
            if line.strip() and not DiagnosticEngine._is_benign_error(line):
                critical_lines.append(line)

        critical_log = "\n".join(critical_lines).upper()

        # 1. Modo 03: Falla en SDRAM (Error de MRC FATAL)
        mrc_fatal_patterns = [
            r"MRC.*(FAIL|FATAL|ABORT|HANG)",
            r"(FAIL|FATAL|ABORT).*MRC",
            r"MEMORY.*(FAIL|ERROR|ABORT)",
            r"SDRAM.*(FAIL|ERROR)",
            r"MRC.*EXCEPTION",
            r"NO MEMORY DETECTED",
            r"MEMORY INIT.*FAIL",
        ]
        for pattern in mrc_fatal_patterns:
            if re.search(pattern, critical_log):
                return {
                    "mode": "03",
                    "status": "FAIL",
                    "diagnosis": "Falla en el sistema SDRAM. El procesador no puede comunicarse con las memorias.",
                    "action": "Revisar corto en el procesador Intel (IC10500) o reemplazar memorias SDRAM (IC10651)."
                }

        # 2. Modo 04: Daño en el Procesador Intel (Kernel Panic)
        if "ACPI MEMORY OR I/O RESET_REG" in critical_log or "MACHINE CHECK EXCEPTION" in critical_log:
            return {
                "mode": "04",
                "status": "FAIL",
                "diagnosis": "Daño interno en el procesador Intel. Error de hardware o acceso a memoria Flash.",
                "action": "Reemplazar el procesador Intel (IC10500)."
            }

        # 3. Falla de Inicialización USB / BIOS Exception
        if "NO/INCORRECT USB CONFIG FOUND" in critical_log or re.search(r"EXCEPTION\s*#\d+", critical_log):
            exception_match = re.search(r"EXCEPTION\s*#(\d+)", critical_log)
            exc_num = exception_match.group(1) if exception_match else "?"

            return {
                "mode": "USB_CONFIG_ERROR",
                "status": "FAIL",
                "diagnosis": f"Falla de inicialización de hardware (USB/PCIe). El BIOS lanzó una excepción (EXCEPTION #{exc_num}).",
                "action": "Revisar falso contacto en el socket LGA (pines USB/PCIe). Verificar el estado del chipset/HUB de la AB."
            }

        # 4. Kernel Panic genérico
        if "KERNEL PANIC" in critical_log:
            return {
                "mode": "KERNEL_PANIC",
                "status": "FAIL",
                "diagnosis": "El kernel de Linux falló durante el arranque (Kernel Panic).",
                "action": "Revisar el log completo para identificar el módulo o driver que causó el fallo."
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