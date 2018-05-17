from sgMaya import sgCmds, sgModel
import pymel.core
from maya import OpenMaya, cmds
import copy


def buildJointFromEdgeLineVertices( edges ):
    pymel.core.select( edges )
    resultCurve = pymel.core.ls( pymel.core.polyToCurve( form=2, degree=1 )[0] )[0]
    resultCurveShape = resultCurve.getShape()
    maxValue = int( resultCurveShape.maxValue.get() ) + 1
    
    nulls = sgCmds.createPointOnCurve( resultCurve, maxValue )
    
    startObj = nulls[0]
    endObj = nulls[-1]
    
    poseStart = OpenMaya.MPoint( *pymel.core.xform( startObj, q=1, ws=1, t=1 ) )
    poseEnd   = OpenMaya.MPoint( *pymel.core.xform( endObj,   q=1, ws=1, t=1 ) )
    
    dist = poseStart.distanceTo( poseEnd )
    if dist == 0:
        pymel.core.delete( nulls.pop() )
    
    newJoints = []
    for null in nulls:
        newJoint = pymel.core.createNode( 'joint' )
        sgCmds.replaceObject( null, newJoint )
        newJoints.append( newJoint )
    pymel.core.select( newJoints )
    pymel.core.delete( nulls )




def getInt2Ptr():
    util = OpenMaya.MScriptUtil()
    util.createFromList([0,0],2)
    return util.asInt2Ptr()




def getListFromInt2Ptr( ptr ):
    util = OpenMaya.MScriptUtil()
    v1 = util.getInt2ArrayItem( ptr, 0, 0 )
    v2 = util.getInt2ArrayItem( ptr, 0, 1 )
    return [v1, v2]



def edgeLoopVerticalStartAndEndHammer( inputEdges, percent=1.0 ):
    
    meshName = inputEdges[0].split( '.' )[0]
    inputEdgeIndices = [ pymel.core.ls( inputEdge )[0].index() for inputEdge in inputEdges ]
    
    dagPath = sgCmds.getDagPath( meshName )
    fnMesh = OpenMaya.MFnMesh( dagPath )
    
    existsVertices = [ False for i in range( fnMesh.numVertices() ) ]
    for i in inputEdgeIndices:
        util = OpenMaya.MScriptUtil()
        util.createFromList([0,0],2)
        ptrEdgeToVtxIndex = util.asInt2Ptr()
        fnMesh.getEdgeVertices( i, ptrEdgeToVtxIndex )
        index1 = util.getInt2ArrayItem( ptrEdgeToVtxIndex, 0, 0 )
        index2 = util.getInt2ArrayItem( ptrEdgeToVtxIndex, 0, 1 )
        existsVertices[ index1 ] = True
        existsVertices[ index2 ] = True
    
    for i in range( fnMesh.numVertices() ):
        if not existsVertices[i]: continue
        
        itVertex = OpenMaya.MItMeshVertex( dagPath )
        util = OpenMaya.MScriptUtil()
        util.createFromInt(0)
        prevIndex = util.asIntPtr()
        
        itVertex.setIndex( i, prevIndex )
        edgeIndices = OpenMaya.MIntArray()
        itVertex.getConnectedEdges( edgeIndices )
        
        targetEdges = []
        for j in range( edgeIndices.length() ):
            if edgeIndices[j] in inputEdgeIndices: continue
            targetEdges.append( meshName + '.e[%d]' % edgeIndices[j] )
        sgCmds.edgeStartAndEndWeightHammer( targetEdges, percent )
        cmds.select( targetEdges )
    




