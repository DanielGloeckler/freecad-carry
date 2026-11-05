# -*- coding: utf-8 -*-
"""Chassi: ein Kreis + zwei lineare Muster (wie im PDF) – neue Screenshots."""
import os, traceback, math
import FreeCAD as App
import Part, Sketcher
import FreeCADGui as Gui
from PySide import QtCore, QtGui, QtWidgets

BASE = r"D:\Dokumente\Standardprojekt\freecad-carry"
OUT = os.path.join(BASE, "assets")
LOG = os.path.join(OUT, "chassi_holes.log")
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
        Gui.activateWorkbench("PartDesignWorkbench"); pump(700)
        doc = App.activeDocument(); doc.Label = "Chassi"
        Gui.runCommand("PartDesign_Body"); pump(1000)
        body = [o for o in doc.Objects if o.TypeId == "PartDesign::Body"][-1]
        body.Label = "Chassi"
        Gui.Selection.clearSelection(); pump(300)
        view = Gui.activeDocument().activeView()
        view.setCameraType("Perspective")

        xy = body.Origin.OriginFeatures[3]
        sk = body.newObject("Sketcher::SketchObject", "Skizze")
        sk.AttachmentSupport = [(xy, "")]; sk.MapMode = "FlatFace"
        doc.recompute()
        Gui.activeDocument().setEdit(sk.Name); pump(500)
        pts = [(-58, -41), (58, -41), (58, 41), (-58, 41)]
        for i in range(4):
            sk.addGeometry(Part.LineSegment(App.Vector(pts[i][0], pts[i][1], 0),
                                            App.Vector(pts[(i + 1) % 4][0], pts[(i + 1) % 4][1], 0)), False)
        for i in range(4):
            sk.addConstraint(Sketcher.Constraint("Coincident", i, 2, (i + 1) % 4, 1))
        for i in (0, 2):
            sk.addConstraint(Sketcher.Constraint("Horizontal", i))
        for i in (1, 3):
            sk.addConstraint(Sketcher.Constraint("Vertical", i))
        sk.addConstraint(Sketcher.Constraint("DistanceX", 0, 1, -1, 1, -58.0))
        sk.addConstraint(Sketcher.Constraint("DistanceY", 0, 1, -1, 1, -41.0))
        sk.addConstraint(Sketcher.Constraint("Distance", 0, 116.0))
        sk.addConstraint(Sketcher.Constraint("Distance", 1, 82.0))
        doc.recompute(); pump(400)
        Gui.activeDocument().resetEdit(); pump(500)

        pad = body.newObject("PartDesign::Pad", "Platte")
        pad.Profile = sk; pad.Length = 5.0
        doc.recompute(); pump(600)
        try: sk.ViewObject.Visibility = False
        except Exception: pass
        view.viewIsometric(); view.fitAll(); pump(500)

        # Loch-Skizze auf der Deckflaeche
        hs = body.newObject("Sketcher::SketchObject", "LochSkizze")
        hs.Label = "Loch-Skizze"
        hs.AttachmentSupport = [(body.Origin.OriginFeatures[3], "")]; hs.MapMode = "FlatFace"
        hs.AttachmentOffset = App.Placement(App.Vector(0, 0, 5), App.Rotation())
        doc.recompute(); pump(300)
        Gui.activeDocument().setEdit(hs.Name); pump(500)
        hx, hy = -48.0, 30.0
        hs.addGeometry(Part.Circle(App.Vector(hx, hy, 0), App.Vector(0, 0, 1), 1.5), False)
        hs.addConstraint(Sketcher.Constraint("Radius", 0, 1.5))
        hs.addConstraint(Sketcher.Constraint("DistanceX", 0, 3, -1, 1, hx))
        hs.addConstraint(Sketcher.Constraint("DistanceY", 0, 3, -1, 1, hy))
        doc.recompute(); pump(600)
        view = Gui.activeDocument().activeView()
        view.setCameraType("Orthographic")
        view.viewTop()
        Gui.SendMsgToActiveView("ViewFit")
        view.fitAll(); pump(900)
        shot("ch_kreis")
        Gui.activeDocument().resetEdit(); pump(500)

        hp = body.newObject("PartDesign::Pocket", "Loch")
        hp.Profile = hs; hp.Type = 1; hp.Reversed = True
        doc.recompute(); pump(600)
        try: hs.ViewObject.Visibility = False
        except Exception: pass
        view.setCameraType("Perspective"); view.viewIsometric(); view.fitAll(); pump(500)
        shot("ch_ein_loch")

        # Erstes lineares Muster
        lp = body.newObject("PartDesign::LinearPattern", "MusterX")
        lp.Originals = [hp]
        lp.Direction = (body.Origin.OriginFeatures[0], [""])
        lp.Length = 96.0
        lp.Occurrences = 9
        doc.recompute(); pump(800)
        log("lp1 ok")
        view.viewIsometric(); view.fitAll(); pump(400)
        try:
            Gui.activeDocument().setEdit(lp.Name); pump(1200)
            shot("ch_muster1")
            Gui.activeDocument().resetEdit(); pump(500)
        except Exception as e:
            log("lp1 edit %r" % e)

        view.viewIsometric(); view.fitAll(); pump(500)
        shot("ch_45")
        log("FERTIG")
    except Exception:
        log("FEHLER\n" + traceback.format_exc())
    finally:
        QtCore.QTimer.singleShot(1000, QtWidgets.QApplication.quit)

QtCore.QTimer.singleShot(2500, run)
