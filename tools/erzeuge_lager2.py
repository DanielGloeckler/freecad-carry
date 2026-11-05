# -*- coding: utf-8 -*-
"""Radlager (Bogenform) mit echten Screenshots und FCStd fuer die Baugruppe."""
import os, traceback, math
import FreeCAD as App
import Part, Sketcher
import FreeCADGui as Gui
from PySide import QtCore, QtGui, QtWidgets

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "assets")
LOG = os.path.join(OUT, "lager2.log")
CARRY = r"D:\Temp\opencode\carry"
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

def shot(name, overlay=None):
    hide_report(); Gui.updateGui(); pump(400)
    mw = Gui.getMainWindow(); pm = mw.grab()
    if overlay is not None:
        try:
            om = overlay.grab()
            pos = mw.mapFromGlobal(overlay.geometry().topLeft()) if overlay.isWindow() else mw.mapFromGlobal(overlay.mapToGlobal(QtCore.QPoint(0,0)))
            p = QtGui.QPainter(pm); p.drawPixmap(pos, om); p.end()
        except Exception as e: log("overlay %r" % e)
    if pm.width() > WIDTH: pm = pm.scaledToWidth(WIDTH, QtCore.Qt.SmoothTransformation)
    pm.save(os.path.join(OUT, name + ".jpg"), "JPG", 88)
    log("shot " + name)

def scale_check(name):
    pass

def loc(sk, gx, gy, gz):
    return sk.Placement.inverse().multVec(App.Vector(gx, gy, gz))

def _watchdog():
    os._exit(0)