def fixEdgeLineJointOrientation( inputTargetJnt ):
    
    targetJnt = pymel.core.ls( inputTargetJnt )[0]
    dcmp = targetJnt.t.listConnections( s=1, d=0, type='decomposeMatrix' )[0]
    mm = dcmp.imat.listConnections( s=1, d=0, type='multMatrix' )[0]
    tr = mm.i[0].listConnections( s=1, d=0 )[0]
    averageNode = tr.listConnections( s=1, d=0, type='plusMinusAverage' )[0]
    
    pointers = averageNode.input3D.listConnections()
    xVector = pymel.core.createNode( 'plusMinusAverage' ); xVector.op.set( 2 )
    zVector = pymel.core.createNode( 'plusMinusAverage' ); zVector.op.set( 2 )
    yVector = pymel.core.createNode( 'vectorProduct' ); yVector.op.set( 2 )
    
    xVector.output3D >> yVector.input2
    zVector.output3D >> yVector.input1
    
    pointers[0].t >> xVector.input3D[0]
    pointers[2].t >> xVector.input3D[1]
    pointers[1].t >> zVector.input3D[0]
    pointers[3].t >> zVector.input3D[1]
    
    fbf = pymel.core.createNode( 'fourByFourMatrix' )
    xVector.output3Dx >> fbf.in00
    xVector.output3Dy >> fbf.in01
    xVector.output3Dz >> fbf.in02
    yVector.outputX >> fbf.in10
    yVector.outputY >> fbf.in11
    yVector.outputZ >> fbf.in12
    zVector.output3Dx >> fbf.in20
    zVector.output3Dy >> fbf.in21
    zVector.output3Dz >> fbf.in22
    dcmp = pymel.core.createNode( 'decomposeMatrix' )
    fbf.output >> dcmp.imat
    
    dcmp.outputRotate >> tr.rotate
    tangentCon = targetJnt.listConnections( s=1, d=0, type='tangentConstraint' )
    if tangentCon: pymel.core.delete( tangentCon )
    
    sgCmds.constrain_rotate( tr, targetJnt )




def copyWeightByOnlySpecifyJoints( srcJointsGrp, trgJointsGrp, srcMesh, trgMesh ):
    
    srcJntsGrp = pymel.core.ls( srcJointsGrp )[0]
    trgJntsGrp = pymel.core.ls( trgJointsGrp )[0]
    
    srcJntsChildren = srcJntsGrp.listRelatives( c=1, ad=1, type='joint' )
    trgJntsChildren = trgJntsGrp.listRelatives( c=1, ad=1, type='joint' )
    
    srcPoses = OpenMaya.MPointArray()
    trgPoses = OpenMaya.MPointArray()
    
    srcPoses.setLength( len( srcJntsChildren ) )
    trgPoses.setLength( len( trgJntsChildren ) )
    
    for i in range( srcPoses.length() ):
        srcJnt = srcJntsChildren[i]
        srcJntPos = OpenMaya.MPoint( *srcJnt.wm.get()[-1] )
        srcPoses.set( srcJntPos, i )
        
    for i in range( trgPoses.length() ):
        trgJnt = trgJntsChildren[i]
        trgJntPos = OpenMaya.MPoint( *trgJnt.wm.get()[-1] )
        trgPoses.set( trgJntPos, i )
    
    srcMeshSkin = sgCmds.getNodeFromHistory( srcMesh, 'skinCluster' )[0]
    trgMeshSkin = sgCmds.getNodeFromHistory( trgMesh, 'skinCluster' )[0]
    
    srcToTrgMap = {}
    srcInflueceIndices = []
    for srcJnt in srcJntsChildren:
        cons = srcJnt.wm.listConnections( type='skinCluster', p=1 )
        for con in cons:
            if con.node().name() != srcMeshSkin.name(): continue
            srcInflueceIndices.append( con.index() )
            break
    
    trgInflueceIndices = []
    for trgJnt in trgJntsChildren:
        cons = trgJnt.wm.listConnections( type='skinCluster', p=1 )
        for con in cons:
            if con.node().name() != trgMeshSkin.name(): continue
            trgInflueceIndices.append( con.index() )
            break
    
    for i in range( srcPoses.length() ):
        closeDist = 10000000.0
        closeIndex = 0
        for j in range( trgPoses.length() ):
            dist = srcPoses[i].distanceTo( trgPoses[j] )
            if dist < closeDist:
                closeDist = dist
                closeIndex = j
        srcToTrgMap.update( { srcInflueceIndices[i] : trgInflueceIndices[closeIndex] } )

    fnSrcSkin = OpenMaya.MFnDependencyNode( sgCmds.getMObject( srcMeshSkin ) )
    fnTrgSkin = OpenMaya.MFnDependencyNode( sgCmds.getMObject( trgMeshSkin ) )
    
    plugSrcWeightList = fnSrcSkin.findPlug( 'weightList' )
    plugTrgWeightList = fnTrgSkin.findPlug( 'weightList' )
    
    for i in range( plugSrcWeightList.numElements() ):
        plugSrcWeights = plugSrcWeightList[i].child(0)
        plugTrgWeights = plugTrgWeightList[i].child(0)
        
        trgLogicalIndices = []
        trgValues = []
        sumValue = 0
        for j in range( plugSrcWeights.numElements() ):
            logicalIndex = plugSrcWeights[j].logicalIndex()
            if not srcToTrgMap.has_key( logicalIndex ): continue
            trgInfluenceLogicalIndex = srcToTrgMap[logicalIndex]
            trgLogicalIndices.append( trgInfluenceLogicalIndex )
            trgValues.append( plugSrcWeights[j].asFloat() )
            sumValue += plugSrcWeights[j].asFloat()
        multValue = 1.0 - sumValue
        
        trgOtherLogicalIndices = []
        for j in range( plugTrgWeights.numElements() ):
            trgLogicalIndex = plugTrgWeights[j].logicalIndex()
            if trgLogicalIndex in trgLogicalIndices: continue
            trgOtherLogicalIndices.append( trgLogicalIndex )
        
        for j in range( len( trgLogicalIndices ) ):
            trgAttr = plugTrgWeights.elementByLogicalIndex( trgLogicalIndices[j] ).name()
            cmds.setAttr( trgAttr, trgValues[j] )
        
        for j in range( len( trgOtherLogicalIndices ) ):
            trgAttr = plugTrgWeights.elementByLogicalIndex( trgOtherLogicalIndices[j] ).name()
            cmds.setAttr( trgAttr, cmds.getAttr( trgAttr ) * multValue )
            


