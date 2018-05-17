#coding=utf-8

from maya import cmds, OpenMaya
import maya.OpenMayaUI
import pymel.core
import copy
import os, json

from maya import cmds

if int(cmds.about(v=1)) < 2017:
    from PySide import QtGui, QtCore
    import shiboken
    from PySide.QtGui import QListWidgetItem, QDialog, QListWidget, QMainWindow, QWidget, QColor, QLabel, \
        QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QAbstractItemView, QMenu, QCursor, QMessageBox, QBrush, \
        QSplitter, \
        QScrollArea, QSizePolicy, QTextEdit, QApplication, QFileDialog, QCheckBox, QDoubleValidator, QSlider, \
        QIntValidator, \
        QImage, QPixmap, QTransform, QPaintEvent, QTabWidget, QFrame, QTreeWidgetItem, QTreeWidget, QComboBox, \
        QGroupBox, QAction, \
        QFont, QGridLayout, QAbstractScrollArea
else:
    from PySide2 import QtGui, QtCore, QtWidgets
    import shiboken2 as shiboken
    from PySide2.QtWidgets import QListWidgetItem, QDialog, QListWidget, QMainWindow, QWidget, QVBoxLayout, QLabel, \
        QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QAbstractItemView, QMenu, QMessageBox, QSplitter, \
        QScrollArea, QSizePolicy, QTextEdit, QApplication, QFileDialog, QCheckBox, QSlider, \
        QTabWidget, QFrame, QTreeWidgetItem, QTreeWidget, QComboBox, QGroupBox, QAction, QGridLayout, QAbstractScrollArea

    from PySide2.QtGui import QColor, QCursor, QBrush, QDoubleValidator, QIntValidator, QImage, QPixmap, QTransform, \
        QPaintEvent, QFont



path_basedir = cmds.about(pd=1) + "/pingo/wiget_default"


