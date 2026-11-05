# -*- coding: utf-8 -*-
"""Screenshots fuer das Carry-Rad."""
import os, traceback
import FreeCAD as App
import Part, Sketcher
import FreeCADGui as Gui
from PySide import QtCore, QtGui, QtWidgets

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "assets")
LOG = os.path.join(OUT, "rad.log")
TMP = os.path.join(OUT, "_rad.FCStd")
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

def visible_button(t):
    for b in Gui.getMainWindow().findChildren(QtWidgets.QPushButton):
        if b.isVisible() and b.text().replace("&", "").strip() == t:
            return b
    return None

def run():
    try:
        mw = Gui.getMainWindow()
        mw.resize(1500, 844); mw.move(20, 20); mw.raise_(); pump(700)
        d = QtWidgets.QApplication.activeModalWidget()
        if d and "DocumentRecovery" in d.objectName():
            d.reject(); pump(400)

        Gui.runCommand("Std_New"); pump(900)
        Gui.activateWorkbench("PartDesignWorkbench"); pump(700)
        doc = App.activeDocument(); doc.Label = "Rad"
        Gui.runCommand("PartDesign_Body"); pump(1200)
        body = [o for o in doc.Objects if o.TypeId == "PartDesign::Body"][-1]
        body.Label = "Rad"
        Gui.Selection.clearSelection(); pump(400)

        xz = body.Origin.OriginFeatures[4]
        yz = body.Origin.OriginFeatures[5]

        # Profil
        sk = body.newObject("Sketcher::SketchObject", "Profil")
        sk.Label = "Profil"
        sk.AttachmentSupport = [(xz, "")]; sk.MapMode = "FlatFace"
        doc.recompute()
        Gui.activeDocument().setEdit(sk.Name); pump(700)
        view = Gui.activeDocument().activeView()
        view.setCameraType("Orthographic"); view.viewFront(); pump(300)
        pts = [(-10,0), (10,0), (10,25), (8,25), (8,22), (-8,22), (-8,25), (-10,25)]
        for i in range(8):
            sk.addGeometry(Part.LineSegment(App.Vector(pts[i][0], pts[i][1], 0),
                                            App.Vector(pts[(i+1)%8][0], pts[(i+1)%8][1], 0)), False)
        for i in range(8):
            sk.addConstraint(Sketcher.Constraint("Coincident", i, 2, (i+1)%8, 1))
        for i in (0,2,4,6):
            sk.addConstraint(Sketcher.Constraint("Horizontal", i))
        for i in (1,3,5,7):
            sk.addConstraint(Sketcher.Constraint("Vertical", i))
        doc.recompute(); pump(400)
        view.fitAll(); pump(500)
        shot("rad_01_profil")

        c1 = sk.addConstraint(Sketcher.Constraint("Distance", 0, 20.0))
        c2 = sk.addConstraint(Sketcher.Constraint("Distance", 1, 25.0))
        c3 = sk.addConstraint(Sketcher.Constraint("Distance", 4, 16.0))
        c4 = sk.addConstraint(Sketcher.Constraint("Distance", 3, 3.0))
        doc.recompute(); pump(500)
        view.fitAll(); pump(500)
        shot("rad_02_masse")

        Gui.activeDocument().resetEdit(); pump(700)
        rev = body.newObject("PartDesign::Revolution", "Revolution")
        rev.Label = "Radkörper"
        rev.Profile = sk
        rev.ReferenceAxis = (sk, ["H_Axis"])
        rev.Angle = 360.0
        doc.recompute(); pump(700)
        try:
            sk.ViewObject.Visibility = False
        except Exception:
            pass
        view.setCameraType("Perspective"); view.viewIsometric(); view.fitAll(); pump(500)
        try:
            Gui.activeDocument().setEdit(rev.Name); pump(1400)
        except Exception as e:
            log("rev edit %r" % e)
        shot("03_revolution")
        try:
            Gui.activeDocument().resetEdit()
        except Exception:
            pass
        pump(600)
        shot("04_rad")

        # Bohrung
        bore = body.newObject("Sketcher::SketchObject", "Bohrung")
        bore.Label = "Bohrung"
        bore.AttachmentSupport = [(yz, "")]; bore.MapMode = "FlatFace"
        doc.recompute(); pump(400)
        Gui.activeDocument().setEdit(bore.Name); pump(600)
        bore.addGeometry(Part.Circle(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 4.0), False)
        bore.addConstraint(Sketcher.Constraint("Radius", 0, 4.0))
        doc.recompute(); pump(400)
        view.viewRight(); view.fitAll(); pump(500)
        shot("05_bohrung")
        Gui.activeDocument().resetEdit(); pump(600)
        bp = body.newObject("PartDesign::Pocket", "BohrungTasche")
        bp.Profile = bore
        bp.Type = 0; bp.Length = 20.0; bp.Midplane = True
        doc.recompute(); pump(600)
        try:
            bore.ViewObject.Visibility = False
        except Exception:
            pass

        # Loch + polares Muster
        hole = body.newObject("Sketcher::SketchObject", "Loch")
        hole.Label = "Loch"
        hole.AttachmentSupport = [(yz, "")]; hole.MapMode = "FlatFace"
        doc.recompute(); pump(400)
        Gui.activeDocument().setEdit(hole.Name); pump(600)
        hole.addGeometry(Part.Circle(App.Vector(0, 15, 0), App.Vector(0, 0, 1), 2.5), False)
        hole.addConstraint(Sketcher.Constraint("Radius", 0, 2.5))
        doc.recompute(); pump(400)
        view.viewRight(); view.fitAll(); pump(500)
        shot("06_loch")
        Gui.activeDocument().resetEdit(); pump(600)
        hp = body.newObject("PartDesign::Pocket", "LochTasche")
        hp.Profile = hole
        hp.Type = 0; hp.Length = 20.0; hp.Midplane = True
        doc.recompute(); pump(600)
        try:
            hole.ViewObject.Visibility = False
        except Exception:
            pass
        pat = body.newObject("PartDesign::PolarPattern", "SechsLöcher")
        pat.Label = "6 Löcher"
        pat.Originals = [hp]
        pat.Axis = (body.Origin.OriginFeatures[0], [""])
        pat.Angle = 300.0; pat.Occurrences = 6
        doc.recompute(); pump(700)
        view.viewIsometric(); view.fitAll(); pump(500)
        try:
            Gui.activeDocument().setEdit(pat.Name); pump(1400)
            for cb in Gui.getMainWindow().findChildren(QtWidgets.QCheckBox):
                if cb.isVisible() and "Vorschau anzeigen" in cb.text():
                    cb.setChecked(False); pump(500); break
        except Exception as e:
            log("pat edit %r" % e)
        shot("07_muster")
        try:
            Gui.activeDocument().resetEdit()
        except Exception:
            pass
        pump(600)
        shot("08_loecher")

        # gruen
        try:
            pat.ViewObject.ShapeColor = (0.15, 0.65, 0.15)
        except Exception:
            pass
        Gui.Selection.clearSelection(); pump(400)
        view.viewIsometric(); view.fitAll(); pump(500)
        shot("09_gruen")

        # Gummiring
        Gui.runCommand("PartDesign_Body"); pump(1200)
        rubber_body = [o for o in doc.Objects if o.TypeId == "PartDesign::Body"][-1]
        rubber_body.Label = "Gummiring"
        gsk = rubber_body.newObject("Sketcher::SketchObject", "GummiProfil")
        gsk.Label = "Gummiprofil"
        gsk.AttachmentSupport = [(xz, "")]; gsk.MapMode = "FlatFace"
        doc.recompute(); pump(400)
        Gui.activeDocument().setEdit(gsk.Name); pump(600)
        gsk.addGeometry(Part.Circle(App.Vector(0, 23, 0), App.Vector(0, 0, 1), 2.2), False)
        gsk.addConstraint(Sketcher.Constraint("Radius", 0, 2.2))
        doc.recompute(); pump(400)
        view.viewFront(); view.fitAll(); pump(500)
        shot("10_gummi")
        Gui.activeDocument().resetEdit(); pump(600)
        grev = rubber_body.newObject("PartDesign::Revolution", "Gummi")
        grev.Label = "Gummi"
        grev.Profile = gsk
        grev.ReferenceAxis = (gsk, ["H_Axis"])
        grev.Angle = 360.0
        doc.recompute(); pump(700)
        try:
            gsk.ViewObject.Visibility = False
            grev.ViewObject.ShapeColor = (0.04, 0.04, 0.04)
        except Exception:
            pass
        Gui.Selection.clearSelection(); pump(400)
        view.setCameraType("Perspective"); view.viewIsometric(); view.fitAll(); pump(600)
        try:
            Gui.activeDocument().setEdit(grev.Name); pump(1400)
            shot("11_gummi_rev")
            Gui.activeDocument().resetEdit(); pump(600)
        except Exception as e:
            log("gummi rev %r" % e)
        view.viewIsometric(); view.fitAll(); pump(500)
        shot("12_fertig")

        # speichern
        doc.saveAs(TMP); pump(600)
        for a in mw.menuBar().actions():
            if a.text().replace("&", "").strip() == "Datei":
                menu = a.menu(); rect = mw.menuBar().actionGeometry(a)
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
