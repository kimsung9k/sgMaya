import pymel.core



import pymel.core

from maya import cmds
import os, ntpath


def convertTextureToColor( meshTr ):
    meshShape = meshTr.getShape()
    if not meshShape: return None
    shadingEngines = meshShape.listConnections( s=0, d=1, type='shadingEngine' )
    if not shadingEngines: return None
    
    for shadingEngine in shadingEngines:
        shaders = shadingEngine.surfaceShader.listConnections( s=1, d=0 )
        if not shaders: continue
        if not pymel.core.attributeQuery( 'color', node= shaders[0], ex=1 ): continue
        shader = shaders[0]
        cons = shader.attr( 'color' ).listConnections( s=1, d=0, p=1, c=1 )
        if not cons: continue
        hists = []
        for origCon, srcCon in cons:
            hists += srcCon.node().listHistory( pdo=1 )
        
        colorValues = None
        for hist in hists:
            try:
                colorValues = pymel.core.colorAtPoint( hist, o='RGB', su=5, sv=5, mu=0.1, mv=0.1, xu=0.9, xv=0.9 )
                break
            except:
                continue
        if not colorValues: return None
        for origCon, srcCon in cons: srcCon // origCon
        rValue = 0; gValue=0; bValue=0
        for i in range( 0, len( colorValues ), 3 ):
            rValue += colorValues[i]
            gValue += colorValues[i+1]
            bValue += colorValues[i+2]
        rValue /= 25; gValue /= 25; bValue /= 25
        shader.attr( 'color' ).set( rValue, gValue, bValue )



def createCombineObject_shaderBase( geoGrp ):

    def copyShader( inputFirst, inputSecond ):
        first = pymel.core.ls( inputFirst )[0]
        second = pymel.core.ls( inputSecond )[0]
        if first.nodeType() == 'transform':
            firstShape = first.getShape()
        else:
            firstShape = first
        if second.nodeType() == 'transform':
            secondShape = second.getShape()
        else:
            secondShape = second
        engines = firstShape.listConnections( type='shadingEngine' )
        if not engines: return None
        engines = list( set( engines ) )
        cmds.sets( secondShape.name(), e=1, forceElement=engines[0].name() )


    def getSeparatedGroupsByShadingEngines( target ):
        meshs = pymel.core.listRelatives( target, c=1, ad=1, type='mesh' )
        targetShadingEngines = []
        for mesh in meshs:
            shadingEngines = mesh.listConnections( s=0, d=1, type='shadingEngine' )
            if not shadingEngines: shadingEngines = [pymel.core.ls( 'initialShadingGroup' )[0]]
            targetShadingEngines += shadingEngines
        targetShadingEngines = list( set( targetShadingEngines ) )
        
        meshsDict = {}
        for engine in targetShadingEngines:
            meshsDict[ engine.name() ] = []
        
        for mesh in meshs:
            shadingEngines = mesh.listConnections( s=0, d=1, type='shadingEngine' )
            if not shadingEngines: shadingEngines = [pymel.core.ls( 'initialShadingGroup' )[0]]
            meshsDict[ shadingEngines[0].name() ].append( mesh )
        return meshsDict


    def createCombinedMesh( meshs ):
        
        def isVisible( target ):
            allParents = target.getAllParents()
            allParents.append( target )
            for parent in allParents:
                if not parent.v.get(): return False
                if parent.io.get(): return False
                if not parent.attr( 'lodVisibility' ).get(): return False
            return True
        
        visibleMeshs = [ mesh for mesh in meshs if isVisible( mesh ) ]
        if not visibleMeshs: return None
        
        polyUnitMesh = pymel.core.createNode( 'polyUnite' )
        newMesh = pymel.core.createNode( 'mesh' )
        polyUnitMesh.output >> newMesh.inMesh
        
        for i in range( len( visibleMeshs ) ):
            if not isVisible( visibleMeshs[i] ): continue
            visibleMeshs[i].outMesh >> polyUnitMesh.inputPoly[i]
            visibleMeshs[i].wm >> polyUnitMesh.inputMat[i]
        cmds.sets( newMesh.name(), e=1, forceElement='initialShadingGroup' )
        return newMesh.getParent()

    meshsDict = getSeparatedGroupsByShadingEngines( geoGrp )
    meshGrp = pymel.core.createNode( 'transform', n = geoGrp.name()+'_geo' )

    for key in meshsDict:
        if not meshsDict[ key ]: continue
        combinedMesh = createCombinedMesh( meshsDict[ key ] )
        if not combinedMesh: continue
        copyShader( meshsDict[ key ], combinedMesh )
        combinedMesh.setParent( meshGrp )



