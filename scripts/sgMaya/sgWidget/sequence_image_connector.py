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



path_basedir = cmds.about(pd=1) + "/pingo/sequence_image_connector"


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


    def save_lineEdit_text(self, lineEdit, path ):

        data = self.readData( path )
        data['lineEdit'] = lineEdit.text()
        self.writeData( data, path )


    def load_lineEdit_text(self, lineEdit, path ):

        data = self.readData( path )
        if data.has_key( 'lineEdit' ):
            lineEdit.setText( data['lineEdit'] )


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




class Cmds_main():

    @staticmethod
    def getImagesFromObject( target ):

        import re, ntpath, glob

        def getFileNodesFromObject( target ):
            target = pymel.core.ls( target )[0]
            targetShape = target.getShape()
            shadingEngines = targetShape.listConnections( s=0, d=1, type='shadingEngine' )
            fileNodes = []
            for shadingEngine in shadingEngines:
                for hist in shadingEngine.history( pdo=1 ):
                    if hist.nodeType() != 'file': continue
                    fileNodes.append( hist )
            return fileNodes

        p = re.compile( "\d+\.[a-z,A-Z]+")

        fileNodes = getFileNodesFromObject( target )
        for fileNode in fileNodes:
            dirName, fileName = ntpath.split( fileNode.fileTextureName.get() )
            try:matchResult = p.search( fileName ).group().split( '.' )[0]
            except:continue
            sequenceFilePaths = glob.glob( dirName + '/' + fileName.replace( matchResult, '*' ) )
            indices = []
            files = []
            for sequenceFilePath in sequenceFilePaths:
                dirName, fileName = ntpath.split(sequenceFilePath)
                try:
                    matchResult = p.search(fileName).group().split( '.' )[0]
                except:
                    continue
                indices.append( int( matchResult ) )
                files.append( sequenceFilePath )

            return fileNode, files, indices

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




class Widget_loadObject( QWidget, Cmds_file_control ):

    def __init__(self, *args, **kwargs):

        self.saveInfo = False
        self.title = ''
        if kwargs.has_key('title'):
            self.title = kwargs.pop('title')
        if kwargs.has_key('saveInfo'):
            self.saveInfo = kwargs.pop('saveInfo')

        self.path_uiInfo = path_basedir + "/Widget_Controller_%s.json" % self.title

        super(Widget_loadObject, self).__init__(*args, **kwargs)
        self.installEventFilter( self )
        mainLayout = QHBoxLayout(self)

        self.setStyleSheet( "font:12px;" )
        label = QLabel( "%s : " % self.title ); label.setFixedWidth( 80 )
        lineEdit = QLineEdit(); lineEdit.setStyleSheet( "padding:2px; padding-bottom:1px" )
        button = QPushButton( "Load" ); button.setFixedWidth( 70 )
        button.setStyleSheet( "padding:3px;padding-left:6px;padding-right:6px" )

        mainLayout.addWidget( label )
        mainLayout.addWidget( lineEdit )
        mainLayout.addWidget( button )

        button.clicked.connect( self.load_target )
        self.lineEdit = lineEdit
        if self.saveInfo : self.load_lineEdit_text( self.lineEdit, self.path_uiInfo )

        self.button = button


    def load_target(self):

        import pymel.core
        sels = pymel.core.ls( sl=1 )
        if not sels:
            QMessageBox.information( self, self.tr( "Info" ), "Select Object First" )
            return
        target = sels[0]
        self.lineEdit.setText( target.name() )
        if self.saveInfo : self.save_lineEdit_text( self.lineEdit, self.path_uiInfo )



class Widget_Separator( QFrame ):

    def __init__(self, *args, **kwargs ):
        super( Widget_Separator, self ).__init__( *args, **kwargs )
        self.setFrameShape(QFrame.HLine)



class Widget_target( QWidget, Cmds_file_control ):

    def __init__(self, *args, **kwargs ):

        super(Widget_target, self).__init__(*args, **kwargs )
        mainLayout = QVBoxLayout( self ); mainLayout.setContentsMargins( 10,0,10,0 ); mainLayout.setSpacing(0)

        w_loadObject = Widget_loadObject( title="Target" )
        listWidget = QListWidget()

        mainLayout.addWidget( w_loadObject )
        mainLayout.addWidget( listWidget )

        self.w_loadObject = w_loadObject
        self.listWidget = listWidget
        w_loadObject.button.clicked.connect( self.load_textures )

    def load_textures(self):
        import ntpath
        target = self.w_loadObject.lineEdit.text()
        if not pymel.core.objExists( target ) and pymel.core.ls( sl=1 ):
            QMessageBox.information( self, self.tr( "Info" ), "%s is not exists" % target )
        fileNode, files, indices = Cmds_main.getImagesFromObject( target )

        self.listWidget.clear()
        for file in files:
            dirName, fileName = ntpath.split( file )
            self.listWidget.addItem( file )




