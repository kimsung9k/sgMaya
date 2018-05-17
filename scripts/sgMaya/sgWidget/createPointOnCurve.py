import maya.OpenMayaUI
import os
import json


from maya import cmds

if int( cmds.about( v=1 ) ) < 2017:
    from PySide import QtGui, QtCore
    import shiboken
    from PySide.QtGui import QListWidgetItem, QDialog, QListWidget, QMainWindow, QWidget, QColor, QLabel,\
    QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QAbstractItemView, QMenu,QCursor, QMessageBox, QBrush, QSplitter,\
    QScrollArea, QSizePolicy, QTextEdit, QApplication, QFileDialog, QCheckBox, QDoubleValidator, QSlider, QIntValidator,\
    QImage, QPixmap, QTransform, QPaintEvent, QTabWidget, QFrame, QTreeWidgetItem, QTreeWidget, QComboBox, QGroupBox, QAction,\
    QFont, QGridLayout, QProgressBar, QIcon
else:
    from PySide2 import QtGui, QtCore, QtWidgets
    import shiboken2 as shiboken
    from PySide2.QtWidgets import QListWidgetItem, QDialog, QListWidget, QMainWindow, QWidget, QVBoxLayout, QLabel,\
    QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QAbstractItemView, QMenu, QMessageBox, QSplitter,\
    QScrollArea, QSizePolicy, QTextEdit, QApplication, QFileDialog, QCheckBox, QSlider,\
    QTabWidget, QFrame, QTreeWidgetItem, QTreeWidget, QComboBox, QGroupBox, QAction, QGridLayout, QProgressBar
    
    from PySide2.QtGui import QColor, QCursor, QBrush, QDoubleValidator, QIntValidator, QImage, QPixmap, QTransform,\
    QPaintEvent, QFont, QIcon




def makeFolder( pathName ):
    if os.path.exists( pathName ):return None
    os.makedirs( pathName )
    return pathName




def makeFile( filePath ):
    if os.path.exists( filePath ): return None
    filePath = filePath.replace( "\\", "/" )
    splits = filePath.split( '/' )
    folder = '/'.join( splits[:-1] )
    makeFolder( folder )
    f = open( filePath, "w" )
    f.close()




class Window_global:
    
    mayaWin = shiboken.wrapInstance( long( maya.OpenMayaUI.MQtUtil.mainWindow() ), QWidget )
    objectName = "sgui_createPointOnCurve"
    title = "Create Point On Curve"
    width = 350
    height = 50
    
    infoPath = cmds.about(pd=True) + "/sg/createPointOnCurve/uiInfo.txt"
    infoPath2 = cmds.about( pd=True ) + '/sg/createPointOnCurve/uiInfo2.txt'
    makeFile( infoPath )
    
    mainGui = QMainWindow()
    listItems = []
    

    @staticmethod
    def saveInfo( filePath = None ):
        
        if not filePath:
            filePath = Window_global.infoPath
        
        posX = Window_global.mainGui.pos().x()
        posY = Window_global.mainGui.pos().y()
        width  = Window_global.mainGui.width()
        height = Window_global.mainGui.height()
        
        f = open( filePath, "w" )
        json.dump( [posX, posY, width, height ], f, True, False, False )
        f.close()
    
    
    @staticmethod
    def loadInfo( filePath = None ):
        
        if not filePath:
            filePath = Window_global.infoPath
        
        f = open( filePath, 'r')
        try:data = json.load( f )
        except: f.close(); return None
        f.close()
    
        if not data: return None
        
        try:
            posX = data[0]
            posY = data[1]
            width = data[2]
            height = data[3]
            
            Window_global.mainGui.resize( width, height )
            
            desktop = QApplication.desktop()
            desktopWidth = desktop.width()
            desktopHeight = desktop.height()
            if posX + width > desktopWidth: posX = desktopWidth - width
            if posY + height > desktopWidth: posY = desktopHeight - height
            if posX < 0 : posX = 0
            if posY < 0 : posY = 0
            
            Window_global.mainGui.move( posX, posY )
        except:
            pass