def createMatrixTransformFromVertex( inputVtx ):
    centerVtx = pymel.core.ls( inputVtx )[0]
    vertices = sgCmds.getConnectedVertices( centerVtx )
    if len( vertices ) < 3: return None
    
    curveTr = pymel.core.curve( p=[ [0,0,0] for i in range( len( vertices ) ) ], d=2 )
    curveShape = curveTr.getShape()
    
    for i in range( len( vertices ) ):
        connectedVtx = vertices[i]
        curveInfo = sgCmds.getPointOnCurveFromMeshVertex( connectedVtx )
        curveInfo.position >> curveShape.controlPoints[i]
    pymel.core.closeCurve(  curveShape, ch=0, ps=0, rpo=1, bb=0.5, bki=0, p=0.1 )
    
    curveInfos = []
    for i in range( 4 ):
        curveInfo = pymel.core.createNode( 'pointOnCurveInfo' )
        curveShape.worldSpace >> curveInfo.inputCurve
        curveInfo.parameter.set( i * 0.25 )
        curveInfos.append( curveInfo )
    
    newTr = pymel.core.createNode( 'transform' )
    distX = pymel.core.createNode( 'distanceBetween' )
    distY = pymel.core.createNode( 'distanceBetween' )
    curveInfos[0].position >> distX.point1
    curveInfos[2].position >> distX.point2
    curveInfos[1].position >> distY.point1
    curveInfos[3].position >> distY.point2
    sgCmds.addAttr( newTr, ln='origLengthX', cb=1, dv=distX.distance.get() )
    sgCmds.addAttr( newTr, ln='origLengthY', cb=1, dv=distY.distance.get() )
    divScaleX = pymel.core.createNode( 'multiplyDivide' ); divScaleX.op.set( 2 )
    divScaleY = pymel.core.createNode( 'multiplyDivide' ); divScaleY.op.set( 2 )
    newTr.origLengthX >> divScaleX.input2X
    distX.distance >> divScaleX.input1X
    newTr.origLengthY >> divScaleY.input2X
    distY.distance >> divScaleY.input1X
    
    divScaleX.outputX >> newTr.sx
    divScaleY.outputX >> newTr.sy
    divScaleY.outputX >> newTr.sz
    
    vectorX = pymel.core.createNode( 'plusMinusAverage' ); vectorX.op.set( 2 )
    vectorY = pymel.core.createNode( 'plusMinusAverage' ); vectorY.op.set( 2 )
    
    curveInfos[0].position >> vectorX.input3D[0]
    curveInfos[2].position >> vectorX.input3D[1]
    curveInfos[1].position >> vectorY.input3D[0]
    curveInfos[3].position >> vectorY.input3D[1]
    centerCurveInfo = sgCmds.getPointOnCurveFromMeshVertex( centerVtx )
    
    fbf = pymel.core.createNode( 'fourByFourMatrix' )
    vectorX.output3Dx >> fbf.in00
    vectorX.output3Dy >> fbf.in01
    vectorX.output3Dz >> fbf.in02
    vectorY.output3Dx >> fbf.in10
    vectorY.output3Dy >> fbf.in11
    vectorY.output3Dz >> fbf.in12
    centerCurveInfo.positionX >> fbf.in30
    centerCurveInfo.positionY >> fbf.in31
    centerCurveInfo.positionZ >> fbf.in32
    
    mm = pymel.core.createNode( 'multMatrix' )
    fbf.output >> mm.i[0]
    newTr.pim >> mm.i[1]
    dcmp = pymel.core.createNode( 'decomposeMatrix' )
    mm.matrixSum >> dcmp.imat
    
    dcmp.ot >> newTr.t
    dcmp.outputRotate >> newTr.r
    
    newTr.dla.set( 1)
    return newTr, curveTr




    
    
