#!/usr/bin/env python3

from datetime import datetime

from core.services.sapme_client import SapMeClient
from core.services.sapme_parser import parse_parametrics
from core.repositories.project_repository import ProjectRepository
import re
from core.state.app_state import app_state


class SapmeService:

    def __init__(self):

        self.client = SapMeClient()

        self.project_repository = ProjectRepository()
    def reset(self):

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

        #
        # Crear cliente nuevo para cada carga
        #
        self.client = SapMeClient()

        print(
            f"Loading SAPME for {sfc}"
        )

        #
        # Login SAPME
        #
        self.client.login()

        #
        # Obtener Status (aquí viene ROUTING_REV)
        #
        status_xml = self.client.get_sfc_status(
            sfc
        )



        project = "UNKNOWN"

        routing_match = re.search(
            r'>([^<]*LGA[^<]*,\d+)<',
            status_xml
        )

        routing_rev = ""

        part_match = re.search(
            r'(\d{11}),\d{3}',
            status_xml
        )

        part_number = ""

        if part_match:

            part_number = part_match.group(1)
            if not part_number:

                print(
                    "ERROR: Part number not found"
                )

                return False
        print(
            f"PART NUMBER: {part_number}"
        )

        project = self.project_repository.get_project(
            part_number
        )

        if project == "UNKNOWN":

            print(
                "\n"
                + "=" * 80
            )

            print(
                f"ERROR: Unknown project for PN {part_number}"
            )

            print(
                "=" * 80
                + "\n"
            )

            app_state.sapme_ready = False

            return False

        print(
            f"PROJECT: {project}"
        )

        app_state.project = project

        xml_text = self.client.get_parametrics(
            sfc
        )


        #


        #
        # Descargar paramétricos
        #
        xml_text = self.client.get_parametrics(
            sfc
        )

        #
        # Parsear paramétricos
        #
        limits = parse_parametrics(
            xml_text
        )
        import json

        print("\n========== SAPME LIMITS ==========\n")

        print(
            json.dumps(
                limits,
                indent=4,
                default=str
            )
        )

        print("\n===============================\n")
##
        traceability = limits.get(
            "_TRACEABILITY",
            {}
        )

        app_state.material_rev = (
            traceability.get(
                "material_rev",
                ""
            )
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