# -*- coding: utf-8 -*-
"""Erzeugt die echten FreeCAD-Screenshots fuer das Carry-Chassi."""
import os, traceback
import FreeCAD as App
import Part, Sketcher
import FreeCADGui as Gui
from PySide import QtCore, QtGui, QtWidgets

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "assets")
os.makedirs(OUT, exist_ok=True)
LOG = os.path.join(OUT, "chassi.log")
TMP = os.path.join(OUT, "_chassi.FCStd")
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
    hide_report()
    Gui.updateGui(); pump(400)
    mw = Gui.getMainWindow()
    pm = mw.grab()
    if overlay is not None:
        try:
            om = overlay.grab()
            if overlay.isWindow():
                pos = mw.mapFromGlobal(overlay.geometry().topLeft())
            else:
                pos = mw.mapFromGlobal(overlay.mapToGlobal(QtCore.QPoint(0, 0)))
            p = QtGui.QPainter(pm); p.drawPixmap(pos, om); p.end()
        except Exception as e:
            log("overlay: %r" % e)
    if pm.width() > WIDTH:
        pm = pm.scaledToWidth(WIDTH, QtCore.Qt.SmoothTransformation)
    pm.save(os.path.join(OUT, name + ".jpg"), "JPG", 88)
    log("shot " + name)

def visible_button(t):
    for b in Gui.getMainWindow().findChildren(QtWidgets.QPushButton):
        if b.isVisible() and b.text().replace("&", "").strip() == t:
            return b
    return None

def add_rect(sk, w, h):
    pts = [App.Vector(-w/2, -h/2, 0), App.Vector(w/2, -h/2, 0),
           App.Vector(w/2, h/2, 0), App.Vector(-w/2, h/2, 0)]
    for i in range(4):
        sk.addGeometry(Part.LineSegment(pts[i], pts[(i+1) % 4]), False)
    for i in range(4):
        sk.addConstraint(Sketcher.Constraint("Coincident", i, 2, (i+1) % 4, 1))
    sk.addConstraint(Sketcher.Constraint("Horizontal", 0))
    sk.addConstraint(Sketcher.Constraint("Horizontal", 2))
    sk.addConstraint(Sketcher.Constraint("Vertical", 1))
    sk.addConstraint(Sketcher.Constraint("Vertical", 3))

