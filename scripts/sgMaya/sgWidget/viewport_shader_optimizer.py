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
        QFont, QGridLayout
else:
    from PySide2 import QtGui, QtCore, QtWidgets
    import shiboken2 as shiboken
    from PySide2.QtWidgets import QListWidgetItem, QDialog, QListWidget, QMainWindow, QWidget, QVBoxLayout, QLabel, \
        QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QAbstractItemView, QMenu, QMessageBox, QSplitter, \
        QScrollArea, QSizePolicy, QTextEdit, QApplication, QFileDialog, QCheckBox, QSlider, \
        QTabWidget, QFrame, QTreeWidgetItem, QTreeWidget, QComboBox, QGroupBox, QAction, QGridLayout

    from PySide2.QtGui import QColor, QCursor, QBrush, QDoubleValidator, QIntValidator, QImage, QPixmap, QTransform, \
        QPaintEvent, QFont



path_uiInfo_basedir = cmds.about(pd=1) + "/pingo/viewport_shader_optimizer"

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




class Cmds_mainCommands:

    @staticmethod
    def getShadingEngines(mesh):
        shadingEngines = mesh.getShape().listConnections(s=0, d=1, type='shadingEngine')
        return shadingEngines

    @staticmethod
    def get_csv_form_google_spreadsheets(link_attributeList, targetPath):
        import re, urllib, urllib2, os, ssl
        p = re.compile('/d/.+/')
        m = p.search(link_attributeList)
        id_sheet = m.group()[3:-1]
        dirPath = os.path.dirname(targetPath)
        if not os.path.exists(dirPath): os.makedirs(dirPath)
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

    @staticmethod
    def get_dictdata_from_csvPath( csvPath ):

        csvData = []
        import csv
        f = open(csvPath, 'r')
        rdr = csv.reader(f)
        for line in rdr:
            csvData.append(line)
        f.close()

        dictData = {}
        for i in range(1, len(csvData)):
            name_shader = csvData[i][0]
            dictData[name_shader] = {}
            for j in range(1, len(csvData[i])):
                type_of_attr = csvData[0][j]
                dictData[name_shader][type_of_attr] = csvData[i][j]
        return dictData


    @staticmethod
    def getRendererListFromURL( rendererTypeUrl ):

        path_csv_seAttrs = path_uiInfo_basedir + '/shadingEngineAttrList.csv'
        Cmds_mainCommands.get_csv_form_google_spreadsheets(rendererTypeUrl, path_csv_seAttrs)
        if not os.path.exists(path_csv_seAttrs):
            cmds.error("%s is not exists" % path_csv_seAttrs)
        dict_seAttrs = Cmds_mainCommands.get_dictdata_from_csvPath(path_csv_seAttrs)
        return dict_seAttrs



    @staticmethod
    def convertToLambert( targetShader, dict_shaderAttrs, dict_removeTargets ):

        from maya import cmds
        cmds.undoInfo( ock=1 )

        from pymel.core.general import Attribute as pm_Attribute

        def isDoNotDeleteTarget(node):
            for attr in ['wm', 'expression']:
                if pymel.core.attributeQuery(attr, node=node, ex=1): return True
            return False

        def getSourceConnectDuplicated(target, attrName):

            def duplicateShadingNetwork(node):
                checkNodes = node.history()
                disconnectedList = []
                for checkNode in checkNodes:
                    if isDoNotDeleteTarget(checkNode): continue
                    nodeSrcCons = checkNode.listConnections(s=1, d=0, p=1, c=1)
                    for origAttr, srcAttr in nodeSrcCons:
                        srcNode = srcAttr.node()
                        if not isDoNotDeleteTarget(srcNode): continue
                        srcAttr // origAttr
                        disconnectedList.append((srcAttr, origAttr))

                duNodes = pymel.core.duplicate( node, un=1 )
                duNode = duNodes[0]

                origHistory = node.history()
                duHistory = duNode.history()

                for srcAttr, origAttr in disconnectedList:
                    srcAttr >> origAttr
                    historyIndex = origHistory.index(origAttr.node())
                    srcAttr >> duHistory[historyIndex].attr(origAttr.longName())
                return duNode

            if not attrName: return None
            connections = target.attr(attrName).listConnections(s=1, d=0, p=1, c=1)
            if connections:
                for origCon, srcCon in connections:
                    duNode = duplicateShadingNetwork(srcCon.node())
                    return duNode.attr(srcCon.longName())
            return target.attr(attrName).get()

        def connecToViewportShader(resultS, resultV, attr_sTrg, attr_vTrg, targetShader, outputShader):

            if attr_sTrg and attr_vTrg:
                if resultS:
                    if isinstance(resultS, pm_Attribute):
                        resultS >> targetShader.attr(attr_sTrg)
                    else:
                        try:
                            targetShader.attr(attr_sTrg).set(resultS)
                        except:
                            cmds.warning("%s can not change the value." % targetShader.attr(attr_sTrg).name())
                if resultV:
                    if isinstance(resultV, pm_Attribute):
                        resultV >> targetShader.attr(attr_vTrg)
                    else:
                        try:
                            targetShader.attr(attr_vTrg).set(resultV)
                        except:
                            cmds.warning("%s can not change the value." % targetShader.attr(attr_vTrg).name())
            elif attr_sTrg:
                if resultS:
                    if isinstance(resultS, pm_Attribute):
                        resultS >> targetShader.attr(attr_sTrg)
                    else:
                        try:
                            targetShader.attr(attr_sTrg).set(resultS)
                        except:
                            cmds.warning("%s can not change the value." % targetShader.attr(attr_sTrg).name())
            elif attr_vTrg:
                if resultV:
                    if isinstance(resultV, pm_Attribute):
                        resultV >> targetShader.attr(attr_vTrg)
                    else:
                        try:
                            targetShader.attr(attr_vTrg).set(resultV)
                        except:
                            cmds.warning("%s can not change the value." % targetShader.attr(attr_vTrg).name())
                elif resultS:
                    if isinstance(resultS, pm_Attribute):
                        revNode = pymel.core.createNode('reverse')
                        [resultS >> revNode.attr(attr) for attr in ['inputX', 'inputY', 'inputZ']]
                        revNode.output >> targetShader.attr(attr_vTrg)
                    else:
                        try:
                            targetShader.attr(attr_vTrg).set([resultS, resultS, resultS])
                        except:
                            cmds.warning("%s can not change the value." % targetShader.attr(attr_vTrg).name())

        if targetShader.nodeType() == 'lambert':
            newShader = targetShader
        else:
            newShader = pymel.core.shadingNode( 'lambert', asShader=1, n='lambert_' + targetShader.name()  )
            for attr in ['color', 'transparency']:
                attr_en_output = dict_shaderAttrs[targetShader.nodeType()]['%s(en)' % attr]
                attr_scala_output = dict_shaderAttrs[targetShader.nodeType()]['%s(a)' % attr]
                attr_vector_output = dict_shaderAttrs[targetShader.nodeType()]['%s(rgb)' % attr]
                attr_scala_viewport = dict_shaderAttrs[newShader.nodeType()]['%s(a)' % attr]
                attr_vector_viewport = dict_shaderAttrs[newShader.nodeType()]['%s(rgb)' % attr]
                if attr_en_output and not targetShader.attr(attr_en_output).get(): continue
                resultScala  = getSourceConnectDuplicated(targetShader, attr_scala_output)
                resultVector = getSourceConnectDuplicated(targetShader, attr_vector_output)
                connecToViewportShader(resultScala, resultVector, attr_scala_viewport, attr_vector_viewport,
                                       newShader, targetShader )
                shadingEngineCons = targetShader.listConnections( s=0, d=1, type='shadingEngine', p=1 )
                if not shadingEngineCons: continue
                newShader.attr( 'outColor' ) >> shadingEngineCons[0]

        hists = newShader.listHistory()
        for hist in hists:
            nodeType = hist.nodeType()
            if not dict_removeTargets.has_key( nodeType ): continue
            inputAttr = dict_removeTargets[nodeType]['attr_input']
            outputAttr = dict_removeTargets[nodeType]['attr_output']

            destAttrCons = hist.attr( outputAttr ).listConnections( s=0, d=1, p=1 )
            srcAttrCons  = hist.attr( inputAttr ).listConnections( s=1, d=0, p=1 )

            if not destAttrCons: continue
            if srcAttrCons:
                srcAttrCons[0] >> destAttrCons[0]
            else:
                try:destAttrCons[0].set( hist.attr( inputAttr ).get() )
                except:pass

        cmds.undoInfo(cck=1)

        return newShader


    @staticmethod
    def separateViewportShader( shadingEngine, rendererType, dict_seAttrs, resolusion=None ):

        try: resolusion = int( resolusion )
        except: resolusion = None

        def separateShader(shadingEngine, dict_seAttrs, renderType):

            def connectShaderToEngine(shader, shadingEngine, shaderOutputName, shaderInputName):
                pymel.core.defaultNavigation(ce=1, source=shader.attr( shaderOutputName ), destination=shadingEngine.attr( shaderInputName ))

            def duplicateShadingNetwork(node, **options ):

                def isDoNotDeleteTarget(node):
                    for attr in ['wm', 'expression']:
                        if pymel.core.attributeQuery(attr, node=node, ex=1): return True
                    return False

                checkNodes = node.history()
                disconnectedList = []
                for checkNode in checkNodes:
                    if isDoNotDeleteTarget(checkNode): continue
                    nodeSrcCons = checkNode.listConnections(s=1, d=0, p=1, c=1)
                    for origAttr, srcAttr in nodeSrcCons:
                        srcNode = srcAttr.node()
                        if not isDoNotDeleteTarget(srcNode): continue
                        srcAttr // origAttr
                        disconnectedList.append((srcAttr, origAttr))

                options.update( {'un':1} )
                try:duNodes = pymel.core.duplicate(node, **options )
                except: return node
                duNode = duNodes[0]

                origHistory = node.history()
                duHistory = duNode.history()

                for srcAttr, origAttr in disconnectedList:
                    srcAttr >> origAttr
                    historyIndex = origHistory.index(origAttr.node())
                    pymel.core.connectAttr(srcAttr, duHistory[historyIndex] + '.' + origAttr.longName())
                return duNode


            def getSourceConnectDuplicated(target, attrName):

                if not attrName: return None
                connections = target.attr(attrName).listConnections(s=1, d=0, p=1, c=1)
                if connections:
                    for origCon, srcCon in connections:
                        duNode = duplicateShadingNetwork(srcCon.node())
                        return duNode.attr(srcCon.longName())
                return target.attr(attrName).get()

            viewportShader = None
            outputShader = None
            viewportShaderOuputName = "outColor"
            outputShaderOutputName = dict_seAttrs[renderType]['shaderOutputName']
            viewportShaderInputName = 'surfaceShader'
            outputShaderInputName = dict_seAttrs[renderType]['shadingEngineInputName']

            for origCon, srcCon in shadingEngine.listConnections(s=1, d=0, p=1, c=1):
                if origCon.longName() == 'surfaceShader':
                    viewportShader = srcCon.node()
                elif origCon.longName() == dict_seAttrs[renderType]['shadingEngineInputName']:
                    outputShader = srcCon.node()

            if outputShader:
                if viewportShader:
                    duViewport = duplicateShadingNetwork( viewportShader )
                    pymel.core.delete( viewportShader )
                else:
                    duViewport = duplicateShadingNetwork(outputShader)
                connectShaderToEngine(duViewport, shadingEngine, viewportShaderOuputName, viewportShaderInputName)
                viewportShader = duViewport
            elif viewportShader:
                duViewport = duplicateShadingNetwork( viewportShader )
                connectShaderToEngine(duViewport, shadingEngine, viewportShaderOuputName, viewportShaderInputName)
                connectShaderToEngine(viewportShader, shadingEngine, outputShaderOutputName, outputShaderInputName )
                outputShader = viewportShader
                viewportShader = duViewport

            return viewportShader, outputShader

        def resizeImage(shader, resolusion):

            def convertTextureSize_inNode(fileNode):

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

                def convertTextureSize(texturePath):
                    if int(cmds.about(v=1)) < 2017:
                        from PySide import QtCore
                        from PySide.QtGui import QPixmap, QImage
                        from PySide.QtCore import QFile, QIODevice
                    else:
                        from PySide2 import QtCore
                        from PySide2.QtGui import QPixmap, QImage
                        from PySide2.QtCore import QFile, QIODevice
                    folder, fileName = ntpath.split(texturePath)
                    origFileName = fileName if fileName[:8] != 'resized_' else fileName[8:]
                    origPath = folder + '/' + origFileName
                    if not os.path.exists(origPath):
                        cmds.warning("original is not exists : %s" % texturePath)
                        return
                    convertedFileName = 'resized_%d_' % (int(resolusion)) + origFileName
                    renamedPath = folder + "/" + convertedFileName
                    ext = os.path.splitext(fileName)[-1]
                    img = QImage(origPath)
                    pixmap = QPixmap()
                    pixmap = pixmap.fromImage(
                        img.scaled(int(resolusion), int(resolusion), QtCore.Qt.IgnoreAspectRatio,
                                   QtCore.Qt.FastTransformation))
                    qfile = QFile(renamedPath)
                    qfile.open(QIODevice.WriteOnly)
                    pixmap.save(qfile, ext[1:], 100)
                    qfile.close()
                    return renamedPath

                import re, ntpath, glob
                texturePath = fileNode.fileTextureName.get()
                renamedPath = None
                if fileNode.attr('useFrameExtension').get():
                    m = re.compile("[\.,_]+\d+\.")
                    folderPath, fileName = ntpath.split(texturePath)
                    p = m.search(fileName)
                    replacedPath = folderPath + '/' + fileName.replace(p.group(), '*.')
                    texturePathSequences = glob.glob(replacedPath)
                    for texturePathSequence in texturePathSequences:
                        renamedPath = convertTextureSize(texturePathSequence)
                else:
                    renamedPath = convertTextureSize(texturePath)
                if renamedPath: fileNode.attr( 'fileTextureName' ).set(renamedPath)

            hists = shader.history(pdo=1)
            fileNodes = []
            for hist in hists:
                if hist.nodeType() != 'file': continue
                fileNodes.append(hist)
            for fileNode in fileNodes:
                convertTextureSize_inNode(fileNode)

        viewportShader, outputShader = separateShader(shadingEngine, dict_seAttrs, rendererType)
        if resolusion: resizeImage( viewportShader, resolusion )
        return viewportShader, outputShader

    @staticmethod
    def showCombinedTexture( shader, resolusion=256 ):

        def setTextureViewportResolution(shader, value):
            if not pymel.core.attributeQuery('resolution', node=shader, ex=1):
                shader.addAttr('resolution', at='long')
            shader.attr("resolution").set(value)

        meterialInfos = shader.message.listConnections(s=0, d=1, type='materialInfo')
        if not meterialInfos: return
        if not pymel.core.isConnected(shader.message, meterialInfos[0].attr('texture[0]')):
            shader.message >> meterialInfos[0].attr('texture[0]')
        setTextureViewportResolution( shader, resolusion )



