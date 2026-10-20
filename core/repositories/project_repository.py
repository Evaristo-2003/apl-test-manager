#!/usr/bin/env python3

import json

from core.utils.resource_path import resource_path


class ProjectRepository:

    def __init__(
        self,
        config_path: str = "projects.json"
    ):

        self.config_path = resource_path(
            config_path
        )

        self._projects = {}

        self._load()

    def _load(self):

        if not self.config_path.exists():

            raise FileNotFoundError(
                f"No se encuentra: {self.config_path}"
            )

        with open(
            self.config_path,
            "r",
            encoding="utf-8"
        ) as file:

            self._projects = json.load(
                file
            )

    def get_project(
        self,
        part_number: str
    ) -> str:

        return self._projects.get(
            part_number,
            "UNKNOWN"
        )

    def reload(self):

        self._load()