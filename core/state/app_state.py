#!/usr/bin/env python3

from datetime import datetime


class AppState:

    def __init__(self):

        self.current_sfc = None

        self.project = ""

        self.sapme_ready = False

        self.sapme_limits = {}

        self.operation = None

        self.tests_loaded = 0

        self.last_sync = None

    def reset(self):

        self.current_sfc = None

        self.project = ""

        self.sapme_ready = False

        self.sapme_limits = {}

        self.operation = None

        self.tests_loaded = 0

        self.last_sync = None


app_state = AppState()