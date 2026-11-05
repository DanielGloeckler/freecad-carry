# -*- coding: utf-8 -*-
"""Screenshot: XY-Ebene im Dialog 'Befestigung auswählen' markieren."""
import os
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtGui, QtWidgets

OUT = r"D:\Dokumente\Standardprojekt\freecad-carry\assets\chassi_00_ebene.jpg"

def pump(ms=400):
    QtWidgets.QApplication.processEvents(); QtCore.QThread.msleep(ms); QtWidgets.QApplication.processEvents()

def run():
    try:
        mw = Gui.getMainWindow(); mw.resize(1500, 844); mw.raise_(); pump(700)
        d = QtWidgets.QApplication.activeModalWidget()
        if d and "DocumentRecovery" in d.objectName():
            d.reject(); pump(400)
        Gui.runCommand("Std_New"); pump(900)
        Gui.activateWorkbench("PartDesignWorkbench"); pump(700)
        doc = App.activeDocument(); doc.Label = "Chassi"
        Gui.runCommand("PartDesign_Body"); pump(1200)
        body = [o for o in doc.Objects if o.TypeId == "PartDesign::Body"][-1]
        body.Label = "Chassi"
        Gui.Selection.clearSelection(); pump(400)
        Gui.runCommand("PartDesign_NewSketch"); pump(1500)
        for lw in mw.findChildren(QtWidgets.QListWidget):
            if lw.isVisible() and lw.count() >= 3:
                lw.setCurrentRow(0); pump(500); break
        Gui.updateGui(); pump(400)
        pm = mw.grab()
        if pm.width() > 1500:
            pm = pm.scaledToWidth(1500, QtCore.Qt.SmoothTransformation)
        pm.save(OUT, "JPG", 88)
        print("saved", OUT)
    except Exception:
        import traceback; print(traceback.format_exc())
    finally:
        QtCore.QTimer.singleShot(800, QtWidgets.QApplication.quit)

QtCore.QTimer.singleShot(2500, run)