class Functions:
    
    @staticmethod
    def setButtonEnabled( evt=0 ):
        
        curveExists = False
        
        sels = cmds.ls( sl=1 )
        for sel in sels:
            if cmds.nodeType( sel ) in ['transform', 'joint']:
                selShape = cmds.listRelatives( sel, s=1, type='nurbsCurve' )
                if not selShape: continue
                curveExists = True
            elif cmds.nodeType( sel ) == 'nurbsCurve':
                curveExists = True
        Window_global.button.setEnabled( curveExists )
    
    
    @staticmethod
    def setAngleEnabled( evt=0 ):
        
        if Window_global.checkBox.isChecked():
            Window_global.leVx.setEnabled( True )
            Window_global.leVy.setEnabled( True )
            Window_global.leVz.setEnabled( True )
        else:
            Window_global.leVx.setEnabled( False )
            Window_global.leVy.setEnabled( False )
            Window_global.leVz.setEnabled( False )
    
    
    @staticmethod
    def createPointOnCurve( evt=0 ):

        from maya import OpenMaya

        def getFnCurve( curveShape ):
            selList = OpenMaya.MSelectionList()
            selList.add( curveShape )
            dagPath = OpenMaya.MDagPath()
            selList.getDagPath( 0, dagPath )
            return OpenMaya.MFnNurbsCurve( dagPath )


        import pymel.core

        sliderValue = Window_global.slider.value()
        sels = cmds.ls( sl=1 )
        curveShapes = []
        for sel in sels:
            if cmds.nodeType( sel ) in ['transform', 'joint']:
                selShapes = cmds.listRelatives( sel, s=1, f=1, type='nurbsCurve' )
                if not selShapes: continue
                for selShape in selShapes:
                    if cmds.getAttr( selShape + '.io' ): continue
                    curveShapes.append( selShape )
            elif cmds.nodeType( sel ) == 'nurbsCurve':
                curveShapes.append( sel )
        
        eachParamValue = 1.0
        if sliderValue == 1:
            addParamValue = 0.5
        else:
            addParamValue = 0.0
            eachParamValue = 1.0/(sliderValue-1)

        cmds.undoInfo( ock=1 )
        for curveShape in curveShapes:
            fnCurve = getFnCurve( curveShape )
            curveLength = fnCurve.length()
            minParam = fnCurve.findParamFromLength( 0 )
            maxParam = fnCurve.findParamFromLength( curveLength )

            for i in range( sliderValue ):
                curveInfo = cmds.createNode( 'pointOnCurveInfo' )
                cmds.connectAttr( curveShape + '.worldSpace', curveInfo+'.inputCurve' )
                trNode = cmds.createNode( 'transform' )
                currentParam = fnCurve.findParamFromLength( ( eachParamValue * i + addParamValue ) * curveLength )
                cmds.addAttr( trNode, ln='param', dv=currentParam, min=minParam, max=maxParam )
                cmds.setAttr( trNode + '.param', e=1, k=1 )
                cmds.setAttr( trNode + '.dh', 1 )
                compose = cmds.createNode( 'composeMatrix' )
                multMtx = cmds.createNode( 'multMatrix' )
                dcmp = cmds.createNode( 'decomposeMatrix' )
                cmds.connectAttr( curveInfo + '.position', compose + '.it' )
                cmds.connectAttr( compose + '.outputMatrix', multMtx + '.i[0]' )
                cmds.connectAttr( trNode + '.pim', multMtx + '.i[1]' )
                cmds.connectAttr( multMtx + '.o', dcmp + '.imat' )
                cmds.connectAttr( dcmp + '.ot', trNode + '.t' )
                cmds.connectAttr( trNode + '.param', curveInfo + '.parameter' )

                if not Window_global.checkBox.isChecked(): continue
                curveInfo = pymel.core.ls( curveInfo )[0]
                angleNode = pymel.core.createNode( 'angleBetween' )
                vectorNode = pymel.core.createNode( 'vectorProduct' )
                trNode = pymel.core.ls( trNode )[0]
                vectorNode.operation.set(3)
                valueX = float( Window_global.leVx.text() )
                valueY = float( Window_global.leVy.text() )
                valueZ = float( Window_global.leVz.text() )
                angleNode.vector1X.set( valueX )
                angleNode.vector1Y.set( valueY )
                angleNode.vector1Z.set( valueZ )
                curveInfo.tangent >> vectorNode.input1
                trNode.pim >> vectorNode.matrix
                vectorNode.output >> angleNode.vector2
                angleNode.euler >> trNode.r
                
        cmds.undoInfo( cck=1 )
    
        