def createNewMeshGroupFromMeshGroup( meshGrp, inverseMtxObj=None ):

    def isVisible( target ):
        allParents = target.getAllParents()
        allParents.append( target )
        for parent in allParents:
            if not parent.v.get(): return False
            if parent.io.get(): return False
            if not parent.attr( 'lodVisibility' ).get(): return False
        return True

    def copyShader( inputFirst, inputSecond, duplicate=False ):
        first = pymel.core.ls( inputFirst )[0]
        second = pymel.core.ls( inputSecond )[0]
        if not pymel.core.objExists( first ): return None
        if not pymel.core.objExists( second ): return None
        
        try:firstShape = first.getShape()
        except:firstShape = first
        try:secondShape = second.getShape()
        except:secondShape = second
        engines = firstShape.listConnections( type='shadingEngine' )
        if not engines: return None
        
        engines = list( set( engines ) )
        
        copyObjAndEngines = []
        for engine in engines:
            cons = [ con for con in engine.listConnections( s=1, d=0, p=1, c=1 ) if con[1].type() in ['float3','message'] ]
            if not cons: continue
            if duplicate:
                newEngine = pymel.core.sets( renderable=True, noSurfaceShader=True, empty=1, n='du_'+engine.nodeName() )
                for origCon, srcCon in cons:
                    du_targetShader = pymel.core.duplicate( srcCon.node(), un=1, n='du_'+srcCon.node().nodeName() )[0]
                    du_targetShader.attr( srcCon.longName() ) >> newEngine.attr( origCon.longName() )
                engine = newEngine
            
            targetShader = cons[0][0].node()
            pymel.core.hyperShade( objects = targetShader )
            selObjs = pymel.core.ls( sl=1 )
            targetObjs = []
            for selObj in selObjs:
                if selObj.node() != firstShape: continue
                if selObj.find( '.' ) != -1:
                    targetObjs.append( second+'.'+ selObj.split( '.' )[-1] )
                else:
                    targetObjs.append( secondShape.name() )
            if not targetObjs: continue
            for targetObj in targetObjs:
                cmds.sets( targetObj, e=1, forceElement=engine.name() )
                copyObjAndEngines.append( [targetObj, engine.name()] )
        return copyObjAndEngines

    meshs = pymel.core.listRelatives( meshGrp, c=1, ad=1, type='mesh' )
    
    newMeshGrp = pymel.core.createNode( 'transform', n= meshGrp.nodeName() + '_separate' )
    if inverseMtxObj:
        inverseMtxTarget = inverseMtxObj
    else:
        inverseMtxTarget = newMeshGrp
    
    for mesh in meshs:
        if not isVisible( mesh ): continue
        newMesh = pymel.core.createNode( 'mesh' )
        newMeshTr = newMesh.getParent()
        trGeo = pymel.core.createNode( 'transformGeometry' )
        mm = pymel.core.createNode( 'multMatrix' )
        mesh.outMesh >> trGeo.attr( 'inputGeometry' )
        mesh.wm >> mm.i[0]
        inverseMtxTarget.wim >> mm.i[1]
        mm.o >> trGeo.transform
        trGeo.attr( 'outputGeometry' ) >> newMesh.attr( 'inMesh' )
        copyShader( mesh, newMesh )
        newMeshTr.setParent( newMeshGrp )
    pymel.core.xform( newMeshGrp, ws=1, matrix=inverseMtxTarget.wm.get() )
    
    return newMeshGrp
    
    
    
