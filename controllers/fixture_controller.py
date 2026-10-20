from core.adapters.serial_adapter import SerialAdapter


class FixtureController:

    def __init__(
        self,
        serial_service,
        log_callback
    ):
        self.serial_service = serial_service
        self.log = log_callback
        self.status_indicators = []
        self.connect_buttons = []
        self.status_widgets = []
        self.analysis_steps = []
        self.analysis_callback = None

    def register_indicator(
        self,
        indicator
    ):

        self.status_indicators.append(
            indicator
        )
    def register_status_widget(
        self,
        widget
    ):

        self.status_widgets.append(
            widget
        )
    def set_status(
        self,
        status
    ):

        for indicator in self.status_indicators:

            indicator.set_status(
                status
            )

        for widget in self.status_widgets:

            widget.set_fixture_status(
                status
            )
    def refresh_ports(self):
        ports = self.serial_service.get_ports()
        self.log(
            f"🔍 Puertos disponibles: {ports if ports else 'Ninguno'}"
        )

    def auto_connect_fixture(self):
        self.log("🔌 Conectando fixture...")
        self.set_status("CONNECTING")
        self.analysis_steps.clear()
        self.log("📡 Buscando CB...")
        cb_port = self.serial_service.find_cb()

        if not cb_port:
            self.set_status("FAILED")
            self.log("❌ CB no encontrado")
            return

        self.log(f"✅ CB encontrado en {cb_port}")
        self.analysis_steps.append(
            "CB_FOUND"
        )
        self.log("⚙️ Preparando CB...")
        if not self.serial_service.prepare_cb():
            self.set_status("FAILED")
            self.log("❌ Error preparando CB")
            return

        self.log("✅ CB preparado")
        self.analysis_steps.append(
            "CB_PREPARED"
        )
        self.log("⏳ Encendiendo AB...")


        if not self.serial_service.power_on_ab():

            self.set_status("FAILED")

            self.log(
                "❌ Error encendiendo AB"
            )

            return

        self.log("✅ Comando de encendido enviado")

        
        self.analysis_steps.append(
            "AB_POWER_ON"
        )

        ab_port = self.serial_service.find_ab(
            timeout=60
        )


 
        if not ab_port:
      

            self.analysis_steps.append(
                "AB_NOT_FOUND"
            )

            if self.analysis_callback:

                self.analysis_callback(
                    "AB_NOT_FOUND",
                    self.analysis_steps.copy()
                )

            self.set_status("FAILED")

            self.log("❌ AB no encontrado")

            return
      
        self.log(f"✅ AB encontrado en {ab_port}")
        self.analysis_steps.append(
            "AB_FOUND"
        )
        self.log("⚙️ Preparando AB...")
        if not self.serial_service.prepare_ab():
            self.set_status("FAILED")
            self.log("❌ Error preparando AB")
            return

        self.log("✅ AB preparado")
        self.analysis_steps.append(
            "AB_PREPARED"
        )
        self.set_status("READY")
        self.log("🎯 FIXTURE LISTO")

    def disconnect_fixture(self):
        self.log("🔌 Desconectando fixture...")
        self.set_status("DISCONNECTING")

        self.log("🧹 Borrando DID...")
        success, msg = self.serial_service.erase_did()
        self.log(msg)

        self.log("⏻ Apagando AB...")
        self.serial_service.power_off_ab()

        self.log("⏻ Apagando CB...")
        self.serial_service.power_off_cb()

        self.log("🔌 Desconectando puertos...")
        self.serial_service.disconnect_all()

        self.set_status("NOT CONNECTED")
        self.log("✅ Fixture desconectado")

    def register_connect_button(
        self,
        button
    ):
        self.connect_buttons.append(
            button
        )

    def set_connect_enabled(
        self,
        enabled
    ):

        for button in self.connect_buttons:

            button.setEnabled(
                enabled
            )