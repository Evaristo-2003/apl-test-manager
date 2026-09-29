#!/usr/bin/env python3

from datetime import datetime

from core.services.sapme_client import SapMeClient
from core.services.sapme_parser import parse_parametrics

from core.state.app_state import app_state


class SapmeService:

    def __init__(self):

        self.client = SapMeClient()

    def count_tests(
        self,
        limits: dict
    ):

        total = 0

        for group_data in limits.values():

            if isinstance(group_data, dict):

                total += len(group_data)

        return total

    def load_sfc(
        self,
        sfc: str
    ):

        print(
            f"Loading SAPME for {sfc}"
        )

        #
        # Login SAPME
        #

        self.client.login()

        #
        # Descargar XML
        #

        xml_text = self.client.get_parametrics(
            sfc
        )

        #
        # Parsear XML
        #

        limits = parse_parametrics(
            xml_text
        )

        print(
            limits.keys()
        )

        #
        # Actualizar AppState
        #

        app_state.current_sfc = sfc

        app_state.sapme_ready = True

        app_state.sapme_limits = limits

        app_state.operation = "OP_FUNC_PCBA"

        app_state.tests_loaded = self.count_tests(
            limits
        )

        app_state.last_sync = datetime.now()

        return True