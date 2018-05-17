from maya import cmds, OpenMaya
import maya.OpenMayaUI
import pymel.core
import copy



from maya import cmds

if int( cmds.about( v=1 ) ) < 2017:
    from PySide import QtGui, QtCore
    import shiboken
    from PySide.QtGui import QListWidgetItem, QDialog, QListWidget, QMainWindow, QWidget, QColor, QLabel,\
    QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QAbstractItemView, QMenu,QCursor, QMessageBox, QBrush, QSplitter,\
    QScrollArea, QSizePolicy, QTextEdit, QApplication, QFileDialog, QCheckBox, QDoubleValidator, QSlider, QIntValidator,\
    QImage, QPixmap, QTransform, QPaintEvent, QTabWidget, QFrame, QTreeWidgetItem, QTreeWidget, QComboBox, QGroupBox, QAction,\
    QFont, QGridLayout
else:
    from PySide2 import QtGui, QtCore, QtWidgets
    import shiboken2 as shiboken
    from PySide2.QtWidgets import QListWidgetItem, QDialog, QListWidget, QMainWindow, QWidget, QVBoxLayout, QLabel,\
    QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QAbstractItemView, QMenu, QMessageBox, QSplitter,\
    QScrollArea, QSizePolicy, QTextEdit, QApplication, QFileDialog, QCheckBox, QSlider,\
    QTabWidget, QFrame, QTreeWidgetItem, QTreeWidget, QComboBox, QGroupBox, QAction, QGridLayout
    
    from PySide2.QtGui import QColor, QCursor, QBrush, QDoubleValidator, QIntValidator, QImage, QPixmap, QTransform,\
    QPaintEvent, QFont


import os, json


class Cmds_file_control( object ):
    
    def __init__(self, *args, **kwargs ):
        
        print "init cmds_file"
        pass
        
    
    def makeFolder( self, pathName ):
        if os.path.exists( pathName ):return None
        os.makedirs( pathName )
        return pathName


    def makeFile( self, filePath ):
        if os.path.exists( filePath ): return None
        filePath = filePath.replace( "\\", "/" )
        splits = filePath.split( '/' )
        folder = '/'.join( splits[:-1] )
        self.makeFolder( folder )
        f = open( filePath, "w" )
        json.dump( {}, f )
        f.close()

    
    def writeData( self, data, filePath ):
        self.makeFile( filePath )
        f = open( filePath, 'w' )
        json.dump( data, f, indent=2 )
        f.close()
    
    
    def readData( self, filePath ):
        self.makeFile( filePath )
        
        f = open( filePath, 'r' )
        data = {}
        try:
            data = json.load( f )
        except:
            pass
        f.close()
        
        return data
    
    
    def save_info(self, path ):
        
        data = self.readData( path )
        data['x'] = self.x()
        data['y'] = self.y()
        data['width']  = self.width()
        data['height'] = self.height()
        self.writeData( data, path )



    def load_info(self, path ):
        
        data = self.readData( path )
        try:
            x = data['x']
            y = data['y']
            width  = data['width']
            height = data['height']
        except:
            return
        self.move( x, y )
        self.resize( width, height )



class Commands:
    
    @staticmethod
    def getSelectedComponents():
        
        selList = OpenMaya.MSelectionList()
        OpenMaya.MGlobal.getActiveSelectionList( selList )
        if selList.length() > 1:
            cmds.error( "Select Component from Only One Object" )
            return
        sels = cmds.ls( sl=1, fl=1 )
        compList = []
        for sel in sels:
            compList = sel.split( '.' )[-1]




class Widget_ComponentList():
    
    def __init__(self, *args, **kwargs ):
        
        super( Widget_ComponentList, self ).__init__( *args, **kwargs )
        mainLayout = QHBoxLayout( self )
        
        label = QLabel( "Components : " )
        lineEdit = QLineEdit()
        button = QPushButton( "Load" )
        
        mainLayout.addWidget( label )
        mainLayout.addWidget( lineEdit )
        mainLayout.addWidget( button )
        
    
    def load(self):
        
        pass
            


class Window( QDialog, Cmds_file_control ):
    
    objectName = "sgWidget_setWeightOnlySpecifyComponent"
    title = "Set Weight Only Specify Component"
    defaultWidth = 400
    defaultHeight = 400    
    path_uiInfo = cmds.about( pd=1 ) + "/pingo/Widget_setWeightOnlySpecifyComponent/uiInfo.json"

    def __init__(self, parent_widget, **kwargs ):
        
        existing_widget = parent_widget.findChildren( QDialog, Window.objectName )
        if existing_widget: map( lambda x : x.deleteLater(), existing_widget )
        
        super( Window, self ).__init__( parent_widget, **kwargs )
        self.setWindowTitle( Window.title )
        self.setObjectName( Window.objectName )
        self.installEventFilter( self )
    
        self.resize( Window.defaultWidth, Window.defaultHeight )
        self.load_info( Window.path_uiInfo )


    def eventFilter(self, *args, **kwargs ):
        event = args[1]
        if event.type() in [ QtCore.QEvent.Resize, QtCore.QEvent.Move ]:
            try:self.save_info( Window.path_uiInfo )
            except:pass
        



def show():
    
    parent_widget = shiboken.wrapInstance( long( maya.OpenMayaUI.MQtUtil.mainWindow() ), QWidget )
    Window(parent_widget).show()


if __name__ == '__main__':
    Window().show()