class Widget_chooseRenderer( QWidget, Cmds_file_control ):

    path_uiInfo = path_uiInfo_basedir + "/renderer.json"
    url = "https://docs.google.com/spreadsheets/d/1hvxG8ET1tfv2rqLfEa7eav0xb1_Ti7jR68ze9aSWt_s/edit?usp=sharing"
    csv = path_uiInfo_basedir + "/renderer.csv"

    def __init__(self, *args, **kwargs ):

        super( Widget_chooseRenderer, self ).__init__()
        self.installEventFilter( self )
        mainLayout = QHBoxLayout( self ); mainLayout.setContentsMargins(5,0,5,0)
        label = QLabel( 'Renderer : ' )
        comboBox = QComboBox()
        mainLayout.addWidget( label )
        mainLayout.addWidget( comboBox )

        self.comboBox = comboBox
        self.get_items()
        self.set_event()
        self.load_comboBox(self.comboBox, self.path_uiInfo)

    def set_event(self):
        QtCore.QObject.connect( self.comboBox, QtCore.SIGNAL( "currentIndexChanged(int)" ), self.chooseItem )
        self.load_comboBox(self.comboBox, self.path_uiInfo)

    def get_items(self):
        try:Cmds_mainCommands.get_csv_form_google_spreadsheets(Widget_chooseRenderer.url, Widget_chooseRenderer.csv )
        except:pass
        dict_renderer = Cmds_mainCommands.get_dictdata_from_csvPath(Widget_chooseRenderer.csv)
        keys = [ key for key in dict_renderer ]; keys.sort()
        [ self.comboBox.addItem( str( key ) ) for key in keys ]

    def chooseItem(self, index ):
        self.save_comboBox( self.comboBox, Widget_chooseRenderer.path_uiInfo )



