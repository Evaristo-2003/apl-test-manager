#!/usr/bin/env python3
from datetime import datetime
from core.state.app_state import app_state

class SapmeService:

    def __init__(self):
        pass


    def load_sfc(
        self,
        sfc: str
    ):

        app_state.current_sfc = sfc

        app_state.sapme_ready = True

        app_state.operation = "OP_FUNC_PCBA"

        app_state.sapme_limits = {}

        app_state.tests_loaded = 48

        app_state.last_sync = datetime.now()

        return True


        print(
            f"Loading SAPME for {sfc}"
        )

        #
        # Aquí después
        # irá tu código actual
        #

        app_state.current_sfc = sfc

        app_state.sapme_ready = True

        app_state.sapme_limits = {}

        app_state.tests_loaded = 0

        return True