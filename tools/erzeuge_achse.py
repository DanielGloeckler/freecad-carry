# -*- coding: utf-8 -*-
"""Achse, Schraube und Mutter mit echten Screenshots."""
import os, traceback
import FreeCAD as App
import Part
import FreeCADGui as Gui
from PySide import QtCore, QtGui, QtWidgets

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "assets")
CARRY = r"D:\Temp\opencode\carry"
LOG = os.path.join(OUT, "achse.log")
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

def show_data_tab():
    mw = Gui.getMainWindow()
    for b in mw.findChildren(QtWidgets.QToolButton):
        if b.isVisible() and b.text().strip() == "Daten":
            b.click(); pump(400); return True
    for b in mw.findChildren(QtWidgets.QPushButton):
        if b.isVisible() and b.text().strip() == "Daten":
            b.click(); pump(400); return True
    return False

def expand_props():
    mw = Gui.getMainWindow()
    for tree in mw.findChildren(QtWidgets.QTreeWidget):
        if tree.isVisible() and tree.columnCount() >= 2 and tree.topLevelItemCount() > 0:
            text = tree.topLevelItem(0).text(0)
            if text in ("Basis", "Base", "Ansicht", "View"):
                tree.collapseAll()
                for i in range(tree.topLevelItemCount()):
                    it = tree.topLevelItem(i)
                    if it.text(0) in ("Parameters", "Parameter"):
                        it.setExpanded(True)
                        tree.scrollToItem(it)
                pump(300)


def widen_dock():
    mw = Gui.getMainWindow()
    for dw in mw.findChildren(QtWidgets.QDockWidget):
        if not dw.isVisible():
            continue
        t = dw.windowTitle()
        if any(k in t for k in ("Modell", "Model", "Eigenschaften", "Property", "Combo")):
            dw.setMinimumWidth(330)
            try:
                mw.resizeDocks([dw], [330], QtCore.Qt.Horizontal)
            except Exception as e:
                log("resize %r" % e)
            pump(300)

def file_menu(name):
    mw = Gui.getMainWindow()
    for a in mw.menuBar().actions():
        if a.text().replace("&", "").strip() == "Datei":
            menu = a.menu(); rect = mw.menuBar().actionGeometry(a)
            menu.popup(mw.menuBar().mapToGlobal(rect.bottomLeft()))
            QtWidgets.QApplication.processEvents(); pump(500)
            pop = QtWidgets.QApplication.activePopupWidget()
            if pop:
                shot(name, pop); pop.close()
            else:
                shot(name)
            return

