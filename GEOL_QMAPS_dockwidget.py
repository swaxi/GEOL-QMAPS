# -*- coding: utf-8 -*-
"""
GEOL_QMAPSDockWidget — pure-Python replacement for the .ui-based dockwidget.
All widget names are preserved so GEOL_QMAPS.py requires no changes.
Each outer tab is wrapped in a QScrollArea so the panel works on small screens.
"""

import os

from qgis.PyQt import QtGui, QtWidgets
from qgis.PyQt.QtCore import pyqtSignal, Qt
from qgis.PyQt.QtWidgets import (
    QDockWidget, QWidget, QTabWidget, QScrollArea, QVBoxLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QGroupBox,
    QTableWidget, QTableWidgetItem, QRadioButton, QCheckBox,
    QPlainTextEdit, QFrame,
)
from qgis.PyQt.QtGui import QFont

# ---------------------------------------------------------------------------
# Shared style constants
# ---------------------------------------------------------------------------

_OUTER_TAB_SS = """
QTabWidget::tab-bar { alignment: left; }
QTabBar::tab {
    min-width: 195px; min-height: 23px;
    background-color: rgb(220,220,220,255);
    border-radius: 2px; border: 1px solid #000000;
    font-family: Arial; font-size: 13px;
}
QTabBar::tab:selected { background-color: rgb(190,190,190); }
QTabBar::tab:hover    { background-color: rgb(229,241,251); }
"""

_INNER_TAB_SS = """
QTabWidget::tab-bar { alignment: left; }
QTabBar::tab {
    min-width: 235px; min-height: 23px;
    background-color: rgb(220,220,220);
    border-radius: 2px; border: 1px solid #000000;
    font-weight: bold; font-size: 8pt;
    qproperty-alignment: 'AlignCenter';
    font-family: Arial;
}
QTabBar::tab:selected { background-color: rgb(190,190,190); }
QTabBar::tab:hover    { background-color: rgb(229,241,251); }
"""

_BTN = ("background-color: rgb(220,220,220);"
        "font-weight: bold; font-style: italic;"
        "font-family: Arial; font-size: 12px;")
_BTN_BROWSE = "background-color: rgb(220,220,220,255);"
_LE = ("QLineEdit {"
       "border-radius:0px;"
       "background-color: rgb(255,255,255,255);"
       "border-style: solid; border-width: 1px; border-color: black;}")
_LBL = "font-family: Arial; font-size: 12px;"
_CPR = "font-family: Arial; font-size: 11px; font-style: italic;"
_HELP_BTN = ("font-family: Arial; font-size: 12px; font-style: italic;"
             "background-color: rgb(220,220,220); font-weight: bold;")

_COPYRIGHT = "© 2025 West African Exploration Initiative. All Rights Reserved."

_ITALIC_FONT = QFont("Arial")
_ITALIC_FONT.setItalic(True)


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def _lbl(parent, text, x, y, w, h, style=_LBL, font=None, align=None, wrap=False):
    lbl = QLabel(text, parent)
    lbl.setGeometry(x, y, w, h)
    lbl.setStyleSheet(style)
    if font:
        lbl.setFont(font)
    if align is not None:
        lbl.setAlignment(align)
    if wrap:
        lbl.setWordWrap(True)
    return lbl


def _btn(parent, text, x, y, w, h, style=_BTN, tooltip=""):
    b = QPushButton(text, parent)
    b.setGeometry(x, y, w, h)
    b.setStyleSheet(style)
    if tooltip:
        b.setToolTip(tooltip)
    return b


def _le(parent, x, y, w, h, placeholder="", style=_LE):
    le = QLineEdit(parent)
    le.setGeometry(x, y, w, h)
    le.setStyleSheet(style)
    le.setPlaceholderText(placeholder)
    le.setFont(_ITALIC_FONT)
    return le


