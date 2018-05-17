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
        QFont, QGridLayout, QAbstractScrollArea, QProgressBar
else:
    from PySide2 import QtGui, QtCore, QtWidgets
    import shiboken2 as shiboken
    from PySide2.QtWidgets import QListWidgetItem, QDialog, QListWidget, QMainWindow, QWidget, QVBoxLayout, QLabel, \
        QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QAbstractItemView, QMenu, QMessageBox, QSplitter, \
        QScrollArea, QSizePolicy, QTextEdit, QApplication, QFileDialog, QCheckBox, QSlider, QProgressBar,\
        QTabWidget, QFrame, QTreeWidgetItem, QTreeWidget, QComboBox, QGroupBox, QAction, QGridLayout, QAbstractScrollArea

    from PySide2.QtGui import QColor, QCursor, QBrush, QDoubleValidator, QIntValidator, QImage, QPixmap, QTransform, \
        QPaintEvent, QFont



class Base:
    path_basedir = cmds.about(pd=1) + "/pingo/scene_optimize_export"
    path_refereceBaseInfo = cmds.about(pd=1) + "/pingo/scene_optimize_export/referenceBasePath.txt"
    mayaWin = shiboken.wrapInstance(long(maya.OpenMayaUI.MQtUtil.mainWindow()), QWidget)


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


