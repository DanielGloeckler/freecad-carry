# -*- coding: utf-8 -*-
"""Baugruppe Carry mit A2plus - Screenshots."""
import os, traceback
import FreeCAD as App
import Part
import FreeCADGui as Gui
from PySide import QtCore, QtGui, QtWidgets

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "assets")
CARRY = r"D:\Temp\opencode\carry"
LOG = os.path.join(OUT, "baugruppe.log")
WIDTH = 1500
open(LOG, "w", encoding="utf-8").close()

def log(m):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(str(m) + "\n")

def pump(ms=400):
    QtWidgets.QApplication.processEvents(); QtCore.QThread.msleep(ms); QtWidgets.QApplication.processEvents()

def hide_report():
    for d in Gui.getMainWindow().findChildren(QtWidgets.QDockWidget):
        t = d.windowTitle()
        if any(w in t for w in ("Ausgabe", "Report", "Python", "Konsole")):
            if d.isVisible(): d.hide()

def shot(name):
    hide_report(); Gui.updateGui(); pump(400)
    mw = Gui.getMainWindow(); pm = mw.grab()
    if pm.width() > WIDTH: pm = pm.scaledToWidth(WIDTH, QtCore.Qt.SmoothTransformation)
    pm.save(os.path.join(OUT, name + ".jpg"), "JPG", 88)
    log("shot " + name)

def run():
    try:
        mw = Gui.getMainWindow(); mw.resize(1500, 844); mw.move(20, 20); mw.raise_(); pump(700)
        dlg = QtWidgets.QApplication.activeModalWidget()
        if dlg and "DocumentRecovery" in dlg.objectName(): dlg.reject(); pump(400)

        Gui.runCommand("Std_New"); pump(900)
        Gui.activateWorkbench("A2plusWorkbench"); pump(1200)
        doc = App.activeDocument(); doc.Label = "Carry"
        view = Gui.activeDocument().activeView()
        view.setCameraType("Perspective")
        view.viewIsometric(); view.fitAll(); pump(500)
        shot("bg_01_leer")

        import a2p_importpart
        def imp(fname, label):
            o = a2p_importpart.importPartFromFile(doc, os.path.join(CARRY, fname))
            o.Label = label
            doc.recompute()
            return o

        ch = imp("Chassi.FCStd", "Chassi")
        log("chassi bb %r" % (ch.Shape.BoundBox,))
        view.viewIsometric(); view.fitAll(); pump(600)
        shot("bg_02_chassi")

        # Radlager
        lg = imp("Radlager.FCStd", "Radlager")
        lg.Placement = App.Placement(App.Vector(36, 30, -25), App.Rotation())
        doc.recompute(); pump(500)
        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(lg)
        Gui.runCommand("Std_ViewFitSelection"); pump(500)
        shot("bg_03_lager")

        # Schraube + Mutter
        Mutter = imp("Mutter M3.FCStd", "Mutter M3")
        Mutter.Placement = App.Placement(App.Vector(48, 30, -13), App.Rotation())
        Schraube = imp("Schraube M3.FCStd", "Schraube M3")
        Schraube.Placement = App.Placement(App.Vector(48, 30, 5), App.Rotation())
        n0 = imp("Mutter M3.FCStd", "Mutter M3")
        n0.Placement = App.Placement(App.Vector(24, 30, -13), App.Rotation())
        s0 = imp("Schraube M3.FCStd", "Schraube M3")
        s0.Placement = App.Placement(App.Vector(24, 30, 5), App.Rotation())
        doc.recompute(); pump(500)
        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(lg); Gui.Selection.addSelection(Schraube)
        Gui.runCommand("Std_ViewFitSelection"); pump(500)
        shot("bg_04_schraube")

        # restliche 3 Radlager mit je 2 Schrauben und Muttern
        for (bx, by) in ((-36, 30), (36, -30), (-36, -30)):
            b = imp("Radlager.FCStd", "Radlager")
            b.Placement = App.Placement(App.Vector(bx, by, -25), App.Rotation())
            for dx in (-12, 12):
                n = imp("Mutter M3.FCStd", "Mutter M3")
                n.Placement = App.Placement(App.Vector(bx + dx, by, -13), App.Rotation())
                s = imp("Schraube M3.FCStd", "Schraube M3")
                s.Placement = App.Placement(App.Vector(bx + dx, by, 5), App.Rotation())
        Gui.Selection.clearSelection(); doc.recompute(); pump(600)
        view.viewIsometric(); view.fitAll(); pump(500)
        shot("bg_05_lager4")

        # Achsen
        for x in (-36, 36):
            a = imp("Achse.FCStd", "Achse")
            a.Placement = App.Placement(App.Vector(x, 52, -10),
                                        App.Rotation(App.Vector(1, 0, 0), 90))
        Gui.Selection.clearSelection(); doc.recompute(); pump(500)
        view.viewIsometric(); view.fitAll(); pump(500)
        shot("bg_06_achsen")

        # Raeder
        for (x, y) in ((-36, 52), (36, 52), (-36, -52), (36, -52)):
            w = imp("Rad.FCStd", "Rad")
            w.Placement = App.Placement(App.Vector(x, y, -10),
                                        App.Rotation(App.Vector(0, 0, 1), 90))
            log("rad bb %r" % (w.Shape.BoundBox,))
        Gui.Selection.clearSelection(); doc.recompute(); pump(700)
        view.viewIsometric(); view.fitAll(); pump(600)
        shot("bg_07_raeder")

        view.viewFront(); view.fitAll(); pump(400)
        shot("bg_08_front")
        view.viewIsometric(); view.fitAll(); pump(500)
        shot("bg_09_fertig")

        doc.saveAs(os.path.join(CARRY, "Carry.FCStd")); pump(600)
        shot("bg_10_speichern")
        log("FERTIG")
    except Exception:
        log("FEHLER\n" + traceback.format_exc())
    finally:
        QtCore.QTimer.singleShot(1200, QtWidgets.QApplication.quit)

QtCore.QTimer.singleShot(2500, run)
