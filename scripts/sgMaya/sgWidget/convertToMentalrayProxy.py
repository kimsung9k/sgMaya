#coding=utf-8

from maya import cmds, mel, OpenMaya
import pymel.core
import ntpath, os, shutil

plugins = ['AbcExport', 'AbcImport', 'gpuCache', 'Mayatomr']

for plugin in plugins:
    if not cmds.pluginInfo( plugin, q=1, l=1 ):
        cmds.loadPlugin( plugin )




class BaseCommands:
    
    @staticmethod
    def getAttrInfo( inputTargetAttr ):

        inputAttrInfo = {}
    
        targetAttr = pymel.core.ls( inputTargetAttr )[0]
        
        inputAttrInfo['shortName'] = targetAttr.shortName()
        inputAttrInfo['longName']  = targetAttr.longName()
        inputAttrInfo['type']    = targetAttr.type()
        inputAttrInfo['keyable'] = targetAttr.isKeyable()
        inputAttrInfo['channelBox'] = targetAttr.isInChannelBox()
        inputAttrInfo['lock'] = targetAttr.isLocked()
        inputAttrInfo['range'] = targetAttr.getRange()
        inputAttrInfo['defaultValue'] = pymel.core.attributeQuery( inputTargetAttr.attrName(), node=inputTargetAttr.node(), ld=1 )[0]
        
        def enumCmp( first, second ):
            if first[-1] < second[-1]:
                return -1
            elif first[-1] > second[-1]:
                return 1
            else:
                return 0
        
        if targetAttr.type() == 'enum':
            items = [ [ key, value ] for key, value in targetAttr.getEnums().items() ]
            items.sort( enumCmp )
            print "enum items : ", items
            inputAttrInfo['enums'] = items
        
        return inputAttrInfo
    
    
    @staticmethod
    def createAttrByAttrInfo( attrInfo, inputNode ):
        
        node = pymel.core.ls( inputNode )[0]
        
        if attrInfo.has_key( 'enums' ):
            en = ':'.join( [ key for key, value in attrInfo['enums'] ] ) + ':'
            BaseCommands.addAttr( node, ln= attrInfo['longName'], sn= attrInfo['shortName'], at=attrInfo['type'],  en=en, dv=attrInfo['defaultValue'] )
        else:
            BaseCommands.addAttr( node, ln= attrInfo['longName'], sn= attrInfo['shortName'], at=attrInfo['type'], dv=attrInfo['defaultValue'] )
            
        nodeAttr = node.attr( attrInfo['longName'] )
        if attrInfo['type'] in [ 'double', 'long', 'doubleAngle', 'short' ]:
            nodeAttr.setRange( attrInfo['range'] )
        if attrInfo['channelBox']:
            nodeAttr.showInChannelBox(True)
        if attrInfo['keyable']:
            nodeAttr.setKeyable(True)
        if attrInfo['lock']:
            nodeAttr.set( lock=1 )
    
    
    @staticmethod
    def addAttr( target, **options ):
    
        items = options.items()
        
        attrName = ''
        channelBox = False
        keyable = False
        for key, value in items:
            if key in ['ln', 'longName']:
                attrName = value
            elif key in ['cb', 'channelBox']:
                channelBox = True
                options.pop( key )
            elif key in ['k', 'keyable']:
                keyable = True 
                options.pop( key )
        
        if pymel.core.attributeQuery( attrName, node=target, ex=1 ): return None
        
        pymel.core.addAttr( target, **options )
        
        if channelBox:
            pymel.core.setAttr( target+'.'+attrName, e=1, cb=1 )
        elif keyable:
            pymel.core.setAttr( target+'.'+attrName, e=1, k=1 )