class Commands:

    @staticmethod
    def getTopTransformNodes():

        trs = cmds.ls(type='transform')

        topTransforms = []
        for tr in trs:
            if cmds.listRelatives(tr, p=1): continue
            topTransforms.append(pymel.core.ls(tr)[0])

        return topTransforms


    @staticmethod
    def isVisible( geo ):
        allParents = geo.getAllParents()
        allParents.append(geo)
        for parent in allParents:
            if parent.io.get(): return False
            if not parent.attr('lodVisibility').get(): return False
        return True


    @staticmethod
    def getBoundingBoxStr(sel):
        values = [ "%.3f" % value for value in pymel.core.exactWorldBoundingBox( sel ) ]
        return ','.join( values )



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
            pymel.core.setAttr( target + '.' + attrName, e=1, cb=1 )
        elif keyable:
            pymel.core.setAttr( target + '.' + attrName, e=1, k=1 )



    @staticmethod
    def copyAttribute(inputSrc, inputDst, attrName, replaceAttrName=None):

        if not replaceAttrName:
            replaceAttrName = attrName

        src = pymel.core.ls(inputSrc)[0]
        dst = pymel.core.ls(inputDst)[0]

        srcAttr = src.attr(attrName)
        defaultList = pymel.core.attributeQuery(attrName, node=src, ld=1)

        try:
            if srcAttr.type() == 'enum':
                enumNames = pymel.core.attributeQuery(attrName, node=inputSrc, le=1)
                enumStr = ':'.join(enumNames) + ':'
                Commands.addAttr(dst, ln=srcAttr.longName(), sn=srcAttr.nodeName(), at=srcAttr.type(), en=enumStr,
                        dv=defaultList[0])
            else:
                Commands.addAttr(dst, ln=srcAttr.longName(), sn=srcAttr.nodeName(), at=srcAttr.type(), dv=defaultList[0])
        except:
            try:
                Commands.addAttr(dst, ln=srcAttr.longName(), sn=srcAttr.nodeName(), dt=srcAttr.type(), dv=defaultList[0])
            except:
                pass

        Commands.addAttr(dst, ln=replaceAttrName)
        dstAttr = dst.attr(replaceAttrName)
        if srcAttr.type() in ['double', 'long']:
            dstAttr.setRange(srcAttr.getRange())
        if srcAttr.isInChannelBox():
            dstAttr.showInChannelBox(True)
        if srcAttr.isKeyable():
            dstAttr.setKeyable(True)

        try:
            dstAttr.set(srcAttr.get())
        except:
            pass


    @staticmethod
    def getSameGeometryList( srcTop, trgTop ):

        srcChildren = list( set( [ mesh for mesh in pymel.core.listRelatives(srcTop, c=1, ad=1, type='mesh') if Commands.isVisible( mesh ) ] ) )
        trgChildren = list( set( [ mesh for mesh in pymel.core.listRelatives(trgTop, c=1, ad=1, type='mesh') if Commands.isVisible( mesh ) ] ) )

        bbStrDict = {}
        for src in srcChildren:
            bbStr = Commands.getBoundingBoxStr(src)
            if bbStrDict.has_key(bbStr):
                bbStrDict[bbStr]["src"] = src.getParent()
            else:
                bbStrDict[bbStr] = {"src": src.getParent() }
        for trg in trgChildren:
            bbStr = Commands.getBoundingBoxStr(trg.getParent())
            if bbStrDict.has_key(bbStr):
                bbStrDict[bbStr]["trg"] = trg.getParent()
            else:
                bbStrDict[bbStr] = { "trg": trg.getParent() }
        return bbStrDict

    @staticmethod
    def duplicateShadingNetwork(node, **options):
        def isDoNotDeleteTarget(node):
            for attr in ['wm']:
                if pymel.core.attributeQuery(attr, node=node, ex=1): return True
            return False

        checkNodes = []
        for srcNode in node.listConnections(s=1, d=0):
            checkNodes += srcNode.history()

        disconnectedList = []
        for checkNode in checkNodes:
            if isDoNotDeleteTarget(checkNode): continue
            nodeSrcCons = checkNode.listConnections(s=1, d=0, p=1, c=1)
            for origAttr, srcAttr in nodeSrcCons:
                srcNode = srcAttr.node()
                if not isDoNotDeleteTarget(srcNode): continue
                srcAttr // origAttr
                disconnectedList.append((srcAttr, origAttr))
        options.update({'un': 1})

        try:
            duNodes = pymel.core.duplicate(node, **options)
            duNode = duNodes[0]
        except:
            return None
        origHistory = node.history()
        duHistory = duNode.history()

        for srcAttr, origAttr in disconnectedList:
            srcAttr >> origAttr
            if not origAttr.node() in origHistory: continue
            historyIndex = origHistory.index(origAttr.node())
            pymel.core.connectAttr(srcAttr, duHistory[historyIndex] + '.' + origAttr.longName())
        return duNode

    @staticmethod
    def duplicateShadingEngine( engine ):

        engine = pymel.core.ls( engine )[0]
        if engine.name() == 'initialShadingGroup':
            #print "engine is initial"
            return None
        cons = [con for con in engine.listConnections(s=1, d=0, p=1, c=1) if con[1].type() in ['float3', 'message']]
        if not cons: None

        newEngine = pymel.core.sets(renderable=True, noSurfaceShader=True, empty=1, n='du_' + engine.nodeName())
        for origCon, srcCon in cons:
            du_targetShader = Commands.duplicateShadingNetwork(srcCon.node(), n='du_' + srcCon.node().nodeName())
            if not du_targetShader: continue
            du_targetShader.attr(srcCon.longName()) >> newEngine.attr(origCon.longName())
        return newEngine.name()


    @staticmethod
    def assignToNewShadingEngines( srcGeo, trgGeo, shadingEngineDict ):

        srcShape = srcGeo.getShape()
        trgShape = trgGeo.getShape()

        srcEngineConnected = [engine.name() for engine in srcShape.listConnections(type='shadingEngine')]

        for srcEngine in srcEngineConnected:
            if not shadingEngineDict.has_key(srcEngine): continue

            targetEngine = shadingEngineDict[srcEngine]
            if not targetEngine: continue

            cons = [con for con in pymel.core.listConnections(srcEngine, s=1, d=0, p=1, c=1) if
                    con[1].type() in ['float3', 'message']]
            targetShader = cons[0][0].node()
            selObjs = targetShader.elements()
            targetObjs = []
            for selObj in selObjs:
                if selObj.node() != srcShape: continue
                if selObj.find('.') != -1:
                    sepSelObjs = pymel.core.ls(selObj)
                    for sepSelObj in sepSelObjs:
                        targetObjs.append(trgGeo + '.' + sepSelObj.split('.')[-1])
                else:
                    targetObjs.append(trgShape.name())

            for targetObj in targetObjs:
                cmds.sets(targetObj, e=1, forceElement=targetEngine)


    @staticmethod
    def copyShaderAndReplaceConnection(origSel, destSel):

        origNamespace = origSel.namespace()
        destNamespace = destSel.namespace()

        def isVisible( target ):
            allParents = target.getAllParents()
            allParents.append( target )
            for parent in allParents:
                if not parent.attr( 'lodVisibility' ).get(): return False
                if parent.io.get(): return False
            return True

        def udAttrCopy( src, trg ):
            udAttrs = cmds.listAttr(src.name(), ud=1)
            if not udAttrs: return
            for udAttr in udAttrs:
                try:Commands.copyAttribute(src, trg, udAttr)
                except: cmds.warning( "Failed to copy attribute : %s" % udAttr )

        origChildren = [ origChild for origChild in origSel.listRelatives(c=1, ad=1, type='transform') ]
        origChildren.append( origSel )

        dialog_progress = Dialog_progressbar( Dialog_progressbar.mayaWin, title="Exporting - %s" % origSel.name() )
        dialog_progress.setModal(True)
        dialog_progress.show()
        QApplication.instance().processEvents()

        childCheckPercent = 0.05
        enginecheckPercent = 0.05
        newShaderAssignPercent = 0.75
        replaceConnectPercent = 0.15

        numChildren = len(origChildren)

        engines = []
        #print "check children"

        for i in range( numChildren ):
            origChild = origChildren[i]
            origChildShape = origChild.getShape()
            if not origChildShape: continue
            if not origChildShape.nodeType() == 'mesh': continue
            enginesEach = origChildShape.listConnections(type='shadingEngine')
            if not enginesEach: continue
            engines += enginesEach
            if not dialog_progress.isVisible(): return
            dialog_progress.setValue( i*(1.0 / numChildren) * childCheckPercent )
        dialog_progress.setValue( childCheckPercent )

        #print "check engine"

        engines = list(set(engines))
        enginesDict = {}
        numEngines = len( engines )
        for i in range( numEngines ):
            engine = engines[i]
            duEngine = Commands.duplicateShadingEngine( engine )
            enginesDict[ engine.name() ] = duEngine
            dialog_progress.setValue(i * (1.0 / numEngines) * enginecheckPercent + childCheckPercent)
        dialog_progress.setValue( childCheckPercent + enginecheckPercent )

        #print "check duplicate shading"

        for i in range(numChildren):
            dialog_progress.setValue( i * (1.0 / numChildren) * newShaderAssignPercent + childCheckPercent + enginecheckPercent)

            origChild = origChildren[i]
            destChildName = '|'.join( [destNamespace + name[len(origNamespace):] for name in origChild.name().split( '|' )] )
            #print "orig child : ", origChild
            #print "destChildName : ", destChildName
            if not pymel.core.objExists( destChildName ): continue
            destChild = pymel.core.ls( destChildName )[0]

            udAttrCopy( origChild, destChild )

            origChildShape = origChild.getShape()
            destChildShape = destChild.getShape()

            if not origChildShape or not destChildShape: continue
            udAttrCopy(origChildShape, destChildShape)

            if not destChild.getShape().nodeType() == 'mesh': continue
            if not isVisible(origChildShape): continue
            if not dialog_progress.isVisible(): return
            #print "orig child : ", origChild
            #print "dst child : " , destChild
            #if not destChild.nodeName() in ['ex_ch_300_paul_rig_v01:eye_in', 'ex_ch_300_paul_rig_v01:eye_out' ] : continue
            Commands.assignToNewShadingEngines( origChild, destChild, enginesDict )
        dialog_progress.setValue(newShaderAssignPercent+childCheckPercent + enginecheckPercent)

        #print "check connecitons"

        engineDictKeys = enginesDict.keys()
        for i in range( numEngines ):
            engine = engineDictKeys[i]
            duEngine = enginesDict[ engine ]
            if not duEngine: continue

            hists = pymel.core.listHistory( duEngine )

            #if duEngine.find( 'ch_000_paul_shadingEngine' ) == -1: continue
            #print "du engine : ", duEngine
            for hist in hists:
                if hist.split('|')[0][:len(origNamespace)] != origNamespace: continue
                #print hist
                for origCon, dstCon in hist.listConnections(s=0, d=1, p=1, c=1):
                    origConAttr = '|'.join( [destNamespace + name[len( origNamespace ):] for name in origCon.name().split( '|' ) ] )
                    dstConAttr  = dstCon

                    #print origCon, dstCon
                    #print origConAttr, dstConAttr
                    #print "copy attribute : ", origCon.node().name(), origConAttr.split( '.' )[0], '.'.join( origConAttr.split( '.' )[1:] )

                    if not pymel.core.ls(origConAttr): continue
                    try:Commands.copyAttribute( origCon.node().name(), origConAttr.split( '.' )[0], '.'.join( origConAttr.split( '.' )[1:] ) )
                    except:pass

                    if pymel.core.isConnected(origConAttr, dstConAttr): continue
                    try:
                        pymel.core.connectAttr(origConAttr, dstConAttr, f=1)
                    except:
                        cmds.warning( "failed to connect : %s >> %s" % ( origConAttr, dstConAttr ) )
            if not dialog_progress.isVisible(): return
            dialog_progress.setValue( i * (1.0 / numEngines ) * replaceConnectPercent + newShaderAssignPercent + childCheckPercent + enginecheckPercent )
        #print "done"


        dialog_progress.setValue(1.0)
        dialog_progress.close()
        dialog_progress.deleteLater()

    @staticmethod
    def cleanScene():
        import pymel.core
        import maya.mel

        audio = pymel.core.ls(type='audio')
        if audio:
            try:
                pymel.core.delete(audio)
            except:
                pass

        for unknown in pymel.core.ls(type='unknown'):
            try:
                pymel.core.delete(unknown)
            except:
                pass

        displayLayers = pymel.core.ls(type='displayLayer')
        for displayLayer in displayLayers:
            if not displayLayer.v.get(): continue
            if displayLayer.name() == 'defaultLayer': continue
            try:
                pymel.core.delete(displayLayer)
            except:
                pass

        sels = pymel.core.ls(type='renderLayer')
        for sel in sels:
            if sel == 'defaultRenderLayer': continue
            try:
                pymel.core.delete(sel)
            except:
                pass
        maya.mel.eval('MLdeleteUnused;')

        try:
            pymel.core.delete('frameCounterUpdate')
        except:
            pass
        try:
            pymel.core.delete('timeCodeUpdate')
        except:
            pass

    @staticmethod
    def createExportNamespace(origNamespace):

        if origNamespace:
            splitNs = origNamespace[:-1].split(':')
            joinedSplits = ':'.join(splitNs[:-1])
            if joinedSplits:
                ex_namespace = 'ex_' + joinedSplits + ':' + splitNs[-1]
            else:
                ex_namespace = 'ex_' + splitNs[-1]
        else:
            ex_namespace = 'ex'
        namespaceList = cmds.namespaceInfo(lon=1)
        if not ex_namespace in namespaceList:
            try:
                cmds.namespace(addNamespace=ex_namespace)
            except:
                pass
        return ex_namespace + ':'

    @staticmethod
    def removeUnknownPlugin():
        plugins = cmds.unknownPlugin(q=1, list=1)
        if not plugins: plugins = []
        for plugin in plugins:
            try:
                cmds.unknownPlugin(plugin, remove=1)
            except:
                pass

    @staticmethod
    def removeNamespaceInScene():
        for ns in cmds.namespaceInfo(lon=1):
            nsNodes = pymel.core.ls(ns + ':*')
            for nsNode in nsNodes:
                renamedName = nsNode.nodeName().replace(ns + ':', '')
                try:
                    nsNode.rename(renamedName)
                except:
                    print nsNode
            try:
                cmds.namespace(deleteNamespaceContent=1, removeNamespace=':' + ns)
            except:
                pass

    @staticmethod
    def cleanMeshInScene(*args):
        from maya import cmds
        def cleanMesh(targetObj):
            targetShapes = cmds.listRelatives(targetObj, s=1, f=1)
            for targetShape in targetShapes:
                if not cmds.getAttr(targetShape + '.io'): continue
                if cmds.listConnections(targetShape + '.outMesh', s=0, d=1): continue
                if cmds.listConnections(targetShape + '.worldMesh', s=0, d=1): continue
                cmds.delete(targetShape)
                cmds.warning("%s is deleted" % targetShape)

        meshs = cmds.ls(type='mesh')

        meshObjs = []
        for mesh in meshs:
            if cmds.getAttr(mesh + '.io'): continue
            meshP = cmds.listRelatives(mesh, p=1, f=1)[0]
            if meshP in meshObjs: continue
            meshObjs.append(meshP)
        for meshObj in meshObjs:
            cleanMesh(meshObj)


    @staticmethod
    def exportElement( targetReferenceNode, buildScene=True, constrainReferences = [] ):

        import pymel.core
        from maya import cmds, mel

        def createExportNamespace(origNamespace):
            if origNamespace:
                splitNs = origNamespace[:-1].split(':')
                joinedSplits = ':'.join(splitNs[:-1])
                if joinedSplits:
                    ex_namespace = 'ex_' + joinedSplits + ':' + splitNs[-1]
                else:
                    ex_namespace = 'ex_' + splitNs[-1]
            else:
                ex_namespace = 'ex'
            namespaceList = cmds.namespaceInfo(lon=1)
            if not ex_namespace in namespaceList:
                try:cmds.namespace(addNamespace=ex_namespace)
                except:pass
            return ex_namespace + ':'
        mel.eval( "DisplayWireframe;" );

        targetReferenceNode = pymel.core.ls( targetReferenceNode )[0].name()

        isLoaded = False
        if cmds.nodeType( targetReferenceNode ) == 'reference':
            referecedTransforms = []
            isLoaded = pymel.core.referenceQuery(targetReferenceNode, isLoaded=1)
            cmds.file(loadReference=1, referenceNode=targetReferenceNode )
            referecedTransforms += [node for node in pymel.core.ls(pymel.core.referenceQuery(targetReferenceNode, nodes=1)) if
                            node.nodeType() == 'transform']
            targetNodes = []
            for referecedTransform in referecedTransforms:
                parents = referecedTransform.getAllParents()
                if not parents:
                    targetNodes.append(referecedTransform)
                    continue
                    targetNodes.append(parents[-1])
            targetNodes = [topParent for topParent in list(set(targetNodes)) if not topParent.attr('hiddenInOutliner').get()]
        else:
            targetNodes = [ pymel.core.ls( targetReferenceNode )[0] ]

        minFrame = cmds.playbackOptions( q=1, min=1 )
        maxFrame = cmds.playbackOptions( q=1, max=1 )

        if not targetNodes:
            cmds.file( unloadReference=1, referenceNode=targetReferenceNode )
            return

        baseDir = os.path.splitext( cmds.file( q=1, sceneName=1 ) )[0]
        if not os.path.exists( baseDir ) or not os.path.isdir( baseDir ):
            os.makedirs(baseDir)
        namespace = targetNodes[0].namespace()
        if not namespace: namespace = targetReferenceNode + ':'
        basePath = baseDir + '/' + namespace[:-1].replace( ':', '_' )
        exportCachePath = basePath + '.abc'

        for constrainReference in constrainReferences:
            cmds.file( loadReference=1, referenceNode=constrainReference )
        cmds.AbcExport( j = "-frameRange %d %d -uvWrite -wholeFrameGeo -writeVisibility -eulerFilter -dataFormat ogawa \
                         %s -file %s" % ( minFrame, maxFrame, ' '.join( ['-root %s' % targetNode.name() for targetNode in targetNodes ] ), exportCachePath ) )
        for constrainReference in constrainReferences:
            cmds.file( unloadReference=1, referenceNode=constrainReference )

        if buildScene:
            exportFilePath = basePath + '.mb'

            origTopTrNodes = Commands.getTopTransformNodes()
            cmds.AbcImport( exportCachePath, mode="import")
            afterTopTrNodes = Commands.getTopTransformNodes()

            importedTargets = []
            for afterTopTrNode in afterTopTrNodes:
                if afterTopTrNode in origTopTrNodes: continue
                importedTargets.append( afterTopTrNode )

            origNamespace = targetNodes[0].namespace()

            lenOrigNamespace = len( origNamespace )
            ex_namespace = createExportNamespace( origNamespace )
            for importedChild in pymel.core.listRelatives(importedTargets, c=1, ad=1):
                if importedChild.nodeName().find( origNamespace ) == -1:
                    pymel.core.delete( importedChild ); continue
                importedChild.rename(ex_namespace + importedChild.nodeName()[lenOrigNamespace:])
            [ importedTargets[i].rename( ex_namespace + targetNodes[i].nodeName()[lenOrigNamespace:] ) for i in range( len(importedTargets) ) ]
            [ Commands.copyShaderAndReplaceConnection( targetNodes[i], importedTargets[i] ) for i in range( len( importedTargets ) ) ]

            pymel.core.select( importedTargets )
            cmds.file( exportFilePath, force=1, options = "v=0;", typ = "mayaBinary", pr=1, es=1 )
            pymel.core.delete( importedTargets )
            Commands.removeSceneNamespace( exportFilePath )

        if pymel.core.nodeType( targetReferenceNode ) == 'reference' and not isLoaded:
            cmds.file(unloadReference=1, referenceNode=targetReferenceNode)
        mel.eval('MLdeleteUnused;')




    @staticmethod
    #Commands.exportElement2.start
    def exportElement2( scenePath, targetReferenceNode, exportFile=True, constrainReferences = [] ):

        def assignToNewShadingEngines(srcGeo, trgGeo, shadingEngineDict):

            srcShape = srcGeo.getShape()
            trgShape = trgGeo.getShape()

            srcEngineConnected = [engine.name() for engine in srcShape.listConnections(type='shadingEngine')]

            for srcEngine in srcEngineConnected:
                if not shadingEngineDict.has_key(srcEngine): continue

                targetEngine = shadingEngineDict[srcEngine]
                if not targetEngine: continue

                cons = [con for con in pymel.core.listConnections(srcEngine, s=1, d=0, p=1, c=1) if
                        con[1].type() in ['float3', 'message']]
                targetShader = cons[0][0].node()
                selObjs = targetShader.elements()
                targetObjs = []
                for selObj in selObjs:
                    if selObj.node() != srcShape: continue
                    if selObj.find('.') != -1:
                        sepSelObjs = pymel.core.ls( selObj )
                        for sepSelObj in sepSelObjs:
                            targetObjs.append( trgGeo + '.' + sepSelObj.split('.')[-1] )
                    else:
                        targetObjs.append(trgShape.name())

                for targetObj in targetObjs:
                    cmds.sets(targetObj, e=1, forceElement=targetEngine)


        def duplicateShadingNetwork(node, **options):
            def isDoNotDeleteTarget(node):
                for attr in ['wm']:
                    if pymel.core.attributeQuery(attr, node=node, ex=1): return True
                return False

            checkNodes = []
            for srcNode in node.listConnections(s=1, d=0):
                checkNodes += srcNode.history()

            disconnectedList = []
            for checkNode in checkNodes:
                if isDoNotDeleteTarget(checkNode): continue
                nodeSrcCons = checkNode.listConnections(s=1, d=0, p=1, c=1)
                for origAttr, srcAttr in nodeSrcCons:
                    srcNode = srcAttr.node()
                    if not isDoNotDeleteTarget(srcNode): continue
                    srcAttr // origAttr
                    disconnectedList.append((srcAttr, origAttr))
            options.update({'un': 1})

            try:
                duNodes = pymel.core.duplicate(node, **options)
                duNode = duNodes[0]
            except:
                return None
            origHistory = node.history()
            duHistory = duNode.history()

            for srcAttr, origAttr in disconnectedList:
                srcAttr >> origAttr
                if not origAttr.node() in origHistory: continue
                historyIndex = origHistory.index(origAttr.node())
                pymel.core.connectAttr(srcAttr, duHistory[historyIndex] + '.' + origAttr.longName())
            return duNode


        def duplicateShadingEngine(engine):

            engine = pymel.core.ls(engine)[0]
            if engine.name() == 'initialShadingGroup':
                # print "engine is initial"
                return None
            cons = [con for con in engine.listConnections(s=1, d=0, p=1, c=1) if con[1].type() in ['float3', 'message']]
            if not cons: None

            newEngine = pymel.core.sets(renderable=True, noSurfaceShader=True, empty=1, n='du_' + engine.nodeName())
            for origCon, srcCon in cons:
                du_targetShader = duplicateShadingNetwork(srcCon.node(), n='du_' + srcCon.node().nodeName())
                if not du_targetShader: continue
                du_targetShader.attr(srcCon.longName()) >> newEngine.attr(origCon.longName())
            return newEngine.name()


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


        def copyAttribute(inputSrc, inputDst, attrName, replaceAttrName=None):

            if not replaceAttrName:
                replaceAttrName = attrName

            src = pymel.core.ls(inputSrc)[0]
            dst = pymel.core.ls(inputDst)[0]

            srcAttr = src.attr(attrName)
            defaultList = pymel.core.attributeQuery(attrName, node=src, ld=1)

            try:
                if srcAttr.type() == 'enum':
                    enumNames = pymel.core.attributeQuery(attrName, node=inputSrc, le=1)
                    enumStr = ':'.join(enumNames) + ':'
                    addAttr(dst, ln=srcAttr.longName(), sn=srcAttr.nodeName(), at=srcAttr.type(), en=enumStr,
                                     dv=defaultList[0])
                else:
                    addAttr(dst, ln=srcAttr.longName(), sn=srcAttr.nodeName(), at=srcAttr.type(),
                                     dv=defaultList[0])
            except:
                try:
                    addAttr(dst, ln=srcAttr.longName(), sn=srcAttr.nodeName(), dt=srcAttr.type(),
                                     dv=defaultList[0])
                except:
                    pass

            addAttr(dst, ln=replaceAttrName)
            dstAttr = dst.attr(replaceAttrName)
            if srcAttr.type() in ['double', 'long']:
                dstAttr.setRange(srcAttr.getRange())
            if srcAttr.isInChannelBox():
                dstAttr.showInChannelBox(True)
            if srcAttr.isKeyable():
                dstAttr.setKeyable(True)

            try:
                dstAttr.set(srcAttr.get())
            except:
                pass


        def copyShaderAndReplaceConnection(origSel, destSel):

            origNamespace = origSel.namespace()
            destNamespace = destSel.namespace()

            def isVisible(target):
                allParents = target.getAllParents()
                allParents.append(target)
                for parent in allParents:
                    if not parent.attr('lodVisibility').get(): return False
                    if parent.io.get(): return False
                return True

            def udAttrCopy(src, trg):
                udAttrs = cmds.listAttr(src.name(), ud=1)
                if not udAttrs: return
                for udAttr in udAttrs:
                    try:
                        copyAttribute(src, trg, udAttr)
                    except:
                        cmds.warning("Failed to copy attribute : %s" % udAttr)

            origChildren = [origChild for origChild in origSel.listRelatives(c=1, ad=1, type='transform')]
            origChildren.append(origSel)

            progressValue = 0

            childCheckPercent = 0.05
            enginecheckPercent = 0.05
            newShaderAssignPercent = 0.75
            replaceConnectPercent = 0.15

            numChildren = len(origChildren)

            engines = []
            # print "check children"

            for i in range(numChildren):
                origChild = origChildren[i]
                origChildShape = origChild.getShape()
                if not origChildShape: continue
                if not origChildShape.nodeType() == 'mesh': continue
                enginesEach = origChildShape.listConnections(type='shadingEngine')
                if not enginesEach: continue
                engines += enginesEach
                progressValue = i * (1.0 / numChildren) * childCheckPercent
            progressValue = childCheckPercent

            # print "check engine"

            engines = list(set(engines))
            enginesDict = {}
            numEngines = len(engines)
            for i in range(numEngines):
                engine = engines[i]
                duEngine = duplicateShadingEngine(engine)
                enginesDict[engine.name()] = duEngine
                progressValue = i * (1.0 / numEngines) * enginecheckPercent + childCheckPercent
            progressValue = childCheckPercent + enginecheckPercent

            # print "check duplicate shading"

            for i in range(numChildren):
                progressValue = i * (1.0 / numChildren) * newShaderAssignPercent + childCheckPercent + enginecheckPercent

                origChild = origChildren[i]
                destChildName = '|'.join(
                    [destNamespace + name[len(origNamespace):] for name in origChild.name().split('|')])
                # print "orig child : ", origChild
                # print "destChildName : ", destChildName
                if not pymel.core.objExists(destChildName): continue
                destChild = pymel.core.ls(destChildName)[0]

                udAttrCopy(origChild, destChild)

                origChildShape = origChild.getShape()
                destChildShape = destChild.getShape()

                if not origChildShape or not destChildShape: continue
                udAttrCopy(origChildShape, destChildShape)

                if not destChild.getShape().nodeType() == 'mesh': continue
                if not isVisible(origChildShape): continue
                # print "orig child : ", origChild
                # print "dst child : " , destChild
                # if not destChild.nodeName() in ['ex_ch_300_paul_rig_v01:eye_in', 'ex_ch_300_paul_rig_v01:eye_out' ] : continue
                assignToNewShadingEngines(origChild, destChild, enginesDict)
            progressValue = newShaderAssignPercent + childCheckPercent + enginecheckPercent

            # print "check connecitons"

            engineDictKeys = enginesDict.keys()
            for i in range(numEngines):
                engine = engineDictKeys[i]
                duEngine = enginesDict[engine]
                if not duEngine: continue

                hists = pymel.core.listHistory(duEngine)

                # if duEngine.find( 'ch_000_paul_shadingEngine' ) == -1: continue
                # print "du engine : ", duEngine
                for hist in hists:
                    if hist.split('|')[0][:len(origNamespace)] != origNamespace: continue
                    # print hist
                    for origCon, dstCon in hist.listConnections(s=0, d=1, p=1, c=1):
                        origConAttr = '|'.join(
                            [destNamespace + name[len(origNamespace):] for name in origCon.name().split('|')])
                        dstConAttr = dstCon

                        # print origCon, dstCon
                        # print origConAttr, dstConAttr
                        # print "copy attribute : ", origCon.node().name(), origConAttr.split( '.' )[0], '.'.join( origConAttr.split( '.' )[1:] )

                        if not pymel.core.ls(origConAttr): continue
                        try:
                            copyAttribute(origCon.node().name(), origConAttr.split('.')[0],
                                                   '.'.join(origConAttr.split('.')[1:]))
                        except:
                            pass

                        if pymel.core.isConnected(origConAttr, dstConAttr): continue
                        try:
                            pymel.core.connectAttr(origConAttr, dstConAttr, f=1)
                        except:
                            cmds.warning("failed to connect : %s >> %s" % (origConAttr, dstConAttr))
                progressValue = i * ( 1.0 / numEngines) * replaceConnectPercent + newShaderAssignPercent + childCheckPercent + enginecheckPercent
            # print "done"
            progressValue = 1.0


        def getTopTransformNodes():
            trs = cmds.ls(type='transform')
            topTransforms = []
            for tr in trs:
                if cmds.listRelatives(tr, p=1): continue
                print tr, cmds.getAttr( tr + '.hiddenInOutliner' )
                if cmds.getAttr( tr + '.hiddenInOutliner' ): continue
                topTransforms.append(pymel.core.ls(tr)[0])
            return topTransforms


        def cleanScene():
            import pymel.core
            import maya.mel

            audio = pymel.core.ls(type='audio')
            if audio:
                try:
                    pymel.core.delete( audio )
                except:
                    pass

            for unknown in pymel.core.ls(type='unknown'):
                try:
                    pymel.core.delete( unknown )
                except:
                    pass

            displayLayers = pymel.core.ls(type='displayLayer')
            for displayLayer in displayLayers:
                if not displayLayer.v.get(): continue
                if displayLayer.name() == 'defaultLayer': continue
                try:pymel.core.delete(displayLayer)
                except:pass

            sels = pymel.core.ls(type='renderLayer')
            for sel in sels:
                if sel == 'defaultRenderLayer': continue
                try:pymel.core.delete(sel)
                except:pass
            maya.mel.eval('MLdeleteUnused;')

            try:
                pymel.core.delete('frameCounterUpdate')
            except:
                pass
            try:
                pymel.core.delete('timeCodeUpdate')
            except:
                pass

        def createExportNamespace(origNamespace):

            if origNamespace:
                splitNs = origNamespace[:-1].split(':')
                joinedSplits = ':'.join(splitNs[:-1])
                if joinedSplits:
                    ex_namespace = 'ex_' + joinedSplits + ':' + splitNs[-1]
                else:
                    ex_namespace = 'ex_' + splitNs[-1]
            else:
                ex_namespace = 'ex'
            namespaceList = cmds.namespaceInfo(lon=1)
            if not ex_namespace in namespaceList:
                try:cmds.namespace(addNamespace=ex_namespace)
                except:pass
            return ex_namespace + ':'


        def removeUnknownPlugin():
            plugins = cmds.unknownPlugin(q=1, list=1)
            if not plugins: plugins = []
            for plugin in plugins:
                try:
                    cmds.unknownPlugin(plugin, remove=1)
                except:
                    pass

        def removeNamespaceInScene():
            for ns in cmds.namespaceInfo(lon=1):
                nsNodes = pymel.core.ls(ns + ':*')
                for nsNode in nsNodes:
                    renamedName = nsNode.nodeName().replace(ns + ':', '')
                    try:
                        nsNode.rename(renamedName)
                    except:
                        print nsNode
                try:
                    cmds.namespace(deleteNamespaceContent=1, removeNamespace=':' + ns)
                except:
                    pass

        def cleanMeshInScene(*args):
            from maya import cmds
            def cleanMesh(targetObj):
                targetShapes = cmds.listRelatives(targetObj, s=1, f=1)
                for targetShape in targetShapes:
                    if not cmds.getAttr(targetShape + '.io'): continue
                    if cmds.listConnections(targetShape + '.outMesh', s=0, d=1): continue
                    if cmds.listConnections(targetShape + '.worldMesh', s=0, d=1): continue
                    cmds.delete(targetShape)
                    cmds.warning("%s is deleted" % targetShape)

            meshs = cmds.ls(type='mesh')

            meshObjs = []
            for mesh in meshs:
                if cmds.getAttr(mesh + '.io'): continue
                meshP = cmds.listRelatives(mesh, p=1, f=1)[0]
                if meshP in meshObjs: continue
                meshObjs.append(meshP)
            for meshObj in meshObjs:
                cleanMesh(meshObj)


        from maya import mel
        import pymel.core

        plugins = ['AbcExport', 'AbcImport', 'gpuCache']

        for plugin in plugins:
            if not cmds.pluginInfo(plugin, q=1, l=1):
                cmds.loadPlugin(plugin)

        cmds.file( scenePath, f=1, options="v=0;", ignoreVersion=1, typ="mayaBinary", o=1, loadReferenceDepth='none' )
        targetNodes = []
        cmds.file( loadReference = 1, referenceNode=targetReferenceNode )
        for constrainReference in constrainReferences:
            cmds.file(loadReference=1, referenceNode=constrainReference)
        targetNodes += [node for node in pymel.core.ls(pymel.core.referenceQuery(targetReferenceNode, nodes=1)) if
                 node.nodeType() == 'transform']
        targetNamespace = cmds.referenceQuery( targetReferenceNode, namespace=1 )[1:]

        exportBaseDir = os.path.splitext( scenePath )[0]
        if not os.path.exists( exportBaseDir ) or not os.path.isdir( exportBaseDir ):
            os.makedirs( exportBaseDir )
        exportCachePath = exportBaseDir + '/' + targetNamespace + '.abc'

        targetNodes = pymel.core.ls( targetNodes )
        topParents = []
        for targetNode in targetNodes:
            parents = targetNode.getAllParents()
            if not parents:
                topParents.append( targetNode )
                continue
            topParents.append( parents[-1] )
        topParents = [ topParent for topParent in list( set( topParents ) ) if not topParent.attr('hiddenInOutliner').get() ]
        cacheDirectory = os.path.dirname(exportCachePath)
        if not os.path.exists(cacheDirectory): os.makedirs(cacheDirectory)

        minFrame = cmds.playbackOptions( q=1, min=1 )
        maxFrame = cmds.playbackOptions( q=1, max=1 )
        cmds.AbcExport(j="-frameRange %d %d -uvWrite -wholeFrameGeo -writeVisibility -eulerFilter\
                      -dataFormat ogawa %s -file %s" % ( minFrame, maxFrame, ' '.join(['-root %s' % targetNode.name() for targetNode in topParents]), exportCachePath))

        if exportFile:
            exportFilePath = exportBaseDir + '/' + targetNamespace + '.mb'
            origTopTrNodes = getTopTransformNodes()
            cmds.AbcImport( exportCachePath, mode="import" )
            afterTopTrNodes = getTopTransformNodes()

            importedTargets = []
            for afterTopTrNode in afterTopTrNodes:
                if afterTopTrNode in origTopTrNodes: continue
                importedTargets.append(afterTopTrNode)

            topParents.sort()
            importedTargets.sort()
            #print "len top parents : ", len( topParents )
            #print "len imported targets : ", len( importedTargets )

            for i in range( len( topParents ) ):
                topParent = topParents[i]
                importedTarget = importedTargets[i]
                origNamespace = topParent.namespace()
                lenOrigNamespace = len( origNamespace )
                ex_namespace = createExportNamespace( origNamespace )
                [ importedChild.rename(ex_namespace + importedChild.nodeName()[lenOrigNamespace:] ) for importedChild in pymel.core.listRelatives(importedTarget, c=1, ad=1)]
                importedTarget.rename(ex_namespace + topParent.nodeName()[lenOrigNamespace:] )
                copyShaderAndReplaceConnection( topParent, importedTarget )

            for ref in cmds.ls(type='reference'):
                try:cmds.file( removeReference=1, referenceNode=ref )
                except:pass

            for topNode in getTopTransformNodes():
                if topNode in importedTargets: continue
                try: pymel.core.delete( topNode )
                except: pass

            try:
                removeUnknownPlugin()
            except:
                cmds.warning( "Failed to remove unknown plugin" )

            try:
                cleanMeshInScene()
            except:
                cmds.warning( "Failed to clean mesh" )

            try:
                cleanScene()
            except:
                cmds.warning( "Failed to clean scene" )

            try:
                removeNamespaceInScene()
            except:
                cmds.warning( "Failed to remove namespace" )

            try:
                mel.eval( 'MLdeleteUnused;' )
            except:
                cmds.warning( "Failed to delete unused nodes" )

            cmds.file( rename=exportFilePath )
            cmds.file( save=1, f=1 )
    #Commands.exportElement2.end


    @staticmethod
    def exportElementStandalone( scenePath, targetReferenceNodes, buildScene=True ):

        import re, ntpath
        from maya import mel

        mainFunction = """
class Commands:
    @staticmethod
    #Commands.exportElement2.start
    def exportElement2( scenePath, targetReferenceNode, exportFile=True, constrainReferences = [] ):

        def assignToNewShadingEngines(srcGeo, trgGeo, shadingEngineDict):

            srcShape = srcGeo.getShape()
            trgShape = trgGeo.getShape()

            srcEngineConnected = [engine.name() for engine in srcShape.listConnections(type='shadingEngine')]

            for srcEngine in srcEngineConnected:
                if not shadingEngineDict.has_key(srcEngine): continue

                targetEngine = shadingEngineDict[srcEngine]
                if not targetEngine: continue

                cons = [con for con in pymel.core.listConnections(srcEngine, s=1, d=0, p=1, c=1) if
                        con[1].type() in ['float3', 'message']]
                targetShader = cons[0][0].node()
                selObjs = targetShader.elements()
                targetObjs = []
                for selObj in selObjs:
                    if selObj.node() != srcShape: continue
                    if selObj.find('.') != -1:
                        sepSelObjs = pymel.core.ls( selObj )
                        for sepSelObj in sepSelObjs:
                            targetObjs.append( trgGeo + '.' + sepSelObj.split('.')[-1] )
                    else:
                        targetObjs.append(trgShape.name())

                for targetObj in targetObjs:
                    cmds.sets(targetObj, e=1, forceElement=targetEngine)


        def duplicateShadingNetwork(node, **options):
            def isDoNotDeleteTarget(node):
                for attr in ['wm']:
                    if pymel.core.attributeQuery(attr, node=node, ex=1): return True
                return False

            checkNodes = []
            for srcNode in node.listConnections(s=1, d=0):
                checkNodes += srcNode.history()

            disconnectedList = []
            for checkNode in checkNodes:
                if isDoNotDeleteTarget(checkNode): continue
                nodeSrcCons = checkNode.listConnections(s=1, d=0, p=1, c=1)
                for origAttr, srcAttr in nodeSrcCons:
                    srcNode = srcAttr.node()
                    if not isDoNotDeleteTarget(srcNode): continue
                    srcAttr // origAttr
                    disconnectedList.append((srcAttr, origAttr))
            options.update({'un': 1})

            try:
                duNodes = pymel.core.duplicate(node, **options)
                duNode = duNodes[0]
            except:
                return None
            origHistory = node.history()
            duHistory = duNode.history()

            for srcAttr, origAttr in disconnectedList:
                srcAttr >> origAttr
                if not origAttr.node() in origHistory: continue
                historyIndex = origHistory.index(origAttr.node())
                pymel.core.connectAttr(srcAttr, duHistory[historyIndex] + '.' + origAttr.longName())
            return duNode


        def duplicateShadingEngine(engine):

            engine = pymel.core.ls(engine)[0]
            if engine.name() == 'initialShadingGroup':
                # print "engine is initial"
                return None
            cons = [con for con in engine.listConnections(s=1, d=0, p=1, c=1) if con[1].type() in ['float3', 'message']]
            if not cons: None

            newEngine = pymel.core.sets(renderable=True, noSurfaceShader=True, empty=1, n='du_' + engine.nodeName())
            for origCon, srcCon in cons:
                du_targetShader = duplicateShadingNetwork(srcCon.node(), n='du_' + srcCon.node().nodeName())
                if not du_targetShader: continue
                du_targetShader.attr(srcCon.longName()) >> newEngine.attr(origCon.longName())
            return newEngine.name()


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


        def copyAttribute(inputSrc, inputDst, attrName, replaceAttrName=None):

            if not replaceAttrName:
                replaceAttrName = attrName

            src = pymel.core.ls(inputSrc)[0]
            dst = pymel.core.ls(inputDst)[0]

            srcAttr = src.attr(attrName)
            defaultList = pymel.core.attributeQuery(attrName, node=src, ld=1)

            try:
                if srcAttr.type() == 'enum':
                    enumNames = pymel.core.attributeQuery(attrName, node=inputSrc, le=1)
                    enumStr = ':'.join(enumNames) + ':'
                    addAttr(dst, ln=srcAttr.longName(), sn=srcAttr.nodeName(), at=srcAttr.type(), en=enumStr,
                                     dv=defaultList[0])
                else:
                    addAttr(dst, ln=srcAttr.longName(), sn=srcAttr.nodeName(), at=srcAttr.type(),
                                     dv=defaultList[0])
            except:
                try:
                    addAttr(dst, ln=srcAttr.longName(), sn=srcAttr.nodeName(), dt=srcAttr.type(),
                                     dv=defaultList[0])
                except:
                    pass

            addAttr(dst, ln=replaceAttrName)
            dstAttr = dst.attr(replaceAttrName)
            if srcAttr.type() in ['double', 'long']:
                dstAttr.setRange(srcAttr.getRange())
            if srcAttr.isInChannelBox():
                dstAttr.showInChannelBox(True)
            if srcAttr.isKeyable():
                dstAttr.setKeyable(True)

            try:
                dstAttr.set(srcAttr.get())
            except:
                pass


        def copyShaderAndReplaceConnection(origSel, destSel):

            origNamespace = origSel.namespace()
            destNamespace = destSel.namespace()

            def isVisible(target):
                allParents = target.getAllParents()
                allParents.append(target)
                for parent in allParents:
                    if not parent.attr('lodVisibility').get(): return False
                    if parent.io.get(): return False
                return True

            def udAttrCopy(src, trg):
                udAttrs = cmds.listAttr(src.name(), ud=1)
                if not udAttrs: return
                for udAttr in udAttrs:
                    try:
                        copyAttribute(src, trg, udAttr)
                    except:
                        cmds.warning("Failed to copy attribute : %s" % udAttr)

            origChildren = [origChild for origChild in origSel.listRelatives(c=1, ad=1, type='transform')]
            origChildren.append(origSel)

            progressValue = 0

            childCheckPercent = 0.05
            enginecheckPercent = 0.05
            newShaderAssignPercent = 0.75
            replaceConnectPercent = 0.15

            numChildren = len(origChildren)

            engines = []
            # print "check children"

            for i in range(numChildren):
                origChild = origChildren[i]
                origChildShape = origChild.getShape()
                if not origChildShape: continue
                if not origChildShape.nodeType() == 'mesh': continue
                enginesEach = origChildShape.listConnections(type='shadingEngine')
                if not enginesEach: continue
                engines += enginesEach
                progressValue = i * (1.0 / numChildren) * childCheckPercent
            progressValue = childCheckPercent

            # print "check engine"

            engines = list(set(engines))
            enginesDict = {}
            numEngines = len(engines)
            for i in range(numEngines):
                engine = engines[i]
                duEngine = duplicateShadingEngine(engine)
                enginesDict[engine.name()] = duEngine
                progressValue = i * (1.0 / numEngines) * enginecheckPercent + childCheckPercent
            progressValue = childCheckPercent + enginecheckPercent

            # print "check duplicate shading"

            for i in range(numChildren):
                progressValue = i * (1.0 / numChildren) * newShaderAssignPercent + childCheckPercent + enginecheckPercent

                origChild = origChildren[i]
                destChildName = '|'.join(
                    [destNamespace + name[len(origNamespace):] for name in origChild.name().split('|')])
                # print "orig child : ", origChild
                # print "destChildName : ", destChildName
                if not pymel.core.objExists(destChildName): continue
                destChild = pymel.core.ls(destChildName)[0]

                udAttrCopy(origChild, destChild)

                origChildShape = origChild.getShape()
                destChildShape = destChild.getShape()

                if not origChildShape or not destChildShape: continue
                udAttrCopy(origChildShape, destChildShape)

                if not destChild.getShape().nodeType() == 'mesh': continue
                if not isVisible(origChildShape): continue
                # print "orig child : ", origChild
                # print "dst child : " , destChild
                # if not destChild.nodeName() in ['ex_ch_300_paul_rig_v01:eye_in', 'ex_ch_300_paul_rig_v01:eye_out' ] : continue
                assignToNewShadingEngines(origChild, destChild, enginesDict)
            progressValue = newShaderAssignPercent + childCheckPercent + enginecheckPercent

            # print "check connecitons"

            engineDictKeys = enginesDict.keys()
            for i in range(numEngines):
                engine = engineDictKeys[i]
                duEngine = enginesDict[engine]
                if not duEngine: continue

                hists = pymel.core.listHistory(duEngine)

                # if duEngine.find( 'ch_000_paul_shadingEngine' ) == -1: continue
                # print "du engine : ", duEngine
                for hist in hists:
                    if hist.split('|')[0][:len(origNamespace)] != origNamespace: continue
                    # print hist
                    for origCon, dstCon in hist.listConnections(s=0, d=1, p=1, c=1):
                        origConAttr = '|'.join(
                            [destNamespace + name[len(origNamespace):] for name in origCon.name().split('|')])
                        dstConAttr = dstCon

                        # print origCon, dstCon
                        # print origConAttr, dstConAttr
                        # print "copy attribute : ", origCon.node().name(), origConAttr.split( '.' )[0], '.'.join( origConAttr.split( '.' )[1:] )

                        if not pymel.core.ls(origConAttr): continue
                        try:
                            copyAttribute(origCon.node().name(), origConAttr.split('.')[0],
                                                   '.'.join(origConAttr.split('.')[1:]))
                        except:
                            pass

                        if pymel.core.isConnected(origConAttr, dstConAttr): continue
                        try:
                            pymel.core.connectAttr(origConAttr, dstConAttr, f=1)
                        except:
                            cmds.warning("failed to connect : %s >> %s" % (origConAttr, dstConAttr))
                progressValue = i * ( 1.0 / numEngines) * replaceConnectPercent + newShaderAssignPercent + childCheckPercent + enginecheckPercent
            # print "done"
            progressValue = 1.0


        def getTopTransformNodes():
            trs = cmds.ls(type='transform')
            topTransforms = []
            for tr in trs:
                if cmds.listRelatives(tr, p=1): continue
                print tr, cmds.getAttr( tr + '.hiddenInOutliner' )
                if cmds.getAttr( tr + '.hiddenInOutliner' ): continue
                topTransforms.append(pymel.core.ls(tr)[0])
            return topTransforms


        def cleanScene():
            import pymel.core
            import maya.mel

            audio = pymel.core.ls(type='audio')
            if audio:
                try:
                    pymel.core.delete( audio )
                except:
                    pass

            for unknown in pymel.core.ls(type='unknown'):
                try:
                    pymel.core.delete( unknown )
                except:
                    pass

            displayLayers = pymel.core.ls(type='displayLayer')
            for displayLayer in displayLayers:
                if not displayLayer.v.get(): continue
                if displayLayer.name() == 'defaultLayer': continue
                try:pymel.core.delete(displayLayer)
                except:pass

            sels = pymel.core.ls(type='renderLayer')
            for sel in sels:
                if sel == 'defaultRenderLayer': continue
                try:pymel.core.delete(sel)
                except:pass
            maya.mel.eval('MLdeleteUnused;')

            try:
                pymel.core.delete('frameCounterUpdate')
            except:
                pass
            try:
                pymel.core.delete('timeCodeUpdate')
            except:
                pass

        def createExportNamespace(origNamespace):

            if origNamespace:
                splitNs = origNamespace[:-1].split(':')
                joinedSplits = ':'.join(splitNs[:-1])
                if joinedSplits:
                    ex_namespace = 'ex_' + joinedSplits + ':' + splitNs[-1]
                else:
                    ex_namespace = 'ex_' + splitNs[-1]
            else:
                ex_namespace = 'ex'
            namespaceList = cmds.namespaceInfo(lon=1)
            if not ex_namespace in namespaceList:
                try:cmds.namespace(addNamespace=ex_namespace)
                except:pass
            return ex_namespace + ':'


        def removeUnknownPlugin():
            plugins = cmds.unknownPlugin(q=1, list=1)
            if not plugins: plugins = []
            for plugin in plugins:
                try:
                    cmds.unknownPlugin(plugin, remove=1)
                except:
                    pass

        def removeNamespaceInScene():
            for ns in cmds.namespaceInfo(lon=1):
                nsNodes = pymel.core.ls(ns + ':*')
                for nsNode in nsNodes:
                    renamedName = nsNode.nodeName().replace(ns + ':', '')
                    try:
                        nsNode.rename(renamedName)
                    except:
                        print nsNode
                try:
                    cmds.namespace(deleteNamespaceContent=1, removeNamespace=':' + ns)
                except:
                    pass

        def cleanMeshInScene(*args):
            from maya import cmds
            def cleanMesh(targetObj):
                targetShapes = cmds.listRelatives(targetObj, s=1, f=1)
                for targetShape in targetShapes:
                    if not cmds.getAttr(targetShape + '.io'): continue
                    if cmds.listConnections(targetShape + '.outMesh', s=0, d=1): continue
                    if cmds.listConnections(targetShape + '.worldMesh', s=0, d=1): continue
                    cmds.delete(targetShape)
                    cmds.warning("%s is deleted" % targetShape)

            meshs = cmds.ls(type='mesh')

            meshObjs = []
            for mesh in meshs:
                if cmds.getAttr(mesh + '.io'): continue
                meshP = cmds.listRelatives(mesh, p=1, f=1)[0]
                if meshP in meshObjs: continue
                meshObjs.append(meshP)
            for meshObj in meshObjs:
                cleanMesh(meshObj)


        from maya import mel
        import pymel.core

        plugins = ['AbcExport', 'AbcImport', 'gpuCache']

        for plugin in plugins:
            if not cmds.pluginInfo(plugin, q=1, l=1):
                cmds.loadPlugin(plugin)

        cmds.file( scenePath, f=1, options="v=0;", ignoreVersion=1, typ="mayaBinary", o=1, loadReferenceDepth='none' )
        targetNodes = []
        cmds.file( loadReference = 1, referenceNode=targetReferenceNode )
        for constrainReference in constrainReferences:
            cmds.file(loadReference=1, referenceNode=constrainReference)
        targetNodes += [node for node in pymel.core.ls(pymel.core.referenceQuery(targetReferenceNode, nodes=1)) if
                 node.nodeType() == 'transform']
        targetNamespace = cmds.referenceQuery( targetReferenceNode, namespace=1 )[1:]

        exportBaseDir = os.path.splitext( scenePath )[0]
        if not os.path.exists( exportBaseDir ) or not os.path.isdir( exportBaseDir ):
            os.makedirs( exportBaseDir )
        exportCachePath = exportBaseDir + '/' + targetNamespace + '.abc'

        targetNodes = pymel.core.ls( targetNodes )
        topParents = []
        for targetNode in targetNodes:
            parents = targetNode.getAllParents()
            if not parents:
                topParents.append( targetNode )
                continue
            topParents.append( parents[-1] )
        topParents = [ topParent for topParent in list( set( topParents ) ) if not topParent.attr('hiddenInOutliner').get() ]
        cacheDirectory = os.path.dirname(exportCachePath)
        if not os.path.exists(cacheDirectory): os.makedirs(cacheDirectory)

        minFrame = cmds.playbackOptions( q=1, min=1 )
        maxFrame = cmds.playbackOptions( q=1, max=1 )
        cmds.AbcExport(j="-frameRange %d %d -uvWrite -wholeFrameGeo -writeVisibility -eulerFilter\
                      -dataFormat ogawa %s -file %s" % ( minFrame, maxFrame, ' '.join(['-root %s' % targetNode.name() for targetNode in topParents]), exportCachePath))

        if exportFile:
            exportFilePath = exportBaseDir + '/' + targetNamespace + '.mb'
            origTopTrNodes = getTopTransformNodes()
            cmds.AbcImport( exportCachePath, mode="import" )
            afterTopTrNodes = getTopTransformNodes()

            importedTargets = []
            for afterTopTrNode in afterTopTrNodes:
                if afterTopTrNode in origTopTrNodes: continue
                importedTargets.append(afterTopTrNode)

            topParents.sort()
            importedTargets.sort()
            #print "len top parents : ", len( topParents )
            #print "len imported targets : ", len( importedTargets )

            for i in range( len( topParents ) ):
                topParent = topParents[i]
                importedTarget = importedTargets[i]
                origNamespace = topParent.namespace()
                lenOrigNamespace = len( origNamespace )
                ex_namespace = createExportNamespace( origNamespace )
                [ importedChild.rename(ex_namespace + importedChild.nodeName()[lenOrigNamespace:] ) for importedChild in pymel.core.listRelatives(importedTarget, c=1, ad=1)]
                importedTarget.rename(ex_namespace + topParent.nodeName()[lenOrigNamespace:] )
                copyShaderAndReplaceConnection( topParent, importedTarget )

            for ref in cmds.ls(type='reference'):
                try:cmds.file( removeReference=1, referenceNode=ref )
                except:pass

            for topNode in getTopTransformNodes():
                if topNode in importedTargets: continue
                try: pymel.core.delete( topNode )
                except: pass

            try:
                removeUnknownPlugin()
            except:
                cmds.warning( "Failed to remove unknown plugin" )

            try:
                cleanMeshInScene()
            except:
                cmds.warning( "Failed to clean mesh" )

            try:
                cleanScene()
            except:
                cmds.warning( "Failed to clean scene" )

            try:
                removeNamespaceInScene()
            except:
                cmds.warning( "Failed to remove namespace" )

            try:
                mel.eval( 'MLdeleteUnused;' )
            except:
                cmds.warning( "Failed to delete unused nodes" )

            cmds.file( rename=exportFilePath )
            cmds.file( save=1, f=1 )
    #Commands.exportElement2.end
        
        """

        mayapyPath = mel.eval('getenv "MAYA_LOCATION"') + '/bin/mayapy.exe'
        basePath = os.path.splitext( scenePath )[0]
        if not os.path.exists( basePath ) or not os.path.isdir( basePath ):
            os.makedirs( basePath )
        launchPath = basePath + "/sa_exportElementStandalone_launch_%s.py" % "standalone_all"

        for path in [scenePath, launchPath ]:
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))

        standaloneScript = '''
import maya.standalone
from maya import cmds
import json, os
maya.standalone.initialize( name='python' )
@@mainFunction@@
for targetReferenceNode, constrainTargets in @@targetReferenceNodes@@:
    try:Commands.exportElement2( '@@scenePath@@', targetReferenceNode, @@buildScene@@, constrainTargets )
    except:
        import os
        scenePath = '@@scenePath@@'
        infoTxt = os.path.dirname( scenePath ) + '/%s_isFailed.txt' % targetReferenceNode 
        f = open( infoTxt, 'w' )
        f.close()
os.remove( "@@launchPath@@" )
'''
        standaloneScript = standaloneScript.replace("@@scenePath@@", scenePath).replace('@@launchPath@@',
                            launchPath ).replace('@@targetReferenceNodes@@', str(targetReferenceNodes) ).replace( '@@buildScene@@',
                            "True" if buildScene else "False" ).replace( '@@mainFunction@@', mainFunction )
        f = open(launchPath, 'w')
        f.write(standaloneScript)
        f.close()

        print "----------------"
        print "standaloneScript"
        print standaloneScript
        print "----------------"

        mel.eval('system( "start %s %s" )' % (mayapyPath, launchPath))


    @staticmethod
    def makeEmptyScene(scenePath ):

        from maya import mel
        import ntpath, os

        sceneDir, sceneName = ntpath.split( scenePath )
        jsonPath = sceneDir + '/' + sceneName.replace( '.' , '_' ) + '.json'
        launchPath = sceneDir + '/' + sceneName.replace( '.', '_' ) + '.py'

        if not os.path.exists(sceneDir) or not os.path.isdir(sceneDir):
            os.makedirs(sceneDir)

        minFrame = cmds.playbackOptions(q=1, min=1)
        maxFrame = cmds.playbackOptions(q=1, max=1)
        timeUnit = cmds.currentUnit(t=1, q=1)
        data = dict(minFrame=minFrame, maxFrame=maxFrame, timeUnit=timeUnit)
        f = open(jsonPath, 'w')
        json.dump(data, f, indent=2)
        f.close()

        mayapyPath = mel.eval('getenv "MAYA_LOCATION"') + '/bin/mayapy.exe'

        for path in [scenePath, jsonPath, launchPath]:
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))

        standaloneScript = '''
import maya.standalone
from maya import cmds
import json, os
maya.standalone.initialize( name='python' )
f = open( '@@jsonPath@@', 'r' )
data = json.load( f )
f.close()
cmds.currentUnit( t=data['timeUnit'] )
cmds.playbackOptions( ast=data['minFrame'] )
cmds.playbackOptions( aet=data['maxFrame'] )
cmds.playbackOptions( min=data['minFrame'] )
cmds.playbackOptions( max=data['maxFrame'] )
cmds.file( rename='@@scenePath@@' )
cmds.file( save=1, f=1 )
os.remove( "@@jsonPath@@" )
os.remove( "@@launchPath@@" )
'''

        standaloneScript = standaloneScript.replace("@@jsonPath@@", jsonPath).replace("@@scenePath@@", scenePath).replace( '@@launchPath@@', launchPath )
        f = open(launchPath, 'w')
        f.write(standaloneScript)
        f.close()

        mel.eval('system( "start %s %s" )' % (mayapyPath, launchPath))



    @staticmethod
    def removeSceneNamespace( scenePath ):

        from maya import mel
        import ntpath

        mayapyPath = mel.eval('getenv "MAYA_LOCATION"') + '/bin/mayapy.exe'

        for path in [scenePath]:
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))

        sceneDir, sceneName = ntpath.split( scenePath )
        launchPath = sceneDir + "/sa_removeSceneNamespace_launch_%s.py" % sceneName.replace( '.', '_' )

        standaloneScript = '''
import maya.standalone
from maya import cmds
maya.standalone.initialize( name='python' )
import pymel.core
cmds.file( "@@scenePath@@", f=1, options="v=0;",  ignoreVersion=1, loadReferenceDepth="none",  typ="mayaBinary", o=1 )
import json, os
plugins = cmds.unknownPlugin( q=1, list=1 )
if not plugins: plugins = []
for plugin in plugins:
    cmds.unknownPlugin( plugin, remove=1 )
nsList = cmds.namespaceInfo( lon=1 )
for ns in nsList:
    nsNodes = pymel.core.ls( ns + ':*' )
    if not nsNodes: continue
    for nsNode in nsNodes:
        renamedName = nsNode.nodeName().replace( ns+':', '' )
        nsNode.rename( renamedName )
    cmds.namespace( removeNamespace=ns )
for ref in cmds.ls( type='reference' ):
    cmds.file( removeReference=1, referenceNode=ref )
cmds.file( save=1 )
os.remove( "@@launchScript@@" )
'''
        standaloneScript = standaloneScript.replace("@@scenePath@@", scenePath).replace( "@@launchScript@@",launchPath )

        f = open(launchPath, 'w')
        f.write(standaloneScript)
        f.close()
        mel.eval('system( "start %s %s" )' % (mayapyPath, launchPath))




    @staticmethod
    def exportFileUnloadedReference( refNode ):

        from maya import mel
        import ntpath

        refNode = cmds.referenceQuery( pymel.core.ls( refNode )[0].name(), rfn=1 )

        mayapyPath = mel.eval('getenv "MAYA_LOCATION"') + '/bin/mayapy.exe'

        scenePath = cmds.file( q=1, sceneName=1 )
        sceneDir, sceneName = ntpath.split( scenePath )
        launchPath = sceneDir + "/sa_exportFileUnloadedReference_launch_%s.py" % refNode

        standaloneScript = """
import maya.standalone
from maya import cmds
import os
maya.standalone.initialize( name='python' )

def exportFileUnloadedReference( scenePath, refNode ):

    from maya import cmds
    import ntpath, os
    import pymel.core

    def getTopTransformNodes():
        trs = cmds.ls(type='transform')
        topTransforms = []
        for tr in trs:
            if cmds.listRelatives(tr, p=1): continue
            topTransforms.append(pymel.core.ls(tr)[0])
        return topTransforms
    
    def removeNamespaceInScene():
        for ns in cmds.namespaceInfo( lon=1 ):
            nsNodes = pymel.core.ls( ns + ':*' )
            for nsNode in nsNodes:
                renamedName = nsNode.nodeName().replace( ns+':', '' )
                try:nsNode.rename( renamedName )
                except:print nsNode
            try:cmds.namespace( deleteNamespaceContent=1, removeNamespace= ':'+ns )
            except:pass
    
    def removeUnknownPlugin():
        plugins = cmds.unknownPlugin( q=1, list=1 )
        if not plugins: plugins = []
        for plugin in plugins:
            try:cmds.unknownPlugin( plugin, remove=1 )
            except:pass
    
    cmds.file( scenePath, f=1, options="v=0;",  ignoreVersion=1, loadReferenceDepth="none",  typ="mayaBinary", o=1 )
    
    cmds.file( loadReference=1, referenceNode=refNode )
    referenceObjects = cmds.ls( [ target for target in cmds.referenceQuery( refNode, nodes = 1 ) if cmds.objExists( target ) ], type='transform' )
    
    import pymel.core
    pymel.core.select( referenceObjects )
    
    fileName = cmds.referenceQuery( refNode, filename=1 )
    ns       = cmds.referenceQuery( refNode, namespace=1 )[1:]

    scenePath = cmds.file( q=1, sceneName=1 )
    sceneDir, sceneName = ntpath.split( scenePath )
    exportDir = sceneDir + '/' + os.path.splitext( sceneName )[0]
    if not os.path.exists( exportDir ) or os.path.isfile( exportDir ):
        os.makedirs( exportDir )
    if not ns: ns = 'bg'
    exportPath = exportDir + '/' + ns + '.mb'
    
    print "export path : ", exportPath
    
    cmds.file( exportPath, es=1, f=1, options='v=0', typ='mayaBinary', pr=1 )
    cmds.file( exportPath, f=1, options="v=0;", ignoreVersion=1, loadReferenceDepth="none", typ="mayaBinary", o=1 )
    cmds.file( loadReference=1, referenceNode=refNode )
    cmds.file( importReference=1, referenceNode=refNode )
    removeNamespaceInScene()
    removeUnknownPlugin()
    cmds.file( save=1, f=1)
    
exportFileUnloadedReference( "@@scenePath@@", "@@refNode@@" )
os.remove( "@@launchPath@@" )
"""
        #print "scene path : ", scenePath
        #print "launchPath : ", launchPath
        #print "refNode : ", refNode
        standaloneScript = standaloneScript.replace("@@scenePath@@", scenePath).replace( "@@launchPath@@",launchPath ).replace( "@@refNode@@", refNode )

        f = open(launchPath, 'w')
        f.write(standaloneScript)
        f.close()
        #print "start %s %s" % (mayapyPath, launchPath)
        mel.eval('system( "start %s %s" )' % (mayapyPath, launchPath))




