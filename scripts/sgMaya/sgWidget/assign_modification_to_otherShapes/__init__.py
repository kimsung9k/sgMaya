#-*- coding: utf-8 -*-

from maya import cmds, OpenMayaUI, OpenMaya
import pymel.core
import json, os

if int( cmds.about( v=1 ) ) < 2017:
    from PySide import QtGui, QtCore
    import shiboken
    from PySide.QtGui import QListWidgetItem, QDialog, QListWidget, QMainWindow, QWidget, QColor, QLabel,\
    QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QAbstractItemView, QMenu,QCursor, QMessageBox, QBrush, QSplitter,\
    QScrollArea, QSizePolicy, QTextEdit, QApplication, QFileDialog, QCheckBox, QDoubleValidator, QSlider, QIntValidator,\
    QImage, QPixmap, QTransform, QPaintEvent, QTabWidget, QFrame, QTreeWidgetItem, QTreeWidget, QComboBox, QGroupBox,\
    QAction, QFont, QGridLayout, QMenuBar
else:
    from PySide2 import QtGui, QtCore, QtWidgets
    import shiboken2 as shiboken
    from PySide2.QtWidgets import QListWidgetItem, QDialog, QListWidget, QMainWindow, QWidget, QVBoxLayout, QLabel,\
    QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QAbstractItemView, QMenu, QMessageBox, QSplitter,\
    QScrollArea, QSizePolicy, QTextEdit, QApplication, QFileDialog, QCheckBox, QSlider,\
    QTabWidget, QFrame, QTreeWidgetItem, QTreeWidget, QComboBox, QGroupBox, QAction, QGridLayout, QMenuBar
    
    from PySide2.QtGui import QColor, QCursor, QBrush, QDoubleValidator, QIntValidator, QImage, QPixmap, QTransform,\
    QPaintEvent, QFont
    



class sgCmds:
    
    @staticmethod
    def getDagPath( inputTarget ):
        target = pymel.core.ls( inputTarget )[0]
        dagPath = OpenMaya.MDagPath()
        selList = OpenMaya.MSelectionList()
        selList.add( target.name() )
        try:
            selList.getDagPath( 0, dagPath )
            return dagPath
        except:
            obj = OpenMaya.MObject()
            selList.getDependNode( 0, obj )
            return obj



class WidgetInfo:
    
    def __init__(self, targetWidget ):
        
        self.targetWidget = targetWidget
        
        
    @staticmethod
    def makeFile( filePath ):
        
        dirPath = os.path.dirname( filePath )
        if not os.path.exists( dirPath ):
            os.makedirs( dirPath )
        if not os.path.exists( filePath ):
            f = open( filePath, 'w' ); f.close()
        
        f = open( filePath, 'r' )
        try:
            json.load( f )
            f.close()
        except:
            f.close()
            f = open( filePath, 'w' )
            json.dump( {}, f )
            f.close()
    
    
    @staticmethod
    def getData( filePath ):
        
        f = open( filePath, 'r' )
        data = json.load( f )
        f.close()
        
        if type( data ) != type( {} ):
            os.remove( filePath )
            WidgetInfo.makeFile( filePath )
            return WidgetInfo.getData( filePath )
        else:
            return data
    
    
    @staticmethod
    def setData( data, filePath ):
        
        f = open( filePath, 'w' )
        json.dump( data, f, indent=2 )
        f.close()
    
    

    def saveTransform( self, filePath, key ):
        
        WidgetInfo.makeFile( filePath )
        data = WidgetInfo.getData( filePath )
        
        posX = self.targetWidget.pos().x(); posY = self.targetWidget.pos().y()
        width  = self.targetWidget.width(); height = self.targetWidget.height()
        
        data[key] = {}
        data[key][ 'position' ] = [ posX, posY ]
        data[key][ 'size' ] = [ width, height ]
        
        WidgetInfo.setData( data, filePath )
    
    
    def loadTransform( self, filePath, key ):
        
        WidgetInfo.makeFile( filePath )
        data = WidgetInfo.getData( filePath )
        
        if not data.has_key( key ): return None
        
        try:
            posX,  posY   = data[key]['position']
            width, height = data[key]['size']
            self.targetWidget.move( posX, posY )
            self.targetWidget.resize( width, height )
        except:
            pass
    
    
    def saveText(self, filePath, key ):
        
        WidgetInfo.makeFile( filePath )
        data = WidgetInfo.getData( filePath )
        data[ key ] = self.targetWidget.text()
        WidgetInfo.setData( data, filePath )
    
    
    def loadText(self, filePath, key ):
        
        WidgetInfo.makeFile(filePath)
        data = WidgetInfo.getData( filePath )
        if not data.has_key( key ): return
        self.targetWidget.setText( data[ key ] )
    

    def saveItems(self, filePath, key ):
        
        WidgetInfo.makeFile( filePath )
        data = WidgetInfo.getData( filePath )
        data[ key ] = [ self.targetWidget.item(i).text() for i in range( self.targetWidget.count() ) ]
        WidgetInfo.setData( data, filePath )
    
    
    def loadItems(self, filePath, key ):
        
        WidgetInfo.makeFile( filePath )
        data = WidgetInfo.getData( filePath )
        if not data.has_key( key ): return
        self.targetWidget.clear()
        self.targetWidget.addItems( data[ key ] )
        




