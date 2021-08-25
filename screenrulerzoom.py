#!/bin/env python3
# -*- coding: utf-8 -*-

# screenrulerzoom v1.0 - Simple screen ruler
# Copyright © 2015 ElMoribond (Michael Herpin)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from collections import deque
from copy import deepcopy
from functools import partial
from gettext import bindtextdomain, gettext, textdomain
from os import path
from time import time
from PyQt5.QtCore import pyqtSignal, QSettings, Qt, QTimer, QUrl
from PyQt5.QtGui import QColor, QCursor, QDesktopServices, QIcon, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import QAction, QApplication, QColorDialog, QDialog, QGridLayout, QMainWindow, QMessageBox, QPushButton, QStyle, QLabel, QLayout, QMenu

PROJECT_NAME = "ScreenRulerZoom"
PROJECT_VERSION = "1.0"
PROJECT_RELEASE_DATE = "2015-04-06"
PROJECT_TEAM = "ElMoribond"
PROJECT_EMAIL = "elmoribond@gmail.com"
PROJECT_URL = "https://github.com/ElMoribond/screenrulerzoom"

bindtextdomain(PROJECT_NAME.lower(), path.join(path.dirname(path.realpath(__file__)), "i18n"))
textdomain(PROJECT_NAME.lower())

class Ruler(QMainWindow):
    cursorMove= pyqtSignal(object)

    class Menu(QMenu):

        class AboutDialog(QDialog):

            class Label(QLabel):

                def __init__(self):
                    super().__init__()
                    self.setPixmap(QPixmap(path.join(path.dirname(path.realpath(__file__)), "png", "gplv3-127x51.png")))

                def mousePressEvent(self, event):
                    if event.button() == Qt.LeftButton:
                        QDesktopServices.openUrl(QUrl("http://www.gnu.org/licenses/quick-guide-gplv3.html"))

                def enterEvent(self, event):
                    QApplication.setOverrideCursor(QCursor(Qt.PointingHandCursor))
                    super().enterEvent(event)

                def leaveEvent(self, event):
                    QApplication.restoreOverrideCursor()
                    super().leaveEvent(event)

            # Init de AboutDialog
            def __init__(self, parent):
                super().__init__(parent)
                self.setWindowTitle("%s %s" % (parent.about, PROJECT_NAME))
                self.setWindowFlags(Qt.Dialog|Qt.WindowStaysOnTopHint)
                self.rejected.connect(self.close)
                logo = QLabel()
                layout = QGridLayout(self)
                closeButton = QPushButton(self.style().standardIcon(QStyle.SP_DialogCloseButton), "")
                logo.setPixmap(Ruler.logo)
                email= QLabel("%s <a href='mailto:%s?subject=[%s]'>%s</a>" % (gettext("Lost in French countryside but reachable"), PROJECT_EMAIL, PROJECT_NAME, PROJECT_EMAIL))
                email.setOpenExternalLinks(True)
                url= QLabel("<br /><a href='%s'>%s</a><br />" % (PROJECT_URL, PROJECT_URL))
                url.setOpenExternalLinks(True)
                closeButton.clicked.connect(self.close)
                layout.addWidget(logo, 0, 0, 4, 1)
                layout.addWidget(QLabel("%s v%s %s %s" % (PROJECT_NAME, PROJECT_VERSION, gettext("released on"), PROJECT_RELEASE_DATE)), 0, 1, 1, 2)
                layout.addWidget(QLabel("%s %s" % (gettext("Created by"), PROJECT_TEAM)), 1, 1, 1, 2)
                layout.addWidget(email, 2, 1, 1, 2)
                layout.addWidget(QLabel(gettext("Released under GNU GPLv3 license")), 3, 1)
                layout.addWidget(self.Label(), 3, 2, 2, 1, Qt.AlignTop|Qt.AlignRight)
                layout.addWidget(QLabel("\nCopyright © 2015 %s (Michael Herpin). %s.\n%s.\n%s." % (PROJECT_TEAM, gettext("All rights reserved"), gettext("This program comes with ABSOLUTELY NO WARRANTY"), gettext("This is free software, and you are welcome to redistribute it under certain conditions"))), 4, 0, 1, 3)
                layout.addWidget(url, 5, 0, 1, 3)
                layout.addWidget(closeButton, 6, 0, 1, 3)
                layout.setSizeConstraint(QLayout.SetFixedSize)

        # Init de Menu
        def __init__(self, parent):
            super().__init__(parent)
            self.parent = parent
            unitDefsItem = QMenu(gettext("Unit Measure"), self)
            # ^ Ce sont des définitions d'unités de mesure.
            #   / These are definitions of units of measure.
            # Item signifie élément de menu (un élément feuille d'un
            # menu est toujours appelé menu dans Qt) :
            # Item stands for menu item (A leaf item on a menu is still
            # called a menu in Qt):
            rulerSizeItem = QMenu(gettext("Ruler Size"), self)
            colorsItem = QMenu(gettext("Colors"), self)
            zoomItem = QMenu(gettext("Zoom"), self)
            self.addAction(QAction(parent.orientation[1 if not parent.oH else 0], self, triggered=partial(parent.changeOrientation, 1 if not parent.oH else 0)))
            menuDefs = [
                [zoomItem, parent.zooms, parent.changeMode, parent.zoom],
                [unitDefsItem, parent.unitDefs, parent.changeUnitMeasure, parent.unitIndex],
                [rulerSizeItem, parent.rulerSize, parent.changeRulerSize, parent.rulerSize],
                [colorsItem, parent.colors, parent.changeRulerColor, parent.defaultColors],
            ]
            for menu in menuDefs:
                for i, item in enumerate(menu[1]):
                    item = QAction(item[0][0], self, triggered=partial(menu[2], i))
                    if type(menu[3]) == type(list()) and i == len(menu[1]) - 1:
                        menu[0].addSeparator()
                        item.setEnabled(False if menu[1] == menu[3] else True)
                    else:
                        item.setCheckable(True)
                        item.setChecked(True if i == menu[3] else False)
                        item.setEnabled(not item.isChecked())
                    menu[0].addAction(item)
                if menu[0] in [unitDefsItem, colorsItem]:
                    menu[0].setEnabled(not bool(parent.zoom))
                self.addMenu(menu[0])
            self.addSeparator()
            self.addAction(QAction(parent.about, self, triggered=self.AboutDialog(parent).exec_))
            self.addSeparator()
            self.addAction(QAction(gettext("Exit"), self, triggered=parent.close))

        def exec_(self, point):
            Ruler.menu = True
            super().exec_(point)

        def closeEvent(self, event):
            Ruler.menu = False
            self.parent.mouseTimer.timeout.connect(self.parent.pollCursor)

    # Init de Ruler
    def __init__(self):
        super().__init__()
        self.dpiX = self.logicalDpiX()
        self.dpiY = self.logicalDpiY()
        Ruler.logo, Ruler.menu= QPixmap(path.join(path.dirname(path.realpath(__file__)), "png", "%s.png" % PROJECT_NAME.lower())), False
        self.setWindowIcon(QIcon(Ruler.logo))
        self.setWindowFlags(Qt.Tool|Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openContextMenu)
        self.about = gettext("About")
        self.orientation = [ gettext("Horizontal"), gettext("Vertical") ]
        self.unitDefs = [
            [[gettext("Pixel"), gettext("px")], [1, 1]],
            [[gettext("Point"), gettext("pt"), 1], [self.dpiX/6*2, self.dpiY/6*2]],
            [[gettext("Inch"), gettext("in")], [self.dpiX, self.dpiY]],
            [[gettext("Pica"), gettext("pc"), 1], [self.dpiX/6, self.dpiY/6]],
            [[gettext("Centimeter"), gettext("cm")], [self.dpiX/2.54, self.dpiY/2.54]],
        ]
        self.screen = app.desktop().screenGeometry().bottomRight()
        self.colors = [
            [[gettext("Text"), QColor(230, 230, 250)]],
            [[gettext("Background"), QColor(0, 30, 120)]],
            [[gettext("Highlight"), QColor(220, 0, 0)]],
            [[gettext("Default Colors")]],
        ]

        self.sX = 600
        self.sY = 70
        zoomNames = [
            [[gettext("Normal")]],
            [[gettext("x2")]],
            [[gettext("x3")]],
            [[gettext("x4")]],
        ]
        self.cursor = None
        self.mouseTimer = QTimer(self)
        self.defaultColors = deepcopy(self.colors)

        self.pix = None
        self.ps = app.primaryScreen()
        self.csec = time()
        self.moving = False
        self.ps = app.primaryScreen()
        self.zooms = [
            [[gettext("None")]],
            [[zoomNames[1][0][0]]],
            [[zoomNames[2][0][0]]],
            [[zoomNames[3][0][0]]],
        ]
        self.mark = deque(maxlen=2)
        self.settings = QSettings(PROJECT_TEAM, PROJECT_NAME)
        self.rulerSize = 0
        self.unitIndex = 0
        self.oH = 0  # Set to true to set the orientation to horizontal.
        self.zoom = 0
        self.cursorMove.connect(self.handleCursorMove)
        self.mouseTimer.setInterval(50)
        self.mouseTimer.timeout.connect(self.pollCursor)
        self.mouseTimer.start()
        for i, item in enumerate([ "Colors/Text", "Colors/Background", "Colors/Highlight" ]):
            if (type(self.settings.value(item, None)) == type(QColor())) and self.settings.value(item, None).isValid():
                self.colors[i][0][1]= self.settings.value(item)
        # Translate the GUI elements to usable properties:
        settingsToProperties = [
            ["GUI/Zoom", "mode", 2],
            ["GUI/Orientation", "oH", 2],
            ["GUI/Size", "rulerSize", len(self.colors)],
            ["GUI/UnitMeasure", "unitIndex", len(self.unitDefs)],
        ]
        for item in settingsToProperties:
            if int(self.settings.value(item[0], -1)) in range(1, item[2]):
                setattr(self, item[1], int(self.settings.value(item[0])))
        self.changeRulerSize(self.rulerSize)
        self.changeOrientation(self.oH)
        if self.settings.contains("GUI/Position"):
            self.move(self.settings.value("GUI/Position"))
        else:
            self.move(app.desktop().screen().rect().center() - self.rect().center())
        self.saveBackground()

    def closeEvent(self, event):
        # Copiez les propriétés dans les paramètres puis enregistrez :
        # / Copy the properties to settings then save:
        propertiesToSettings = [
            ["GUI/Zoom", self.zoom],
            ["GUI/Orientation", self.oH],
            ["GUI/Position", self.pos()],
            ["GUI/Size", self.rulerSize],
            ["GUI/UnitMeasure", self.unitIndex],
            ["Colors/Text", self.colors[0][0][1]],
            ["Colors/Background", self.colors[1][0][1]],
            ["Colors/Highlight", self.colors[2][0][1]],
        ]
        for item in propertiesToSettings:
            self.settings.setValue(item[0], item[1])
        self.settings.sync()
        app.quit()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() in [ Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down ]:
            if time() > self.csec + 1:
                point= self.frameGeometry().topLeft()
                unitIndex = 10 if (event.modifiers() == Qt.ControlModifier) else 1
                if event.key() == Qt.Key_Left and point.x() >= unitIndex:
                    point.setX(point.x() - unitIndex)
                elif event.key() == Qt.Key_Right and point.x() + self.width() <= self.screen.x():
                    point.setX(point.x() + unitIndex)
                elif event.key() == Qt.Key_Up and point.y() >= unitIndex:
                    point.setY(point.y() - unitIndex)
                elif event.key() == Qt.Key_Down and point.y() + self.height() <= self.screen.y():
                    point.setY(point.y() + unitIndex)
                self.move(point)
                self.repaint()
                self.csec= time()
                self.saveBackground()
        else:
            super().keyPressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if not self.unitIndex:
            self.mark.append(event.pos())
            if len(self.mark) == 2:
                QMessageBox.information(self, "\0", str(event.pos().y() - self.mark[0].y() if self.oH else event.pos().x() - self.mark[0].x()).replace("-", ""), QMessageBox.Ok)
                self.mark.clear()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset, self.moving= event.pos(), True
            self.repaint()
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.saveBackground()
            self.offset, self.moving= None, False
        else:
            super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        self.mark.clear()
        self.move(self.mapToParent(event.pos() - self.offset))

    def paintEvent(self, event):
        qp = QPainter()
        unit = self.unitDefs[self.unitIndex][1][self.oH]
        count = -1
        # ^ C'est le nombre indiqué sur la règle. /
        #   This is the number shown on the ruler.
        first = 10
        mid = 15
        last = 20
        qp.begin(self)
        qp.setPen(self.colors[0][0][1])
        if self.zoom:
            if not self.moving:
                if self.pix is None:
                    self.saveBackground()
                qp.drawPixmap(0, 0, self.pix.scaled(self.size() * (self.zoom + 1), Qt.KeepAspectRatio))
            else:
                qp.setBrush(self.colors[1][0][1])
                qp.drawRect(-1, -1, self.width() + 1, self.height() + 1)
        else:
            qp.setBrush(self.colors[1][0][1])
            qp.drawRect(-1, -1, self.width() + 1, self.height() + 1)
            # Affichage de la graduation / incremental display
            for i in range(self.height() if self.oH else self.width()):
                length= 0
                # Affichage en pixel / pixel-based increments
                if not self.unitIndex:
                    # length, count = last if not i % 50 else mid if not i % 10 else first if not i % 2 else 0, count + 1
                    # ^ Il n'y a pas besoin de se crâner. / There is no need to show off.
                    length = 0
                    if i % 50 == 0:
                        length = last
                    elif i % 10 == 0:
                        length = mid
                    elif i % 2 == 0:
                        length = first

                    count = count + 1
                # Autre unité / other unit of measure
                else:
                    if (self.unitIndex in [ 1, 2, 3 ] and not i % unit) or (self.unitIndex == 4 and not i % round(unit)):
                        length, count = last, count + 1
                    elif (self.unitIndex in [ 1, 2, 3 ] and not i % (unit / 4)) or (self.unitIndex == 4 and not i % round(unit / 2)):
                        length= first
                cS= self.fontMetrics().tightBoundingRect(str(count) if count else self.unitDefs[self.unitIndex][0][1])
                # Unités d'affichage et lignes. / Display units and lines.
                if i == 1:
                    # Dessinez des messages globaux sur la première colonne de pixels. / Draw global messages at the first column of pixels.
                    if self.oH:
                        qp.drawText((self.width() - cS.width()) / 2, cS.height(), self.unitDefs[self.unitIndex][0][1]  + " " + str(self.dpiX) + "dpi")
                    else:
                        qp.drawText(3, self.height() / 2 + cS.height() / 3, self.unitDefs[self.unitIndex][0][1]  + " " + str(self.dpiX) + "dpi")
                elif i and length:
                    # Tracez une ligne car une longueur non nulle indique qu'il s'agit d'un incrément. / Draw a line since a non-zero length indicates this is an increment.
                    if self.oH:
                        qp.drawLine(0, i, length, i)
                        qp.drawLine(self.width(), i, self.width() - length - 1, i)
                        if length == last:
                            qp.drawText((self.width() - cS.width()) / 2, i + cS.height() / 2, str(count))
                    else:
                        qp.drawLine(i, 0, i, length)
                        qp.drawLine(i, self.height(), i, self.height() - length - 1)
                        if length == last:
                            qp.drawText(i - cS.width() / 2, self.height() / 2 + cS.height() / 2, str(count))
            # Affichage de la position du curseur / Display the cursor position.
            if self.cursor is not None and not Ruler.menu and (self.oH and self.mapFromParent(self.cursor).y() > -1 or not self.oH and self.mapFromParent(self.cursor).x() > -1) and (self.oH and self.mapFromParent(self.cursor).y() < self.height() or not self.oH and self.mapFromParent(self.cursor).x() < self.width()):
                self.drawCursorPosition(qp, self.mapFromParent(self.cursor))
            if not self.unitIndex:
                # Affichage des positions sauvegardés / Display saved positions.
                for m in self.mark:
                    self.drawCursorPosition(qp, m)

    def drawCursorPosition(self, qp, cp):
        qp.setPen(QPen(self.colors[2][0][1], 1, Qt.DashLine))
        cS= self.fontMetrics().tightBoundingRect(str(cp.y() if self.oH else cp.x()))
        # Unité autre que pixel, juste ligne hachurée
        if self.unitIndex:
            if self.oH:
                qp.drawLine(0, cp.y(), self.width(), cp.y())
            else:
                qp.drawLine(cp.x(), 0, cp.x(), self.height())
        # Unité pixel, ligne hacurée + position
        else:
            # Affichage vertical
            if self.oH:
                qp.drawLine(0, cp.y(), (self.width() / 2) - (cS.width() / 2), cp.y())
                qp.drawLine((self.width() / 2) + (cS.width() / 2), cp.y(), self.width(), cp.y())
                qp.setPen(QPen(Qt.NoPen))
                # Curseur en deça de la fenêtre
                if cp.y() - cS.height() / 2 < 1:
                    y= cS.height() + 2
                # Curseur au dela
                elif cp.y() + cS.height() / 2 + 2 > self.height():
                    y= self.height() - (cS.height() / 2)
                # Dans la fenêtre
                else:
                    y= cp.y() + cS.height() / 2
                # Mode zoom
                if not self.zoom:
                    qp.drawRect((self.width() / 2 - cS.width() / 2) - 2, y - cS.height() - 2, cS.width() + 4, cS.height() + 4)
                qp.setPen(QPen(self.colors[2][0][1], 1, Qt.SolidLine))
                qp.drawText(self.width() / 2 - cS.width() / 2, y, str(cp.y()))
            # Affichage horizontcal
            else:
                qp.drawLine(cp.x(), 0, cp.x(), (self.height() / 2) - (cS.height() / 2))
                qp.drawLine(cp.x(), (self.height() / 2) + (cS.height() / 2), cp.x(), self.height())
                qp.setPen(QPen(Qt.NoPen))
                # Curseur en deça de la fenêtre
                if cp.x() - cS.width() / 2 < 1:
                    x= 2
                # Curseur au dela
                elif cp.x() + cS.width() / 2 + 2 > self.width():
                    x= self.width() - cS.width() - 2
                # Dans la fenêtre
                else:
                    x= cp.x() - cS.width() / 2
                # Mode zoom
                if not self.zoom:
                    qp.drawRect(x - 2, (self.height() / 2 - cS.height() / 2) - 2, cS.width() + 4, cS.height() + 4)
                qp.setPen(QPen(self.colors[2][0][1], 1, Qt.SolidLine))
                qp.drawText(x, self.height() / 2 + cS.height() / 2, str(cp.x()))

    def openContextMenu(self, point):
        self.Menu(self).exec_(self.mapToGlobal(point))

    def changeMode(self, zoom):
        self.zoom = zoom
        self.pix = None
        self.mark.clear()
        self.repaint()

    def changeRulerSize(self, scale):
        self.rulerSize = scale
        self.setFixedSize(self.sX * (scale + 1), self.sY * (scale + 1))

    def changeUnitMeasure(self, unitIndex):
        self.unitIndex = unitIndex
        self.repaint()

    def changeRulerColor(self, color):
        if color == len(self.colors) - 1:
            self.colors= deepcopy(self.defaultColors)
        else:
            co= QColorDialog.getColor(self.colors[color][0][1], self)
            if co.isValid():
                self.colors[color][0][1]= co
                self.repaint()

    def changeOrientation(self, orientation):
        self.mark.clear()
        self.setFixedSize(self.sX * (self.rulerSize + 1) if not orientation else self.sY, self.sY if not orientation else self.sX * (self.rulerSize + 1))
        self.oH, geometry= orientation, self.frameGeometry()
        if geometry.top() < 0:
            geometry.moveTop(0)
            self.move(geometry.topLeft())
        if geometry.left() < 0:
            geometry.moveLeft(0)
            self.move(geometry.topLeft())
        self.repaint()

    def pollCursor(self):
        if QCursor.pos() != self.cursor:
            self.cursor= QCursor.pos()
            self.cursorMove.emit(QCursor.pos())

    def handleCursorMove(self, pos):
        if (not self.oH and pos.x() >= self.geometry().left() and pos.x() <= self.geometry().right()) or (self.oH and pos.y() >= self.geometry().top() and pos.y() <= self.geometry().bottom()):
            self.repaint()
        else:
            self.cursor= None

    def saveBackground(self):
        if self.zoom:
            self.hide()
            self.pix = self.ps.grabWindow(app.desktop().winId(), self.x(), self.y(), self.width(), self.height())
            self.show()

if __name__ == "__main__":
    app= QApplication([])
    ui= Ruler()
    ui.show()
    exit(app.exec_())