class Widget_Separator( QFrame ):

    def __init__(self, *args, **kwargs ):
        super( Widget_Separator, self ).__init__( *args, **kwargs )
        self.setFrameShape(QFrame.HLine)




class Widget_basePath( QWidget, Cmds_file_control ):

    path_uiInfo = Base.path_basedir + "/Widget_export_basePath.json"

    def __init__(self, *args,  **kwargs):
        super( Widget_basePath, self ).__init__( *args, **kwargs )
        mainLayout = QHBoxLayout(self);mainLayout.setContentsMargins(0, 0, 0, 0)

        label = QLabel( "Base Path : " )
        label.setStyleSheet( "font-size: 14px;" )
        lineEdit = QLineEdit(); lineEdit.setFixedHeight( 25 )
        button = QPushButton( "..." ); button.setMaximumWidth( 30 )

        mainLayout.addWidget( label )
        mainLayout.addWidget( lineEdit )
        mainLayout.addWidget( button )

        targetdir = os.path.splitext( cmds.file( q=1, sceneName=1 ) )[0]
        lineEdit.setText( targetdir )
        self.lineEdit = lineEdit
        button.clicked.connect( self.getBasePath )


    def getBasePath(self):

        if int(cmds.about(v=1)) < 2017:
            import shiboken
            from PySide.QtGui import QFileDialog, QWidget, QDialog
        else:
            import shiboken2 as shiboken
            from PySide2.QtWidgets import QFileDialog, QWidget, QDialog

        winName = "dialog_getDirectory"
        mayaWin = shiboken.wrapInstance(long(maya.OpenMayaUI.MQtUtil.mainWindow()), QWidget)

        existing_widgets = mayaWin.findChildren(QDialog, winName)
        if existing_widgets: map(lambda x: x.deleteLater(), existing_widgets)

        dialog = QFileDialog( mayaWin )
        dialog.setObjectName( winName )
        dialog.setDirectory( os.path.splitext( cmds.file( q=1, sceneName=1 ) )[0] )
        choosedFolder = dialog.getExistingDirectory()
        if choosedFolder: self.lineEdit.setText(choosedFolder)




