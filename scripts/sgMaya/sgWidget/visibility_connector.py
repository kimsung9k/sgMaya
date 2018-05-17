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



path_basedir = cmds.about(pd=1) + "/pingo/visibilityConnector"


class Cmds_file_control(object):

    def __init__(self, *args, **kwargs):

        print "init cmds_file"
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



class sgCmds:

    @staticmethod
    def addAttr(target, **options):

        items = options.items()
        attrName = ''
        channelBox = False
        keyable = False
        for key, value in items:
            if key in ['ln', 'longName']:
                attrName = value
            elif key in ['cb', 'channelBox']:
                channelBox = True
                options.pop(key)
            elif key in ['k', 'keyable']:
                keyable = True
                options.pop(key)

        if pymel.core.attributeQuery(attrName, node=target, ex=1): return None

        pymel.core.addAttr(target, **options)
        if channelBox:
            pymel.core.setAttr(target + '.' + attrName, e=1, cb=1)
        elif keyable:
            pymel.core.setAttr(target + '.' + attrName, e=1, k=1)





class Widget_Separator( QFrame ):

    def __init__(self, *args, **kwargs ):
        super( Widget_Separator, self ).__init__( *args, **kwargs )
        self.setFrameShape(QFrame.HLine)



class Widget_Controller( QWidget, Cmds_file_control ):

    path_uiInfo = path_basedir + "/Widget_Controller.json"

    def __init__(self, *args, **kwargs):

        super(Widget_Controller, self).__init__(*args, **kwargs)
        self.installEventFilter(self)
        mainLayout = QHBoxLayout(self)

        self.setStyleSheet( "font:12px;" )
        label = QLabel( "Controller : " )
        lineEdit = QLineEdit(); lineEdit.setStyleSheet( "padding:2px; padding-bottom:1px" )
        button = QPushButton( "Load Controller" )
        button.setStyleSheet( "padding:3px;padding-left:6px;padding-right:6px" )

        mainLayout.addWidget( label )
        mainLayout.addWidget( lineEdit )
        mainLayout.addWidget( button )

        button.clicked.connect( self.load_Controller )
        self.lineEdit = lineEdit
        #self.load_lineEdit_text( self.lineEdit, Widget_Controller.path_uiInfo )


    def load_Controller(self):

        import pymel.core
        sels = pymel.core.ls( sl=1 )
        if not sels:
            QMessageBox.information( self, self.tr( "Info" ), "Select Controller First" )
            return
        target = sels[0]
        self.lineEdit.setText( target.name() )
        self.save_lineEdit_text( self.lineEdit, Widget_Controller.path_uiInfo )