class Window( QMainWindow ):
    
    def __init__(self, *args, **kwargs ):
        
        self.minimum = 1
        self.maximum = 100
        self.lineEditMaximum = 10000
        
        QMainWindow.__init__( self, *args, **kwargs )
        self.installEventFilter( self )
        #self.setWindowFlags( QtCore.Qt.Drawer )
        self.setWindowTitle( Window_global.title )
        
        widgetMain = QWidget()
        layoutVertical = QVBoxLayout( widgetMain )
        self.setCentralWidget( widgetMain )
        
        layoutSlider = QHBoxLayout()
        lineEdit     = QLineEdit(); lineEdit.setFixedWidth( 100 )
        lineEdit.setText( str( 1 ) )
        validator    = QIntValidator(self.minimum, self.lineEditMaximum, self)
        lineEdit.setValidator( validator )
        slider       = QSlider(); slider.setOrientation( QtCore.Qt.Horizontal )
        slider.setMinimum( self.minimum )
        slider.setMaximum( self.maximum )
        layoutSlider.addWidget( lineEdit )
        layoutSlider.addWidget( slider )
        layoutAngle = QVBoxLayout()
        checkBox = QCheckBox( 'Connect Angle By Tangent' )
        layoutVector = QHBoxLayout()
        leVx = QLineEdit(); leVx.setText( str( 1.000 ) ); leVx.setEnabled( False )
        leVx.setValidator( QDoubleValidator( -100, 100, 5, self ) )
        leVy = QLineEdit(); leVy.setText( str( 0.000 ) ); leVy.setEnabled( False )
        leVy.setValidator( QDoubleValidator( -100, 100, 5, self ) )
        leVz = QLineEdit(); leVz.setText( str( 0.000 ) ); leVz.setEnabled( False )
        leVz.setValidator( QDoubleValidator( -100, 100, 5, self ) )
        layoutAngle.addWidget( checkBox )
        layoutAngle.addLayout( layoutVector )
        layoutVector.addWidget( leVx ); layoutVector.addWidget( leVy ); layoutVector.addWidget( leVz )
        button       = QPushButton( 'Create' )
        
        layoutVertical.addLayout( layoutSlider )
        layoutVertical.addLayout( layoutAngle )
        layoutVertical.addWidget( button )
        
        QtCore.QObject.connect( slider, QtCore.SIGNAL('valueChanged(int)'),   self.sliderValueChanged )
        QtCore.QObject.connect( lineEdit, QtCore.SIGNAL('textEdited(QString)'), self.lineEditValueChanged )
        QtCore.QObject.connect( button, QtCore.SIGNAL('clicked()'), Functions.createPointOnCurve )
        QtCore.QObject.connect( checkBox, QtCore.SIGNAL( 'clicked()'), Functions.setAngleEnabled )
        self.slider = slider
        self.lineEdit = lineEdit
        
        Window_global.slider = slider
        Window_global.button = button
        Window_global.checkBox = checkBox
        Window_global.leVx = leVx
        Window_global.leVy = leVy
        Window_global.leVz = leVz
        
    
    def sliderValueChanged( self, value, evt=0 ):
        
        self.lineEdit.setText( str(value) )
    
    
    def lineEditValueChanged(self, value, evt=0 ):
        
        if value:
            self.slider.setValue( int( value ) )
    
    
    def eventFilter( self, *args, **kwargs):
        event = args[1]
        if event.type() in [QtCore.QEvent.LayoutRequest,QtCore.QEvent.Move,QtCore.QEvent.Resize] :
            Window_global.saveInfo()




def show( evt=0 ):
    
    if cmds.window( Window_global.objectName, ex=1 ):
        cmds.deleteUI( Window_global.objectName )
    
    Window_global.mainGui = Window(Window_global.mayaWin)
    Window_global.mainGui.setObjectName( Window_global.objectName )
    Window_global.mainGui.resize( Window_global.width, Window_global.height )
    
    Window_global.loadInfo()
    Window_global.mainGui.show()




if __name__ == '__main__':
    show()




