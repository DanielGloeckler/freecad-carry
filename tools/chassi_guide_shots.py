# -*- coding: utf-8 -*-
"""Erzeugt die Screenshots fuer die neue Chassi-Anleitung (FreeCAD 1.1, dunkles Theme).

Aufruf (Beispiel):
  freecad.exe -u <user.cfg> -s <system.cfg> tools/chassi_guide_shots.py
"""
import os, traceback
import FreeCAD as App
import Part, Sketcher
import FreeCADGui as Gui
from PySide import QtCore, QtGui, QtWidgets

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "assets", "chassi")
ICONS = os.path.join(OUT, "icons")
os.makedirs(OUT, exist_ok=True)
os.makedirs(ICONS, exist_ok=True)
LOG = os.path.join(OUT, "shots.log")
TMP = os.path.join(OUT, "_chassi_guide.FCStd")
open(LOG, "w", encoding="utf-8").close()

def log(m):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(str(m) + "\n")

def pump(ms=400):
    QtWidgets.QApplication.processEvents()
    QtCore.QThread.msleep(ms)
    QtWidgets.QApplication.processEvents()

def mainwin():
    return Gui.getMainWindow()

def tasks_widget():
    for d in mainwin().findChildren(QtWidgets.QDockWidget):
        if d.isVisible() and d.windowTitle() == "Aufgaben":
            return d.widget()
    return None

def model_widget():
    for d in mainwin().findChildren(QtWidgets.QDockWidget):
        if d.isVisible() and d.windowTitle() == "Modell":
            return d.widget()
    return None

def save_pm(pm, name):
    path = os.path.join(OUT, name + ".png")
    pm.save(path, "PNG")
    log("shot " + name + " %sx%s" % (pm.width(), pm.height()))

def mark_pm(pm, marks, scale=1.0):
    if not marks:
        return pm
    p = QtGui.QPainter(pm)
    p.setRenderHint(QtGui.QPainter.Antialiasing)
    for m in marks:
        x, y, r = m["x"] * scale, m["y"] * scale, m.get("r", 34) * scale
        pen = QtGui.QPen(QtGui.QColor(235, 45, 45), max(2.0, 2.4 * scale))
        pen.setCapStyle(QtCore.Qt.RoundCap)
        p.setPen(pen)
        p.setBrush(QtCore.Qt.NoBrush)
        if m.get("box"):
            p.drawRoundedRect(QtCore.QRectF(x, y, m["w"] * scale, m["h"] * scale), 6 * scale, 6 * scale)
        else:
            p.drawEllipse(QtCore.QPointF(x, y), r, r)
        if m.get("label"):
            p.setPen(QtGui.QPen(QtGui.QColor(235, 45, 45)))
            f = p.font(); f.setPointSizeF(max(8, 12 * scale)); f.setBold(True); p.setFont(f)
            p.drawText(QtCore.QPointF(x + r + 5 * scale, y - r + 2 * scale), m["label"])
    p.end()
    return pm

def canvas(name, obj=None, marks=None, pad=100, view=None, crop=None):
    v = view or Gui.activeDocument().activeView()
    Gui.updateGui(); pump(350)
    img = v.getViewer().grabFramebuffer()
    if crop is not None:
        r = QtCore.QRect(*[int(x) for x in crop])
        r = r.intersected(QtCore.QRect(0, 0, img.width(), img.height()))
        img = img.copy(r)
        if marks:
            offx, offy = r.x(), r.y()
            marks = [dict(m, x=m["x"] - offx, y=m["y"] - offy) for m in marks]
    elif obj is not None:
        try:
            bb = obj.Shape.BoundBox
            pts = []
            for xs in (bb.XMin, bb.XMax):
                for ys in (bb.YMin, bb.YMax):
                    for zs in (bb.ZMin, bb.ZMax):
                        q = v.getPointOnScreen(App.Vector(xs, ys, zs))
                        pts.append((q[0], q[1]))
            x0 = min(p[0] for p in pts) - pad
            y0 = min(p[1] for p in pts) - pad
            x1 = max(p[0] for p in pts) + pad
            y1 = max(p[1] for p in pts) + pad
            crop_r = QtCore.QRect(int(max(0, x0)), int(max(0, y0)),
                                  int(x1 - x0), int(y1 - y0))
            crop_r = crop_r.intersected(QtCore.QRect(0, 0, img.width(), img.height()))
            img = img.copy(crop_r)
            if marks:
                # marks are in framebuffer pixels; shift to crop coordinates
                offx, offy = crop_r.x(), crop_r.y()
                marks = [dict(m, x=m["x"] - offx, y=m["y"] - offy) for m in marks]
        except Exception as e:
            log("crop %s: %r" % (name, e))
    mark_pm(img, marks, 1.0)
    save_pm(img, name)

