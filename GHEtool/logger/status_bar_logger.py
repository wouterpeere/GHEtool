"""
script for a status bar logger class
"""
from __future__ import annotations
from logging import Handler
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QStatusBar

from GHEtool.gui.color_definition import WARNING, WHITE

if TYPE_CHECKING:
    from logging import LogRecord

    from PySide6.QtWidgets import QWidget


class StatusBar(Handler):
    """
    Class to create a status bar logger. To display messages in the GUI Status Bar
    """
    level_2_color: dict[str, str] = {'DEBUG': f"{WHITE}", 'INFO': f"{WHITE}", 'ERROR': 'rgb(255,0,0)', 'CRITICAL': 'rgb(255,0,0)', 'WARNING': f"{WARNING}"}

    def __init__(self, parent: QWidget):
        """
        init status bar

        Parameters
        ----------
        parent: QtW.QWidget
            parent to create QStatusBar in
        """
        super().__init__()
        self.widget: QStatusBar = QStatusBar(parent)

    def emit(self, record: LogRecord) -> None:
        """
        display record in statusbar.

        Parameters
        ----------
        record: logging.LogRecord
            record to be displayed

        """
        message = self.format(record)
        self.widget.setStyleSheet(f'color: {self.level_2_color[record.levelname]};')
        self.widget.showMessage(message, 10_000)