def run():
    try:
        mw = Gui.getMainWindow()
        mw.resize(1500, 844); mw.move(20, 20); mw.raise_()
        pump(800)
        d = QtWidgets.QApplication.activeModalWidget()
        if d and "DocumentRecovery" in d.objectName():
            d.reject(); pump(400)

        Gui.runCommand("Std_New"); pump(900)
        Gui.activateWorkbench("PartDesignWorkbench"); pump(700)
        doc = App.activeDocument(); doc.Label = "Chassi"
        Gui.Selection.clearSelection(); pump(300)
        shot("01_neues_dokument")

        Gui.runCommand("PartDesign_Body"); pump(1200)
        body = [o for o in doc.Objects if o.TypeId == "PartDesign::Body"][-1]
        body.Label = "Chassi"
        Gui.Selection.clearSelection(); pump(500)

        # --- Skizze 116 x 82 ---
        sk = body.newObject("Sketcher::SketchObject", "Sketch")
        sk.Label = "Chassis-Skizze"
        plane = [o for o in body.Origin.OriginFeatures if o.Name == "XY_Plane"][0]
        sk.AttachmentSupport = [(plane, "")]; sk.MapMode = "FlatFace"
        doc.recompute(); pump(400)
        Gui.activeDocument().setEdit(sk.Name); pump(700)
        view = Gui.activeDocument().activeView()
        view.setCameraType("Orthographic"); view.viewTop(); pump(400)
        add_rect(sk, 116, 82)
        doc.recompute(); pump(500)
        view.fitAll(); pump(500)
        shot("02_rechteck")

        sk.addConstraint(Sketcher.Constraint("Symmetric", 0, 1, 2, 1, -1, 1))
        doc.recompute(); pump(500)
        view.fitAll(); pump(500)
        shot("03_symmetrie")

        cw = sk.addConstraint(Sketcher.Constraint("Distance", 2, 116.0))
        ch = sk.addConstraint(Sketcher.Constraint("Distance", 1, 82.0))
        doc.recompute(); pump(500)
        try:
            sk.setDatum(cw, App.Units.Quantity("116.00 mm"))
            sk.setDatum(ch, App.Units.Quantity("82.00 mm"))
        except Exception as e:
            log("datum: %r" % e)
        view.fitAll(); pump(500)
        shot("04_masse")

        Gui.activeDocument().resetEdit(); pump(700)
        pad = body.newObject("PartDesign::Pad", "Pad")
        pad.Label = "Platte"
        pad.Profile = sk; pad.Length = 5.0
        doc.recompute(); pump(700)
        try:
            sk.ViewObject.Visibility = False
        except Exception:
            pass
        view.setCameraType("Perspective"); view.viewIsometric(); view.fitAll(); pump(500)
        try:
            Gui.activeDocument().setEdit(pad.Name); pump(1400)
        except Exception as e:
            log("pad edit: %r" % e)
        shot("05_aufpolstern")
        try:
            Gui.activeDocument().resetEdit()
        except Exception:
            pass
        pump(700)
        shot("06_platte")

        # --- Loch ---
        hs = body.newObject("Sketcher::SketchObject", "HoleSketch")
        hs.Label = "Loch-Skizze"
        hs.AttachmentSupport = [(pad, "Face6")]; hs.MapMode = "FlatFace"
        doc.recompute(); pump(400)
        Gui.activeDocument().setEdit(hs.Name); pump(600)
        view.viewTop(); pump(300)
        for j in range(5):
            hs.addGeometry(Part.Circle(App.Vector(-48, 30 - 15*j, 0), App.Vector(0, 0, 1), 1.5), False)
            hs.addConstraint(Sketcher.Constraint("Radius", j, 1.5))
        doc.recompute(); pump(400)
        view.fitAll(); pump(500)
        shot("07_loch_skizze")

        Gui.activeDocument().resetEdit(); pump(700)
        pocket = body.newObject("PartDesign::Pocket", "Pocket")
        pocket.Label = "Loch"
        pocket.Profile = hs; pocket.Type = 1
        doc.recompute(); pump(700)
        try:
            hs.ViewObject.Visibility = False
        except Exception:
            pass
        view.viewIsometric(); view.fitAll(); pump(500)
        shot("08_loch")

        # --- Muster 9 x ---
        lin1 = body.newObject("PartDesign::LinearPattern", "LinearPattern")
        lin1.Label = "9 Löcher"
        lin1.Originals = [pocket]
        lin1.Direction = (body.Origin.OriginFeatures[0], [""])
        lin1.Length = 96.0; lin1.Occurrences = 9
        doc.recompute(); pump(700)
        try:
            Gui.activeDocument().setEdit(lin1.Name); pump(1400)
        except Exception as e:
            log("lin1 edit: %r" % e)
        shot("09_muster9")
        try:
            Gui.activeDocument().resetEdit()
        except Exception:
            pass
        pump(600)

        view.viewIsometric(); view.fitAll(); pump(500)
        shot("10_muster45")

        # --- Senkungen ---
        edges = []
        for i, e in enumerate(lin1.Shape.Edges):
            try:
                if e.Curve.TypeId == "Part::GeomCircle" and abs(e.Curve.Radius - 1.5) < 0.01:
                    if abs(e.Curve.Center.z - 5.0) < 0.01:
                        edges.append("Edge%d" % (i + 1))
            except Exception:
                pass
        log("Kanten: %d" % len(edges))
        cham = body.newObject("PartDesign::Chamfer", "Chamfer")
        cham.Label = "Senkungen"
        cham.Base = (lin1, edges)
        cham.Size = 0.75
        doc.recompute(); pump(800)
        view.viewIsometric(); view.fitAll(); pump(500)
        try:
            Gui.activeDocument().setEdit(cham.Name); pump(1400)
        except Exception as e:
            log("cham edit: %r" % e)
        shot("11_senkungen")
        try:
            Gui.activeDocument().resetEdit()
        except Exception:
            pass
        pump(600)

        # --- Farbe ---
        try:
            cham.ViewObject.ShapeColor = (0.85, 0.05, 0.05)
        except Exception:
            try:
                lin1.ViewObject.ShapeColor = (0.85, 0.05, 0.05)
            except Exception:
                pass
        Gui.Selection.clearSelection(); pump(500)
        view.viewIsometric(); view.fitAll(); pump(500)
        shot("12_rot")

        # --- Speichern ---
        doc.saveAs(TMP); pump(700)
        for a in mw.menuBar().actions():
            if a.text().replace("&", "").strip() == "Datei":
                menu = a.menu()
                rect = mw.menuBar().actionGeometry(a)
                menu.popup(mw.menuBar().mapToGlobal(rect.bottomLeft()))
                QtWidgets.QApplication.processEvents(); pump(500)
                pop = QtWidgets.QApplication.activePopupWidget()
                if pop:
                    shot("13_speichern", pop); pop.close()
                else:
                    shot("13_speichern")
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