class TransformKeep:
    
    def __init__( self, inputTarget ):
        
        import pymel.core
        
        self.target = pymel.core.ls( inputTarget )[0]
        self.t = self.target.t.get()
        self.r = self.target.r.get()
        self.s = self.target.s.get()
        self.sh = self.target.sh.get()
        self.rotatePivot = self.target.rotatePivot.get()
        self.scalePivot = self.target.scalePivot.get()
        self.rotatePivotTranslate = self.target.rotatePivotTranslate.get()
        self.scalePivotTranslate = self.target.scalePivotTranslate.get()
        
        self.parent = self.target.getParent()


    def setToDefault(self):
        
        self.target.setParent( w=1 )

        self.cons = self.target.listConnections( s=1, d=0, p=1, c=1 )
        for origCon, dstCon in self.cons:
            dstCon // origCon

        self.target.t.set( 0,0,0 )
        self.target.r.set( 0,0,0 )
        self.target.s.set( 1,1,1 )
        self.target.sh.set( 0,0,0 )
        self.target.rotatePivot.set( 0,0,0 )
        self.target.scalePivot.set( 0,0,0 )
        self.target.rotatePivotTranslate.set( 0,0,0 )
        self.target.scalePivotTranslate.set( 0,0,0 )


    def setToOrig(self):
        
        if self.parent:self.target.setParent( self.parent )
        
        self.target.t.set( self.t )
        self.target.r.set( self.r )
        self.target.s.set( self.s )
        self.target.sh.set( self.sh )
        self.target.rotatePivot.set( self.rotatePivot )
        self.target.scalePivot.set( self.scalePivot )
        self.target.rotatePivotTranslate.set( self.rotatePivotTranslate )
        self.target.scalePivotTranslate.set( self.scalePivotTranslate )
        
        for origCon, dstCon in self.cons:
            dstCon >> origCon
    
    
    def setToOther( self, inputOther ):
        
        other = pymel.core.ls( inputOther )[0]
        origParent = other.getParent()
        if self.parent:
            try:other.setParent( self.parent )
            except:pass
        else:
            other.setParent( w=1 )
        other.t.set( self.t )
        other.r.set( self.r )
        other.s.set( self.s )
        other.sh.set( self.sh )
        other.rotatePivot.set( self.rotatePivot )
        other.scalePivot.set( self.scalePivot )
        other.rotatePivotTranslate.set( self.rotatePivotTranslate )
        other.scalePivotTranslate.set( self.scalePivotTranslate )
        if origParent:
            try:other.setParent( origParent )
            except:pass




def convertToOrig( target ):
    
    if not pymel.core.attributeQuery( 'origObjectPath', node=target, ex=1 ): return
    origObjectPath = target.attr( 'origObjectPath' ).get()
    namespace = 'scene_optimizeElement'
    cmds.file( origObjectPath, i=1, type="mayaBinary", ignoreVersion=1, ra=True, mergeNamespacesOnClash=False, namespace=namespace, options="v=0;", pr=1 )
    pymel.core.refresh()
    
    def getTopTransformNodes():
        trs = cmds.ls( type='transform' )
        topTransforms = []
        for tr in trs:
            if cmds.listRelatives( tr, p=1 ): continue
            topTransforms.append( pymel.core.ls( tr )[0] )
        return topTransforms
    
    topTrNodes = getTopTransformNodes()
    
    targetTopTrNode = None
    for topTrNode in topTrNodes:
        if topTrNode.find( namespace ) == -1: continue
        targetTopTrNode = topTrNode
        break

    if target.getParent():
        targetTopTrNode.setParent( target.getParent() )

    targetName = target.nodeName()
    trKeep = TransformKeep( target )    
    trKeep.setToOther( targetTopTrNode )
  
    namespace = ':'.join( topTrNode.split( ':' )[:-1] )
    for nstarget in pymel.core.ls( namespace + ':*' ):
        nstarget.rename( nstarget.replace( namespace + ':', '' ) )
    topTrNode.rename( targetName )
    cmds.namespace( removeNamespace = namespace )
    try:
        topTrNode.lodv.set( 1 )
    except:
        pass
    
    try:
        target.attr( 'lodVisibility' ).set( 0 )
    except:pass
    try:
        target.attr( 'v' ).set( 0 )
    except:pass
    
    return topTrNode



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