class Cmds_file_control(object):

    def __init__(self, *args, **kwargs):
        pass

    def makeFolder(self, pathName):
        if os.path.exists(pathName): return None
        os.makedirs(pathName)
        return pathName

    def makeFile(self, filePath):
        if os.path.exists(filePath): return None
        filePath = filePath.replace("\\", "/")
        splits = filePath.split('/')
        folder = '/'.join(splits[:-1])
        self.makeFolder(folder)
        f = open(filePath, "w")
        json.dump({}, f)
        f.close()

    def writeData(self, data, filePath):
        self.makeFile(filePath)
        f = open(filePath, 'w')
        json.dump(data, f, indent=2)
        f.close()

    def readData(self, filePath):
        self.makeFile(filePath)

        f = open(filePath, 'r')
        data = {}
        try:
            data = json.load(f)
        except:
            pass
        f.close()

        return data

    def save_shapeInfo(self, path):

        data = self.readData(path)
        data['x'] = self.x()
        data['y'] = self.y()
        data['width'] = self.width()
        data['height'] = self.height()
        self.writeData(data, path)

    def load_shapeInfo(self, path):

        data = self.readData(path)
        try:
            x = data['x']
            y = data['y']
            width = data['width']
            height = data['height']
        except:
            return
        self.move(x, y)
        self.resize(width, height)


    def save_lineEdit_text(self, lineEdit, path ):

        data = self.readData( path )
        data['lineEdit'] = lineEdit.text()
        self.writeData( data, path )


    def load_lineEdit_text(self, lineEdit, path ):

        data = self.readData( path )
        if data.has_key( 'lineEdit' ):
            lineEdit.setText( data['lineEdit'] )


    def save_comboBox(self, comboBox, path ):

        data = self.readData( path )
        data[ 'selectedItem' ] = comboBox.currentText()
        self.writeData( data, path )


    def load_comboBox(self, comboBox, path ):

        data = self.readData( path )
        if data.has_key( 'selectedItem' ):
            itemText = data['selectedItem' ]
        else:
            return
        for i in range( comboBox.count() ):
            if itemText == comboBox.itemText( i ):
                comboBox.setCurrentIndex( i )
                break

    def get_csv_form_google_spreadsheets( self, link_attributeList, targetPath):

        #print "before get google spreadsheets"
        import re, urllib, urllib2, os, ssl
        p = re.compile('/d/.+/')
        m = p.search(link_attributeList)
        id_sheet = m.group()[3:-1]
        dirPath = os.path.dirname(targetPath)
        if not os.path.exists(dirPath): os.makedirs( dirPath )
        link_donwload_attributeList = 'https://docs.google.com/spreadsheets/d/%s/export?format=csv' % id_sheet
        try:
            context = ssl._create_unverified_context()
            response = urllib2.urlopen(link_donwload_attributeList,
                                       context=context)  # How should i pass authorization details here?
            data = response.read()
            f = open(targetPath, 'w')
            f.write(data)
            f.close()
        except:
            testfile = urllib.URLopener()
            testfile.retrieve(link_donwload_attributeList, targetPath)
        #print "after get google spreadsheets"


    def get_dictList_from_csvPath( self, csvPath):

        csvData = []
        import csv
        f = open(csvPath, 'r')
        rdr = csv.reader(f)
        for line in rdr:
            csvData.append(line)
        f.close()

        keys = csvData[0]
        dictList =[]
        for i in range(1, len(csvData)):
            targetDict = {}
            for j in range( len( csvData[i] ) ):
                targetDict[ keys[j] ] = csvData[i][j]
            dictList.append( targetDict )
        return dictList

    def save_checkBoxValue(self, checkBox, filePath ):

        data = self.readData(filePath)
        data['checkValue'] = checkBox.isChecked()
        self.writeData( data, filePath )

    def load_checkBoxValue(self, checkBox, filePath ):

        data = self.readData(filePath)
        if data.has_key("checkValue"):
            checkBox.setChecked(data['checkValue'])


    def save_splitterPosition(self, splitter, filePath ):

        data = self.readData(filePath)
        data['size'] = splitter.sizes()
        self.writeData(data, filePath)


    def load_splitterPosition(self, splitter, filePath ):

        data = self.readData(filePath)
        if data.has_key( 'size' ):
            splitter.setSizes( [ value for value in data['size'] ] )





class Widget_Separator( QFrame ):

    def __init__(self, *args, **kwargs ):
        super( Widget_Separator, self ).__init__( *args, **kwargs )
        self.setFrameShape(QFrame.HLine)




class Window( QDialog, Cmds_file_control ):

    mayaWin = shiboken.wrapInstance(long(maya.OpenMayaUI.MQtUtil.mainWindow()), QWidget)
    objectName = "sg_pingo_widget_default"
    title = "PINGO - Widget default"
    defaultWidth = 400
    defaultHeight = 100
    path_uiInfo = path_basedir + "/Window.json"

    def __init__(self, *args, **kwrgs):

        existing_widgets = Window.mayaWin.findChildren( QDialog, Window.objectName )
        if existing_widgets: map( lambda x: x.deleteLater(), existing_widgets )

        super( Window, self ).__init__(  *args, **kwrgs )
        self.installEventFilter( self )
        self.setObjectName( Window.objectName )
        self.setWindowTitle( Window.title )

        mainLayout = QVBoxLayout( self ); mainLayout.setContentsMargins( 0,0,0,0 ); mainLayout.setSpacing(0)

        self.resize( Window.defaultWidth, Window.defaultHeight )
        self.load_shapeInfo( Window.path_uiInfo )


    def eventFilter(self, *args, **kwargs ):
        event = args[1]
        if event.type() in [ QtCore.QEvent.Resize, QtCore.QEvent.Move ]:
            try:self.save_shapeInfo( Window.path_uiInfo )
            except:pass


def show():
    try: cmds.deleteUI( Window.objectName, wnd=1 )
    except:pass
    Window( Window.mayaWin ).show()



if __name__ == '__main__':
    show()