class TreeWidgetItem_asset( QTreeWidgetItem, Cmds_file_control ):

    def __init__(self, *args, **kwargs ):

        super(TreeWidgetItem_asset, self).__init__(*args, **kwargs)
        self.asset = None

        self.checkBox = QCheckBox();
        self.checkBox.setFixedWidth(20)
        self.checkBox.setChecked(True)
        self.treeWidget().setItemWidget(self, 0, self.checkBox)

        w_constrainObjects = QWidget(self.treeWidget())
        lay_constrainObjects = QHBoxLayout(w_constrainObjects)
        lay_constrainObjects.setContentsMargins(0, 0, 0, 0);
        lay_constrainObjects.setSpacing(0)
        lineEdit_constrainObjects = QLineEdit()
        button_constrainObjects = QPushButton("Load")
        lay_constrainObjects.addWidget(lineEdit_constrainObjects)
        lay_constrainObjects.addWidget(button_constrainObjects)
        self.treeWidget().setItemWidget( self, 2, w_constrainObjects )

        self.lineEdit = lineEdit_constrainObjects

        self.checkBox.stateChanged.connect(self.setCheckState)
        button_constrainObjects.clicked.connect( self.loadConstrainObjects )


    def loadConstrainObjects(self):

        selReferences = cmds.ls( sl=1, type='reference' )
        if selReferences:
            self.lineEdit.setText(','.join(selReferences))
        else:
            self.lineEdit.setText("")


    def setAsset(self, asset ):

        self.asset = asset
        self.setText(1, asset.name() )
        self.treeWidget().resizeColumnToContents( 1 )


    def setCheckState(self):

        allChecked = True
        originalCheckValues = []
        for checkBox in [ self.treeWidget().topLevelItem(i).checkBox for i in range( self.treeWidget().topLevelItemCount() )]:
            if not checkBox.isChecked():
                allChecked = False;
            originalCheckValues.append( checkBox.isChecked() )

        if allChecked:
            self.treeWidget().checkBox_allItems.setChecked( True )
        else:
            self.treeWidget().checkBox_allItems.setChecked( False )

        for i in range( self.treeWidget().topLevelItemCount() ):
            checkBox = self.treeWidget().topLevelItem(i).checkBox
            checkBox.setChecked( originalCheckValues[i] )


    def getAsset(self):
        return self.asset


    def getFileName(self):
        namespace = self.asset.namespace()
        if not namespace: namespace = self.asset.name()
        return namespace.replace( ':', '_' ) + '.mb'


    def getCacheName(self):
        namespace = self.asset.namespace()
        if not namespace: namespace = self.asset.name()
        return namespace.replace(':', '_') + '.abc'


    def getConstrainReferences(self):
        constrainReferences = self.lineEdit.text()
        if not constrainReferences:
            return []
        else:
            return constrainReferences.split( ',' )