class Widget_objectList( QWidget, Cmds_file_control ):

    path_uiInfo = path_basedir + "/Widget_objectList.json"

    def __init__(self, *args, **kwargs ):

        super( Widget_objectList, self ).__init__( *args, **kwargs )
        self.installEventFilter( self )
        mainLayout = QVBoxLayout( self )

        treeWidget = QTreeWidget()
        treeWidget.setColumnCount(2)
        headerItem = treeWidget.headerItem()
        headerItem.setText(0, "Target Node")
        headerItem.setText(1, "Attribute Name")
        treeWidget.setRootIsDecorated(False)
        treeWidget.setStyleSheet("QTreeWidget::item { border-left: 1px solid gray;border-bottom: 1px solid gray; padding: 3px}\
                                 QTreeWidget{ font-size:13px;}" )
        treeWidget.header().setStyleSheet( "font-size:12px;" )

        w_buttons = QWidget()
        lay_buttons  = QHBoxLayout( w_buttons ); lay_buttons.setContentsMargins( 0,0,0,0 ); lay_buttons.setSpacing( 0 )
        button_load = QPushButton( "Load List" )
        button_load.setStyleSheet( "font:14px;" )
        lay_buttons.addWidget( button_load )

        mainLayout.addWidget( treeWidget )
        mainLayout.addWidget( w_buttons )

        self.treeWidget = treeWidget
        QtCore.QObject.connect(treeWidget,  QtCore.SIGNAL("itemChanged(QTreeWidgetItem * , int )"), self.writeData)
        QtCore.QObject.connect(button_load, QtCore.SIGNAL("clicked()"), self.cmd_loadList)
        #self.readData()


    def cmd_loadList(self):

        self.treeWidget.clear()
        sels = pymel.core.ls( sl=1, type='transform' )

        data = []
        for sel in sels:
            widgetItem = QTreeWidgetItem( self.treeWidget )
            widgetItem.setText( 0, sel.name() )
            widgetItem.setText( 1, sel.nodeName().split( '_' )[-1] )
            widgetItem.setFlags( widgetItem.flags() | QtCore.Qt.ItemIsEditable )
            data.append([widgetItem.text(0), widgetItem.text(1)])


    def writeData(self, *args ):

        data = {}
        for i in range( self.treeWidget.topLevelItemCount() ):
            item = self.treeWidget.topLevelItem( i )
            data[i] = [item.text(0), item.text(1)]
        super( Widget_objectList, self ).writeData( data, Widget_objectList.path_uiInfo )


    def readData(self, *args):

        data = super( Widget_objectList, self ).readData( Widget_objectList.path_uiInfo )
        if not type( data ) == dict: return
        self.treeWidget.clear()
        keys = data.keys()
        keys.sort()
        for key in keys:
            try:nodeName, attrName = data[key]
            except:return
            widgetItem = QTreeWidgetItem( self.treeWidget )
            widgetItem.setText( 0, nodeName )
            widgetItem.setText( 1, attrName )
            widgetItem.setFlags(widgetItem.flags() | QtCore.Qt.ItemIsEditable)


    def eventFilter(self, *args, **kwargs ):
        event = args[1]
        if event.type() in [ QtCore.QEvent.Resize, QtCore.QEvent.Show ]:
            self.treeWidget.setColumnWidth(0, self.treeWidget.width()*0.5 )




class Widget_ConnectionType( QWidget, Cmds_file_control ):

    path_uiInfo = path_basedir + "/Widget_ConnectionType.json"

    def __init__(self, *args, **kwargs ):
        super(Widget_ConnectionType, self).__init__(*args, **kwargs)
        self.installEventFilter(self)
        mainLayout = QVBoxLayout(self); mainLayout.setSpacing(0)

        self.setStyleSheet("font-size:12px;")
        w_comboBox = QWidget()
        lay_comboBox = QHBoxLayout( w_comboBox ); lay_comboBox.setContentsMargins(5,5,5,5); lay_comboBox.setSpacing(0)
        label = QLabel( "Connection Type : " )
        comboBox = QComboBox(); comboBox.setStyleSheet( "padding:2px; padding-left:5px")
        comboBox.addItem("Long Type")
        comboBox.addItem("Enum Type")
        lay_comboBox.addWidget( label )
        lay_comboBox.addWidget( comboBox )

        w_enumAttrName = QWidget()
        lay_enumAttrName = QHBoxLayout( w_enumAttrName ); lay_enumAttrName.setContentsMargins( 5,5,5,5 ); lay_enumAttrName.setSpacing(0)
        label_enumName = QLabel( "Enum Attribute Name :  " )
        lineEdit = QLineEdit(); lineEdit.setStyleSheet( "padding:2px")
        lay_enumAttrName.addWidget( label_enumName )
        lay_enumAttrName.addWidget( lineEdit )
        w_enumAttrName.setEnabled( False )

        mainLayout.addWidget( w_comboBox )
        mainLayout.addWidget( w_enumAttrName )

        self.comboBox = comboBox
        self.w_enumAttrName = w_enumAttrName
        self.lineEdit = lineEdit
        self.comboBox.currentIndexChanged.connect( self.cmd_attrTypeCondition )
        self.readData()

        lineEdit.textEdited.connect( self.writeData )
        comboBox.currentIndexChanged.connect( self.writeData )
        self.readData()


    def cmd_attrTypeCondition(self):

        if self.comboBox.currentText() == 'Enum Type':
            self.w_enumAttrName.setEnabled( True )
        else:
            self.w_enumAttrName.setEnabled( False )


    def writeData(self):

        currentText  = self.comboBox.currentText()
        lineEditText = self.lineEdit.text()
        data = dict( attrType=currentText, enumName=lineEditText )
        super( Widget_ConnectionType, self ).writeData( data, Widget_ConnectionType.path_uiInfo )


    def readData(self):

        data = super( Widget_ConnectionType, self ).readData( Widget_ConnectionType.path_uiInfo )

        if not data.has_key( 'attrType' ) or not data.has_key( "enumName" ): return
        attrType = data['attrType']
        enumName = data['enumName']

        for i in range( self.comboBox.count() ):
            if self.comboBox.itemText( i ) != attrType: continue
            self.comboBox.setCurrentIndex( i )
        self.lineEdit.setText( enumName )