class Label_descriptionImage( QLabel ):
    
    try:descriptionImagePath = os.path.dirname( __file__ ) + '/img/tool_description.png'
    except:descriptionImagePath=""
    
    def __init__(self, *args, **kwargs ):
        
        super( Label_descriptionImage, self ).__init__( *args, **kwargs )
        
        self.setAlignment( QtCore.Qt.AlignCenter )
        
        if Label_descriptionImage.descriptionImagePath:
            frontImage = QImage()
            frontImage.load( Label_descriptionImage.descriptionImagePath )
            origWidth = frontImage.width()
            trValue = QTransform().scale( float(origWidth)/frontImage.width(), float(origWidth)/frontImage.width() )
            transformedImage = frontImage.transformed( trValue )
            pixmap     = QPixmap.fromImage( transformedImage )
            self.setPixmap( pixmap )
            self.setGeometry( 0,0, transformedImage.width() , transformedImage.height() )
            self.paintEvent(QPaintEvent(QtCore.QRect( 0,0,self.width(), self.height() )))





class MenuBar( QMenuBar ):
    
    def __init__(self, *args, **kwargs ):
        
        super( MenuBar, self ).__init__( *args, **kwargs )
        try:
            menu = self.addMenu( "&정보".decode( 'utf-8') )
            menu.addAction( "툴 정보".decode( 'utf-8'), self.loadToolTip )
        except:
            pass
    
    
    def loadToolTip(self ):
        
        try:
            self.dialog.deleteLater()
        except:
            pass
        
        self.dialog = QDialog( self )
        self.dialog.setWindowTitle( "툴 정보".decode( 'utf-8') )
        dialogLayout = QVBoxLayout( self.dialog )
        lb_description = Label_descriptionImage()
        dialogLayout.addWidget( lb_description )
        self.dialog.show()
    
        



class Widget_mesh( QWidget ):
    
    def __init__(self, *args, **kwargs ):
        
        title = ""
        if kwargs.has_key( "title" ):
            title = kwargs.pop( "title" )
        
        super( Widget_mesh, self ).__init__( *args, **kwargs )
        
        label = QLabel( title ); label.setFixedWidth( 90 )
        lineEdit = QLineEdit();
        button = QPushButton("Load"); button.setFixedWidth( 60 )
        
        mainLayout = QHBoxLayout( self ); mainLayout.setContentsMargins(0,0,0,0)
        mainLayout.addWidget( label )
        mainLayout.addWidget( lineEdit )
        mainLayout.addWidget( button )
        
        self.title = title
        self.lineEdit = lineEdit
        QtCore.QObject.connect( button, QtCore.SIGNAL( "clicked()" ), self.loadSelected )
        
        WidgetInfo( self.lineEdit ).loadText( Window.infoPath, 'Widget_mesh_%s_lineEdit' % title )
    
    
    def loadSelected(self):
        
        sels = [ target for target in cmds.ls( sl=1, type='transform' ) if cmds.listRelatives( target, s=1, type='mesh' ) ]
        if not sels: 
            self.lineEdit.setText('')
        else:
            self.lineEdit.setText( sels[0] )
        WidgetInfo( self.lineEdit ).saveText( Window.infoPath, 'Widget_mesh_%s_lineEdit' % self.title )
        



class GroupBox_targetMeshs( QGroupBox ):

    def __init__(self, *args, **kwargs ):
        
        title = ""
        if kwargs.has_key( "title" ):
            title = kwargs.pop( "title" )
        
        super( GroupBox_targetMeshs, self ).__init__( *args, **kwargs )
        self.setTitle( title )
        
        listWidget = QListWidget()
        button     = QPushButton( "Load Selected" )
        
        mainLayout = QVBoxLayout( self ); mainLayout.setSpacing( 0 )
        mainLayout.addWidget( listWidget )
        mainLayout.addWidget( button )
        
        self.title = title
        self.listWidget = listWidget
        QtCore.QObject.connect( button, QtCore.SIGNAL( "clicked()" ), self.loadSelected )
        
        WidgetInfo( self.listWidget ).loadItems( Window.infoPath, "GroupBox_targetMeshs_%s_listWidget" % title )
    
    
    def loadSelected(self):
        
        sels = [ target for target in cmds.ls( sl=1, type='transform' ) if cmds.listRelatives( target, s=1, type='mesh' ) ]
        self.listWidget.clear()
        self.listWidget.addItems( sels )
        WidgetInfo( self.listWidget ).saveItems( Window.infoPath, "GroupBox_targetMeshs_%s_listWidget" % self.title )





