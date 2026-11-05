# -*- coding: utf-8 -*-
"""Echte FreeCAD-Screenshots: ein Kreis + ein Loch (Chassi)."""
import os, traceback
import FreeCAD as App
import Part, Sketcher
import FreeCADGui as Gui
from PySide import QtCore, QtGui, QtWidgets

BASE = r"D:\Dokumente\Standardprojekt\freecad-carry"
OUT = os.path.join(BASE, "assets")
LOG = os.path.join(OUT, "ch_test.log")
open(LOG, "w", encoding="utf-8").close()

def log(m):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(str(m) + "\n")

def pump(ms=300):
    QtWidgets.QApplication.processEvents(); QtCore.QThread.msleep(ms); QtWidgets.QApplication.processEvents()

def hide_report():
    for d in Gui.getMainWindow().findChildren(QtWidgets.QDockWidget):
        t = d.windowTitle()
        if any(w in t for w in ("Ausgabe", "Report", "Python", "Konsole")):
            if d.isVisible(): d.hide()

def shot(name):
    hide_report(); Gui.updateGui(); pump(400)
    mw = Gui.getMainWindow(); pm = mw.grab()
    if pm.width() > 1500: pm = pm.scaledToWidth(1500, QtCore.Qt.SmoothTransformation)
    pm.save(os.path.join(OUT, name + ".jpg"), "JPG", 88)
    log("shot " + name)

def run():
    try:
        mw = Gui.getMainWindow(); mw.resize(1500, 844); mw.move(20, 20); mw.raise_(); pump(700)
        dlg = QtWidgets.QApplication.activeModalWidget()
        if dlg and "DocumentRecovery" in dlg.objectName(): dlg.reject(); pump(400)

        Gui.runCommand("Std_New"); pump(800)
        Gui.activateWorkbench("PartDesignWorkbench"); pump(600)
        doc = App.activeDocument(); doc.Label = "Chassi"
        Gui.runCommand("PartDesign_Body"); pump(900)
        body = [o for o in doc.Objects if o.TypeId == "PartDesign::Body"][-1]
        body.Label = "Chassi"
        view = Gui.activeDocument().activeView()

        # Rechteck auf XY
        sk = body.newObject("Sketcher::SketchObject", "Skizze")
        sk.AttachmentSupport = [(body.Origin.OriginFeatures[3], "")]; sk.MapMode = "FlatFace"
        doc.recompute(); pump(300)
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
        sk.addConstraint(Sketcher.Constraint("Distance", 0, 116.0))
        sk.addConstraint(Sketcher.Constraint("Distance", 1, 82.0))
        sk.addConstraint(Sketcher.Constraint("Symmetric", 0, 1, 2, 1, -1, 1))
        doc.recompute(); pump(300)
        Gui.activeDocument().resetEdit(); pump(400)

        pad = body.newObject("PartDesign::Pad", "Platte")
        pad.Profile = sk; pad.Length = 5.0
        doc.recompute(); pump(600)
        log("pad bb %r" % (pad.Shape.BoundBox,))
        try: sk.ViewObject.Visibility = False
        except Exception: pass

        # Loch-Skizze: XY mit Offset z=5
        hs = body.newObject("Sketcher::SketchObject", "LochSkizze")
        hs.Label = "Loch-Skizze"
        hs.AttachmentSupport = [(body.Origin.OriginFeatures[3], "")]; hs.MapMode = "FlatFace"
        hs.AttachmentOffset = App.Placement(App.Vector(0, 0, 5), App.Rotation())
        doc.recompute(); pump(300)
        Gui.activeDocument().setEdit(hs.Name); pump(700)
        hs.addGeometry(Part.Circle(App.Vector(-48, 30, 0), App.Vector(0, 0, 1), 1.5), False)
        hs.addConstraint(Sketcher.Constraint("Radius", 0, 1.5))
        hs.addConstraint(Sketcher.Constraint("DistanceX", 0, 3, -1, 2, -48.0))
        hs.addConstraint(Sketcher.Constraint("DistanceY", 0, 3, -1, 1, 30.0))
        doc.recompute(); pump(500)
        log("hs placement %r" % (hs.Placement,))
        view = Gui.activeDocument().activeView()
        view.setCameraType("Orthographic")
        view.viewTop(); pump(400)
        Gui.SendMsgToActiveView("ViewFit"); pump(900)
        view.fitAll(); pump(600)
        shot("ch_kreis")
        Gui.activeDocument().resetEdit(); pump(500)

        hp = body.newObject("PartDesign::Pocket", "Loch")
        hp.Profile = hs; hp.Type = 1; hp.Reversed = False
        doc.recompute(); pump(700)
        log("pocket vol %.1f" % hp.Shape.Volume)
        try: hs.ViewObject.Visibility = False
        except Exception: pass
        view = Gui.activeDocument().activeView()
        view.setCameraType("Perspective"); view.viewIsometric(); view.fitAll(); pump(700)
        shot("ch_ein_loch")
        log("FERTIG")
    except Exception:
        log("FEHLER\n" + traceback.format_exc())
    finally:
        QtCore.QTimer.singleShot(900, QtWidgets.QApplication.quit)

QtCore.QTimer.singleShot(2500, run)