class Widget_resolusion( QWidget, Cmds_file_control ):

    path_uiInfo = path_uiInfo_basedir + "/resolusion.json"
    url = "https://docs.google.com/spreadsheets/d/1Hzv2nkQeYZ-Ody_cdr75p3uyqRfGGkTr_-Vbc8Q_byc/edit?usp=sharing"
    csv = path_uiInfo_basedir + "/resolusion.csv"

    def __init__(self, *args, **kwargs ):

        super( Widget_resolusion, self ).__init__()
        self.installEventFilter( self )
        mainLayout = QHBoxLayout( self ); mainLayout.setContentsMargins( 5,0,5,0 )
        label = QLabel( "Convert resolution : " )
        comboBox = QComboBox()
        mainLayout.addWidget( label )
        mainLayout.addWidget( comboBox )

        self.comboBox = comboBox
        self.get_items()
        self.set_event()
        self.load_comboBox(self.comboBox, self.path_uiInfo )

    def set_event(self):
        QtCore.QObject.connect( self.comboBox, QtCore.SIGNAL( "currentIndexChanged(int)" ), self.chooseItem )

    def get_items(self):
        try:Cmds_mainCommands.get_csv_form_google_spreadsheets(Widget_resolusion.url, Widget_resolusion.csv )
        except:pass
        dict_resolusion = Cmds_mainCommands.get_dictdata_from_csvPath(Widget_resolusion.csv)
        keys = [ int(key) for key in dict_resolusion ]
        keys.sort()
        [ self.comboBox.addItem( str(key) ) for key in keys ]
        self.comboBox.addItem('None')

    def chooseItem(self, index ):
        self.save_comboBox( self.comboBox, Widget_resolusion.path_uiInfo )