def run():
    try:
        import threading
        threading.Timer(90, _watchdog).start()
        mw = Gui.getMainWindow(); mw.resize(1500, 844); mw.move(20, 20); mw.raise_(); pump(700)
        dlg = QtWidgets.QApplication.activeModalWidget()
        if dlg and "DocumentRecovery" in dlg.objectName(): dlg.reject(); pump(400)

        Gui.runCommand("Std_New"); pump(900)
        Gui.activateWorkbench("PartDesignWorkbench"); pump(700)
        doc = App.activeDocument(); doc.Label = "Radlager"
        Gui.runCommand("PartDesign_Body"); pump(1200)
        body = [o for o in doc.Objects if o.TypeId == "PartDesign::Body"][-1]
        body.Label = "Radlager"
        Gui.Selection.clearSelection(); pump(400)

        xz = body.Origin.OriginFeatures[4]
        view = Gui.activeDocument().activeView()
        view.setCameraType("Orthographic")

        # ---------- Profil ----------
        sk = body.newObject("Sketcher::SketchObject", "Profil")
        sk.Label = "Halterprofil"
        sk.AttachmentSupport = [(xz, "")]; sk.MapMode = "FlatFace"
        doc.recompute()
        Gui.activeDocument().setEdit(sk.Name); pump(600)
        view.viewFront(); pump(300)

        a = math.sqrt(50.0)   # 7.0711
        p = [(0.0, 0.0)]
        segs = [
            ("L", (-20, 0), (20, 0)),
            ("L", (20, 0), (20, 5)),
            ("A", (10, 5), 10.0, 0.0, 45.0),
            ("L", (20 - (10 - a), 5 + a), (a, 15 + a)),
            ("A", (0, 15), 10.0, 45.0, 135.0),
            ("L", (-a, 15 + a), (-20 + (10 - a), 5 + a)),
            ("A", (-10, 5), 10.0, 135.0, 180.0),
            ("L", (-20, 5), (-20, 0)),
        ]
        for s in segs:
            if s[0] == "L":
                sk.addGeometry(Part.LineSegment(App.Vector(s[1][0], s[1][1], 0),
                                                App.Vector(s[2][0], s[2][1], 0)), False)
            else:
                c = Part.Circle(App.Vector(s[1][0], s[1][1], 0), App.Vector(0, 0, 1), s[2])
                sk.addGeometry(Part.ArcOfCircle(c, math.radians(s[3]), math.radians(s[4])), False)
        for i in range(8):
            sk.addConstraint(Sketcher.Constraint("Coincident", i, 2, (i + 1) % 8, 1))
        for gi in (0,):
            sk.addConstraint(Sketcher.Constraint("Horizontal", gi))
        for gi in (1, 7):
            sk.addConstraint(Sketcher.Constraint("Vertical", gi))
        doc.recompute(); pump(400)
        view.fitAll(); pump(500)
        shot("la2_01_profil")

        # ---------- Bemaßung ----------
        def tryc(c, txt):
            log("c+ " + txt)
            try:
                sk.addConstraint(c)
            except Exception as e:
                log("constraint %s: %r" % (txt, e))
            log("c- " + txt)

        def dim(c, txt):
            b0 = sk.Shape.BoundBox
            log("c+ " + txt)
            idx = sk.addConstraint(c)
            doc.recompute()
            b1 = sk.Shape.BoundBox
            moved = (abs(b0.XLength - b1.XLength) > 0.3 or abs(b0.YLength - b1.YLength) > 0.3
                     or abs(b0.Center.x - b1.Center.x) > 0.3 or abs(b0.Center.y - b1.Center.y) > 0.3)
            if moved:
                sk.setDriving(idx, False)
                doc.recompute()
                log("   -> Referenzmass (Skizze haette sich verschoben)")
            log("c- " + txt)

        doc.recompute(); pump(600)
        log("dof %r" % sk.FullyConstrained)
        view.fitAll(); pump(500)
        shot("la2_02_bemassung")

        Gui.activeDocument().resetEdit(); pump(700)
        pad = body.newObject("PartDesign::Pad", "Pad")
        pad.Label = "Radlager"
        pad.Profile = sk
        pad.Length = 10.0
        pad.Midplane = True
        doc.recompute(); pump(700)
        try: sk.ViewObject.Visibility = False
        except Exception: pass
        view.setCameraType("Perspective"); view.viewIsometric(); view.fitAll(); pump(500)
        try:
            Gui.activeDocument().setEdit(pad.Name); pump(1300)
            for sb in mw.findChildren(QtWidgets.QDoubleSpinBox):
                if sb.isVisible() and abs(sb.value()) < 0.01:
                    sb.setValue(10.0); pump(200); break
            shot("la2_03_polstern")
            Gui.activeDocument().resetEdit(); pump(600)
        except Exception as e:
            log("pad edit %r" % e)
        shot("la2_04_koerper")

        # ---------- Bohrung ----------
        face = None
        for i, f in enumerate(pad.Shape.Faces):
            n = f.normalAt(0, 0)
            if abs(n.y + 1) < 0.01 and f.Area > 300:
                face = "Face%d" % (i + 1); break
        log("front face %r" % face)
        hs = body.newObject("Sketcher::SketchObject", "Bohrung")
        hs.Label = "Bohrung"
        hs.AttachmentSupport = [(pad, face)]; hs.MapMode = "FlatFace"
        doc.recompute(); pump(400)
        Gui.activeDocument().setEdit(hs.Name); pump(500)
        c = loc(hs, 0, -5, 15)
        hs.addGeometry(Part.Circle(App.Vector(c.x, c.y, 0), App.Vector(0, 0, 1), 2.25), False)
        hs.addConstraint(Sketcher.Constraint("Radius", 0, 2.25))
        doc.recompute(); pump(400)
        view.viewFront(); view.fitAll(); pump(500)
        shot("la2_05_bohrung")
        Gui.activeDocument().resetEdit(); pump(600)
        hp = body.newObject("PartDesign::Pocket", "Bohrung")
        hp.Profile = hs; hp.Type = 1
        doc.recompute(); pump(700)
        try: hs.ViewObject.Visibility = False
        except Exception: pass
        view.viewIsometric(); view.fitAll(); pump(500)
        shot("la2_06_bohrung2")

        # ---------- Montagebohrungen ----------
        bface = None
        for i, f in enumerate(pad.Shape.Faces):
            n = f.normalAt(0, 0)
            if abs(n.z + 1) < 0.01 and f.Area > 200:
                bface = "Face%d" % (i + 1); break
        log("bottom face %r" % bface)
        ms = body.newObject("Sketcher::SketchObject", "Montage")
        ms.Label = "Montagebohrungen"
        ms.AttachmentSupport = [(pad, bface)]; ms.MapMode = "FlatFace"
        doc.recompute(); pump(400)
        Gui.activeDocument().setEdit(ms.Name); pump(500)
        pts = []
        for sx in (-1, 1):
            q = loc(ms, 12 * sx, 0, 0)
            pts.append(q)
            ms.addGeometry(Part.Circle(App.Vector(q.x, q.y, 0), App.Vector(0, 0, 1), 1.75), False)
        ms.addConstraint(Sketcher.Constraint("Radius", 0, 1.75))
        ms.addConstraint(Sketcher.Constraint("Radius", 1, 1.75))
        doc.recompute(); pump(400)
        view.viewBottom(); view.fitAll(); pump(500)
        shot("la2_07_montage")
        Gui.activeDocument().resetEdit(); pump(600)
        mp = body.newObject("PartDesign::Pocket", "Montagebohrung")
        mp.Profile = ms; mp.Type = 1
        doc.recompute(); pump(700)
        try: ms.ViewObject.Visibility = False
        except Exception: pass
        view.viewIsometric(); view.fitAll(); pump(500)
        shot("la2_08_montage2")

        # ---------- Sechskant-Vertiefungen ----------
        ns = body.newObject("Sketcher::SketchObject", "Muttern")
        ns.Label = "Mutternvertiefungen"
        ns.AttachmentSupport = [(pad, bface)]; ns.MapMode = "FlatFace"
        doc.recompute(); pump(400)
        Gui.activeDocument().setEdit(ns.Name); pump(500)
        for q in pts:
            hexpts = []
            for k in range(6):
                ang = math.radians(30 + 60 * k)
                hexpts.append(App.Vector(q.x + 3.25 * math.cos(ang), q.y + 3.25 * math.sin(ang), 0))
            for k in range(6):
                ns.addGeometry(Part.LineSegment(hexpts[k], hexpts[(k + 1) % 6]), False)
            base = ns.GeometryCount - 6
            for k in range(6):
                ns.addConstraint(Sketcher.Constraint("Coincident", base + k, 2, base + (k + 1) % 6, 1))
        doc.recompute(); pump(400)
        view.viewBottom(); view.fitAll(); pump(500)
        shot("la2_09_muttern")
        Gui.activeDocument().resetEdit(); pump(600)
        np_ = body.newObject("PartDesign::Pocket", "Mutternvertiefung")
        np_.Profile = ns; np_.Type = 0; np_.Length = 12.0; np_.Reversed = False
        doc.recompute(); pump(700)
        try: ns.ViewObject.Visibility = False
        except Exception: pass
        log("pockets: %r" % [o.Name for o in body.Group])
        # pruefen ob Vertiefung in die richtige Richtung geht
        log("vol %.1f" % pad.Shape.Volume)
        view.viewIsometric(); view.fitAll(); pump(500)
        shot("la2_10_fertig")

        # Farbe
        try: pad.ViewObject.ShapeColor = (0.62, 0.66, 0.70)
        except Exception: pass
        view.viewIsometric(); view.fitAll(); pump(500)
        shot("la2_11_farbe")
        view.viewBottom(); view.fitAll(); pump(500)
        shot("la2_13_unten")
        view.viewIsometric(); view.fitAll(); pump(400)

        # speichern
        doc.saveAs(os.path.join(CARRY, "Radlager.FCStd")); pump(500)
        for a in mw.menuBar().actions():
            if a.text().replace("&", "").strip() == "Datei":
                menu = a.menu(); rect = mw.menuBar().actionGeometry(a)
                menu.popup(mw.menuBar().mapToGlobal(rect.bottomLeft()))
                QtWidgets.QApplication.processEvents(); pump(500)
                pop = QtWidgets.QApplication.activePopupWidget()
                if pop:
                    shot("la2_12_speichern", pop); pop.close()
                else:
                    shot("la2_12_speichern")
                break
        log("FERTIG")
    except Exception:
        log("FEHLER\n" + traceback.format_exc())
    finally:
        QtCore.QTimer.singleShot(1200, QtWidgets.QApplication.quit)

QtCore.QTimer.singleShot(2500, run)