class Widget_exportAsset( QWidget, Cmds_file_control ):

    def __init__(self, *args, **kwargs ):

        super( Widget_exportAsset, self ).__init__( *args, **kwargs )
        self.installEventFilter( self )
        mainLayout = QVBoxLayout( self ); mainLayout.setContentsMargins( 0,0,0,0 ); mainLayout.setSpacing( 5 )

        treeWidget = QTreeWidget()
        headerItem = treeWidget.headerItem()
        checkBox_allItems = QCheckBox( treeWidget ); checkBox_allItems.setFixedWidth( 20 )
        checkBox_allItems.setChecked( True )
        checkBox_allItems.setStyleSheet( "margin: 6px 6px" )
        treeWidget.setItemWidget( headerItem, 0, checkBox_allItems )
        headerItem.setText( 0, "" )
        headerItem.setText(1, "Target Node")
        headerItem.setText(2, "Constrain Objects")
        treeWidget.setRootIsDecorated( False )
        treeWidget.setStyleSheet("QTreeWidget::item { border-left: 1px solid gray;border-bottom: 1px solid gray; padding: 3px}\
                                 QTreeWidget{ font-size:13px;}" )
        treeWidget.header().setStyleSheet( "font-size:12px;" )
        treeWidget.setColumnWidth( 0, 22 )

        w_buttons = QWidget()
        lay_buttons  = QHBoxLayout( w_buttons ); lay_buttons.setContentsMargins( 0,0,0,0 ); lay_buttons.setSpacing( 5 )
        button_load = QPushButton( "Load Selected" )
        button_clear = QPushButton( "Clear" )
        lay_buttons.addWidget( button_load )
        lay_buttons.addWidget( button_clear )
        w_buttons.setStyleSheet( "font:14px;" )

        mainLayout.addWidget( treeWidget )
        mainLayout.addWidget( w_buttons )

        self.treeWidget = treeWidget
        QtCore.QObject.connect( button_load,  QtCore.SIGNAL("clicked()"), self.cmd_loadList )
        QtCore.QObject.connect( button_clear, QtCore.SIGNAL("clicked()"), self.treeWidget.clear )

        self.treeWidget.setSelectionMode( QAbstractItemView.ExtendedSelection )
        self.treeWidget.checkBox_allItems = checkBox_allItems

        checkBox_allItems.stateChanged.connect( self.cmd_setCheckAsset )
        treeWidget.itemPressed.connect( self.cmd_selectItems )


    def cmd_setCheckAsset(self):

        if self.treeWidget.checkBox_allItems.isChecked():
            for item in [ self.treeWidget.topLevelItem(i) for i in range( self.treeWidget.topLevelItemCount() ) ]:
                item.checkBox.setChecked( True )
        else:
            for item in [self.treeWidget.topLevelItem(i) for i in range(self.treeWidget.topLevelItemCount())]:
                item.checkBox.setChecked( False )


    def cmd_selectItems(self, itemWidget, column ):
        if column == 0:
            itemWidget.checkBox.setChecked( not itemWidget.checkBox.isChecked() )
        else:
            pymel.core.select( [ item.asset for item in self.treeWidget.selectedItems() ] )



    def cmd_loadList( self ):

        self.treeWidget.clear()
        def cmpAsset( first, second ):
            firstName = first.name().split( ':' )[0]
            secondName = second.name().split( ':' )[0]
            if firstName > secondName:
                return 1
            elif firstName < secondName:
                return -1
            else:
                return 0

        currentItems = [ self.treeWidget.topLevelItem( i ).asset for i in range( self.treeWidget.topLevelItemCount() ) ]

        for asset in pymel.core.ls(sl=1):
            if asset in currentItems: continue
            currentItems.append( asset )
        currentItems.sort( cmpAsset )

        self.treeWidget.clear()
        for asset in currentItems:
            item = TreeWidgetItem_asset(self.treeWidget)
            item.setAsset( asset )

        self.treeWidget.checkBox_allItems.setChecked( True )
        self.treeWidget.resizeColumnToContents(0)
        self.treeWidget.resizeColumnToContents(1)
        self.treeWidget.setColumnWidth(0, self.treeWidget.columnWidth(0) - 10)
        self.treeWidget.setColumnWidth(1, self.treeWidget.columnWidth(1) + 10)