def run():
    try:
        mw = Gui.getMainWindow(); mw.resize(1500, 844); mw.move(20, 20); mw.raise_(); pump(700)
        dlg = QtWidgets.QApplication.activeModalWidget()
        if dlg and "DocumentRecovery" in dlg.objectName(): dlg.reject(); pump(400)

        Gui.runCommand("Std_New"); pump(900)
        Gui.activateWorkbench("PartDesignWorkbench"); pump(600)
        doc = App.activeDocument(); doc.Label = "Achse"
        Gui.runCommand("PartDesign_Body"); pump(1000)
        body = [o for o in doc.Objects if o.TypeId == "PartDesign::Body"][-1]
        body.Label = "Achse"
        Gui.Selection.clearSelection(); pump(300)
        view = Gui.activeDocument().activeView()

        cyl = body.newObject("PartDesign::AdditiveCylinder", "Zylinder")
        cyl.Label = "Achse"
        cyl.Radius = 2.0
        cyl.Height = 104.0
        doc.recompute(); pump(600)
        view.setCameraType("Perspective"); view.viewIsometric(); view.fitAll(); pump(400)
        Gui.activeDocument().setEdit(cyl.Name); pump(1200)
        shot("ach_01_zylinder")
        Gui.activeDocument().resetEdit(); pump(600)

        fil = body.newObject("PartDesign::Fillet", "Abrundung")
        fil.Label = "Kanten abgerundet"
        fil.Base = (cyl, ["Edge2", "Edge3"])
        fil.Radius = 1.0
        try:
            doc.recompute(); pump(600)
        except Exception as e:
            log("fillet recompute %r" % e)
        view.viewIsometric(); view.fitAll(); pump(400)
        Gui.activeDocument().setEdit(fil.Name); pump(1200)
        shot("ach_02_abrunden")
        Gui.activeDocument().resetEdit(); pump(600)

        try:
            fil.ViewObject.ShapeColor = (0.55, 0.35, 0.12)
        except Exception:
            body.ViewObject.ShapeColor = (0.55, 0.35, 0.12)
        view.viewIsometric(); view.fitAll(); pump(500)
        shot("ach_03_braun")

        doc.saveAs(os.path.join(CARRY, "Achse.FCStd")); pump(600)
        file_menu("ach_04_speichern")
        App.closeDocument(doc.Name); pump(600)

        # ---------- Werkzeuge-Menue (Addon Manager) ----------
        for a in mw.menuBar().actions():
            if a.text().replace("&", "").strip() in ("Werkzeuge", "Tools"):
                menu = a.menu(); rect = mw.menuBar().actionGeometry(a)
                menu.popup(mw.menuBar().mapToGlobal(rect.bottomLeft()))
                QtWidgets.QApplication.processEvents(); pump(600)
                pop = QtWidgets.QApplication.activePopupWidget()
                if pop:
                    shot("ach_05_addon", pop); pop.close()
                else:
                    shot("ach_05_addon")
                break

        # ---------- Fasteners ----------
        Gui.runCommand("Std_New"); pump(800)
        Gui.activateWorkbench("FastenersWorkbench"); pump(1200)
        doc2 = App.activeDocument(); doc2.Label = "Schraube"
        view = Gui.activeDocument().activeView()
        view.setCameraType("Perspective"); view.viewIsometric(); view.fitAll(); pump(400)
        shot("ach_06_fasteners")

        Gui.runCommand("FSISO7046"); pump(1600)
        s = [o for o in doc2.Objects if o.TypeId == "Part::FeaturePython"][-1]
        log("screw obj %s" % s.Name)
        s.Diameter = "M3"
        s.Length = "Custom"
        s.LengthCustom = 20.0
        s.Thread = True
        doc2.recompute(); pump(800)
        s.Label = "Schraube M3x20"
        try:
            s.ViewObject.Visibility = True
        except Exception as e:
            log("vis schraube %r" % e)
        Gui.updateGui(); pump(400)
        view.viewIsometric(); Gui.SendMsgToActiveView("ViewFit"); view.fitAll(); pump(600)
        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(s)
        widen_dock()
        show_data_tab(); pump(400)
        expand_props()
        shot("ach_07_schraube")
        doc2.saveAs(os.path.join(CARRY, "Schraube M3.FCStd")); pump(500)

        # ---------- Mutter ----------
        Gui.runCommand("Std_New"); pump(800)
        doc3 = App.activeDocument(); doc3.Label = "Mutter"
        Gui.runCommand("FSISO4035"); pump(1600)
        n = [o for o in doc3.Objects if o.TypeId == "Part::FeaturePython"][-1]
        log("nut obj %s" % n.Name)
        n.Diameter = "M3"
        doc3.recompute(); pump(800)
        n.Label = "Mutter M3"
        try:
            n.ViewObject.Visibility = True
        except Exception as e:
            log("vis mutter %r" % e)
        view = Gui.activeDocument().activeView()
        view.setCameraType("Perspective"); view.viewIsometric(); Gui.SendMsgToActiveView("ViewFit"); view.fitAll(); pump(600)
        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(n)
        widen_dock()
        show_data_tab(); pump(400)
        expand_props()
        shot("ach_08_mutter")
        doc3.saveAs(os.path.join(CARRY, "Mutter M3.FCStd")); pump(500)
        App.closeDocument(doc3.Name); pump(400)

        # ---------- Uebersicht ----------
        doc4 = App.newDocument("Teile")
        teile = [("Achse.FCStd", "Kanten abgerundet", (0, 0, 0), True),
                 ("Schraube M3.FCStd", "Schraube M3x20", (20, -25, 22), True),
                 ("Mutter M3.FCStd", "Mutter M3", (30, -25, 2), True)]
        for fname, label, pos, _ in teile:
            src = App.openDocument(os.path.join(CARRY, fname))
            shape = None; col = None
            for o in src.Objects:
                if o.Label == label and hasattr(o, "Shape") and o.Shape.Volume > 0:
                    shape = o.Shape.copy()
                    try:
                        col = o.ViewObject.ShapeColor
                    except Exception:
                        pass
            App.closeDocument(src.Name); pump(200)
            if shape is None:
                log("nicht gefunden: %s" % label)
                continue
            obj = doc4.addObject("Part::Feature", label)
            obj.Shape = shape
            if label == "Kanten abgerundet":
                obj.Placement.Rotation = App.Rotation(App.Vector(0, 1, 0), 90)
            obj.Placement.Base = App.Vector(*pos)
            doc4.recompute()
            if col:
                try:
                    obj.ViewObject.ShapeColor = col
                except Exception:
                    pass
        view4 = Gui.activeDocument().activeView()
        view4.viewIsometric(); Gui.SendMsgToActiveView("ViewFit"); view4.fitAll(); pump(700)
        shot("ach_09_teile")
        log("FERTIG")
    except Exception:
        log("FEHLER\n" + traceback.format_exc())
    finally:
        QtCore.QTimer.singleShot(1200, QtWidgets.QApplication.quit)

QtCore.QTimer.singleShot(2500, run)