import json
from maya import OpenMayaUI


class Widget_file_control:
    
    @staticmethod
    def makeFolder( pathName ):
        if os.path.exists( pathName ):return None
        os.makedirs( pathName )
        return pathName


    @staticmethod
    def makeFile( filePath ):
        if os.path.exists( filePath ): return None
        filePath = filePath.replace( "\\", "/" )
        splits = filePath.split( '/' )
        folder = '/'.join( splits[:-1] )
        Widget_file_control.makeFolder( folder )
        f = open( filePath, "w" )
        json.dump( {}, f )
        f.close()

    
    @staticmethod
    def writeData( data, filePath ):
        Widget_file_control.makeFile( filePath )
        f = open( filePath, 'w' )
        json.dump( data, f, indent=2 )
        f.close()
    
    
    @staticmethod
    def readData( filePath ):
        Widget_file_control.makeFile( filePath )
        
        f = open( filePath, 'r' )
        data = {}
        try:
            data = json.load( f )
        except:
            pass
        f.close()
        
        return data




class Dialog_ImportOriginal( QDialog ):

    parent_widget = shiboken.wrapInstance( long( OpenMayaUI.MQtUtil.mainWindow() ), QWidget )
    
    objectName = "Dialog_ImportOriginal"
    title = "Pingo - Convert to Mentalay Proxy"
    defaultWidth = 300
    defaultHeight = 30
    
    path_uiInfo = cmds.about( pd=1 ) + "/pingo/Dialog_ConvertMentalayProxy/uiInfo.json"


    def __init__(self, *args, **kwargs ):
        
        existing_widget = Dialog_ImportOriginal.parent_widget.findChildren( QDialog, Dialog_ImportOriginal.objectName )
        if existing_widget: map( lambda x : x.deleteLater(), existing_widget )
        
        QDialog.__init__( self, Dialog_ImportOriginal.parent_widget, **kwargs )
        self.installEventFilter( self )
        
        layout_main = QVBoxLayout( self )
        button_toOrig  = QPushButton( "Import orig" )
        
        layout_main.addWidget( button_toOrig )
        
        self.setWindowTitle( Dialog_ImportOriginal.title )
        self.setObjectName( Dialog_ImportOriginal.objectName )
        self.resize( Dialog_ImportOriginal.defaultWidth, Dialog_ImportOriginal.defaultHeight )
        self.load_info()
        self.show()
        
        QtCore.QObject.connect( button_toOrig, QtCore.SIGNAL( 'clicked()'  ), self.convertToOrig )

    
    def convertToOrig(self):
        
        cmds.undoInfo( ock=1 )
        sels = pymel.core.ls( sl=1 )
        for sel in sels:
            convertToOrig( sel )
        cmds.undoInfo( cck=1 )



    def save_info(self):
        
        data = Widget_file_control.readData( Dialog_ImportOriginal.path_uiInfo )
        data['x'] = self.x()
        data['y'] = self.y()
        data['width']  = self.width()
        data['height'] = self.height()
        Widget_file_control.writeData( data, Dialog_ImportOriginal.path_uiInfo )



    def load_info(self):
        
        data = Widget_file_control.readData( Dialog_ImportOriginal.path_uiInfo )
        try:
            x = data['x']
            y = data['y']
            width  = data['width']
            height = data['height']
        except:
            return
        self.move( x, y )
        self.resize( width, height )



    def eventFilter(self, *args, **kwargs ):

        event = args[1]
        if event.type() in [ QtCore.QEvent.Resize, QtCore.QEvent.Move ]:
            self.save_info()


def show():
    Dialog_ImportOriginal().show()


if __name__ == '__main__':
    Dialog_ImportOriginal().show()