class Widget_exportOption( QGroupBox, Cmds_file_control ):

    path_uiInfo = Base.path_basedir + '/Widget_unloadReferenceCheck.json'

    def __init__(self, *args, **kwargs ):

        super( Widget_exportOption, self ).__init__( *args, **kwargs )
        mainLayout = QGridLayout( self ); mainLayout.setContentsMargins( 0,0,0,0 )

        def getCheckBoxWidget( label ):
            w_checkBox = QWidget()
            lay_checkBox = QHBoxLayout(w_checkBox)
            checkBox = QCheckBox();
            checkBox.setFixedWidth(30)
            checkBox.setChecked( True )
            label = QLabel(label)
            lay_checkBox.addWidget(checkBox)
            lay_checkBox.addWidget(label)
            w_checkBox.checkBox = checkBox
            return w_checkBox

        w_buildScene  = getCheckBoxWidget("Build Scene")
        mainLayout.addWidget( w_buildScene, 0, 0 )
        self.w_buildScene  = w_buildScene

        w_buildScene.checkBox.stateChanged.connect( self.saveInfo )
        self.loadInfo()


    def saveInfo(self):

        isCheckedBuildScene = self.w_buildScene.checkBox.isChecked()

        data = {}
        data[ 'isChecked_buildScene' ] = isCheckedBuildScene

        self.writeData( data, Widget_exportOption.path_uiInfo )


    def loadInfo(self):

        data = self.readData( Widget_exportOption.path_uiInfo )
        if not data: data = {}
        if data.has_key( 'isChecked_buildScene' ):
            self.w_buildScene.checkBox.setChecked( data['isChecked_buildScene'] )



