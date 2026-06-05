# -*- coding: utf-8 -*-
"""
GEOL_QMAPSDockWidget — pure-Python replacement for the .ui-based dockwidget.
All widget names are preserved so GEOL_QMAPS.py requires no changes.
Each outer tab is wrapped in a QScrollArea so the panel works on small screens.
"""

import os

from qgis.PyQt import QtGui, QtWidgets
from qgis.PyQt.QtCore import pyqtSignal, Qt, QCoreApplication, QSize
from qgis.PyQt.QtWidgets import (
    QDockWidget, QWidget, QTabWidget, QScrollArea, QVBoxLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QGroupBox,
    QTableWidget, QTableWidgetItem, QRadioButton, QCheckBox,
    QPlainTextEdit, QFrame, QTabBar,
)
from qgis.PyQt.QtGui import QFont


def _tr(text):
    return QCoreApplication.translate("GQMapsDock", text)


# ---------------------------------------------------------------------------
# Shared style constants
# ---------------------------------------------------------------------------

_OUTER_TAB_SS = """
QTabWidget::tab-bar { alignment: left; }
QTabBar::tab {
    min-height: 23px;
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

_TOOLTIP_SS = """
QToolTip {
    background-color: #ffffdc;
    color: black;
    border: 1px solid #767676;
    padding: 3px;
    font-family: Arial;
    font-size: 11px;
}
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

_PANEL_W = 760
_GROUP_W = 741

_ITALIC_FONT = QFont("Arial")
_ITALIC_FONT.setItalic(True)


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def _lbl(parent, text, x, y, w, h, style=None, font=None, align=None, wrap=False):
    lbl = QLabel(text, parent)
    lbl.setGeometry(x, y, w, h)

    if font:
        lbl.setFont(font)
    else:
        lbl.setStyleSheet(style or _LBL)

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
# Tab Panel Bars
# ---------------------------------------------------------------------------