def createGpuCache( inputTarget, timeRange=None ):

    import sgModel
    from maya import mel

    target = pymel.core.ls( inputTarget )[0]
    sceneName = cmds.file( q=1, sceneName=1 )
    gpuCacheDir = os.path.dirname( sceneName ) + '/gpuCache'
    if not os.path.exists( gpuCacheDir ):
        os.makedirs( gpuCacheDir )
    fileName = target.name().replace( '|', '_' ).replace( ':', '_' )
    transformKeep = sgModel.TransformKeep( target )
    transformKeep.setToDefault()
    
    commandsStr = 'gpuCache -startTime @@start@@ -endTime @@end@@ -optimize -optimizationThreshold 10000 -dataFormat ogawa -useBaseTessellation -directory "@@path@@" -fileName "@@filename@@" @@target@@;'
    commandsStr = commandsStr.replace( '@@path@@', gpuCacheDir ).replace( '@@target@@', target.name() ).replace( '@@filename@@', fileName )
    if not timeRange:
        commandsStr = commandsStr.replace( '@@start@@', str( cmds.currentTime( q=1 ) ) )
        commandsStr = commandsStr.replace( '@@end@@', str( cmds.currentTime( q=1 ) ) )
    else:
        commandsStr = commandsStr.replace( '@@start@@', str(timeRange[0]) )
        commandsStr = commandsStr.replace( '@@end@@', str(timeRange[1]) )
    
    print commandsStr
    abcPath = mel.eval( commandsStr )
    transformKeep.setToOrig()
    
    gpuCacheNode = pymel.core.createNode( 'gpuCache' )
    gpuCacheNode.cacheFileName.set( abcPath )
    gpuCacheTr = gpuCacheNode.getParent()
    gpuCacheTr.rename( target.nodeName() + '_gpu' )
    gpuCacheNode.rename( gpuCacheTr.nodeName() + 'Shape' )
    transformKeep.setToOther( gpuCacheTr )
    
    return gpuCacheTr


def createRedshiftProxy( inputTarget, timeRange=None ):
    
    import sgModel
    from maya import mel
    
    target = pymel.core.ls( inputTarget )[0]
    sceneName = cmds.file( q=1, sceneName=1 )
    proxydir = os.path.dirname( sceneName ) + '/proxy'
    if not os.path.exists( proxydir ):
        os.makedirs( proxydir )
    targetName = target.name().replace( '|', '_' ).replace( ':', '_' )
    proxyPath = proxydir + '/%s.rs' % targetName
    pymel.core.select( target )
    transformKeep = sgModel.TransformKeep( target )
    transformKeep.setToDefault()
    if not timeRange:
        mel.eval( 'rsProxy -fp "%s" -sl;' % proxyPath )
    else:
        proxyPath = proxyPath[:-3] + '.####.rs'
        minFrame = pymel.core.playbackOptions( q=1, min=1 )
        maxFrame = pymel.core.playbackOptions( q=1, max=1 )
        mel.eval( 'rsProxy -fp "%s" -s %d -e %d -b 1 -sl;' % ( proxyPath, minFrame, maxFrame ) )
    transformKeep.setToOrig()
    
    newMesh = pymel.core.createNode( 'mesh' )
    rsProxyNode = pymel.core.createNode( 'RedshiftProxyMesh' )
    rsProxyNode.fileName.set( proxyPath )
    if rsProxyNode:
        rsProxyNode.attr( 'useFrameExtension' ).set( 1 )
    rsProxyNode.outMesh >> newMesh.inMesh
    newTransform = newMesh.getParent()
    
    newTransform.rename( target.nodeName() + '_rsProxy' )
    rsProxyNode.rename( newTransform.nodeName() + 'Shape' )
    transformKeep.setToOther( newTransform )
    
    return newTransform



def getShadingEngines( mesh ):
    shadingEngines = mesh.getShape().listConnections( s=0, d=1, type='shadingEngine' )
    return shadingEngines