def point(v, x, y, z):
    q = v.getPointOnScreen(App.Vector(x, y, z))
    return q[0], q[1]

def panel(name, marks=None, crop=None):
    for d in mainwin().findChildren(QtWidgets.QDockWidget):
        if d.isVisible() and d.windowTitle() == "Aufgaben" and d.height() < 600:
            try:
                d.setMinimumHeight(600)
                d.resize(d.width(), 620)
                pump(350)
            except Exception:
                pass
    w = tasks_widget()
    if w is None:
        log("NO TASK PANEL " + name)
        return
    pm = w.grab()
    sc = pm.width() / float(w.width())
    if crop is not None:
        r = QtCore.QRect(*[int(v * sc) for v in crop])
        r = r.intersected(QtCore.QRect(0, 0, pm.width(), pm.height()))
        pm = pm.copy(r)
        if marks:
            marks = [dict(m, x=m["x"] - crop[0], y=m["y"] - crop[1]) for m in marks]
    mark_pm(pm, marks, sc)
    save_pm(pm, name)

def tree(name, marks=None, height=420):
    w = model_widget()
    if w is None:
        log("NO TREE " + name)
        return
    pm = w.grab()
    sc = pm.width() / float(w.width())
    if height and pm.height() > height * sc:
        pm = pm.copy(0, 0, pm.width(), int(height * sc))
    mark_pm(pm, marks, sc)
    save_pm(pm, name)

def select(obj, sub=None):
    Gui.Selection.clearSelection()
    if sub:
        Gui.Selection.addSelection(obj, sub)
    else:
        Gui.Selection.addSelection(obj)

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

def dump_icons():
    seen = set()
    for b in mainwin().findChildren(QtWidgets.QToolButton):
        try:
            if not b.isVisible():
                continue
            act = b.defaultAction()
            name = act.objectName() if act else ""
            if not name or name in seen:
                continue
            pm = b.icon().pixmap(64, 64)
            if pm.isNull() or pm.width() < 4:
                continue
            seen.add(name)
            pm.save(os.path.join(ICONS, name + ".png"), "PNG")
        except Exception:
            pass
    log("icons %d" % len(seen))

