class FixtureController:
    def __init__(self, serial_service, log_callback, status_indicator):
        self.serial_service = serial_service
        self.log = log_callback
        self.fixture_status = status_indicator

    def refresh_ports(self):
        ports = self.serial_service.get_ports()
        self.log(
            f"🔍 Puertos disponibles: {ports if ports else 'Ninguno'}"
        )

    def auto_connect_fixture(self):
        self.log("🔌 Conectando fixture...")
        self.fixture_status.set_status("CONNECTING")

        self.log("📡 Buscando CB...")
        cb_port = self.serial_service.find_cb()

        if not cb_port:
            self.fixture_status.set_status("FAILED")
            self.log("❌ CB no encontrado")
            return

        self.log(f"✅ CB encontrado en {cb_port}")

        self.log("⚙️ Preparando CB...")
        if not self.serial_service.prepare_cb():
            self.fixture_status.set_status("FAILED")
            self.log("❌ Error preparando CB")
            return

        self.log("✅ CB preparado")

        self.log("⏳ Encendiendo AB...")
        if not self.serial_service.power_on_ab():
            self.fixture_status.set_status("FAILED")
            self.log("❌ Error encendiendo AB")
            return

        self.log("✅ Comando de encendido enviado")

        self.log("📡 Buscando AB (esto puede tomar hasta 60s)...")
        ab_port = self.serial_service.find_ab(timeout=60)

        if not ab_port:
            self.fixture_status.set_status("FAILED")
            self.log("❌ AB no encontrado")
            return

        self.log(f"✅ AB encontrado en {ab_port}")

        self.log("⚙️ Preparando AB...")
        if not self.serial_service.prepare_ab():
            self.fixture_status.set_status("FAILED")
            self.log("❌ Error preparando AB")
            return

        self.log("✅ AB preparado")

        self.fixture_status.set_status("READY")
        self.log("🎯 FIXTURE LISTO")

    def disconnect_fixture(self):
        self.log("🔌 Desconectando fixture...")
        self.fixture_status.set_status("CONNECTING")

        self.log("🧹 Borrando DID...")
        success, msg = self.serial_service.erase_did()
        self.log(msg)

        self.log("⏻ Apagando AB...")
        self.serial_service.power_off_ab()

        self.log("⏻ Apagando CB...")
        self.serial_service.power_off_cb()

        self.log("🔌 Desconectando puertos...")
        self.serial_service.disconnect_all()

        self.fixture_status.set_status("NOT CONNECTED")
        self.log("✅ Fixture desconectado")