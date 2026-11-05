# -*- coding: utf-8 -*-
"""Screenshots fuer das Carry-Radlager (vereinfachter Halter)."""
import os, traceback
import FreeCAD as App
import Part, Sketcher
import FreeCADGui as Gui
from PySide import QtCore, QtGui, QtWidgets

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "assets")
LOG = os.path.join(OUT, "lager.log")
TMP = os.path.join(OUT, "_lager.FCStd")
WIDTH = 1500
open(LOG, "w", encoding="utf-8").close()

def log(m):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(str(m) + "\n")

def pump(ms=400):
    QtWidgets.QApplication.processEvents()
    QtCore.QThread.msleep(ms)
    QtWidgets.QApplication.processEvents()

def hide_report():
    for d in Gui.getMainWindow().findChildren(QtWidgets.QDockWidget):
        t = d.windowTitle()
        if any(w in t for w in ("Ausgabe", "Report", "Python", "Konsole")):
            if d.isVisible():
                d.hide()

def shot(name, overlay=None):
    hide_report(); Gui.updateGui(); pump(400)
    mw = Gui.getMainWindow(); pm = mw.grab()
    if overlay is not None:
        try:
            om = overlay.grab()
            pos = mw.mapFromGlobal(overlay.geometry().topLeft()) if overlay.isWindow() else mw.mapFromGlobal(overlay.mapToGlobal(QtCore.QPoint(0,0)))
            p = QtGui.QPainter(pm); p.drawPixmap(pos, om); p.end()
        except Exception as e:
            log("overlay %r" % e)
    if pm.width() > WIDTH:
        pm = pm.scaledToWidth(WIDTH, QtCore.Qt.SmoothTransformation)
    pm.save(os.path.join(OUT, name + ".jpg"), "JPG", 88)
    log("shot " + name)

def run():
    try:
        mw = Gui.getMainWindow()
        mw.resize(1500, 844); mw.move(20, 20); mw.raise_(); pump(700)
        d = QtWidgets.QApplication.activeModalWidget()
        if d and "DocumentRecovery" in d.objectName():
            d.reject(); pump(400)

        Gui.runCommand("Std_New"); pump(900)
        Gui.activateWorkbench("PartDesignWorkbench"); pump(700)
        doc = App.activeDocument(); doc.Label = "Radlager"
        Gui.runCommand("PartDesign_Body"); pump(1200)
        body = [o for o in doc.Objects if o.TypeId == "PartDesign::Body"][-1]
        body.Label = "Radlager"
        Gui.Selection.clearSelection(); pump(400)

        # Profil: Linie + Bogen
        sk = body.newObject("Sketcher::SketchObject", "Profil")
        sk.Label = "Halterprofil"
        plane = body.Origin.OriginFeatures[3]
        sk.AttachmentSupport = [(plane, "")]; sk.MapMode = "FlatFace"
        doc.recompute()
        Gui.activeDocument().setEdit(sk.Name); pump(700)
        view = Gui.activeDocument().activeView()
        view.setCameraType("Orthographic"); view.viewTop(); pump(300)
        sk.addGeometry(Part.LineSegment(App.Vector(-30, 20, 0), App.Vector(30, 20, 0)), False)
        sk.addGeometry(Part.Arc(App.Vector(30, 20, 0), App.Vector(0, -30, 0), App.Vector(-30, 20, 0)), False)
        sk.addConstraint(Sketcher.Constraint("Coincident", 0, 1, 1, 2))
        sk.addConstraint(Sketcher.Constraint("Coincident", 0, 2, 1, 1))
        sk.addConstraint(Sketcher.Constraint("Horizontal", 0))
        doc.recompute(); pump(400)
        view.fitAll(); pump(500)
        shot("01_profil")

        c1 = sk.addConstraint(Sketcher.Constraint("Distance", 0, 60.0))
        c2 = sk.addConstraint(Sketcher.Constraint("Radius", 1, 34.0))
        doc.recompute(); pump(500)
        view.fitAll(); pump(500)
        shot("02_masse")

        Gui.activeDocument().resetEdit(); pump(700)
        pad = body.newObject("PartDesign::Pad", "Pad")
        pad.Label = "Halter"
        pad.Profile = sk; pad.Length = 6.0
        doc.recompute(); pump(700)
        try:
            sk.ViewObject.Visibility = False
        except Exception:
            pass
        view.setCameraType("Perspective"); view.viewIsometric(); view.fitAll(); pump(500)
        try:
            Gui.activeDocument().setEdit(pad.Name); pump(1400)
        except Exception as e:
            log("pad edit %r" % e)
        shot("03_aufpolstern")
        try:
            Gui.activeDocument().resetEdit()
        except Exception:
            pass
        pump(600)
        shot("04_halter")

        # Bohrungen
        hs = body.newObject("Sketcher::SketchObject", "Bohrungen")
        hs.Label = "Bohrungen"
        hs.AttachmentSupport = [(pad, "Face6")]; hs.MapMode = "FlatFace"
        doc.recompute(); pump(400)
        Gui.activeDocument().setEdit(hs.Name); pump(600)
        hs.addGeometry(Part.Circle(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 5.0), False)
        hs.addConstraint(Sketcher.Constraint("Radius", 0, 5.0))
        hs.addGeometry(Part.Circle(App.Vector(-20, 14, 0), App.Vector(0, 0, 1), 1.5), False)
        hs.addConstraint(Sketcher.Constraint("Radius", 1, 1.5))
        hs.addGeometry(Part.Circle(App.Vector(20, 14, 0), App.Vector(0, 0, 1), 1.5), False)
        hs.addConstraint(Sketcher.Constraint("Radius", 2, 1.5))
        doc.recompute(); pump(400)
        view.viewTop(); view.fitAll(); pump(500)
        shot("05_bohrungen")
        Gui.activeDocument().resetEdit(); pump(600)
        hp = body.newObject("PartDesign::Pocket", "Löcher")
        hp.Label = "Bohrungen"
        hp.Profile = hs; hp.Type = 1
        doc.recompute(); pump(700)
        try:
            hs.ViewObject.Visibility = False
        except Exception:
            pass
        view.viewIsometric(); view.fitAll(); pump(500)
        shot("06_fertig")

        # Farbe
        try:
            hp.ViewObject.ShapeColor = (0.65, 0.68, 0.72)
        except Exception:
            pass
        Gui.Selection.clearSelection(); pump(400)
        view.viewIsometric(); view.fitAll(); pump(500)
        shot("07_farbe")

        doc.saveAs(TMP); pump(600)
        for a in mw.menuBar().actions():
            if a.text().replace("&", "").strip() == "Datei":
                menu = a.menu(); rect = mw.menuBar().actionGeometry(a)
                menu.popup(mw.menuBar().mapToGlobal(rect.bottomLeft()))
                QtWidgets.QApplication.processEvents(); pump(500)
                pop = QtWidgets.QApplication.activePopupWidget()
                if pop:
                    shot("08_speichern", pop); pop.close()
                else:
                    shot("08_speichern")
                break
        log("FERTIG")
    except Exception:
        log("FEHLER\n" + traceback.format_exc())
    finally:
        try:
            if App.activeDocument() and App.activeDocument().FileName == TMP:
                App.closeDocument(App.activeDocument().Name)
        except Exception:
            pass
        pump(400)
        try:
            if os.path.exists(TMP): os.remove(TMP)
        except Exception:
            pass
        QtCore.QTimer.singleShot(1200, QtWidgets.QApplication.quit)

QtCore.QTimer.singleShot(2500, run)