class Widget_attributeName( QWidget, Cmds_file_control ):

    path_uiInfo = path_basedir + "/Widget_attributeName.json"

    def __init__(self, *args, **kwargs ):

        super(Widget_attributeName, self).__init__(*args, **kwargs )
        mainLayout = QHBoxLayout( self ); mainLayout.setContentsMargins( 15, 10, 10, 10 )

        label = QLabel( "Attribute name : " ); label.setFixedWidth( 120 )
        lineEdit = QLineEdit()

        mainLayout.addWidget( label )
        mainLayout.addWidget( lineEdit )

        self.lineEdit = lineEdit
        QtCore.QObject.connect( lineEdit, QtCore.SIGNAL( "textChanged(const QString & )" ), self.save_info )
        self.load_info()

    def save_info(self):
        self.save_lineEdit_text( self.lineEdit, self.path_uiInfo )

    def load_info(self):
        self.load_lineEdit_text( self.lineEdit, self.path_uiInfo )



class Widget_startIndex( QWidget, Cmds_file_control ):

    path_uiInfo = path_basedir + '/Widget_startIndex.json'
    def __init__(self, *args, **kwargs ):

        super( Widget_startIndex, self ).__init__( *args, **kwargs )
        mainLayout = QHBoxLayout( self ); mainLayout.setContentsMargins(15, 0, 10, 10 )

        validator = QIntValidator()
        label = QLabel( "Start Index : " ); label.setFixedWidth( 120 )
        lineEdit = QLineEdit(); lineEdit.setValidator( validator ); lineEdit.setText( "0" ); lineEdit.setFixedWidth( 50 )
        space = QLabel(); space.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Preferred )

        mainLayout.addWidget(label)
        mainLayout.addWidget(lineEdit)
        mainLayout.addWidget( space )

        self.lineEdit = lineEdit
        QtCore.QObject.connect(lineEdit, QtCore.SIGNAL("textChanged(const QString & )"), self.save_info)
        self.load_info()

    def save_info(self):
        self.save_lineEdit_text( self.lineEdit, self.path_uiInfo )

    def load_info(self):
        self.load_lineEdit_text( self.lineEdit, self.path_uiInfo )






class Window(QDialog, Cmds_file_control ):

    mayaWin = shiboken.wrapInstance(long(maya.OpenMayaUI.MQtUtil.mainWindow()), QWidget)
    objectName = "sg_pingo_sequence_image_connector"
    title = "PINGO - Sequence Image Connector"
    defaultWidth = 400
    defaultHeight = 100
    path_uiInfo = path_basedir + "/Window.json"

    def __init__(self, *args, **kwrgs):

        existing_widgets = Window.mayaWin.findChildren( QDialog, Window.objectName )
        if existing_widgets: map( lambda x: x.deleteLater(), existing_widgets )

        super( Window, self ).__init__( *args, **kwrgs )
        self.installEventFilter( self )
        self.setObjectName( Window.objectName )
        self.setWindowTitle( Window.title )

        mainLayout = QVBoxLayout( self ); mainLayout.setContentsMargins( 0,0,0,0 ); mainLayout.setSpacing(0)

        w_controller = Widget_loadObject( title="Controller", saveInfo=False )
        w_separator1 = Widget_Separator()
        w_target     = Widget_target()
        w_attrName = Widget_attributeName()
        w_startIndex = Widget_startIndex()
        w_buttons = QWidget()
        lay_buttons = QHBoxLayout( w_buttons ); lay_buttons.setContentsMargins( 10,0,10,10 ); lay_buttons.setSpacing( 0 )
        button_connect = QPushButton( "Connect" ); button_connect.setFixedHeight( 25 )
        button_close   = QPushButton( "Close" ); button_close.setFixedHeight( 25 )
        lay_buttons.addWidget( button_connect )
        lay_buttons.addWidget( button_close )

        mainLayout.addWidget(w_controller)
        mainLayout.addWidget(w_separator1)
        mainLayout.addWidget( w_target )
        mainLayout.addWidget(w_attrName)
        mainLayout.addWidget(w_startIndex)
        mainLayout.addWidget( w_buttons )

        self.resize( Window.defaultWidth, Window.defaultHeight )
        self.load_shapeInfo( Window.path_uiInfo )

        button_connect.clicked.connect( self.cmd_connect )
        button_close.clicked.connect( self.deleteLater )

        self.w_controller = w_controller
        self.w_target = w_target
        self.w_attrName = w_attrName
        self.w_startIndex = w_startIndex

    def cmd_connect(self):

        controller = self.w_controller.lineEdit.text()
        targetObject = self.w_target.w_loadObject.lineEdit.text()
        attributeName = self.w_attrName.lineEdit.text()
        startIndex = int( self.w_startIndex.lineEdit.text() )

        fileNode, files, indices = Cmds_main.getImagesFromObject(targetObject)
        Cmds_main.addAttr( controller, ln='____', at='enum', en='Sequence:', cb=1 )
        Cmds_main.addAttr( controller, ln=attributeName, at='long', k=1, min=0, max= len(files)-1 )

        exname = 'expression_%s_%s' %( targetObject, attributeName )
        expressionString = "int $indicesList[] = {%s}; int $indexValue = int(%s.%s-%d); if( $indexValue < 0 ) $indexValue=0;%s.frameExtension = $indicesList[ $indexValue ]" % ( ','.join([ str(index) for index in indices ]), controller, attributeName, startIndex, fileNode )
        if cmds.objExists(exname): cmds.delete(exname)
        origExpressions = fileNode.attr( 'frameExtension' ).listConnections( s=1, d=0, type='expression' )
        if origExpressions: pymel.core.delete( origExpressions )
        cmds.expression(s=expressionString, o="", ae=1, uc='all', n=exname)




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