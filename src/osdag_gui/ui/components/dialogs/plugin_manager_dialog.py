from pathlib import Path
import sys, shutil, json
from dataclasses import dataclass
from PySide6.QtWidgets import (
    QApplication, 
    QDialog, 
    QVBoxLayout, 
    QPushButton, 
    QHBoxLayout, 
    QWidget, 
    QSizePolicy, 
    QLabel,
    QTextEdit,
    QScrollArea
)
from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtGui import QIcon


from osdag_gui.ui.components.dialogs.custom_titlebar import CustomTitleBar

@dataclass
class PluginMetaData:      # Metadata for each plugin
    name: str
    description: str = "No description available."
    author: str = "Unknown"
    version: str = "1.0"
    status: str = "Inactive" 

class PluginWidget(QWidget):
    def __init__(self, plugin: PluginMetaData):
        super().__init__()
        self.plugin = plugin
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Header: name + status + buttons
        header = QWidget()
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(0,0,0,0)
        h_layout.setSpacing(5)

        self.label = QLabel(f"{plugin.name} ({plugin.status})")
        h_layout.addWidget(self.label)

        self.btnActivate = QPushButton("Activate")
        self.btnDeactivate = QPushButton("Deactivate")
        self.btnRemove = QPushButton("Remove")
        for btn in (self.btnActivate, self.btnDeactivate, self.btnRemove):
            btn.setStyleSheet("""
                QPushButton { background-color: #90AF13; color: white; border: none; border-radius: 5px;
                               padding: 5px 15px; font-size: 10pt; font-weight: bold; }
                QPushButton:hover { background-color: #7A9611; }
                QPushButton:pressed { background-color: #6B850F; }
            """)
        h_layout.addWidget(self.btnActivate)
        h_layout.addWidget(self.btnDeactivate)
        h_layout.addWidget(self.btnRemove)
        layout.addWidget(header)

        # Content: plugin description
        self.content = QTextEdit()
        self.content.setReadOnly(True)
        self.content.setText(plugin.description)
        self.content.setFixedHeight(60)
        layout.addWidget(self.content)

        # Button callbacks
        self.btnActivate.clicked.connect(self.on_activate)
        self.btnDeactivate.clicked.connect(self.on_deactivate)
        self.btnRemove.clicked.connect(self.on_remove)

    def on_activate(self):
        self.plugin.status = "Active"
        self.label.setText(f"{self.plugin.name} ({self.plugin.status})")

    def on_deactivate(self):
        self.plugin.status = "Inactive"
        self.label.setText(f"{self.plugin.name} ({self.plugin.status})")

    def on_remove(self):
        self.setParent(None)
        self.deleteLater()


class PluginListModel(QAbstractListModel):
    def __init__(self, plugins=None):
        super().__init__()
        self._plugins = plugins or []

    def rowCount(self, parent=QModelIndex()):
        return len(self._plugins)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        plugin = self._plugins[index.row()]
        if role == Qt.DisplayRole:
            return plugin.name
        elif role == Qt.UserRole:
            return plugin
        return None

    def removePlugin(self, row):
        self.beginRemoveRows(QModelIndex(), row, row)
        del self._plugins[row]
        self.endRemoveRows()


class PluginManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("PluginManagerDialog")
        self.setWindowIcon(QIcon(":/images/osdag_logo.png"))
        self.setFixedSize(580, 450)


        # Layout and style
        self.setStyleSheet("""
            QDialog#PluginManagerDialog { background-color: #ffffff; border: 1px solid #90AF13; }
            QWidget#ContentWidget { background-color: #ffffff; }
            QTextBrowser { background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 4px;
                           font-family: 'Arial'; font-size: 8pt; padding: 8px; }
            QPushButton { background-color: #90AF13; color: white; border: none; border-radius: 5px;
                          padding: 5px 20px; font-size: 12px; font-weight: bold; }
            QPushButton:hover { background-color: #7A9611; }
            QPushButton:pressed { background-color: #6B850F; }
        """)

        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(1, 1, 1, 1)
        mainLayout.setSpacing(0)

        # Title bar
        self.titleBar = CustomTitleBar()
        self.titleBar.setTitle("Plugin Manager")
        mainLayout.addWidget(self.titleBar)

        # Content
        contentWidget = QWidget(self)
        contentWidget.setObjectName("ContentWidget")
        contentLayout = QVBoxLayout(contentWidget)
        contentLayout.setContentsMargins(10, 10, 10, 10)
        contentLayout.setSpacing(10)

        self.logoLabel = QSvgWidget(":/vectors/Osdag.svg", self)
        self.logoLabel.setFixedHeight(106)
        self.logoLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        contentLayout.addWidget(self.logoLabel, 0, Qt.AlignCenter)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        contentLayout.addWidget(scroll)

        self.pluginContainer = QWidget()
        self.pluginLayout = QVBoxLayout(self.pluginContainer)
        self.pluginLayout.setAlignment(Qt.AlignTop)
        scroll.setWidget(self.pluginContainer)

        # Add plugins
        plugins = [
            PluginMetaData("Calculator", "A simple calculator plugin"),
            PluginMetaData("Steel Designer", "Design steel joints with advanced features"),
            PluginMetaData("Purlin Designer")
        ]
        for plugin in plugins:
            pw = PluginWidget(plugin)
            pw.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self.pluginLayout.addWidget(pw)

        # OK button
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        self.okButton = QPushButton("OK", self)
        self.okButton.setFixedHeight(30)
        self.okButton.setStyleSheet("""
            QPushButton { background-color: #90AF13; color: white; border: none; border-radius: 5px;
                           padding: 5px 20px; font-size: 12px; font-weight: bold; }
            QPushButton:hover { background-color: #7A9611; }
            QPushButton:pressed { background-color: #6B850F; }
        """)
        self.okButton.clicked.connect(self.accept)
        buttonLayout.addWidget(self.okButton)

        contentLayout.addLayout(buttonLayout)
        mainLayout.addWidget(contentWidget)


# Test the dialog
if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = PluginManagerDialog()
    dialog.exec()
    sys.exit(app.exec())