def treeBendingLookAtConnect( inputLookTarget, inputRotTarget ):
    
    lookTarget = pymel.core.ls( inputLookTarget )[0]
    rotTarget  = pymel.core.ls( inputRotTarget )[0]
    
    rotTargetBase = rotTarget.getParent()
    rotTargetList = rotTarget.listRelatives( c=1, ad=1, type='joint' )
    map( lambda x : sgCmds.makeParent( x ) if x.getParent().nodeType() == 'joint' else None, rotTargetList )
    rotTargetPoints = map( lambda x : sgCmds.putObject( x ), rotTargetList )
    map( lambda x : x.dh.set( 0 ), rotTargetPoints )
    rotTargetPointsBase = sgCmds.makeChild( rotTargetBase )
    rotTargetList.append( rotTarget )
    
    sgCmds.lookAtConnect( lookTarget, rotTargetPointsBase )
    sgCmds.makeParent( rotTargetPointsBase )
    pymel.core.parent( rotTargetPoints, rotTargetPointsBase )
    
    rotTargetList.reverse()
    rotTargetPoints.reverse()
    
    numRotTargets = len( rotTargetList )
    sgCmds.addAttr( lookTarget, ln='bendWeight', min=0, max=1, dv=1, k=1 )
    sgCmds.addAttr( lookTarget, ln='powRate', min=0, max=2, dv=1, k=1 )
    
    for i in range( len( rotTargetList )-1 ):
        powRateBaseValue = ( i + 1.0 )/numRotTargets
        rotTargetH = rotTargetList[i]
        rotTargetHBase = rotTargetH.getParent()
        rotTargetChild = rotTargetH.listRelatives( c=1 )[0]
        aimCuPointPiv = sgCmds.makeChild( rotTargetHBase )
        aimCuPointBase = sgCmds.makeChild( aimCuPointPiv )
        aimCuPoint = sgCmds.makeChild( aimCuPointBase )
        pymel.core.xform( aimCuPointPiv, ws=1, matrix=rotTargetH.wm.get() )
        pymel.core.xform( aimCuPointBase, ws=1, matrix=rotTargetChild.wm.get() )
        
        rotTargetPoint = rotTargetPoints[i]
        dcmp = sgCmds.getLocalDecomposeMatrix( rotTargetPoint.wm, aimCuPointBase.wim )
        sgCmds.addAttr( rotTargetH, ln='lookWeight', min=0, max=1, k=1, dv= 1.0/numRotTargets )
        
        multEnv = pymel.core.createNode( 'multDoubleLinear' )
        multPow = pymel.core.createNode( 'multiplyDivide' ); multPow.op.set( 3 )
        multPowAndEnv = pymel.core.createNode( 'multDoubleLinear' )
        multEnv.output >> multPowAndEnv.input1
        multPow.outputX >> multPowAndEnv.input2
        multPow.input1X.set( powRateBaseValue )
        lookTarget.powRate >> multPow.input2X
        
        rotTargetH.lookWeight >> multEnv.input1
        lookTarget.bendWeight >> multEnv.input2
        
        multTrans = pymel.core.createNode( 'multiplyDivide' )
        dcmp.outputTranslate >> multTrans.input1
        multPowAndEnv.output >> multTrans.input2X
        multPowAndEnv.output >> multTrans.input2Y
        multPowAndEnv.output >> multTrans.input2Z
        multTrans.output >> aimCuPoint.t
        sgCmds.lookAtConnect( aimCuPoint, rotTargetH )
    
    sgCmds.addAttr( lookTarget, ln='rotTarget', at='message' )
    rotTargetPointsBase.message >> lookTarget.rotTarget
    



