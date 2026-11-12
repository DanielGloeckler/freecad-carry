/* Zusatzinfos und Statusbilder für die Stufe „Viel“ */
(function () {
  'use strict';

  var DEEP = {
    "skizze-0": {status:["assets/chassi/03_koerper.png","Der Körper steht im Modellbaum."], more:"<p>Falls die Startseite erscheint: <b>Neue Datei</b> wählen. Der Arbeitsbereich steht oben in der Mitte. Ohne <b>Part Design</b> fehlen die Werkzeuge zum Aufpolstern.</p>"},
    "skizze-1": {status:["assets/chassi/05_skizze_leer.png","Der Skizzenmodus ist geöffnet."], more:"<p>Der Dialog zeigt <b>XY</b>, <b>XZ</b> und <b>YZ</b>. Für die Platte brauchst du <b>XY</b> (Draufsicht). Die Ebene kannst du später über <b>Befestigung</b> ändern.</p>"},
    "skizze-2": {status:["assets/chassi/07_symmetrie.png","Das Rechteck ist gezeichnet."], more:"<p>Ziehe das Rechteck mit zwei Klicks auf: erst die eine Ecke, dann die gegenüberliegende. Die genaue Größe kommt erst durch die Bemaßung.</p>"},
    "skizze-3": {status:["assets/chassi/08_masse.png","Die Skizze ist vollständig bestimmt."], more:"<p>Klicke zuerst die beiden Ecken an, dann den Ursprung. FreeCAD legt die Symmetrieachse durch den Ursprung; die Reihenfolge entscheidet, welche Punkte gespiegelt werden.</p>"},
    "skizze-4": {status:["assets/chassi/09_skizze_schliessen.png","Jetzt kannst du die Skizze schließen."], more:"<p>Klicke die Linie an, dann an die Stelle, wo das Maß stehen soll, und tippe den Wert ein. Mit <b>Enter</b> bestätigen. Grün = vollständig bestimmt.</p>"},
    "skizze-5": {status:["assets/chassi/11_platte.png","Nach dem Schließen folgt die Aufpolsterung."], more:"<p>Wenn der Button <b>Schließen</b> nicht sichtbar ist, scrolle im Aufgabenfenster nach oben. Die Skizze bleibt im Modellbaum erhalten.</p>"},
    "aufpolstern-0": {status:["assets/chassi/11_platte.png","Die Platte ist 5 mm dick."], more:"<p>Tiefe <b>5,00 mm</b>; <b>Symmetrisch</b> ist nicht nötig. Die Vorschau ist grün, wenn die Skizze geschlossen ist. Bei rot: Skizze prüfen.</p>"},
    "aufpolstern-1": {status:["assets/chassi/12_flaeche.png","Die Oberseite ist bereit für die Lochskizze."], more:"<p>Die Platte ist jetzt ein Körper. Im Modellbaum siehst du <b>Pad</b> bzw. <b>Platte</b>.</p>"},
    "aufpolstern-2": {status:["assets/chassi/12_flaeche.png","Die Oberseite ist ausgewählt."], more:"<p>Mit der Maus drehen: linke Taste + ziehen. Mit dem Mausrad zoomen. Mit <b>Ansicht → Fit All</b> holst du die Platte zurück ins Bild.</p>"},
    "loch-0": {status:["assets/chassi/13_kreis.png","Die Lochskizze liegt auf der Oberseite."], more:"<p>Die Fläche wird grün. Achte auf die <b>Oberseite</b>, nicht auf eine Seitenfläche.</p>"},
    "loch-1": {status:["assets/chassi/14_kreis_schliessen.png","Die Randbedingungen zeigen 10 mm, 5 mm und R1,5."], more:"<p>Kreis aufziehen, dann <b>Radius 1,5 mm</b>. Die Lage kommt über die Bemaßung: <b>10 mm</b> von links, <b>5 mm</b> von oben.</p>"},
    "loch-2": {status:["assets/chassi/14_kreis_schliessen.png","Die Bezugskanten sind übernommen und bemaßt."], more:"<p>Das Werkzeug <b>Externe Geometrie</b> holt die Plattenkante in die Skizze. Klicke zuerst das Werkzeug, dann die Kante. Die Kante wird als Bezugskante übernommen und kann bemaßt werden.</p>"},
    "loch-3": {status:["assets/chassi/16_ein_loch.png","Die Tasche geht durch die ganze Platte."], more:"<p>Typ <b>Durch alles</b> schneidet komplett durch. Bei <b>Dimension</b> müsstest du 5 mm eintragen.</p>"},
    "loch-4": {status:["assets/chassi/17_pocket_wahl.png","Die Tasche ist im Modellbaum markiert."], more:"<p>Die Tasche heißt <b>Loch</b>. Sie wird für die Mehrfach-Transformation markiert.</p>"},
    "loch-5": {status:["assets/chassi/16_ein_loch.png","Ein Loch ist die Grundlage für das Muster."], more:"<p>Nur ein Loch – die restlichen 44 entstehen gleich durch das Muster.</p>"},
    "muster-0": {status:["assets/chassi/18_mtf.png","Der Dialog Mehrfach-Transformation ist offen."], more:"<p><b>Formelemente transformieren</b> wählen, nicht <b>Körper transformieren</b>.</p>"},
    "muster-1": {status:["assets/chassi/pattern_menu.png","Das Menü zeigt Lineares Muster hinzufügen."], more:"<p>Die Tasche <b>Loch</b> steht in der Liste. Mit <b>Formelement hinzufügen</b> kommen die Muster dazu.</p>"},
    "muster-2": {status:["assets/chassi/pattern1.png","Das erste Muster ist eingestellt."], more:"<p>Der Eintrag <b>Lineares Muster hinzufügen</b> ist gelb markiert. Das erste Muster erscheint in der Liste.</p>"},
    "muster-3": {status:["assets/chassi/pattern2.png","Das zweite Muster ist eingestellt."], more:"<p><b>96 mm</b> ist die Gesamtstrecke vom ersten bis zum letzten Loch. 9 Löcher = 8 Abstände → <b>12 mm</b>.</p>"},
    "muster-4": {status:["assets/chassi/22_45loecher.png","Das Raster ist fertig."], more:"<p>Richtung vertikal, <b>60 mm</b>, <b>5 Vorkommen</b>. 4 Abstände → <b>15 mm</b>. Bei Bedarf <b>Umgekehrte Richtung</b>.</p>"},
    "muster-5": {status:["assets/chassi/23_senkung_auswahl.png","Jetzt kommen die Senkungen."], more:"<p>Kontrolle: 9 Spalten × 5 Reihen = <b>45 Löcher</b>. Im Modellbaum steht das Muster.</p>"},
    "muster-6": {status:["assets/chassi/23_senkung_auswahl.png","Jetzt kommen die Senkungen."], more:"<p>Falls das Raster nicht passt: Muster öffnen und Richtung/Vorkommen prüfen.</p>"},
    "senkungen-0": {status:["assets/chassi/24_senkung.png","Der Fase-Dialog ist offen."], more:"<p>Drahtgittermodus macht die Kanten sichtbar. Wähle nur die <b>8 Schraubenlöcher</b>: obere/untere Reihe, <b>1., 3., 7., 9.</b></p>"},
    "senkungen-1": {status:["assets/chassi/25_senkung_fertig.png","Die 8 Schraubenlöcher sind gesenkt."], more:"<p>8 Kanten in der Liste, Typ <b>Gleicher Abstand</b>, <b>1,50 mm</b>. Die übrigen 37 Löcher bleiben ohne Fase.</p>"},
    "senkungen-2": {status:["assets/chassi/26_rot.png","Jetzt fehlt nur noch die Farbe."], more:"<p>Kontrolle: <b>8 große Senkungen</b>, 37 kleine Löcher. Die Senkungen sind für die Schrauben der Radhalter.</p>"},
    "senkungen-3": {status:["assets/chassi/26_rot.png","Kontrolle: 8 große Senkungen."], more:"<p>Die 8 Positionen: 2 Schrauben pro Radhalter, 4 Halter. Bei einer anderen Halterung Auswahl anpassen.</p>"},
    "farbe-0": {status:["assets/chassi/27_speichern.png","Die Datei wird gespeichert."], more:"<p>M2 auf <b>Body</b> (nicht auf die Fase) → <b>Darstellung</b> → <b>Flächenfarbe</b>. Rot auswählen und mit <b>OK</b> bestätigen.</p>"},
    "farbe-1": {status:["assets/chassi/26_rot.png","Fertig – das Chassi ist rot."], more:"<p><b>Datei → Speichern unter</b> → Ordner <b>Carry</b> → Dateiname <b>Chassi.FCStd</b>.</p>"},
    "farbe-2": {status:["assets/chassi/27_speichern.png","Im Ordner Carry speichern."], more:"<p>Nach jedem größeren Schritt mit <b>Strg + S</b> speichern. Die Farbe wird mitgespeichert.</p>"}
  };

  document.querySelectorAll('.section').forEach(function (sec) {
    Array.prototype.forEach.call(sec.querySelectorAll('.row'), function (row, idx) {
      var d = DEEP[sec.id + '-' + idx];
      if (!d) return;
      var vis = row.querySelector('.visual');
      if (d.status && vis) {
        var fig = document.createElement('figure');
        fig.className = 'status';
        fig.innerHTML = '<span class="status-label">So sollte es aussehen</span>' +
          '<img src="' + d.status[0] + '" alt="" data-zoom>' +
          '<figcaption>' + d.status[1] + '</figcaption>';
        vis.appendChild(fig);
      }
      if (d.more) {
        var det = document.createElement('details');
        det.className = 'deep';
        det.innerHTML = '<summary>Mehr erklären</summary><div class="deep-body">' + d.more + '</div>';
        row.querySelector('.text').appendChild(det);
      }
    });
  });
})();