def _cb(parent, x, y, w, h, placeholder=""):
    cb = QComboBox(parent)
    cb.setGeometry(x, y, w, h)
    cb.setPlaceholderText(placeholder)
    cb.setFont(_ITALIC_FONT)
    return cb


def _gb(parent, title, x, y, w, h, ptsize=10):
    gb = QGroupBox(title, parent)
    gb.setGeometry(x, y, w, h)
    f = QFont("Arial", ptsize)
    f.setBold(True)
    gb.setFont(f)
    return gb


def _table(parent, x, y, w, h, rows, cols, headers):
    tw = QTableWidget(rows, cols, parent)
    tw.setGeometry(x, y, w, h)
    tw.setFont(QFont("Arial", 8))
    tw.setStyleSheet('font-family: Arial; font: 8pt "Arial";')
    tw.setShowGrid(True)
    tw.setWordWrap(True)
    hf = QFont("Arial")
    hf.setBold(True)
    hf.setItalic(True)
    for i, txt in enumerate(headers):
        item = QTableWidgetItem(txt)
        item.setFont(hf)
        tw.setHorizontalHeaderItem(i, item)
    tw.horizontalHeader().setDefaultSectionSize(182)
    tw.horizontalHeader().setMinimumSectionSize(29)
    tw.verticalHeader().setDefaultSectionSize(24)
    tw.verticalHeader().setMinimumSectionSize(19)
    return tw


def _scrollwrap(widget):
    """Wrap *widget* in a QScrollArea with a permanent vertical scrollbar."""
    sa = QScrollArea()
    sa.setWidget(widget)
    sa.setWidgetResizable(False)
    sa.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    sa.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
    return sa


# ---------------------------------------------------------------------------
# Main dock widget
# ---------------------------------------------------------------------------