def treeBendingLookAtConnectReset( inputLookTarget ):
    
    lookTarget = pymel.core.ls( inputLookTarget )[0]
    rotTargetPointsBase = lookTarget.attr( 'rotTarget' ).listConnections( s=1, d=0 )[0]
    
    localMtx = rotTargetPointsBase.m.get()
    origWorldMtx = rotTargetPointsBase.pm.get()
    cuWorldMtx = localMtx * origWorldMtx
    
    rotTargetPoints = rotTargetPointsBase.listRelatives( c=1 )
    rotPointMtxs = map( lambda x : x.wm.get() * cuWorldMtx.inverse() * origWorldMtx, rotTargetPoints )
    
    pymel.core.xform( rotTargetPointsBase.getParent(), ws=1, matrix=cuWorldMtx )
    
    for i in range( len( rotTargetPoints ) ):
        pymel.core.xform( rotTargetPoints[i], ws=1, matrix=rotPointMtxs[i] )

        
        


def treeBendingRig( topJnt ):
    children = topJnt.listRelatives( c=1, ad=1 )
    lastChild = children[0]
    ctl = sgCmds.makeController( sgModel.Controller.diamondPoints, 1, makeParent=1 )
    pCtl = ctl.getParent()
    pymel.core.xform( pCtl, ws=1, matrix=lastChild.wm.get() )
    treeBendingLookAtConnect( ctl, topJnt )