class Window(QDialog, Cmds_file_control ):

    mayaWin = shiboken.wrapInstance(long(maya.OpenMayaUI.MQtUtil.mainWindow()), QWidget)
    objectName = "sg_pingo_viewport_shader_optimizer"
    title = "PINGO - Viewport shader optimizer"
    defaultWidth = 400
    defaultHeight = 400
    path_uiInfo = path_uiInfo_basedir + "/uiInfo.json"
    shaderAttr_url = "https://docs.google.com/spreadsheets/d/1p1GkGgXlsVYBL8m0ZQG8Ghg7Fr-0HdXalusE-wUF-oA/edit?usp=sharing"
    shaderAttr_csv = path_uiInfo_basedir + "/shaderAttrs.csv"
    removeTarget_url = "https://docs.google.com/spreadsheets/d/1UD6FBDJ1gAj7vpHAHmHnBtDlY-WD-LfwBYv_lY9ZlbM/edit?usp=sharing"
    removeTarget_csv = path_uiInfo_basedir + "/removeTargets.csv"

    def __init__(self, *args, **kwrgs):

        existing_widgets = Window.mayaWin.findChildren(QDialog, Window.objectName)
        if existing_widgets: map( lambda x: x.deleteLater(), existing_widgets )

        super(Window, self).__init__(*args, **kwrgs)
        self.installEventFilter( self )
        self.setObjectName( Window.objectName )
        self.setWindowTitle( Window.title )

        mainLayout = QVBoxLayout( self )
        w_rendererSelect = Widget_chooseRenderer()
        w_resolusion = Widget_resolusion()
        optimizer = QFrame();optimizer.setFrameShape(QFrame.HLine)
        button_sep  = QPushButton( "SEPARATE" )
        listWidget = QListWidget()
        listWidget.setSelectionMode( QAbstractItemView.ExtendedSelection )
        button_convert = QPushButton( "CONVERT TO LAMBERT" )
        button_convert.setEnabled( False )

        mainLayout.addWidget( w_rendererSelect )
        mainLayout.addWidget( w_resolusion )
        mainLayout.addWidget( button_sep )
        mainLayout.addWidget( listWidget )
        mainLayout.addWidget( button_convert )

        self.resize( Window.defaultWidth, Window.defaultHeight )
        self.load_shapeInfo( Window.path_uiInfo )

        self.w_rendererSelect = w_rendererSelect
        self.w_resolusion = w_resolusion
        self.listWidget = listWidget
        self.button_convert = button_convert

        QtCore.QObject.connect(button_sep, QtCore.SIGNAL("clicked()"), self.separate)
        QtCore.QObject.connect(button_convert, QtCore.SIGNAL("clicked()"), self.convert )
        QtCore.QObject.connect( listWidget, QtCore.SIGNAL( "itemSelectionChanged()" ), self.selectShader )

        try:Cmds_mainCommands.get_csv_form_google_spreadsheets(Window.shaderAttr_url, Window.shaderAttr_csv )
        except:pass
        self.dict_shaderAttr = Cmds_mainCommands.get_dictdata_from_csvPath( Window.shaderAttr_csv )
        try:Cmds_mainCommands.get_csv_form_google_spreadsheets(Window.removeTarget_url, Window.removeTarget_csv )
        except:pass
        self.dict_removeTargets = Cmds_mainCommands.get_dictdata_from_csvPath( Window.removeTarget_csv )


    def selectShader(self):
        selItems = [ item.text() for item in self.listWidget.selectedItems() ]
        if selItems:
            selectedTargets = []
            for selItem in selItems:
                pymel.core.hyperShade(objects=selItem)
                selectedTargets += pymel.core.ls( sl=1 )
            pymel.core.select( selectedTargets )
            pymel.core.select( selItems, add=1 )
            self.button_convert.setEnabled( True )
        else:
            pymel.core.select( d=1 )
            self.button_convert.setEnabled( False )


    def convert(self):
        for item in  self.listWidget.selectedItems():
            sel = pymel.core.ls( item.text() )[0]
            nodeType = sel.nodeType()
            if not self.dict_shaderAttr.has_key( nodeType ):
                pymel.core.warning( "%s has no convert infomation" %  sel.nodeName() )
                continue
            newShader = Cmds_mainCommands.convertToLambert( sel, self.dict_shaderAttr, self.dict_removeTargets )
            item.setText( newShader.name() )


    def separate(self):
        rendererType = self.w_rendererSelect.comboBox.currentText()
        resolusion = self.w_resolusion.comboBox.currentText()

        import pymel.core
        cmds.undoInfo( ock=1 )
        sels = pymel.core.ls( sl=1 )
        sels += pymel.core.listRelatives( sels, c=1, ad=1, type='transform' )
        targetShadingEngines = []
        for sel in sels:
            if not sel.getShape(): continue
            selShapes = [ shape for shape in sel.listRelatives( s=1 ) if not shape.io.get() ]
            if not selShapes: continue
            for selShape in selShapes:
                if not selShape.nodeType() == 'mesh': continue
                shadingEngines = selShape.listConnections( s=0, d=1, type='shadingEngine' )
                if not shadingEngines: continue
                targetShadingEngines += shadingEngines

        targetShadingEngines = list( set( targetShadingEngines ) )
        viewportShaders = []

        Cmds_mainCommands.get_csv_form_google_spreadsheets( Widget_chooseRenderer.url, Widget_chooseRenderer.csv )
        if not os.path.exists(Widget_chooseRenderer.csv): cmds.error("%s is not exists" % Widget_chooseRenderer.csv)

        dict_seAttrs = Cmds_mainCommands.get_dictdata_from_csvPath(Widget_chooseRenderer.csv)

        for shadingEngine in targetShadingEngines:
            viewportShader, outputShader = Cmds_mainCommands.separateViewportShader( shadingEngine, rendererType, dict_seAttrs, resolusion )
            Cmds_mainCommands.showCombinedTexture( viewportShader, 256 )
            viewportShaders.append( viewportShader.name() )

        self.listWidget.clear()
        for viewportShader in viewportShaders:
            self.listWidget.addItem( viewportShader )
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