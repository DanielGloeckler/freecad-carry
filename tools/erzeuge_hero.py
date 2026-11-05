# -*- coding: utf-8 -*-
"""Sauberes Hero-Bild der fertigen Baugruppe (ohne FreeCAD-Oberfläche)."""
import os, traceback
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtGui, QtWidgets

OUT = r"D:\Dokumente\Standardprojekt\freecad-carry\assets\carry_hero.jpg"
SRC = r"D:\Temp\opencode\carry\Carry.FCStd"

def pump(ms=400):
    QtWidgets.QApplication.processEvents(); QtCore.QThread.msleep(ms); QtWidgets.QApplication.processEvents()

def run():
    try:
        mw = Gui.getMainWindow()
        mw.resize(1400, 860); mw.move(30, 30); mw.raise_(); pump(900)
        dlg = QtWidgets.QApplication.activeModalWidget()
        if dlg and "DocumentRecovery" in dlg.objectName():
            dlg.reject(); pump(400)

        App.openDocument(SRC); pump(1600)
        doc = App.activeDocument()
        for o in doc.Objects:
            try:
                if o.TypeId == "App::Origin" or o.TypeId == "App::Line" or o.TypeId == "App::Plane":
                    o.ViewObject.Visibility = False
            except Exception:
                pass
        view = Gui.activeDocument().activeView()
        view.setCameraType("Perspective")
        view.viewIsometric()
        view.fitAll()
        pump(600)
        try:
            view.setAxisCross(False)
        except Exception as e:
            print("axiscross", e)
        try:
            view.setNavigationCube(False)
        except Exception as e:
            print("cube", e)

        # Oberflaeche ausblenden
        for tb in mw.findChildren(QtWidgets.QToolBar):
            tb.hide()
        mw.menuBar().hide()
        mw.statusBar().hide()
        for d in mw.findChildren(QtWidgets.QDockWidget):
            d.hide()
        for tabbar in mw.findChildren(QtWidgets.QTabBar):
            tabbar.hide()
        pump(700)
        view.fitAll(); pump(700)

        pm = mw.grab()
        pm.save(OUT, "JPG", 92)
        print("saved", OUT, pm.width(), pm.height())
    except Exception:
        import traceback as tb
        print(tb.format_exc())
    finally:
        QtCore.QTimer.singleShot(800, QtWidgets.QApplication.quit)

QtCore.QTimer.singleShot(2500, run)