class Dialog_progressbar(QDialog):

    mayaWin = shiboken.wrapInstance(long(maya.OpenMayaUI.MQtUtil.mainWindow()), QWidget)
    objectName = "sg_pingo_widget_scene_optimize_export_progress"
    title = "Progress"
    defaultWidth = 600
    defaultHeight = 30

    def __init__(self, *args, **kwargs):
        title = Dialog_progressbar.title
        if kwargs.has_key('title'):
            title = kwargs.pop('title')

        super(Dialog_progressbar, self).__init__(*args, **kwargs)
        self.setObjectName(Dialog_progressbar.objectName)
        self.setWindowTitle(title)
        self.resize(Dialog_progressbar.defaultWidth, Dialog_progressbar.defaultHeight)

        mainLayout = QVBoxLayout(self);
        mainLayout.setContentsMargins(3, 3, 3, 3);
        mainLayout.setSpacing(0)
        progressbar = QProgressBar()
        mainLayout.addWidget(progressbar)

        progressbar.setRange(0, 1000)
        progressbar.valueChanged
        self.progressbar = progressbar
        self.title = title


    def setValue(self, value):
        self.setWindowTitle("%s : %.2f" % (self.title, value * 100))
        self.progressbar.setValue( value * 1000 )
        QApplication.instance().processEvents()