class Window( QDialog ):
    
    mayawin = shiboken.wrapInstance( long(OpenMayaUI.MQtUtil.mainWindow() ), QWidget )
    objectName = "sg_modeling_assign_modification_to_otherShapes"
    title = "Assign Modification to other shapes"
    infodir = cmds.about(pd=True) + "/sg/assign_modification_to_otherShapes"
    infoTransformPath = infodir + '/transformInfo.txt'
    infoPath = infodir + "/uiInfo.txt"
    
    size = [ 300, 100 ]
    
    def __init__(self, *args, **kwargs ):
        
        super( Window, self ).__init__( *args, **kwargs )
        self.installEventFilter( self )
        self.setObjectName( Window.objectName )
        self.setWindowTitle( Window.title )
        
        self.resize( *Window.size )
        WidgetInfo( self ).loadTransform( Window.infoTransformPath, "Window" )
        
        sep1 = QFrame();sep1.setFrameShape(QFrame.HLine)
        sep2 = QFrame();sep2.setFrameShape(QFrame.HLine)
        
        menubar = MenuBar()
        wdg_mesh_orig = Widget_mesh( title="Original Mesh : " )
        wdg_mesh_modified = Widget_mesh( title="Modified Mesh : " )
        gb_targets = GroupBox_targetMeshs( title="Target Meshs" )
        bt_transform = QPushButton( "Transform" )
        
        
        mainLayout = QVBoxLayout( self ); mainLayout.setSpacing(5)
        mainLayout.addWidget( menubar )
        mainLayout.addWidget( sep1 )
        mainLayout.addWidget( wdg_mesh_orig )
        mainLayout.addWidget( wdg_mesh_modified )
        mainLayout.addWidget( sep2 )
        mainLayout.addWidget( gb_targets )
        mainLayout.addWidget( bt_transform )
        
        QtCore.QObject.connect( bt_transform, QtCore.SIGNAL('clicked()'), self.cmd_transform )

        self.wdg_mesh_orig = wdg_mesh_orig
        self.wdg_mesh_modified = wdg_mesh_modified
        self.gb_targets = gb_targets 


    def eventFilter(self, *args, **kwargs ):
        event = args[1]
        if event.type() in [ QtCore.QEvent.Resize, QtCore.QEvent.Move ]:
            WidgetInfo( self ).saveTransform( Window.infoTransformPath, "Window" )


    def cmd_transform(self):
        
        cmds.undoInfo( ock=1 )
        origMesh =  pymel.core.ls( self.wdg_mesh_orig.lineEdit.text() )[0].getShape()
        modifiedMesh = pymel.core.ls( self.wdg_mesh_modified.lineEdit.text() )[0].getShape()
        targetMeshs = [ pymel.core.ls( self.gb_targets.listWidget.item( i ).text() )[0].getShape() for i in range( self.gb_targets.listWidget.count() ) ]
        
        fnOrig = OpenMaya.MFnMesh( sgCmds.getDagPath( origMesh ) )
        fnModified = OpenMaya.MFnMesh( sgCmds.getDagPath( modifiedMesh ) )
        
        numVertices = fnOrig.numVertices()
        if fnModified.numVertices() != numVertices:
            cmds.error( "Orig and modified has no same number of vertices" );return None
        
        origPoints = OpenMaya.MPointArray()
        modifiedPoints = OpenMaya.MPointArray()
        offsetPoints = OpenMaya.MVectorArray()
        
        fnOrig.getPoints( origPoints )
        fnModified.getPoints( modifiedPoints )
        
        offsetPoints.setLength( origPoints.length() )
        for i in range( offsetPoints.length() ):
            offsetPoints.set( modifiedPoints[i] - origPoints[i], i )
        
        for targetMesh in targetMeshs:
            fnTarget = OpenMaya.MFnMesh( sgCmds.getDagPath( targetMesh ) )
            if fnTarget.numVertices() != numVertices: 
                cmds.warning( "%s has no same number of vertices with Orig mesh")
                continue
            for i in range( offsetPoints.length() ):
                vtxName = targetMesh + '.vtx[%d]' % i
                cmds.move( offsetPoints[i].x, offsetPoints[i].y, offsetPoints[i].z, vtxName, os=1, r=1 )
        cmds.undoInfo( cck=1 )


def show():
    
    mainwins = Window.mayawin.findChildren( QDialog, Window.objectName )
    if mainwins: map( lambda x : x.deleteLater(), mainwins )
    Window( Window.mayawin ).show()


if __name__ == '__main__':
    show()