def run():
    try:
        mw = mainwin()
        mw.resize(1539, 844)
        Gui.runCommand("Std_New"); pump(900)
        Gui.activateWorkbench("PartDesignWorkbench"); pump(700)
        doc = App.activeDocument()
        doc.Label = "Chassi"
        view = Gui.activeDocument().activeView()
        view.setCameraType("Perspective")
        view.viewIsometric(); view.fitAll(); pump(400)

        # 01 - new document / overview
        pm = mw.grab()
        pm = pm.copy(0, 0, pm.width(), int(pm.height() * 0.18))
        save_pm(pm, "01_neues_dokument")

        # 02 - workbench selector
        pm = mw.grab()
        sc = pm.width() / float(mw.width())
        pm = pm.copy(int(270 * sc), int(18 * sc), int(330 * sc), int(46 * sc))
        mark_pm(pm, [{"x": 30, "y": 12, "r": 0, "box": True, "w": 250, "h": 34}], sc)
        save_pm(pm, "02_arbeitsbereich")

        # Body
        body = doc.addObject("PartDesign::Body", "Body")
        body.Label = "Chassi"
        doc.recompute(); pump(500)
        select(body)
        tree("03_koerper", height=260)

        # 04 - new sketch dialog
        Gui.Selection.clearSelection()
        try:
            Gui.runCommand("PartDesign_NewSketch")
            pump(1200)
            panel("04_neue_skizze", crop=(0, 0, 395, 200),
                  marks=[{"x": 18, "y": 55, "r": 0, "box": True, "w": 350, "h": 24}])
            wd = tasks_widget()
            if wd is not None:
                for b in wd.findChildren(QtWidgets.QPushButton):
                    if b.isVisible() and ("Schlie" in b.text() or "Abbrechen" in b.text()):
                        b.click(); pump(700); break
            else:
                Gui.activeDocument().resetEdit(); pump(500)
        except Exception as e:
            log("newsketch: %r" % e)
        # remove any sketch created by the command
        for o in list(doc.Objects):
            if o.TypeId == "Sketcher::SketchObject":
                doc.removeObject(o.Name)
        doc.recompute(); pump(300)

        # real sketch
        plane = [o for o in body.Origin.OriginFeatures if o.Name == "XY_Plane"][0]
        sk = body.newObject("Sketcher::SketchObject", "Sketch")
        sk.Label = "Chassi-Skizze"
        sk.AttachmentSupport = [(plane, "")]
        sk.MapMode = "FlatFace"
        doc.recompute()
        Gui.activeDocument().setEdit(sk.Name); pump(900)
        dump_icons()
        view.viewTop(); view.fitAll(); pump(500)

        add_rect(sk, 116, 70)
        doc.recompute(); view.fitAll(); pump(500)
        c1 = point(view, -58, -35, 0); c2 = point(view, 58, 35, 0)
        canvas("06_rechteck", sk, marks=[{"x": c1[0], "y": c1[1], "r": 26},
                                         {"x": c2[0], "y": c2[1], "r": 26}], pad=100)

        # Symmetry: mark two opposite corners and the origin
        sk.addConstraint(Sketcher.Constraint("Symmetric", 0, 1, 2, 1, -1, 1))
        doc.recompute(); view.fitAll(); pump(500)
        p1 = point(view, -58, -35, 0); p2 = point(view, 58, 35, 0); o = point(view, 0, 0, 0)
        canvas("07_symmetrie", sk, marks=[{"x": p1[0], "y": p1[1], "r": 28, "label": "1"},
                                          {"x": p2[0], "y": p2[1], "r": 28, "label": "2"},
                                          {"x": o[0], "y": o[1], "r": 30, "label": "3"}], pad=100)

        # dimensions
        sk.addConstraint(Sketcher.Constraint("Distance", 2, 116.0))
        sk.addConstraint(Sketcher.Constraint("Distance", 1, 70.0))
        doc.recompute(); view.fitAll(); pump(600)
        canvas("08_masse", sk, pad=120)

        # close sketch
        panel("09_skizze_schliessen", crop=(0, 0, 395, 64))
        Gui.activeDocument().resetEdit(); pump(700)

        # Pad
        pad = body.newObject("PartDesign::Pad", "Pad")
        pad.Label = "Platte"
        pad.Profile = sk
        pad.Length = 5.0
        doc.recompute(); pump(500)
        try:
            sk.ViewObject.Visibility = False
        except Exception:
            pass
        view.viewIsometric(); view.fitAll(); pump(500)
        Gui.activeDocument().setEdit(pad.Name); pump(1200)
        panel("10_aufpolstern", crop=(0, 0, 395, 260))
        Gui.activeDocument().resetEdit(); pump(700)
        canvas("11_platte", pad, pad=130)

        # Top face selected
        top = None
        for i, f in enumerate(pad.Shape.Faces):
            try:
                if f.Surface.__class__.__name__ == "Plane" and abs(f.normalAt(0, 0).z - 1) < 1e-6 and f.CenterOfMass.z > 4.9:
                    top = "Face%d" % (i + 1)
            except Exception:
                pass
        log("top face %s" % top)
        select(pad, top); pump(400)
        c = point(view, 0, 0, 5)
        canvas("12_flaeche", pad, marks=[{"x": c[0], "y": c[1], "r": 95, "label": "Oberseite"}], pad=110)

        # Hole sketch
        hs = body.newObject("Sketcher::SketchObject", "HoleSketch")
        hs.Label = "Loch-Skizze"
        hs.AttachmentSupport = [(pad, top)]
        hs.MapMode = "FlatFace"
        doc.recompute()
        Gui.Selection.clearSelection()
        Gui.activeDocument().setEdit(hs.Name); pump(800)
        dump_icons()
        view.setCameraType("Orthographic")
        view.viewTop(); view.fitAll(); pump(500)
        hs.addGeometry(Part.Circle(App.Vector(-48, 30, 0), App.Vector(0, 0, 1), 1.5), False)
        hs.addGeometry(Part.Point(App.Vector(-58, 35, 0)), True)
        hs.addConstraint(Sketcher.Constraint("Block", 1))
        hs.addConstraint(Sketcher.Constraint("DistanceX", 1, 1, 0, 3, 10.0))
        hs.addConstraint(Sketcher.Constraint("DistanceY", 0, 3, 1, 1, 5.0))
        hs.addConstraint(Sketcher.Constraint("Radius", 0, 1.5))
        doc.recompute(); pump(400)
        try:
            rm = view.getViewer().getSoRenderManager()
            cam = rm.getCamera()
            cam.height = 34.0
            cam.position = (-48.0, 25.0, 100.0)
            view.redraw(); pump(600)
        except Exception as e:
            log("cam: %r" % e)
        hc = point(view, -48, 30, 5)
        canvas("13_kreis", crop=(420, 0, 940, 500))
        panel("14_kreis_schliessen", crop=(0, 0, 395, 300))
        Gui.activeDocument().resetEdit(); pump(600)
        view.setCameraType("Perspective")

        # Pocket
        pk = body.newObject("PartDesign::Pocket", "Pocket")
        pk.Label = "Loch"
        pk.Profile = hs
        pk.Type = 1
        doc.recompute(); pump(500)
        try:
            hs.ViewObject.Visibility = False
        except Exception:
            pass
        view.viewIsometric(); view.fitAll(); pump(400)
        Gui.activeDocument().setEdit(pk.Name); pump(1200)
        panel("15_tasche", crop=(0, 0, 395, 220))
        Gui.activeDocument().resetEdit(); pump(600)
        canvas("16_ein_loch", pk, pad=130)

        select(pk); pump(300)
        tree("17_pocket_wahl", height=300)

        # --- MultiTransform (nur fuer die Dialog-Screenshots) ---
        mt = body.newObject("PartDesign::MultiTransform", "MultiTransform")
        mt.Label = "Mehrfach-Transformation"
        mt.Originals = [pk]
        mt.Shape = pk.Shape
        doc.recompute()
        lp1 = doc.addObject("PartDesign::LinearPattern", "LP1")
        lp1.Label = "Lineares Muster (9 x 96)"
        lp1.Originals = [pk]
        lp1.Direction = (body.Origin.OriginFeatures[0], [""])
        lp1.Length = 96.0
        lp1.Occurrences = 9
        body.addObject(lp1)
        doc.recompute()
        lp2 = doc.addObject("PartDesign::LinearPattern", "LP2")
        lp2.Label = "Lineares Muster (5 x 60)"
        lp2.Originals = [pk]
        lp2.Direction = (body.Origin.OriginFeatures[1], [""])
        lp2.Length = 60.0
        lp2.Occurrences = 5
        lp2.Reversed = True
        body.addObject(lp2)
        doc.recompute()
        mt.Transformations = [lp1, lp2]
        doc.recompute(); pump(500)
        view.viewIsometric(); view.fitAll(); pump(400)
        Gui.activeDocument().setEdit(mt.Name); pump(1400)
        panel("18_mtf", crop=(0, 0, 395, 440))
        try:
            btn = None
            for b in tasks_widget().findChildren(QtWidgets.QPushButton):
                if b.isVisible() and b.text().startswith("Formelement") and "hinzuf" in b.text():
                    btn = b; break
            if btn:
                btn.click(); pump(500)
                pop = QtWidgets.QApplication.activePopupWidget()
                if pop:
                    pop.grab().save(os.path.join(OUT, "18b_muster_menu.png"), "PNG")
                    log("shot 18b_muster_menu %sx%s" % (pop.width(), pop.height()))
                    pop.close(); pump(300)
        except Exception as e:
            log("menu: %r" % e)
        Gui.activeDocument().resetEdit(); pump(600)
        # Display-MT wieder entfernen
        try:
            doc.removeObject(mt.Name)
            doc.removeObject(lp1.Name)
            doc.removeObject(lp2.Name)
            doc.recompute(); pump(400)
        except Exception as e:
            log("remove mt: %r" % e)

        # --- endgueltiges 9x5-Muster (zwei Richtungen) ---
        lp = body.newObject("PartDesign::LinearPattern", "Pattern")
        lp.Label = "45 Löcher"
        lp.Originals = [pk]
        lp.Direction = (body.Origin.OriginFeatures[0], [""])
        lp.Length = 96.0
        lp.Occurrences = 9
        lp.Direction2 = (body.Origin.OriginFeatures[1], [""])
        lp.Length2 = 60.0
        lp.Occurrences2 = 5
        lp.Reversed2 = True
        doc.recompute(); pump(600)
        view.viewIsometric(); view.fitAll(); pump(500)
        canvas("22_45loecher", lp, pad=130)

        # Chamfer: wireframe + select all top circles
        try:
            view.setDrawStyle("Wireframe")
        except Exception:
            try:
                Gui.runCommand("Std_DrawStyleWireframe")
            except Exception:
                pass
        view.viewTop(); view.fitAll(); pump(600)
        edges = []
        # Nur die 8 Schraubenloecher senken: obere/untere Reihe, Spalten 1, 3, 7, 9
        want = [(-48, 30), (-24, 30), (24, 30), (48, 30),
                (-48, -30), (-24, -30), (24, -30), (48, -30)]
        for i, e in enumerate(lp.Shape.Edges):
            try:
                if e.Curve.TypeId == "Part::GeomCircle" and abs(e.Curve.Radius - 1.5) < 0.01 and abs(e.Curve.Center.z - 5.0) < 0.01:
                    c = e.Curve.Center
                    if any(abs(c.x - wx) < 0.6 and abs(c.y - wy) < 0.6 for wx, wy in want):
                        edges.append("Edge%d" % (i + 1))
            except Exception:
                pass
        log("Senkungskanten: %d" % len(edges))
        Gui.Selection.clearSelection()
        for en in edges:
            Gui.Selection.addSelection(lp, en)
        pump(500)
        canvas("23_senkung_auswahl", lp, pad=110)

        ch = body.newObject("PartDesign::Chamfer", "Chamfer")
        ch.Label = "Senkungen"
        ch.Base = (lp, edges)
        ch.Size = 1.5
        doc.recompute(); pump(700)
        Gui.activeDocument().setEdit(ch.Name); pump(1200)
        try:
            wd = tasks_widget()
            for sa in wd.findChildren(QtWidgets.QScrollArea):
                sa.verticalScrollBar().setValue(sa.verticalScrollBar().maximum())
            pump(500)
        except Exception as e:
            log("scroll: %r" % e)
        panel("24_senkung", crop=(0, 120, 395, 250))
        Gui.activeDocument().resetEdit(); pump(600)
        try:
            view.setDrawStyle("As is")
        except Exception:
            pass
        view.viewIsometric(); view.fitAll(); pump(500)
        canvas("25_senkung_fertig", ch, pad=130)

        # color red
        try:
            ch.ViewObject.ShapeColor = (0.85, 0.05, 0.05)
        except Exception:
            try:
                ch.ViewObject.ShapeColor = (0.85, 0.05, 0.05, 0.0)
            except Exception:
                pass
        Gui.Selection.clearSelection()
        view.viewIsometric(); view.fitAll(); pump(600)
        canvas("26_rot", ch, pad=110)

        # save menu
        doc.saveAs(TMP); pump(700)
        for a in mw.menuBar().actions():
            if a.text().replace("&", "").strip() == "Datei":
                menu = a.menu()
                rect = mw.menuBar().actionGeometry(a)
                menu.popup(mw.menuBar().mapToGlobal(rect.bottomLeft()))
                pump(500)
                pop = QtWidgets.QApplication.activePopupWidget()
                if pop:
                    pop.grab().save(os.path.join(OUT, "27_speichern.png"), "PNG")
                    log("shot 27_speichern %sx%s" % (pop.width(), pop.height()))
                    pop.close()
                break

        dump_icons()
        log("FERTIG")
    except Exception:
        log("FEHLER\n" + traceback.format_exc())
    finally:
        try:
            if App.activeDocument() and App.activeDocument().FileName == TMP:
                App.closeDocument(App.activeDocument().Name)
        except Exception:
            pass
        try:
            if os.path.exists(TMP):
                os.remove(TMP)
        except Exception:
            pass
        pump(300)
        QtCore.QTimer.singleShot(1000, QtWidgets.QApplication.quit)

QtCore.QTimer.singleShot(5000, run)