def optimizeViewportShader( shadingEngine, rendererType, download_csv=True ):
    
    def get_csv_form_google_spreadsheets( link_attributeList, targetPath ):
        import re, urllib, urllib2, os, ssl
        p = re.compile('/d/.+/')
        m = p.search( link_attributeList )
        id_sheet = m.group()[3:-1]
        dirPath = os.path.dirname( targetPath )
        if not os.path.exists( dirPath ): os.makedirs( dirPath )
        
        link_donwload_attributeList = 'https://docs.google.com/spreadsheets/d/%s/export?format=csv' % id_sheet
        
        try:
            context = ssl._create_unverified_context()
            response = urllib2.urlopen(link_donwload_attributeList, context=context)  #How should i pass authorization details here?
            data = response.read()
            f = open( targetPath, 'w' )
            f.write( data )
            f.close()
        except:
            testfile = urllib.URLopener()
            testfile.retrieve( link_donwload_attributeList, targetPath )

    def get_listData_from_csv( csvPath ):
        lines = []
        import csv
        f = open(csvPath, 'r')
        rdr = csv.reader(f)
        for line in rdr:
            lines.append( line )
        f.close() 
        return lines

    def get_dictdata_from_csvData( csvData ):
        dictData = {}
        for i in range( 1, len( csvData ) ):
            name_shader = csvData[i][0]
            dictData[ name_shader ] = {}
            for j in range( 1, len( csvData[i] ) ):
                type_of_attr = csvData[0][j]
                dictData[name_shader][type_of_attr] = csvData[i][j]
        return dictData

    path_csv_shaderAttrs = cmds.about(pd=True) + '/pingo/convert_viewport_shader/shaderAttrList.csv'
    path_csv_seAttrs = cmds.about(pd=True) + '/pingo/convert_viewport_shader/shadingEngineAttrList.csv'
    
    if download_csv:
        link_google_spreadsheets_shaderAttrs = 'https://docs.google.com/spreadsheets/d/1p1GkGgXlsVYBL8m0ZQG8Ghg7Fr-0HdXalusE-wUF-oA/edit?usp=sharing'    
        get_csv_form_google_spreadsheets( link_google_spreadsheets_shaderAttrs, path_csv_shaderAttrs )
        
        link_google_spreadsheets_seAttrs = 'https://docs.google.com/spreadsheets/d/1hvxG8ET1tfv2rqLfEa7eav0xb1_Ti7jR68ze9aSWt_s/edit?usp=sharing'
        get_csv_form_google_spreadsheets( link_google_spreadsheets_seAttrs, path_csv_seAttrs )
        
    if not os.path.exists( path_csv_shaderAttrs ):
        cmds.error( "%s is not exists" % path_csv_shaderAttrs )    
    if not os.path.exists( path_csv_seAttrs ):
        cmds.error( "%s is not exists" % path_csv_seAttrs )
    
    csvdata_shaderAttrs = get_listData_from_csv( path_csv_shaderAttrs )
    csvdata_seAttrs  = get_listData_from_csv( path_csv_seAttrs )
    
    dict_shaderAttrs = get_dictdata_from_csvData( csvdata_shaderAttrs )
    dict_seAttrs     = get_dictdata_from_csvData( csvdata_seAttrs )
    
    """
    print "shader attrs"
    for key in dict_shaderAttrs:
        print key, dict_shaderAttrs[key]
    
    print "se attrs"
    for key in dict_seAttrs:
        print key, dict_shaderAttrs[key]
    """
    
    def separateShader( shadingEngine, dict_seAttrs, renderType ):
        
        def connectToViewportSeAttr( shader, shadingEngine ):
            pymel.core.defaultNavigation( ce=1, source = shader.outColor, destination = shadingEngine.surfaceShader )
        def connectToOutputSeAttr( shader, shadingEngine ):
            pymel.core.defaultNavigation( ce=1, source = shader.outColor, destination = shadingEngine.rsSurfaceShader )
            
        viewportShader = None
        outputShader = None
        
        for origCon, srcCon in shadingEngine.listConnections( s=1, d=0, p=1, c=1 ):
            if not srcCon.type() == 'float3': continue
            if origCon.longName() == dict_seAttrs['viewport']['surfaceShaderAttr']: viewportShader = srcCon.node()
            if origCon.longName() == dict_seAttrs[renderType]['surfaceShaderAttr']: outputShader = srcCon.node()

        if outputShader:
            if viewportShader == outputShader or not viewportShader:
                lambertNode = pymel.core.shadingNode( 'blinn', asShader=1 )
                connectToViewportSeAttr( lambertNode, shadingEngine )
                viewportShader = lambertNode
        if viewportShader:
            if not outputShader:
                connectToOutputSeAttr( viewportShader, shadingEngine )
                lambertNode = pymel.core.shadingNode( 'blinn', asShader=1 )
                connectToViewportSeAttr( lambertNode, shadingEngine )
                outputShader = viewportShader
                viewportShader = lambertNode
        return viewportShader, outputShader


    def connectToViewport_optimized( outputShader, viewportShader, dict_shaderAttrs ):
        
        from pymel.core.general import Attribute as pm_Attribute
        
        def isDoNotDeleteTarget( node ):
            for attr in [ 'wm', 'expression']:
                if pymel.core.attributeQuery( attr, node=node, ex=1 ): return True
            return False
        
        def getSourceConnectDuplicated( target, attrName ):
            
            def duplicateShadingNetwork( node ):
                checkNodes = node.history()
                disconnectedList = []
                for checkNode in checkNodes:
                    if isDoNotDeleteTarget( checkNode ): continue
                    nodeSrcCons = checkNode.listConnections( s=1, d=0, p=1, c=1 )
                    for origAttr, srcAttr in nodeSrcCons:
                        srcNode = srcAttr.node()
                        if not isDoNotDeleteTarget( srcNode ): continue
                        srcAttr // origAttr
                        disconnectedList.append( (srcAttr,origAttr) )
                
                duNodes = pymel.core.duplicate( node, un=1 )
                duNode = duNodes[0]
                
                origHistory = node.history()
                duHistory   = duNode.history()
                
                for srcAttr, origAttr in disconnectedList:
                    srcAttr >> origAttr
                    historyIndex = origHistory.index( origAttr.node() )
                    pymel.core.connectAttr(srcAttr, duHistory[historyIndex] + '.' + origAttr.longName())
                return duNode
            
            if not attrName: return None
            connections = target.attr( attrName ).listConnections( s=1, d=0, p=1, c=1 )
            print target.attr( attrName )
            if connections:
                for origCon, srcCon in connections:
                    duNode = duplicateShadingNetwork( srcCon.node() )
                    return duNode.attr( srcCon.longName() )
            return target.attr( attrName ).get()
        
        def connecToViewportShader( resultS, resultV, attr_sTrg, attr_vTrg, targetShader, outputShader ):
            def deleteOrigConnections( targetAttr ):
                cons = targetAttr.listConnections( s=1, d=0 )
                if not cons: return None
                for con in cons:
                    if isDoNotDeleteTarget( con ): continue
                    [ deleteOrigConnections( attr[0] ) for attr in con.listConnections( s=1, d=0, c=1 ) ]
                    pymel.core.delete( con )
            
            def isConnectedWithOutputShader( targetAttr, outputShader ):
                srcNodes = targetAttr.listConnections( s=1, d=0 )
                for srcNode in srcNodes:
                    cons = srcNode.listConnections( s=0, d=1 )
                    if outputShader in cons: return True
                return False
            
            if attr_sTrg and not isConnectedWithOutputShader( targetShader.attr( attr_sTrg ), outputShader ): 
                deleteOrigConnections( targetShader.attr( attr_sTrg ) )
            if attr_vTrg and not isConnectedWithOutputShader( targetShader.attr( attr_vTrg ), outputShader ):
                deleteOrigConnections( targetShader.attr( attr_vTrg ) )
            
            if attr_sTrg and attr_vTrg:
                if resultS:
                    if isinstance( resultS, pm_Attribute ): resultS >> targetShader.attr( attr_sTrg )
                    else: targetShader.attr( attr_sTrg ).set( resultS )
                if resultV:
                    if isinstance( resultV, pm_Attribute ): resultV >> targetShader.attr( attr_vTrg )
                    else: targetShader.attr( attr_vTrg ).set( resultV )
            elif attr_sTrg:
                if resultS:
                    if isinstance( resultS, pm_Attribute ): resultS >> targetShader.attr( attr_sTrg )
                    else: targetShader.attr( attr_sTrg ).set( resultS )
            elif attr_vTrg:
                if resultV:
                    print "result v"
                    if isinstance( resultV, pm_Attribute ): resultV >> targetShader.attr( attr_vTrg )
                    else: targetShader.attr( attr_vTrg ).set( resultV )
                elif resultS:
                    if isinstance( resultS, pm_Attribute ):
                        revNode = pymel.core.createNode( 'reverse' )
                        [ resultS >> revNode.attr( attr ) for attr in ['inputX','inputY','inputZ'] ]
                        revNode.output >> targetShader.attr( attr_vTrg )
                    else:
                        targetShader.attr( attr_vTrg ).set( [resultS,resultS,resultS] )

        def resizeImage( shader ):
            
            def convertTextureSize_inNode( fileNode ):
                
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
                
                def convertTextureSize( texturePath ):
                    if int( cmds.about( v=1 ) ) < 2017:
                        from PySide import QtCore
                        from PySide.QtGui import QPixmap, QImage
                        from PySide.QtCore import QFile, QIODevice
                    else:
                        from PySide2 import QtCore
                        from PySide2.QtGui import QPixmap, QImage
                        from PySide2.QtCore import QFile, QIODevice
                    folder, fileName = ntpath.split( texturePath )
                    origFileName = fileName if fileName[:8] != 'resized_' else fileName[8:]
                    convertedFileName = 'resized_' + fileName if fileName[:8] != 'resized_' else fileName
                    ext = os.path.splitext( fileName )[-1]
                    origPath = folder + '/' + origFileName
                    renamedPath = folder+"/"+convertedFileName
                    img = QImage( origPath )
                    pixmap = QPixmap()
                    pixmap = pixmap.fromImage( img.scaled(512,512,QtCore.Qt.IgnoreAspectRatio,QtCore.Qt.FastTransformation) )
                    qfile = QFile( renamedPath )
                    qfile.open( QIODevice.WriteOnly )
                    pixmap.save( qfile, ext[1:] ,100)
                    qfile.close()
                    return renamedPath
                
                import re, ntpath, glob
                texturePath = fileNode.fileTextureName.get()
                if fileNode.attr( 'useFrameExtension' ).get():
                    m = re.compile( '\.\d+\.' )
                    folderPath, fileName = ntpath.split( texturePath )
                    p = m.search( fileName )
                    replacedPath = folderPath + '/' + fileName.replace( p.group(), '.*.' )
                    texturePathSequences = glob.glob( replacedPath )
                    for texturePathSequence in texturePathSequences:
                        renamedPath = convertTextureSize( texturePathSequence )
                else:
                    renamedPath = convertTextureSize( texturePath )
                fileNode.fileTextureName.set( renamedPath )

            hists = shader.history( pdo=1 )
            fileNodes = []
            for hist in hists:
                if hist.nodeType() != 'file': continue
                fileNodes.append( hist )
            for fileNode in fileNodes:
                convertTextureSize_inNode( fileNode )
        
        for attr in [ 'color', 'transparency', 'specular' ]:    
            attr_scala_output = dict_shaderAttrs[outputShader.nodeType()]['scala_%s' % attr ]
            attr_vector_output = dict_shaderAttrs[outputShader.nodeType()]['vector_%s' % attr ]
            attr_scala_viewport = dict_shaderAttrs[viewportShader.nodeType()]['scala_%s' % attr ]
            attr_vector_viewport = dict_shaderAttrs[viewportShader.nodeType()]['vector_%s' % attr ]
            resultScala = getSourceConnectDuplicated( outputShader, attr_scala_output )
            resultVector = getSourceConnectDuplicated( outputShader, attr_vector_output )
            connecToViewportShader( resultScala, resultVector, attr_scala_viewport, attr_vector_viewport, viewportShader, outputShader )
        resizeImage( viewportShader )

    viewportShader, outputShader = separateShader( shadingEngine, dict_seAttrs, rendererType )
    connectToViewport_optimized( outputShader, viewportShader, dict_shaderAttrs )
    
    