class Window( QDialog, Cmds_file_control ):

    mayaWin = shiboken.wrapInstance(long(maya.OpenMayaUI.MQtUtil.mainWindow()), QWidget)
    objectName = "sg_pingo_widget_scene_optimize_export"
    title = "PINGO - Scene Optimize - Export"
    defaultWidth = 400
    defaultHeight = 100
    path_uiInfo = Base.path_basedir + "/Main_Window.json"

    def __init__(self, *args, **kwrgs):

        existing_widgets = Window.mayaWin.findChildren( QDialog, Window.objectName )
        if existing_widgets: map( lambda x: x.deleteLater(), existing_widgets )

        super( Window, self ).__init__(  *args, **kwrgs )
        self.installEventFilter( self )
        self.setObjectName( Window.objectName )
        self.setWindowTitle( Window.title )

        mainLayout = QVBoxLayout( self )

        w_basePath    = Widget_basePath()
        w_exportAsset = Widget_exportAsset()
        w_exportOption = Widget_exportOption()
        w_buttons = QWidget()
        lay_buttons = QGridLayout(w_buttons); lay_buttons.setContentsMargins( 0,0,0,0 )
        button_export = QPushButton("EXPORT")
        button_exportStandalone = QPushButton("EXPORT STANDALONE")
        button_reload = QPushButton("RELOAD")
        w_buttons.setStyleSheet("font-size:15px")

        lay_buttons.addWidget(button_export, 0, 0, 1, 1 )
        lay_buttons.addWidget(button_exportStandalone, 0, 1, 1, 1 )
        lay_buttons.addWidget(button_reload, 1, 0, 1, 2 )

        mainLayout.addWidget( w_basePath )
        mainLayout.addWidget( w_exportAsset )
        mainLayout.addWidget( w_exportOption )
        mainLayout.addWidget( w_buttons )

        self.resize( Window.defaultWidth, Window.defaultHeight )
        self.load_shapeInfo( Window.path_uiInfo )

        button_export.clicked.connect( self.cmd_export )
        button_exportStandalone.clicked.connect( self.cmd_exportStandalone )
        button_reload.clicked.connect( self.cmd_reload )

        self.w_w_basePath   = w_basePath
        self.w_exportAsset  = w_exportAsset
        self.w_exportOption = w_exportOption



    def cmd_export(self):

        print "top level item count : ", self.w_exportAsset.treeWidget.topLevelItemCount()

        buildScene = self.w_exportOption.w_buildScene.checkBox.isChecked()
        basePath = self.w_w_basePath.lineEdit.text()
        currentItems = [ self.w_exportAsset.treeWidget.topLevelItem(i) for i in range(self.w_exportAsset.treeWidget.topLevelItemCount()) ]
        exportList = [ [ pymel.core.referenceQuery( currentItem.getAsset(), rfn=1 ) if pymel.core.referenceQuery( currentItem.getAsset(), inr=1 ) else None,
                         currentItem.getAsset(), currentItem.getFileName(), currentItem.getCacheName(), currentItem.getConstrainReferences() ]
                       for currentItem in currentItems if currentItem.checkBox.isChecked() ]

        exportListDict = {}
        for refNode, asset, fileName, cacheName, constrainReferences in exportList:
            if exportListDict.has_key( asset.name() ):
                exportListDict[ asset.name() ][ 'assets' ].append( asset )
            else:
                exportListDict[ asset.name() ] = dict( constrainReferences = constrainReferences )

        #emptyScenePath = basePath + "/emptyScene.mb"
        #if buildScene: Commands.makeEmptyScene( emptyScenePath )

        print "len exportListDict : ", len( exportListDict )

        for assetName in exportListDict:
            constrainReferences = exportListDict[assetName]['constrainReferences']
            Commands.exportElement( assetName, buildScene, constrainReferences )

        f = open( Base.path_refereceBaseInfo, 'w' )
        f.write( basePath )
        f.close()


    def cmd_exportStandalone(self):

        buildScene = self.w_exportOption.w_buildScene.checkBox.isChecked()
        basePath = self.w_w_basePath.lineEdit.text()
        currentItems = [ self.w_exportAsset.treeWidget.topLevelItem(i) for i in range(self.w_exportAsset.treeWidget.topLevelItemCount()) ]
        exportList = [ [ pymel.core.referenceQuery( currentItem.getAsset(), rfn=1 ) if pymel.core.referenceQuery( currentItem.getAsset(), inr=1 ) else None,
                         currentItem.getAsset(), currentItem.getFileName(), currentItem.getCacheName(), currentItem.getConstrainReferences() ]
                       for currentItem in currentItems if currentItem.checkBox.isChecked() ]

        exportListDict = {}
        for refNode, asset, fileName, cacheName, constrainReferences in exportList:
            if exportListDict.has_key( fileName ):
                exportListDict[ fileName ][ 'assets' ].append( asset )
            else:
                exportListDict[ fileName ] = dict( assets = [asset], cacheName=cacheName, refNode=refNode, constrainReferences = constrainReferences )

        #emptyScenePath = basePath + "/emptyScene.mb"
        #if buildScene: Commands.makeEmptyScene( emptyScenePath )

        standaloneAssets = []
        for fileName in exportListDict:
            refNode = exportListDict[ fileName ]['refNode']
            assets  = exportListDict[ fileName ]['assets']
            cacheName = exportListDict[fileName]['cacheName']
            constrainReferences = exportListDict[fileName]['constrainReferences']

            if assets[0].type() == 'reference':
                standaloneAssets.append( [assets[0].name(), constrainReferences] )
            else:
                Commands.exportElement( assets, buildScene, constrainReferences )

        if standaloneAssets:
            Commands.exportElementStandalone(cmds.file(q=1, sceneName=1), standaloneAssets, buildScene )

        f = open( Base.path_refereceBaseInfo, 'w' )
        f.write( basePath )
        f.close()


    def cmd_reload(self):
        Window(Window.mayaWin).show()


    def eventFilter(self, *args, **kwargs ):
        event = args[1]
        if event.type() in [ QtCore.QEvent.Resize, QtCore.QEvent.Move ]:
            try:self.save_shapeInfo( Window.path_uiInfo )
            except:pass



def show():
    from maya import mel, cmds
    plugins = ['AbcExport', 'AbcImport']
    for plugin in plugins:
        if not cmds.pluginInfo(plugin, q=1, l=1):
            cmds.loadPlugin(plugin)

    try: cmds.deleteUI( Window.objectName, wnd=1 )
    except:pass
    Window( Window.mayaWin ).show()



if __name__ == '__main__':
    show()