def fixAngFurConstraint():
    import pymel.core
    from maya import cmds

    if not cmds.pluginInfo( 'matrixNodes', q=1, l=1 ):
        cmds.loadPlugin( 'matrixNodes' )

    mainCtls = pymel.core.ls( ['FurBottomCtrl', 'FurBackCtrl', 'FurRightCtrl', 'FurLeftCtrl', 'FurTopCtrl'] )

    targetConstObjs = []
    for mainCtl in mainCtls:
        constrains = list( set( mainCtl.listConnections( s=0, d=1, type='constraint' ) ) )
        for constrain in constrains:
            targetConstObjs += [ target for target in list( set( constrain.listConnections( s=0, d=1, type='transform' ) ) ) if target.nodeType() == 'transform' ]

    targetConstObjs = list( set( targetConstObjs ) )
    for targetConstObj in targetConstObjs:
        aimConstraintObj = list( set( pymel.core.listConnections( targetConstObj, s=1, d=0, type='aimConstraint' ) ) )

        def connectAngleNode( targetConstObj ):
            composePivot = pymel.core.createNode( 'composeMatrix' )
            multPiv = pymel.core.createNode( 'multMatrix' )
            invPiv = pymel.core.createNode('inverseMatrix')
            composeCurrentPosition = pymel.core.createNode('composeMatrix')
            multCurrentPosition = pymel.core.createNode( 'multMatrix' )
            dcmpCurrentPosition = pymel.core.createNode( 'decomposeMatrix' )
            angleNode = pymel.core.createNode('angleBetween')

            composePivot.it.set( [ -value for value in targetConstObj.t.get() ] )
            composePivot.outputMatrix >> multPiv.i[0]
            targetConstObj.getParent().wm >> multPiv.i[1]
            multPiv.o >> invPiv.inputMatrix

            targetConstObj.t >> composeCurrentPosition.it
            composeCurrentPosition.outputMatrix >> multCurrentPosition.i[0]
            targetConstObj.getParent().wm >> multCurrentPosition.i[1]
            invPiv.outputMatrix >> multCurrentPosition.i[2]
            multCurrentPosition.matrixSum >> dcmpCurrentPosition.imat

            angleNode.vector1.set( dcmpCurrentPosition.ot.get() )
            dcmpCurrentPosition.ot >> angleNode.vector2
            angleNode.euler >> targetConstObj.r

        pymel.core.delete( aimConstraintObj )
        connectAngleNode( targetConstObj )

        targetChild = targetConstObj.listRelatives( c=1, type='transform' )[0]
        parentConstObjs = list( set( targetChild.listConnections( s=0, d=1, type='parentConstraint' ) ) )
        if not parentConstObjs: continue
        parentConstObj = parentConstObjs[0]

        targetSecond = parentConstObj.attr( 'constraintParentInverseMatrix').listConnections( s=1, d=0 )[0]
        src1 = parentConstObj.attr('target[0].targetParentMatrix').listConnections(s=1, d=0)[0]
        src2 = parentConstObj.attr('target[1].targetParentMatrix').listConnections(s=1, d=0)[0]

        src1_offset_trans = parentConstObj.attr('target[0].targetOffsetTranslate').get()
        src1_offset_rotate = parentConstObj.attr('target[0].targetOffsetRotate').get()
        src2_offset_trans = parentConstObj.attr('target[1].targetOffsetTranslate').get()
        src2_offset_rotate = parentConstObj.attr('target[1].targetOffsetRotate').get()

        def getOffsetMultMatrix( offsetTr, offsetRo, target ):

            offsetCompose = pymel.core.createNode('composeMatrix')
            multMatrix = pymel.core.createNode( 'multMatrix' )
            offsetCompose.it.set(offsetTr)
            offsetCompose.ir.set(offsetRo)
            offsetCompose.outputMatrix >> multMatrix.i[0]
            target.wm >> multMatrix.i[1]
            return multMatrix

        mm1 = getOffsetMultMatrix(src1_offset_trans, src1_offset_rotate, src1 )
        mm2 = getOffsetMultMatrix(src2_offset_trans, src2_offset_rotate, src2 )

        blMtx = pymel.core.createNode( 'wtAddMatrix' )
        multMtxResult = pymel.core.createNode( 'multMatrix' )
        dcmpResult = pymel.core.createNode( 'decomposeMatrix' )

        mm1.o >> blMtx.i[0].m
        mm2.o >> blMtx.i[1].m
        blMtx.i[0].w.set(0.5)
        blMtx.i[1].w.set(0.5)
        blMtx.matrixSum >> multMtxResult.i[0]
        targetSecond.pim >> multMtxResult.i[1]
        multMtxResult.o >> dcmpResult.imat

        dcmpResult.ot >> targetSecond.t
        dcmpResult.outputRotate >> targetSecond.r

        pymel.core.delete( parentConstObj )




