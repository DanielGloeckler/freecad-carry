# -*- coding: utf-8 -*-
"""Erzeugt die Screenshots fuer die Rad-Anleitung (FreeCAD 1.1, dunkles Theme)."""
import os, traceback
import FreeCAD as App
import Part, Sketcher
import FreeCADGui as Gui
from PySide import QtCore, QtGui, QtWidgets

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "assets", "rad")
os.makedirs(OUT, exist_ok=True)
LOG = os.path.join(OUT, "shots.log")
TMP = os.path.join(OUT, "_rad_guide.FCStd")
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
            p.drawRoundedRect(QtCore.QRectF(x, y, m.get("w", 100) * scale, m.get("h", 24) * scale), 6 * scale, 6 * scale)
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
            crop_r = QtCore.QRect(int(max(0, x0)), int(max(0, y0)), int(x1 - x0), int(y1 - y0))
            crop_r = crop_r.intersected(QtCore.QRect(0, 0, img.width(), img.height()))
            img = img.copy(crop_r)
            if marks:
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
                d.setMinimumHeight(600); d.resize(d.width(), 620); pump(350)
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

def run():
    try:
        mw = mainwin()
        mw.resize(1539, 844)
        Gui.runCommand("Std_New"); pump(900)
        Gui.activateWorkbench("PartDesignWorkbench"); pump(700)
        doc = App.activeDocument(); doc.Label = "Rad"
        body = doc.addObject("PartDesign::Body", "Body"); body.Label = "Rad"
        doc.recompute(); pump(400)
        view = Gui.activeDocument().activeView()
        try:
            select(body); tree("00_koerper", height=260)
        except Exception as e:
            log("tree %r" % e)
        xz = body.Origin.OriginFeatures[4]
        yz = body.Origin.OriginFeatures[5]

        # 01 new document / workbench
        pm = mw.grab()
        sc = pm.width() / float(mw.width())
        pm = pm.copy(int(270 * sc), int(18 * sc), int(330 * sc), int(46 * sc))
        save_pm(pm, "01_arbeitsbereich")

        # 02 profile sketch
        sk = body.newObject("Sketcher::SketchObject", "Profil")
        sk.Label = "Profil"
        sk.AttachmentSupport = [(xz, "")]; sk.MapMode = "FlatFace"
        doc.recompute()
        Gui.activeDocument().setEdit(sk.Name); pump(800)
        dump = None
        view.setCameraType("Orthographic"); view.viewFront(); view.fitAll(); pump(500)
        pts = [(2.0,17.5),(3.0,17.5),(6.0,17.5),(7.0,17.5),(7.0,2.0),(6.0,2.0),(6.0,0.0),(3.0,0.0),(3.0,2.0),(0.0,2.0),(0.0,4.0),(2.0,4.0)]
        # Linien: A-L, dann Bogen L-K, dann K-J, J-I, I-H, H-G, G-F, F-E, E-D, D-C, C-B, B-A
        line_idx = [(0,1),(2,3),(3,4),(4,5),(5,6),(6,7),(7,8),(8,9),(9,10),(10,11),(11,0)]
        # zuerst A-L
        sk.addGeometry(Part.LineSegment(App.Vector(pts[0][0], pts[0][1], 0),
                                        App.Vector(pts[1][0], pts[1][1], 0)), False)
        # Bogen L-K (R1,75), Mittelpunkt oberhalb der Oberflaeche
        arc = Part.ArcOfCircle(App.Vector(3.0,17.5,0), App.Vector(4.5,16.651,0), App.Vector(6.0,17.5,0))
        sk.addGeometry(arc, False)
        for a,b in line_idx[1:]:
            sk.addGeometry(Part.LineSegment(App.Vector(pts[a][0], pts[a][1], 0),
                                            App.Vector(pts[b][0], pts[b][1], 0)), False)
        # Reihenfolge: 0 A-L, 1 Bogen, 2 K-J, 3 J-I, 4 I-H, 5 H-G, 6 G-F, 7 F-E, 8 E-D, 9 D-C, 10 C-B, 11 B-A
        for i in range(12):
            sk.addConstraint(Sketcher.Constraint("Coincident", i, 2, (i+1)%12, 1))
        for i in (0,2,4,6,8,10):
            sk.addConstraint(Sketcher.Constraint("Horizontal", i))
        for i in (3,5,7,9,11):
            sk.addConstraint(Sketcher.Constraint("Vertical", i))
        doc.recompute(); view.fitAll(); pump(500)
        canvas("02_profil", sk, pad=110)

        sk.addConstraint(Sketcher.Constraint("Radius", 1, 1.75))
        canvas("03_masse", sk, pad=130)
        panel("04_skizze_schliessen", crop=(0,0,395,70))
        Gui.activeDocument().resetEdit(); pump(600)

        rev = body.newObject("PartDesign::Revolution", "Radkörper")
        rev.Label = "Radkörper"
        rev.Profile = sk
        rev.ReferenceAxis = (sk, ["H_Axis"])
        rev.Angle = 360.0
        doc.recompute(); pump(600)
        try: sk.ViewObject.Visibility = False
        except Exception: pass
        view.setCameraType("Perspective"); view.viewIsometric(); view.fitAll(); pump(500)
        Gui.activeDocument().setEdit(rev.Name); pump(1200)
        panel("05_revolution", crop=(0,0,395,300))
        Gui.activeDocument().resetEdit(); pump(600)
        canvas("06_rad", rev, pad=110)

        # center bore
        bore = body.newObject("Sketcher::SketchObject", "Bohrung")
        bore.Label = "Bohrung"
        bore.AttachmentSupport = [(yz, "")]; bore.MapMode = "FlatFace"
        doc.recompute(); pump(400)
        Gui.activeDocument().setEdit(bore.Name); pump(700)
        bore.addGeometry(Part.Circle(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 4.0), False)
        bore.addConstraint(Sketcher.Constraint("Radius", 0, 4.0))
        doc.recompute(); view.setCameraType("Orthographic"); view.viewRight(); view.fitAll(); pump(500)
        try:
            cam = view.getViewer().getSoRenderManager().getCamera(); cam.height = 62.0; view.redraw(); pump(500)
        except Exception as e: log("cam07 %r" % e)
        canvas("07_bohrung_skizze", rev, pad=110)
        Gui.activeDocument().resetEdit(); pump(600)
        bp = body.newObject("PartDesign::Pocket", "BohrungTasche")
        bp.Label = "Achsbohrung"
        bp.Profile = bore; bp.Type = 0; bp.Length = 20.0; bp.Midplane = True
        doc.recompute(); pump(600)
        try: bore.ViewObject.Visibility = False
        except Exception: pass
        view.viewIsometric(); view.fitAll(); pump(400)
        canvas("08_bohrung", bp, pad=110)

        # hole + polar pattern
        hole = body.newObject("Sketcher::SketchObject", "Loch")
        hole.Label = "Loch"
        hole.AttachmentSupport = [(yz, "")]; hole.MapMode = "FlatFace"
        doc.recompute(); pump(400)
        Gui.activeDocument().setEdit(hole.Name); pump(700)
        hole.addGeometry(Part.Circle(App.Vector(0, 10, 0), App.Vector(0, 0, 1), 2.5), False)
        hole.addConstraint(Sketcher.Constraint("Radius", 0, 2.5))
        doc.recompute(); view.setCameraType("Orthographic"); view.viewRight(); view.fitAll(); pump(500)
        try:
            cam = view.getViewer().getSoRenderManager().getCamera(); cam.height = 62.0; view.redraw(); pump(500)
        except Exception as e: log("cam09 %r" % e)
        canvas("09_loch_skizze", rev, pad=110)
        Gui.activeDocument().resetEdit(); pump(600)
        hp = body.newObject("PartDesign::Pocket", "LochTasche")
        hp.Label = "Loch"
        hp.Profile = hole; hp.Type = 0; hp.Length = 20.0; hp.Midplane = True
        doc.recompute(); pump(600)
        try: hole.ViewObject.Visibility = False
        except Exception: pass
        view.viewIsometric(); view.fitAll(); pump(400)
        canvas("10_ein_loch", hp, pad=110)

        pat = body.newObject("PartDesign::PolarPattern", "SechsLöcher")
        pat.Label = "6 Löcher"
        pat.Originals = [hp]
        pat.Axis = (body.Origin.OriginFeatures[0], [""])
        pat.Angle = 360.0; pat.Occurrences = 6
        doc.recompute(); pump(600)
        view.viewIsometric(); view.fitAll(); pump(500)
        Gui.activeDocument().setEdit(pat.Name); pump(1200)
        panel("11_muster", crop=(0,0,395,500))
        Gui.activeDocument().resetEdit(); pump(600)
        canvas("12_loecher", pat, pad=110)

        # green
        try: pat.ViewObject.ShapeColor = (0.15, 0.65, 0.15)
        except Exception: pass
        Gui.Selection.clearSelection(); view.viewIsometric(); view.fitAll(); pump(500)
        canvas("13_gruen", pat, pad=110)

        # gummi body
        Gui.runCommand("PartDesign_Body"); pump(1100)
        rubber = [o for o in doc.Objects if o.TypeId == "PartDesign::Body"][-1]
        rubber.Label = "Gummiring"
        try: body.ViewObject.Visibility = False
        except Exception: pass
        gsk = rubber.newObject("Sketcher::SketchObject", "GummiProfil")
        gsk.Label = "Gummiprofil"
        gsk.AttachmentSupport = [(xz, "")]; gsk.MapMode = "FlatFace"
        doc.recompute(); pump(400)
        Gui.activeDocument().setEdit(gsk.Name); pump(700)
        gsk.addGeometry(Part.Circle(App.Vector(0, 18.5, 0), App.Vector(0, 0, 1), 1.75), False)
        gsk.addConstraint(Sketcher.Constraint("Radius", 0, 1.75))
        doc.recompute(); view.setCameraType("Orthographic"); view.viewFront(); view.fitAll(); pump(500)
        canvas("14_gummi_profil", gsk, pad=110)
        Gui.activeDocument().resetEdit(); pump(600)
        grev = rubber.newObject("PartDesign::Revolution", "Gummi")
        grev.Label = "Gummi"
        grev.Profile = gsk; grev.ReferenceAxis = (gsk, ["H_Axis"]); grev.Angle = 360.0
        doc.recompute(); pump(600)
        try:
            gsk.ViewObject.Visibility = False
            grev.ViewObject.ShapeColor = (0.04, 0.04, 0.04)
        except Exception: pass
        try: body.ViewObject.Visibility = True
        except Exception: pass
        Gui.Selection.clearSelection(); view.setCameraType("Perspective"); view.viewRight(); view.fitAll(); pump(600)
        canvas("15_gummi", grev, pad=110)

        # final compound
        comp = doc.addObject("Part::Compound", "Ansicht")
        comp.Links = [body, rubber]
        doc.recompute(); pump(400)
        try: comp.ViewObject.Visibility = False
        except Exception: pass
        try:
            body.ViewObject.Visibility = True
            rubber.ViewObject.Visibility = True
        except Exception: pass
        view.viewRight(); view.fitAll(); pump(500)
        canvas("16_fertig", comp, pad=120)
        try: doc.removeObject(comp.Name)
        except Exception: pass

        # save menu
        doc.saveAs(TMP); pump(600)
        for a in mw.menuBar().actions():
            if a.text().replace("&", "").strip() == "Datei":
                menu = a.menu(); rect = mw.menuBar().actionGeometry(a)
                menu.popup(mw.menuBar().mapToGlobal(rect.bottomLeft()))
                pump(500)
                pop = QtWidgets.QApplication.activePopupWidget()
                if pop:
                    pop.grab().save(os.path.join(OUT, "17_speichern.png"), "PNG")
                    log("shot 17_speichern %sx%s" % (pop.width(), pop.height()))
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
            if os.path.exists(TMP): os.remove(TMP)
        except Exception:
            pass
        pump(300)
        QtCore.QTimer.singleShot(1000, QtWidgets.QApplication.quit)

def dump_icons():
    ICONS = os.path.join(OUT, "icons")
    os.makedirs(ICONS, exist_ok=True)
    seen = set()
    for b in mainwin().findChildren(QtWidgets.QToolButton):
        try:
            if not b.isVisible(): continue
            act = b.defaultAction(); name = act.objectName() if act else ""
            if not name or name in seen: continue
            pm = b.icon().pixmap(64, 64)
            if pm.isNull() or pm.width() < 4: continue
            seen.add(name); pm.save(os.path.join(ICONS, name + ".png"), "PNG")
        except Exception:
            pass
    log("icons %d" % len(seen))

QtCore.QTimer.singleShot(5000, run)







