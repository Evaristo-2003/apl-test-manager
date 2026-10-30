from PySide6.QtGui import QIcon

from core.utils.resource_path import resource_path


def get_app_icon():

    return QIcon(
        str(
            resource_path(
                "assets/icon.ico"
            )
        )
    )