class GEOL_QMAPSDockWidget(QDockWidget):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GEOL_QMAPS")
        self._build_ui()

    # ------------------------------------------------------------------
    # Top-level layout
    # ------------------------------------------------------------------

    def _build_ui(self):
        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(10, 0, 0, 0)

        self.tabWidget = QTabWidget()
        bold13 = QFont("Arial", 13)
        bold13.setBold(True)
        self.tabWidget.setFont(bold13)
        self.tabWidget.setStyleSheet(_OUTER_TAB_SS)
        self.tabWidget.setUsesScrollButtons(False)
        self.tabWidget.setMinimumSize(80, 500)

        self.tabWidget.addTab(_scrollwrap(self._tab_import()),    "Import Field Data")
        self.tabWidget.addTab(_scrollwrap(self._tab_fieldwork()), "Fieldwork Preparation")
        self.tabWidget.addTab(_scrollwrap(self._tab_data_mgmt()), "Data Management")
        self.tabWidget.addTab(_scrollwrap(self._tab_help()),      "Help - Roadmap")

        vbox.addWidget(self.tabWidget)
        self.setWidget(container)

    # ------------------------------------------------------------------
    # Tab 1 — Import Field Data
    # ------------------------------------------------------------------

    def _tab_import(self):
        W = QWidget()
        W.setFixedSize(780, 810)
        W.setObjectName("Import_data")
        W.setStyleSheet(
            "#Import_data {"
            "background-color: rgb(240,240,240,255);"
            "}"
        )

        f12b = QFont("Arial", 12)
        f12b.setBold(True)

        # Title row
        self.label_19 = _lbl(W, "Import Legacy Field Data Shapefiles (Point Geometry)",
                              10, 10, 521, 21, font=f12b)
        self.versions_label = _lbl(W, "version", 230, 10, 521, 20,
                                    style="font-family: Arial;",
                                    align=Qt.AlignRight | Qt.AlignVCenter)

        # --- Step 1 ---
        self.groupBox = _gb(W, "Step 1: Select the Shapefile to Import", 10, 40, 371, 61)
        self.lineEdit_13 = _le(self.groupBox, 10, 30, 311, 21,
                                "Lithology and structural datapoints supported only")
        self.pushButton_7 = _btn(self.groupBox, "...", 330, 30, 31, 21,
                                  _BTN_BROWSE, "Choose your Main Project")

        # --- Step 3 ---
        self.groupBox_3 = _gb(W, "Step 3: Generate Standardised Legacy Data (Scratch)",
                               400, 40, 371, 61)
        self.pushButton_14 = _btn(self.groupBox_3, "Generate QGIS Layers", 120, 30, 141, 21)

        # --- Step 4 ---
        self.groupBox_15 = _gb(W, "Step 4: Merge into Field Data Compilation Layers",
                                10, 110, 371, 131)
        _lbl(self.groupBox_15, "Add Standardised Data from Layer...:",
             10, 20, 101, 41, wrap=True,
             align=Qt.AlignRight | Qt.AlignVCenter)
        _lbl(self.groupBox_15, "... to Compiled Data Stored in...:",
             10, 60, 101, 41, wrap=True,
             align=Qt.AlignRight | Qt.AlignVCenter)
        self.comboBox_merge1_2 = _cb(self.groupBox_15, 120, 30, 241, 21,
                                      "Select the layer containing standardised data")
        self.comboBox_merge2_2 = _cb(self.groupBox_15, 120, 70, 241, 21,
                                      "Select the legacy data compilation layer")
        self.merge_layers_pushButton_2 = _btn(self.groupBox_15, "Merge Layers", 270, 100, 91, 21)

        # --- Import FieldMove ---
        self.groupBox_19 = _gb(W, "Import FieldMove Project", 400, 110, 371, 61, ptsize=12)
        self.lineEdit_FM_project_path = _le(self.groupBox_19, 10, 30, 221, 21,
                                             "Select a FieldMove project directory")
        self.pushButton_FM_project_select = _btn(self.groupBox_19, "...", 240, 30, 31, 21,
                                                  _BTN_BROWSE, "Choose your Main Project")

        # Step 2 header label
        f10b = QFont("Arial", 10)
        f10b.setBold(True)
        self.label_35 = _lbl(
            W,
            "Step 2: Verify Best-Match Assignement of Standard Values to Imported Legacy Field Data",
            30, 250, 691, 16, font=f10b, wrap=True)

        # Reset button
        self.pushButton_13 = _btn(W, "RESET THE WINDOW", 630, 200, 141, 21)

        # --- Inner tab widget (Step 2 sub-tabs) ---
        self.tabWidget_Step2_3 = QTabWidget(W)
        self.tabWidget_Step2_3.setGeometry(40, 280, 711, 491)
        self.tabWidget_Step2_3.setFont(QFont("Arial", 16))
        self.tabWidget_Step2_3.setStyleSheet(_INNER_TAB_SS)

        _hdrs = ["Legacy data value", "Assigned standard value", "Modify the assigned value"]

        # Sub-tab: Database Fields
        step2 = QWidget()
        step2.setStyleSheet("background-color: rgb(220,220,220);")
        self.tableWidget1 = _table(step2, 10, 10, 571, 341, 13, 3, _hdrs)
        self.legendbox_3 = _gb(step2, "Matching Score", 590, 10, 101, 341, ptsize=8)
        self.legendbox_3.setStyleSheet("font-family: Arial; font-size: 8pt;")
        self.pushButton_9  = _btn(step2, "Fields OK", 590, 360, 101, 21)
        self.pushButton_11 = _btn(step2, "Undo",      470, 360, 101, 21)
        self.label_33 = _lbl(step2, _COPYRIGHT, 10, 360, 311, 21, _CPR)
        self.tabWidget_Step2_3.addTab(step2, "Database Fields")

        # Sub-tab: Lithology Names
        step3 = QWidget()
        self.tableWidget2 = _table(step3, 10, 10, 571, 341, 13, 3, _hdrs)
        self.legendbox = _gb(step3, "Matching Score", 590, 10, 101, 341, ptsize=8)
        self.legendbox.setStyleSheet("font-family: Arial; font-size: 8pt;")
        self.pushButton_10 = _btn(step3, "Lithologies OK", 590, 360, 101, 21)
        self.pushButton_12 = _btn(step3, "Undo",           470, 360, 101, 21)
        self.label_38 = _lbl(step3, _COPYRIGHT, 10, 360, 311, 21, _CPR)
        self.tabWidget_Step2_3.addTab(step3, "Lithology Names")

        # Sub-tab: Structure Types
        step4 = QWidget()
        self.tableWidget3 = _table(step4, 10, 10, 571, 341, 13, 3, _hdrs)
        self.legendbox_2 = _gb(step4, "Matching Score", 590, 10, 101, 341, ptsize=8)
        self.legendbox_2.setStyleSheet("font-family: Arial; font-size: 8pt;")
        self.pushButton_25 = _btn(step4, "Undo",          470, 360, 101, 21)
        self.pushButton_26 = _btn(step4, "Structures OK", 590, 360, 101, 21)
        self.label_34 = _lbl(step4, _COPYRIGHT, 10, 360, 311, 21, _CPR)
        self.tabWidget_Step2_3.addTab(step4, "Structure Types")

        return W

    # ------------------------------------------------------------------
    # Tab 2 — Fieldwork Preparation
    # ------------------------------------------------------------------

    def _tab_fieldwork(self):
        W = QWidget()
        W.setFixedSize(780, 710)
        W.setObjectName("Fieldwork_preparation")
        W.setStyleSheet(
            "#Fieldwork_preparation {"
            "background-color: rgb(240,240,240,255);"
            "}"
        )

        # Update Project ID and Location
        self.groupBox_6 = _gb(W, "Update Project ID and Location", 10, 30, 761, 61, ptsize=12)
        _lbl(self.groupBox_6, "Project ID:", 10, 30, 61, 21,
             align=Qt.AlignRight | Qt.AlignVCenter)
        self.lineEdit_9 = _le(self.groupBox_6, 80, 30, 261, 21,
                               "Enter the mapping project ID")
        _lbl(self.groupBox_6, "Location:", 340, 30, 71, 21,
             align=Qt.AlignRight | Qt.AlignVCenter)
        self.lineEdit_10 = _le(self.groupBox_6, 420, 30, 261, 21,
                                "Type the mapping location")
        self.projName_pushButton = _btn(self.groupBox_6, "Update", 700, 30, 51, 21)

        # Set User by Default
        self.groupBox_18 = _gb(W, "Set User by Default", 10, 120, 761, 91, ptsize=12)
        _lbl(self.groupBox_18, "New or Existing User:", 10, 30, 121, 21)
        self.lineEdit_39 = _le(self.groupBox_18, 140, 30, 311, 20,
                                "Type the name of an existing or new user")
        self.pushButton_user_default = _btn(self.groupBox_18, "  Set User by Default ",
                                             620, 30, 131, 21)
        self.radioButton_Some = QRadioButton(" Change for One Layer:", self.groupBox_18)
        self.radioButton_Some.setGeometry(10, 60, 151, 21)
        self.radioButton_Some.setStyleSheet(_LBL)
        self.comboBox_layers_user = _cb(self.groupBox_18, 160, 60, 291, 21,
                                         "Select the layer to update")
        self.radioButton_All = QRadioButton(
            " Change for All Layers (1-2 min-long processing)", self.groupBox_18)
        self.radioButton_All.setGeometry(470, 60, 281, 21)
        self.radioButton_All.setChecked(True)
        self.radioButton_All.setStyleSheet(_LBL)

        # Edit Dictionaries
        self.groupBox_5 = _gb(W, "Edit Dictionaries", 10, 240, 761, 91, ptsize=12)
        _lbl(self.groupBox_5, "Dictionary: ", 10, 20, 81, 41)
        self.comboBox = _cb(self.groupBox_5, 70, 30, 431, 21,
                             "Select a dictionary to update")
        _lbl(self.groupBox_5, "Item to Add:", 10, 60, 71, 21)
        self.lineEdit_38 = _le(self.groupBox_5, 80, 60, 211, 21, "Type the item to add")
        self.csv_pushButton = _btn(self.groupBox_5, "Add Item", 300, 60, 61, 21)
        vline = QFrame(self.groupBox_5)
        vline.setGeometry(350, 60, 20, 21)
        vline.setFrameShape(QFrame.VLine)
        vline.setLineWidth(1)
        _lbl(self.groupBox_5, "Item to Delete:", 380, 60, 101, 21)
        self.comboBox_delete = _cb(self.groupBox_5, 470, 60, 201, 21,
                                    "Select the item to delete")
        self.csv_pushButton_2 = _btn(self.groupBox_5, "Delete Item", 680, 60, 71, 21)

        # Define Default Structural Measurement
        self.groupBox_20 = _gb(
            W, "Define Default Structural Measurement for Planar Structures",
            10, 360, 761, 61, ptsize=12)
        self.structure_style_on_pushButton = QRadioButton(
            "Dip/Dip Direction", self.groupBox_20)
        self.structure_style_on_pushButton.setGeometry(70, 20, 121, 41)
        self.structure_style_on_pushButton.setStyleSheet(_LBL)
        self.structure_style_off_pushButton = QRadioButton(
            "Strike (Right-Hand Rule)-Dip", self.groupBox_20)
        self.structure_style_off_pushButton.setGeometry(250, 20, 181, 41)
        self.structure_style_off_pushButton.setStyleSheet(_LBL)

        # Save Changes to Field Data Forms
        self.groupBox_17 = _gb(
            W, "Save Changes Made to the Field Data Forms", 10, 450, 761, 81, ptsize=12)
        self.label_36 = _lbl(
            self.groupBox_17,
            "Select a Folder to Save a QGIS Layer Definition File for Customised "
            "Field Data Layers and Dictionaries:",
            10, 21, 631, 31, wrap=True)
        self.lineEdit_18 = _le(
            self.groupBox_17, 10, 50, 591, 21,
            "***project-repository/99_COMMAND_FILES or any-other-folder***")
        self.pushButton_17 = _btn(self.groupBox_17, "...", 610, 50, 31, 21,
                                   _BTN_BROWSE, "Choose your Main Project")
        self.pushButton_save__project_template_style_2 = _btn(
            self.groupBox_17, "Save .qlr File", 660, 50, 91, 21)

        # Clip Field Data to Current Canvas
        self.groupBox_4 = _gb(
            W, "Clip Field Data to Current Canvas", 10, 560, 761, 91, ptsize=12)
        _lbl(self.groupBox_4, "Path to New Directory:", 10, 30, 121, 21,
             align=Qt.AlignRight | Qt.AlignVCenter)
        _lbl(self.groupBox_4, "Clipping Polygon (optional):", 10, 60, 161, 21)
        self.lineEdit_3 = _le(self.groupBox_4, 140, 30, 571, 21,
                               "Select a folder to store clipped field data")
        self.lineEdit_8 = _le(self.groupBox_4, 160, 60, 501, 21,
                               "Select a polygon shapefile to be used as a clipping mask")
        self.pushButton  = _btn(self.groupBox_4, "...", 720, 30, 31, 21, _BTN)
        self.pushButton_6 = _btn(self.groupBox_4, "...", 670, 60, 31, 21, _BTN)
        self.clip_pushButton = _btn(self.groupBox_4, "Clip", 720, 60, 31, 21, _BTN)

        # Bottom bar
        self.pushButton_19 = _btn(W, "RESET THE WINDOW", 620, 660, 141, 21)
        self.label_31 = _lbl(W, _COPYRIGHT, 10, 660, 311, 21, _CPR)

        return W

    # ------------------------------------------------------------------
    # Tab 3 — Data Management
    # ------------------------------------------------------------------

    def _tab_data_mgmt(self):
        W = QWidget()
        W.setFixedSize(780, 760)
        W.setObjectName("Data_management")
        W.setStyleSheet(
            "#Data_management {"
            "background-color: rgb(240,240,240,255);"
            "}"
        )

        # Update old project
        self.groupBox_22 = _gb(
            W,
            "Update an Old GEOL-QMAPS QGIS Project to the Latest Version "
            "(requires an Internet connection)",
            10, 20, 761, 61, ptsize=12)
        _lbl(self.groupBox_22,
             "Old Project Folder ( version must be >v3.1.0):",
             10, 30, 241, 21)
        self.lineEdit_15 = _le(self.groupBox_22, 260, 30, 331, 21,
                                "***old-project-folder***")
        self.pushButton_37 = _btn(self.groupBox_22, "...", 600, 30, 31, 21, _BTN_BROWSE)
        self.rejig_pushButton_4 = _btn(self.groupBox_22, "Update Version", 650, 30, 101, 21)

        # Sync QField to QGIS
        self.groupBox_23 = _gb(
            W, "Synchronise a QField Package to the QGIS Master Project",
            10, 110, 761, 61, ptsize=12)
        _lbl(self.groupBox_23, "QField Package:", 10, 30, 91, 21)
        self.lineEdit_QFieldPackage = _le(self.groupBox_23, 110, 30, 161, 21,
                                           "***QField-folder-or-.zip-archive***")
        self.pushButton_QFieldPackage = _btn(self.groupBox_23, "...", 280, 30, 31, 21,
                                              _BTN_BROWSE)
        self.label_QGISFolder = _lbl(
            self.groupBox_23, "QGIS Master Project Repository:",
            320, 30, 181, 21, wrap=True,
            align=Qt.AlignRight | Qt.AlignVCenter)
        self.lineEdit_QGISFolder = _le(self.groupBox_23, 510, 30, 131, 21,
                                        "***QGIS-project-folder***")
        self.pushButton_QGISFolder = _btn(self.groupBox_23, "...", 650, 30, 31, 21,
                                           _BTN_BROWSE)
        self.pushButton_SyncQFieldToQGIS = _btn(self.groupBox_23, "Sync", 700, 30, 51, 21)

        # Merge Projects
        self.groupBox_8 = _gb(W, "Merge Projects", 10, 200, 761, 91, ptsize=12)
        _lbl(self.groupBox_8, "Path to Main Project:", 10, 30, 121, 21)
        self.lineEdit_11 = _le(self.groupBox_8, 130, 30, 211, 21, "***main-project.qgz***")
        self.pushButton_29 = _btn(self.groupBox_8, "...", 350, 30, 31, 21, _BTN_BROWSE)
        _lbl(self.groupBox_8, "Path to Sub-Project:", 10, 50, 111, 31,
             align=Qt.AlignRight | Qt.AlignVCenter)
        self.lineEdit_26 = _le(self.groupBox_8, 130, 60, 211, 21, "***sub-project.qgz***")
        self.pushButton_20 = _btn(self.groupBox_8, "...", 350, 60, 31, 21, _BTN_BROWSE)
        _lbl(self.groupBox_8, "Path to New Directory:", 400, 30, 121, 21,
             align=Qt.AlignRight | Qt.AlignVCenter)
        self.lineEdit_37 = _le(self.groupBox_8, 530, 30, 181, 21,
                                "***merged-project-repository***")
        self.pushButton_27 = _btn(self.groupBox_8, "...", 720, 30, 31, 21, _BTN_BROWSE)
        self.merge_pushButton = _btn(self.groupBox_8, "Merge Projects", 650, 60, 101, 21)

        # Archive Current Field Data
        self.groupBox_21 = _gb(W, "Archive Current Field Data", 10, 320, 371, 61, ptsize=12)
        self.merge_current_existing_pushButton_3 = _btn(
            self.groupBox_21,
            "Merge Data in CURRENT MISSION to EXISTING FIELD DATA",
            10, 30, 351, 21)

        # Remove Duplicate UUIDs
        self.groupBox_9 = _gb(
            W, "Remove Duplicate UUIDs from Project", 400, 320, 371, 61, ptsize=12)
        fi = QFont("Arial")
        fi.setItalic(True)
        lbl25 = QLabel("Should be used after merging operations", self.groupBox_9)
        lbl25.setGeometry(10, 30, 211, 21)
        lbl25.setFont(fi)
        self.merge_pushButton_2 = _btn(self.groupBox_9, "Remove Duplicates", 240, 30, 121, 21)

        # Export Compilation Layers
        self.groupBox_10 = _gb(
            W, "Export Compilation Layers to Common Themes", 10, 410, 491, 91, ptsize=12)
        _lbl(self.groupBox_10, "Path to Export Directory:", 10, 30, 141, 21)
        self.lineEdit_7 = _le(self.groupBox_10, 150, 30, 291, 21,
                               "***compilation-field-data-layers-merged-by-theme-folder***")
        self.pushButton_5 = _btn(self.groupBox_10, "...", 450, 30, 31, 21, _BTN_BROWSE)
        self.export_pushButton = _btn(self.groupBox_10, "Export Layers", 390, 60, 91, 21)

        # Create Virtual Stops
        self.groupBox_11 = _gb(W, "Create Virtual Stops", 510, 410, 261, 91, ptsize=12)
        _lbl(self.groupBox_11, "Minimal Neighbour Distance (m) :", 10, 30, 181, 21)
        self.lineEdit_53 = _le(self.groupBox_11, 190, 30, 61, 21)
        self.lineEdit_53.setText("100")
        self.virtual_pushButton = _btn(self.groupBox_11, "Create Virtual Stops",
                                        120, 60, 131, 21)

        # Picture Management
        self.groupBox_16 = _gb(W, "Picture Management", 10, 530, 761, 141, ptsize=12)
        _lbl(self.groupBox_16,
             "Path to Field and Sample Photograph Directory:",
             10, 30, 341, 21)
        self.lineEdit_14 = _le(self.groupBox_16, 270, 30, 441, 21,
                                "Select the updated field and sample photograph folder")
        self.pushButton_15 = _btn(self.groupBox_16, "...", 720, 30, 31, 21,
                                   _BTN_BROWSE, "Choose your Main Project")
        self.option1_ckeckbox = QCheckBox(
            "Update the Filepath Information for Existing Photographs",
            self.groupBox_16)
        self.option1_ckeckbox.setGeometry(10, 50, 471, 31)
        self.option1_ckeckbox.setStyleSheet(_LBL)
        self.option2_ckeckbox = QCheckBox(
            "Set the New Path as a Default Value for Future Field and Sample "
            "Photograph Entry",
            self.groupBox_16)
        self.option2_ckeckbox.setGeometry(10, 70, 481, 31)
        self.option2_ckeckbox.setStyleSheet(_LBL)
        self.pushButton_update_source_photo = _btn(
            self.groupBox_16, "Update Repository", 630, 70, 121, 21)
        _lbl(self.groupBox_16,
             "Use Photograph EXIF Metadata to Retrieve Image Direction:",
             10, 110, 341, 21)
        self.pushButton_use_exif_azimuth = _btn(
            self.groupBox_16, "Update Image Direction from Metadata",
            340, 110, 231, 21)

        # Bottom bar
        self.pushButton_22 = _btn(W, "RESET THE WINDOW", 630, 710, 141, 21)
        self.label_32 = _lbl(W, _COPYRIGHT, 10, 710, 611, 21, _CPR)

        return W

    # ------------------------------------------------------------------
    # Tab 4 — Help / Roadmap
    # ------------------------------------------------------------------

    def _tab_help(self):
        W = QWidget()
        W.setFixedSize(780, 760)
        W.setObjectName("Help")
        W.setStyleSheet(
            "#Help {"
            "background-color: rgb(240,240,240,255);"
            "}"
        )
        fp = QFont("Arial", 8)

        def _pte(parent, x, y, w, h, text, obj_name=""):
            pt = QPlainTextEdit(parent)
            pt.setGeometry(x, y, w, h)
            pt.setFont(fp)
            pt.setReadOnly(True)
            pt.setFrameShape(QFrame.NoFrame)
            pt.setLineWidth(0)
            pt.setPlainText(text)
            if obj_name:
                pt.setObjectName(obj_name)
                pt.setStyleSheet(
                    f"#{obj_name}{{background-color: rgb(240,240,240,0);"
                    f'font: 8pt "Arial";}}'
                )
            return pt

        # Where to Download
        gb14 = _gb(W, "Where to Download the GEOL-QMAPS QGIS Mapping Template?",
                   10, 10, 761, 61, ptsize=12)
        self.pushButton_34 = _btn(gb14, "Zenodo Repository ", 320, 30, 121, 21, _HELP_BTN)

        # Need Help
        gb13 = _gb(W, "Need Some Help? Contact Us!", 10, 90, 381, 151, ptsize=12)
        self.plainTextEdit_8 = _pte(
            gb13, 10, 30, 741, 111,
            "M.W. Jessell*, J. Perret* and E. Bétend - Developers of the Plugin\n\n"
            "J. Perret* - Developer of the GEOL-QMAPS QGIS Mapping Template \n\n"
            "*Contact Us:\n\nOnline Documentation:",
            "plainTextEdit_8")
        self.pushButton_24 = _btn(gb13, "Send Email", 110,  80, 81, 21, _HELP_BTN)
        self.pushButton_21 = _btn(gb13, "User Guide", 130, 110, 81, 21, _HELP_BTN)

        # Feedback
        gb30 = _gb(W, "Please Provide Feedback", 400, 90, 371, 151, ptsize=12)
        self.plainTextEdit_9 = _pte(
            gb30, 10, 30, 351, 111,
            "If you have bugs to report, suggestions for improvements or new tools "
            "to add to this plugin, please submit them on the GitHub issues page, "
            "or contact us !",
            "plainTextEdit_9")
        self.pushButton_23 = _btn(gb30, "Bug Report",  60, 110,  91, 21, _HELP_BTN)
        self.pushButton_28 = _btn(gb30, "Send Email", 210, 110,  81, 21, _HELP_BTN)

        # Roadmap
        gb33 = _gb(W, "Roadmap for Future Development", 10, 260, 761, 61, ptsize=12)
        self.plainTextEdit_11 = _pte(
            gb33, 10, 30, 731, 31,
            "Please visit the Help - Roadmap section of the User Guide:",
            "plainTextEdit_11")
        self.pushButton_30 = _btn(gb33, "User Guide - Roadmap", 300, 30, 141, 21, _HELP_BTN)

        # WAXI
        gb31 = _gb(W, "Keen to Learn More About the West Africa Exploration Initiative?",
                   10, 340, 761, 121, ptsize=12)
        self.plainTextEdit_5 = _pte(
            gb31, 10, 30, 741, 81,
            "The AMIRA West African Exploration Initiative (WAXI) is a unique "
            "collaborative research and training program focusing on the tectonics "
            "and mineral potential of the West African Craton, involving research "
            "institutions, geological surveys, governements and actors of the "
            "mineral industry.\n\nFor more information, please consult: ",
            "plainTextEdit_5")
        self.pushButton_41 = _btn(gb31, "WAXI website",  260, 70, 121, 21, _HELP_BTN)
        self.pushButton_40 = _btn(gb31, "AMIRA website", 400, 70, 121, 21, _HELP_BTN)

        # Copyright
        self.label_37 = _lbl(W, _COPYRIGHT, 10, 710, 311, 21, _CPR)

        return W

    # ------------------------------------------------------------------

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()