class EqualWidthTabBar(QTabBar):
    """Tab bar with four tabs evenly distributed across the available width."""

    def tabSizeHint(self, index):
        size = super().tabSizeHint(index)

        count = max(1, self.count())

        parent = self.parentWidget()
        parent_width = parent.width() if parent is not None else 0

        available_width = max(self.width(), parent_width, 760)

        tab_width = available_width // count

        if index == count - 1:
            tab_width = available_width - tab_width * (count - 1)

        return QSize(tab_width, max(size.height(), 26))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateGeometry()

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
        self.tabWidget.setTabBar(EqualWidthTabBar())
        bold13 = QFont("Arial", 13)
        bold13.setBold(True)
        self.tabWidget.setFont(bold13)
        self.tabWidget.setStyleSheet(_OUTER_TAB_SS)
        self.tabWidget.setUsesScrollButtons(True)
        self.tabWidget.setMinimumSize(80, 500)

        self.tabWidget.addTab(_scrollwrap(self._tab_import()),    _tr("Import Field Data"))
        self.tabWidget.addTab(_scrollwrap(self._tab_fieldwork()), _tr("Fieldwork Preparation"))
        self.tabWidget.addTab(_scrollwrap(self._tab_data_mgmt()), _tr("Data Management"))
        self.tabWidget.addTab(_scrollwrap(self._tab_help()),      _tr("Help - Roadmap"))

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
        self.label_19 = _lbl(W, _tr("Import Legacy Field Data Shapefiles (Point Geometry)"),
                              10, 10, 700, 21, font=f12b)
        self.versions_label = _lbl(W, "version", 230, 10, 521, 20,
                                    style="font-family: Arial;",
                                    align=Qt.AlignRight | Qt.AlignVCenter)


        # --- Step 1 ---
        self.groupBox = _gb(W, _tr("Step 1: Select the Shapefile to Import"), 10, 40, 371, 61)
        self.lineEdit_13 = _le(self.groupBox, 10, 30, 311, 21,
                                _tr("Lithology and structural datapoints supported only"))
        self.pushButton_7 = _btn(self.groupBox, "...", 330, 30, 31, 21,
                                  _BTN_BROWSE, "Choose your Main Project")

        # --- Step 3 --- (Generate button widened: 141→210)
        self.groupBox_3 = _gb(W, _tr("Step 3: Generate Standardised Legacy Data (Scratch)"),
                               400, 40, 371, 61)
        self.pushButton_14 = _btn(self.groupBox_3, _tr("Generate QGIS Layers"), 90, 30, 210, 21)

        # --- Step 4 --- (labels above comboBoxes; Merge Layers button widened)
        self.groupBox_15 = _gb(W, _tr("Step 4: Merge into Field Data Compilation Layers"),
                                10, 110, 371, 160)
        _lbl(self.groupBox_15, _tr("Add Standardised Data from Layer...:"),
             10, 18, 351, 21)
        self.comboBox_merge1_2 = _cb(self.groupBox_15, 10, 40, 341, 21,
                                      _tr("Select the layer containing standardised data"))
        _lbl(self.groupBox_15, _tr("... to Compiled Data Stored in...:"),
             10, 65, 351, 21)
        self.comboBox_merge2_2 = _cb(self.groupBox_15, 10, 87, 341, 21,
                                      _tr("Select the legacy data compilation layer"))
        self.merge_layers_pushButton_2 = _btn(self.groupBox_15, _tr("Merge Layers"), 180, 113, 181, 21)

        # --- Import FieldMove ---
        self.groupBox_19 = _gb(W, _tr("Import FieldMove Project"), 400, 110, 371, 61, ptsize=12)
        self.lineEdit_FM_project_path = _le(self.groupBox_19, 10, 30, 221, 21,
                                             _tr("Select a FieldMove project directory"))
        self.pushButton_FM_project_select = _btn(self.groupBox_19, "...", 240, 30, 31, 21,
                                                  _BTN_BROWSE, "Choose your Main Project")

        # Step 2 header label
        f10b = QFont("Arial", 10)
        f10b.setBold(True)
        self.label_35 = _lbl(
            W,
            _tr("Step 2: Verify Best-Match Assignement of Standard Values to Imported Legacy Field Data"),
            30, 279, 691, 32, font=f10b, wrap=True)

        # Reset button widened: 141→215, moved left
        self.pushButton_13 = _btn(W, _tr("RESET THE WINDOW"), 565, 200, 215, 21)

        # --- Inner tab widget (Step 2 sub-tabs) ---
        self.tabWidget_Step2_3 = QTabWidget(W)
        self.tabWidget_Step2_3.setGeometry(40, 315, 711, 462)
        self.tabWidget_Step2_3.setFont(QFont("Arial", 16))
        self.tabWidget_Step2_3.setStyleSheet(_INNER_TAB_SS)

        _hdrs = [_tr("Legacy data value"), _tr("Assigned standard value"), _tr("Modify the assigned value")]

        # Sub-tab: Database Fields
        step2 = QWidget()
        step2.setStyleSheet("background-color: rgb(220,220,220);")
        self.tableWidget1 = _table(step2, 10, 10, 571, 341, 13, 3, _hdrs)
        self.legendbox_3 = _gb(step2, _tr("Matching Score"), 590, 10, 101, 341, ptsize=8)
        self.legendbox_3.setStyleSheet("font-family: Arial; font-size: 8pt;")
        self.pushButton_9  = _btn(step2, _tr("Fields OK"), 590, 360, 101, 21)
        self.pushButton_11 = _btn(step2, _tr("Undo"),      470, 360, 101, 21)
        self.label_33 = _lbl(step2, _COPYRIGHT, 10, 360, 311, 21, _CPR)
        self.tabWidget_Step2_3.addTab(step2, _tr("Database Fields"))

        # Sub-tab: Lithology Names
        step3 = QWidget()
        self.tableWidget2 = _table(step3, 10, 10, 571, 341, 13, 3, _hdrs)
        self.legendbox = _gb(step3, _tr("Matching Score"), 590, 10, 101, 341, ptsize=8)
        self.legendbox.setStyleSheet("font-family: Arial; font-size: 8pt;")
        self.pushButton_10 = _btn(step3, _tr("Lithologies OK"), 590, 360, 101, 21)
        self.pushButton_12 = _btn(step3, _tr("Undo"),           470, 360, 101, 21)
        self.label_38 = _lbl(step3, _COPYRIGHT, 10, 360, 311, 21, _CPR)
        self.tabWidget_Step2_3.addTab(step3, _tr("Lithology Names"))

        # Sub-tab: Structure Types
        step4 = QWidget()
        self.tableWidget3 = _table(step4, 10, 10, 571, 341, 13, 3, _hdrs)
        self.legendbox_2 = _gb(step4, _tr("Matching Score"), 590, 10, 101, 341, ptsize=8)
        self.legendbox_2.setStyleSheet("font-family: Arial; font-size: 8pt;")
        self.pushButton_25 = _btn(step4, _tr("Undo"),          470, 360, 101, 21)
        self.pushButton_26 = _btn(step4, _tr("Structures OK"), 590, 360, 101, 21)
        self.label_34 = _lbl(step4, _COPYRIGHT, 10, 360, 311, 21, _CPR)
        self.tabWidget_Step2_3.addTab(step4, _tr("Structure Types"))

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
        # lineEdit_10 shrunk 261→201 to make room; Update button widened 51→120
        self.groupBox_6 = _gb(W, _tr("Update Project ID and Location"), 10, 30, 761, 61, ptsize=12)
        _lbl(self.groupBox_6, _tr("Project ID:"), 10, 30, 120, 21,
             align=Qt.AlignRight | Qt.AlignVCenter)
        self.lineEdit_9 = _le(self.groupBox_6, 135, 30, 175, 21,
                               _tr("Enter the mapping project ID"))
        _lbl(self.groupBox_6, _tr("Location:"), 320, 30, 120, 21,
             align=Qt.AlignRight | Qt.AlignVCenter)
        self.lineEdit_10 = _le(self.groupBox_6, 445, 30, 176, 21,
                                _tr("Type the mapping location"))
        self.projName_pushButton = _btn(self.groupBox_6, _tr("Update"), 631, 30, 120, 21)

        # Set User by Default
        # "Set User by Default" button widened 131→280, moved left
        self.groupBox_18 = _gb(W, _tr("Set User by Default"), 10, 120, 761, 91, ptsize=12)
        _lbl(self.groupBox_18, _tr("New or Existing User:"), 10, 30, 260, 21)
        self.lineEdit_39 = _le(self.groupBox_18, 275, 30, 186, 20,
                                _tr("Type the name of an existing or new user"))
        self.pushButton_user_default = _btn(self.groupBox_18, _tr("  Set User by Default "),
                                             471, 30, 280, 21)
        self.radioButton_Some = QRadioButton(_tr(" Change for One Layer:"), self.groupBox_18)
        self.radioButton_Some.setGeometry(10, 60, 151, 21)
        self.radioButton_Some.setStyleSheet(_LBL)
        self.comboBox_layers_user = _cb(self.groupBox_18, 160, 60, 291, 21,
                                         _tr("Select the layer to update"))
        self.radioButton_All = QRadioButton(
            _tr(" Change for All Layers (1-2 min-long processing)"), self.groupBox_18)
        self.radioButton_All.setGeometry(470, 60, 281, 21)
        self.radioButton_All.setChecked(True)
        self.radioButton_All.setStyleSheet(_LBL)

        # Edit Dictionaries — dropdown and labels shifted down to avoid overlap with the group-box title
        self.groupBox_5 = _gb(W, _tr("Edit Dictionaries"), 10, 240, 761, 110, ptsize=12)

        _lbl(self.groupBox_5, _tr("Dictionary: "), 10, 28, 120, 21)

        self.comboBox = _cb(
            self.groupBox_5,
            125, 28, 376, 21,
            _tr("Select a dictionary to update")
        )

        _lbl(self.groupBox_5, _tr("Item to Add:"), 10, 55, 175, 21)
        _lbl(self.groupBox_5, _tr("Item to Delete:"), 395, 55, 185, 21)

        self.lineEdit_38 = _le(
            self.groupBox_5,
            10, 77, 115, 21,
            _tr("Type the item to add")
        )

        self.csv_pushButton = _btn(
            self.groupBox_5,
            _tr("Add Item"),
            130, 77, 150, 21
        )

        vline = QFrame(self.groupBox_5)
        vline.setGeometry(385, 55, 1, 43)
        vline.setFrameShape(QFrame.VLine)
        vline.setLineWidth(1)

        self.comboBox_delete = _cb(
            self.groupBox_5,
            395, 77, 105, 21,
            _tr("Select the item to delete")
        )

        self.csv_pushButton_2 = _btn(
            self.groupBox_5,
            _tr("Delete Item"),
            505, 77, 150, 21
        )

        # Define Default Structural Measurement
        # Dip button widened 121→225; Strike button widened 181→480
        self.groupBox_20 = _gb(
            W, _tr("Define Default Structural Measurement for Planar Structures"),
            10, 369, 761, 61, ptsize=12)
        self.structure_style_on_pushButton = QRadioButton(
            _tr("Dip/Dip Direction"), self.groupBox_20)
        self.structure_style_on_pushButton.setGeometry(10, 20, 225, 41)
        self.structure_style_on_pushButton.setStyleSheet(_LBL)
        self.structure_style_off_pushButton = QRadioButton(
            _tr("Strike (Right-Hand Rule)/Dip"), self.groupBox_20)
        self.structure_style_off_pushButton.setGeometry(250, 20, 480, 41)
        self.structure_style_off_pushButton.setStyleSheet(_LBL)

        # Save Changes to Field Data Forms
        # lineEdit_18 shrunk 591→470; browse moved; Save .qlr widened 91→220
        self.groupBox_17 = _gb(
            W, _tr("Save Changes Made to the Field Data Forms"), 10, 459, 761, 81, ptsize=12)
        self.label_36 = _lbl(
            self.groupBox_17,
            _tr("Select a Folder to Save a QGIS Layer Definition File for Customised "
                "Field Data Layers and Dictionaries:"),
            10, 21, 631, 31, wrap=True)
        self.lineEdit_18 = _le(
            self.groupBox_17, 10, 50, 470, 21,
            "***project-repository/99_COMMAND_FILES or any-other-folder***")
        self.pushButton_17 = _btn(self.groupBox_17, "...", 490, 50, 31, 21,
                                   _BTN_BROWSE, "Choose your Main Project")
        self.pushButton_save__project_template_style_2 = _btn(
            self.groupBox_17, _tr("Save .qlr File"), 531, 50, 220, 21)

        # Clip Field Data to Current Canvas
        # lineEdit_8 shrunk 501→411; browse moved; Clip widened 31→120
        self.groupBox_4 = _gb(
            W, _tr("Clip Field Data to Current Canvas"), 10, 569, 761, 91, ptsize=12)
        _lbl(self.groupBox_4, _tr("Path to New Directory:"), 10, 27, 121, 27,
             wrap=True, align=Qt.AlignRight | Qt.AlignVCenter)
        _lbl(self.groupBox_4, _tr("Clipping Polygon (optional):"), 10, 57, 161, 27, wrap=True)
        self.lineEdit_3 = _le(self.groupBox_4, 140, 30, 571, 21,
                               _tr("Select a folder to store clipped field data"))
        self.lineEdit_8 = _le(self.groupBox_4, 160, 60, 411, 21,
                               _tr("Select a polygon shapefile to be used as a clipping mask"))
        self.pushButton  = _btn(self.groupBox_4, "...", 720, 30, 31, 21, _BTN_BROWSE)
        self.pushButton_6 = _btn(self.groupBox_4, "...", 581, 60, 31, 21, _BTN_BROWSE)
        self.clip_pushButton = _btn(self.groupBox_4, _tr("Clip"), 622, 60, 120, 21, _BTN)

        # Bottom bar — RESET widened 141→215, moved left
        self.pushButton_19 = _btn(W, _tr("RESET THE WINDOW"), 565, 669, 215, 21)
        self.label_31 = _lbl(W, _COPYRIGHT, 10, 669, 311, 21, _CPR)

        return W

    # ------------------------------------------------------------------
    # Tab 3 — Data Management
    # ------------------------------------------------------------------

    def _tab_data_mgmt(self):
        W = QWidget()
        W.setFixedSize(780, 840)   # height increased from 760 to 840
        W.setObjectName("Data_management")
        W.setStyleSheet(
            "#Data_management {"
            "background-color: rgb(240,240,240,255);"
            "}"
        )

        # Update old project
        # lineEdit_15 shrunk 331→281; Update Version widened 101→200
        self.groupBox_22 = _gb(
            W,
            _tr("Update an Old GEOL-QMAPS QGIS Project to the Latest Version "
                "(requires an Internet connection)"),
            10, 20, 761, 80, ptsize=12
        )

        _lbl(self.groupBox_22, _tr("Old Project Folder (version must be >v3.1.0):"),
             10, 25, 741, 21)

        self.lineEdit_15 = _le(self.groupBox_22, 10, 50, 450, 21, "***old-project-folder***")
        self.pushButton_37 = _btn(self.groupBox_22, "...", 470, 50, 31, 21, _BTN_BROWSE)
        self.rejig_pushButton_4 = _btn(self.groupBox_22, _tr("Update Version"), 511, 50, 200, 21)

        # Sync QField to QGIS
        # lineEdit_QGISFolder shrunk 131→111; Sync widened 51→120
        self.groupBox_23 = _gb(
            W, _tr("Synchronise a QField Package to the QGIS Master Project"),
            10, 120, 761, 61, ptsize=12)
        _lbl(self.groupBox_23, _tr("QField Package:"), 10, 30, 110, 21)
        self.lineEdit_QFieldPackage = _le(self.groupBox_23, 120, 30, 151, 21,
                                           "***QField-folder-or-.zip-archive***")
        self.pushButton_QFieldPackage = _btn(self.groupBox_23, "...", 280, 30, 31, 21,
                                              _BTN_BROWSE)
        self.label_QGISFolder = _lbl(
            self.groupBox_23, _tr("QGIS Master Project Repository:"),
            320, 30, 181, 21, wrap=True,
            align=Qt.AlignRight | Qt.AlignVCenter)
        self.lineEdit_QGISFolder = _le(self.groupBox_23, 510, 30, 71, 21,
                                        "***QGIS-project-folder***")
        self.pushButton_QGISFolder = _btn(self.groupBox_23, "...", 591, 30, 31, 21,
                                           _BTN_BROWSE)
        self.pushButton_SyncQFieldToQGIS = _btn(self.groupBox_23, _tr("Sync"), 631, 30, 120, 21)

        # Merge Projects
        # merge_pushButton widened 101→180, moved left
        self.groupBox_8 = _gb(W, _tr("Merge Projects"), 10, 210, 761, 91, ptsize=12)
        _lbl(self.groupBox_8, _tr("Path to Main Project:"), 10, 27, 121, 31, wrap=True)
        self.lineEdit_11 = _le(self.groupBox_8, 130, 30, 211, 21, "***main-project.qgz***")
        self.pushButton_29 = _btn(self.groupBox_8, "...", 350, 30, 31, 21, _BTN_BROWSE)
        _lbl(self.groupBox_8, _tr("Path to Sub-Project:"), 10, 55, 111, 31,
             wrap=True, align=Qt.AlignRight | Qt.AlignVCenter)
        self.lineEdit_26 = _le(self.groupBox_8, 130, 60, 211, 21, "***sub-project.qgz***")
        self.pushButton_20 = _btn(self.groupBox_8, "...", 350, 60, 31, 21, _BTN_BROWSE)
        _lbl(self.groupBox_8, _tr("Path to New Directory:"), 395, 27, 126, 31,
             wrap=True, align=Qt.AlignRight | Qt.AlignVCenter)
        self.lineEdit_37 = _le(self.groupBox_8, 530, 30, 181, 21,
                                "***merged-project-repository***")
        self.pushButton_27 = _btn(self.groupBox_8, "...", 720, 30, 31, 21, _BTN_BROWSE)
        self.merge_pushButton = _btn(self.groupBox_8, _tr("Merge Projects"), 571, 60, 180, 21)

        # Archive Current Field Data — expanded to full width (was w=371)
        self.groupBox_21 = _gb(W, _tr("Archive Current Field Data"), 10, 320, 761, 61, ptsize=12)
        self.merge_current_existing_pushButton_3 = _btn(
            self.groupBox_21,
            _tr("Merge Data in CURRENT MISSION to EXISTING FIELD DATA"),
            10, 30, 741, 21)

        # Remove Duplicate UUIDs — moved to its own row (y=400), full width
        self.groupBox_9 = _gb(
            W, _tr("Remove Duplicate UUIDs from Project"), 10, 400, 761, 61, ptsize=12)
        fi = QFont("Arial")
        fi.setItalic(True)
        lbl25 = QLabel(_tr("Should be used after merging operations"), self.groupBox_9)
        lbl25.setGeometry(10, 30, 350, 21)
        lbl25.setFont(fi)
        self.merge_pushButton_2 = _btn(self.groupBox_9, _tr("Remove Duplicates"), 560, 30, 185, 21)

        # Export Compilation Layers (y shifted +80; groupBox slightly narrower)
        self.groupBox_10 = _gb(
            W, _tr("Export Compilation Layers to Common Themes"), 10, 490, 480, 91, ptsize=12)
        _lbl(self.groupBox_10, _tr("Path to Export Directory:"), 10, 27, 141, 27, wrap=True)
        self.lineEdit_7 = _le(self.groupBox_10, 150, 30, 270, 21,
                               "***compilation-field-data-layers-merged-by-theme-folder***")
        self.pushButton_5 = _btn(self.groupBox_10, "...", 430, 30, 31, 21, _BTN_BROWSE)
        self.export_pushButton = _btn(self.groupBox_10, _tr("Export Layers"), 300, 60, 170, 21)

        # Create Virtual Stops — label above lineEdit on row 1; button on row 2
        self.groupBox_11 = _gb(
            W,
            _tr("Create Virtual Stops"),
            500, 490, 270, 100,
            ptsize=12
        )
        _lbl(
            self.groupBox_11,
            _tr("Minimal Neighbour Distance (m):"),
            10, 25, 250, 21
        )
        self.lineEdit_53 = _le(
            self.groupBox_11,
            10, 50, 61, 21,
            "100"
        )
        self.virtual_pushButton = _btn(
            self.groupBox_11,
            _tr("Create Virtual Stops"),
            10, 73, 250, 21
        )

        # Picture Management — "Path to..." label on own row above lineEdit
        self.groupBox_16 = _gb(
            W,
            _tr("Picture Management"),
            10, 610, 761, 150,
            ptsize=12
        )

        _lbl(
            self.groupBox_16,
            _tr("Path to Field and Sample Photograph Directory:"),
            10, 25, 741, 21
        )

        self.lineEdit_14 = _le(
            self.groupBox_16,
            10, 50, 680, 21,
            _tr("Select the updated field and sample photograph folder")
        )

        self.pushButton_15 = _btn(
            self.groupBox_16,
            "...",
            700, 50, 31, 21,
            _BTN_BROWSE
        )

        self.option1_ckeckbox = QCheckBox(
            _tr("Update the Filepath Information for Existing Photographs"),
            self.groupBox_16
        )
        self.option1_ckeckbox.setGeometry(10, 75, 741, 21)

        self.option2_ckeckbox = QCheckBox(
            _tr("Set the New Path as a Default Value for Future Field and Sample Photograph Entry"),
            self.groupBox_16
        )
        self.option2_ckeckbox.setGeometry(10, 96, 511, 21)

        self.pushButton_update_source_photo = _btn(
            self.groupBox_16,
            _tr("Update Repository"),
            531, 96, 220, 21,
            _BTN,
            _tr("Update photograph paths in the project repository.")
        )

        _lbl(
            self.groupBox_16,
            _tr("Use Photograph EXIF Metadata to Retrieve Image Direction:"),
            10, 121, 381, 21
        )

        self.pushButton_use_exif_azimuth = _btn(
            self.groupBox_16,
            _tr("Update Image Direction from Metadata"),
            391, 121, 360, 21
        )

        # Bottom bar — RESET widened 141→215, moved left; y shifted +80
        self.pushButton_22 = _btn(W, _tr("RESET THE WINDOW"), 565, 790, 215, 21)
        self.label_32 = _lbl(W, _COPYRIGHT, 10, 790, 611, 21, _CPR)

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

        # Where to Download — Zenodo button widened 121→185
        gb14 = _gb(W, _tr("Where to Download the GEOL-QMAPS QGIS Mapping Template?"),
                   10, 10, 761, 61, ptsize=12)
        self.pushButton_34 = _btn(gb14, _tr("Zenodo Repository "), 290, 30, 185, 21, _HELP_BTN)

        # Need Help — Send Email widened 81→200; User Guide widened 81→155
        gb13 = _gb(W, _tr("Need Some Help? Contact Us!"), 10, 90, 381, 151, ptsize=12)
        self.plainTextEdit_8 = _pte(
            gb13, 10, 30, 741, 111,
            "M.W. Jessell*, J. Perret* and E. Bétend - Developers of the Plugin\n\n"
            "J. Perret* - Developer of the GEOL-QMAPS QGIS Mapping Template \n\n"
            "*Contact Us:\n\nOnline Documentation:",
            "plainTextEdit_8")
        self.pushButton_24 = _btn(gb13, _tr("Send Email"), 10,  80, 200, 21, _HELP_BTN)
        self.pushButton_21 = _btn(gb13, _tr("User Guide"), 10, 110, 155, 21, _HELP_BTN)

        # Feedback — Bug Report widened 91→170; Send Email widened 81→200
        gb30 = _gb(W, _tr("Please Provide Feedback"), 400, 90, 371, 151, ptsize=12)
        self.plainTextEdit_9 = _pte(
            gb30, 10, 30, 351, 111,
            _tr("If you have bugs to report, suggestions for improvements or new tools "
                "to add to this plugin, please submit them on the GitHub issues page, "
                "or contact us !"),
            "plainTextEdit_9")
        self.pushButton_23 = _btn(gb30, _tr("Bug Report"),  10, 110, 170, 21, _HELP_BTN)
        self.pushButton_28 = _btn(gb30, _tr("Send Email"), 190, 110, 171, 21, _HELP_BTN)

        # Roadmap — User Guide - Roadmap widened 141→250
        gb33 = _gb(W, _tr("Roadmap for Future Development"), 10, 260, 761, 61, ptsize=12)
        self.plainTextEdit_11 = _pte(
            gb33, 10, 30, 731, 31,
            _tr("Please visit the following page:"),
            "plainTextEdit_11")
        self.pushButton_30 = _btn(gb33, _tr("User Guide - Roadmap"), 255, 30, 250, 21, _HELP_BTN)

        # WAXI — WAXI/AMIRA buttons widened 121→160/165
        gb31 = _gb(W, _tr("Keen to Learn More About the West Africa Exploration Initiative?"),
                   10, 340, 761, 121, ptsize=12)
        self.plainTextEdit_5 = _pte(
            gb31, 10, 30, 741, 81,
            _tr("The AMIRA West African Exploration Initiative (WAXI) is a unique "
                "collaborative research and training program focusing on the tectonics "
                "and mineral potential of the West African Craton, involving research "
                "institutions, geological surveys, governements and actors of the "
                "mineral industry.\n\nFor more information, please consult: "),
            "plainTextEdit_5")
        self.pushButton_41 = _btn(gb31, _tr("WAXI website"),  210, 70, 160, 21, _HELP_BTN)
        self.pushButton_40 = _btn(gb31, _tr("AMIRA website"), 380, 70, 165, 21, _HELP_BTN)

        # Copyright
        self.label_37 = _lbl(W, _COPYRIGHT, 10, 710, 311, 21, _CPR)

        return W

    # ------------------------------------------------------------------

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()
