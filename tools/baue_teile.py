# -*- coding: utf-8 -*-
"""Baut die Einzelteile fuer die Baugruppe und speichert sie als FCStd."""
import os, traceback, math
import FreeCAD as App
import Part
import FreeCADGui as Gui
from PySide import QtCore

OUT = r"D:\Temp\opencode\carry"
os.makedirs(OUT, exist_ok=True)
LOG = r"D:\Temp\opencode\baue_teile.log"
open(LOG, "w", encoding="utf-8").close()

def log(m):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(str(m) + "\n")

def color(obj, rgb):
    obj.ViewObject.ShapeColor = rgb

def run():
    try:
        # ---------------- Chassi ----------------
        d = App.newDocument("Chassi")
        box = Part.makeBox(116, 82, 5, App.Vector(-58, -41, 0))
        cut = []
        for i in range(9):
            x = -48 + i * 12
            for j in range(5):
                y = -30 + j * 15
                cut.append(Part.makeCylinder(1.5, 6, App.Vector(x, y, -0.5)))
        shape = box.cut(Part.makeCompound(cut))
        ch = d.addObject("Part::Feature", "Chassi")
        ch.Shape = shape
        d.recompute()
        color(ch, (0.75, 0.10, 0.10))
        d.saveAs(os.path.join(OUT, "Chassi.FCStd"))
        log("Chassi ok, holes %d" % len(shape.Faces))
        App.closeDocument(d.Name)

        # ---------------- Rad ----------------
        d = App.newDocument("Rad")
        pts = [(-10, 0), (10, 0), (10, 25), (8, 25), (8, 22), (-8, 22), (-8, 25), (-10, 25)]
        lines = []
        for i in range(8):
            p1 = App.Vector(pts[i][0], 0, pts[i][1])
            p2 = App.Vector(pts[(i + 1) % 8][0], 0, pts[(i + 1) % 8][1])
            lines.append(Part.LineSegment(p1, p2).toShape())
        wire = Part.Wire([e for e in lines])
        face = Part.Face(wire)
        body = face.revolve(App.Vector(0, 0, 0), App.Vector(1, 0, 0), 360)
        holes = []
        for k in range(6):
            a = math.radians(60 * k)
            holes.append(Part.makeCylinder(2.5, 30, App.Vector(15 * math.cos(a), -15, 15 * math.sin(a)),
                                           App.Vector(0, 1, 0)))
        body = body.cut(Part.makeCompound(holes))
        rad = d.addObject("Part::Feature", "Rad")
        rad.Shape = body
        d.recompute()
        color(rad, (0.25, 0.65, 0.20))
        # Gummiring
        ring = Part.makeTorus(23.0, 2.2, App.Vector(0, 0, 0), App.Vector(1, 0, 0))
        gummi = d.addObject("Part::Feature", "Gummiring")
        gummi.Shape = ring
        d.recompute()
        color(gummi, (0.05, 0.05, 0.05))
        d.saveAs(os.path.join(OUT, "Rad.FCStd"))
        log("Rad ok %r" % (body.BoundBox,))
        App.closeDocument(d.Name)

        # ---------------- Achse ----------------
        d = App.newDocument("Achse")
        cyl = Part.makeCylinder(2.0, 104.0, App.Vector(0, 0, 0), App.Vector(0, 1, 0))
        try:
            cyl = cyl.makeFillet(1.0, cyl.Edges)
        except Exception as e:
            log("achse fillet %r" % e)
        ach = d.addObject("Part::Feature", "Achse")
        ach.Shape = cyl
        d.recompute()
        color(ach, (0.55, 0.35, 0.12))
        d.saveAs(os.path.join(OUT, "Achse.FCStd"))
        log("Achse ok %r" % (cyl.BoundBox,))
        App.closeDocument(d.Name)

        log("FERTIG")
    except Exception:
        log("FEHLER\n" + traceback.format_exc())
    finally:
        QtCore.QTimer.singleShot(600, Gui.getMainWindow().close)

QtCore.QTimer.singleShot(1500, run)