class Window(QDialog, Cmds_file_control ):

    mayaWin = shiboken.wrapInstance( long(maya.OpenMayaUI.MQtUtil.mainWindow()), QWidget )
    objectName = "sg_pingo_visibility_connector"
    title = "PINGO - Visibility Connector"
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

        w_controller = Widget_Controller()
        w_separator1 = Widget_Separator()
        w_objectList = Widget_objectList()
        w_separator2 = Widget_Separator()
        w_connectionType = Widget_ConnectionType()
        w_buttons = QWidget(); w_buttons.setStyleSheet( "font:14px")
        lay_buttons = QHBoxLayout( w_buttons ); lay_buttons.setSpacing( 0 )
        button_connect = QPushButton( "CONNECT" )
        button_close = QPushButton( "CLOSE" )
        lay_buttons.addWidget( button_connect ); lay_buttons.addWidget( button_close )

        mainLayout.addWidget( w_controller )
        mainLayout.addWidget( w_separator1 )
        mainLayout.addWidget( w_objectList )
        mainLayout.addWidget( w_separator2 )
        mainLayout.addWidget( w_connectionType )
        mainLayout.addWidget( w_buttons )
        self.resize( Window.defaultWidth, Window.defaultHeight )
        self.load_shapeInfo( Window.path_uiInfo )

        button_connect.clicked.connect( self.cmd_connect )
        button_close.clicked.connect( self.deleteLater )

        self.w_controller = w_controller
        self.w_objectList = w_objectList
        self.w_connectionType = w_connectionType


    def cmd_connect(self):

        controllerName = self.w_controller.lineEdit.text()
        attributeType  =  self.w_connectionType.comboBox.currentText()
        enumAttrName = self.w_connectionType.lineEdit.text()

        targetObjects = []
        targetAttrs   = []
        for i in range( self.w_objectList.treeWidget.topLevelItemCount() ):
            targetObjects.append( self.w_objectList.treeWidget.topLevelItem(i).text( 0 ) )
            targetAttrs.append( self.w_objectList.treeWidget.topLevelItem(i).text(1 ) )

        from maya import cmds
        cmds.undoInfo( ock=1 )
        sgCmds.addAttr( controllerName, ln='_____', at='enum', en='visible_control', cb=1 )
        if attributeType == 'Long Type':
            for i in range( len( targetObjects ) ):
                sgCmds.addAttr( controllerName, ln=targetAttrs[i], k=1, min=0, max=1, at='long' )
                if cmds.isConnected(  controllerName + '.' + targetAttrs[i], targetObjects[i] + '.v' ): continue
                pymel.core.connectAttr( controllerName + '.' + targetAttrs[i], targetObjects[i] + '.v', f=1  )
        elif attributeType == 'Enum Type':
            sgCmds.addAttr( controllerName, ln=enumAttrName, at='enum', en=":".join( targetAttrs ) + ':', k=1 )
            for i in range( len( targetObjects ) ):
                conNode = pymel.core.createNode( 'condition' )
                pymel.core.connectAttr( controllerName + '.' + enumAttrName, conNode + '.firstTerm' )
                conNode.attr( 'secondTerm' ).set( i )
                conNode.attr( 'colorIfTrueR' ).set( 1 )
                conNode.attr( 'colorIfFalseR' ).set( 0 )
                pymel.core.connectAttr( conNode.attr( 'outColorR' ), targetObjects[i] + '.v', f=1 )
        cmds.undoInfo( cck=1 )



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