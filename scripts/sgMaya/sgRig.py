from maya import OpenMaya
from maya import cmds, mel
import pymel.core
import sgModel, sgCmds, sgBase
import random
import math



def createXLookAtJointLine( inputTargets ):
    
    targets = []
    for inputTarget in inputTargets:
        targets.append( pymel.core.ls( inputTarget )[0] )
    
    beforeJnt = None
    baseMatrix = None
    joints = []
    for i in range( len( targets )-1 ):
        if not baseMatrix:
            baseMatrix = sgCmds.listToMatrix( cmds.getAttr( targets[i].wm.name() ) )
        else:
            baseMatrixList = sgCmds.matrixToList( baseMatrix )
            targetPos = pymel.core.xform( targets[i], q=1, ws=1, t=1 )
            baseMatrixList[12] = targetPos[0]
            baseMatrixList[13] = targetPos[1]
            baseMatrixList[14] = targetPos[2]
            baseMatrix = sgCmds.listToMatrix( baseMatrixList )

        targetPos = OpenMaya.MPoint( *pymel.core.xform( targets[i+1], q=1, ws=1, t=1 ) )
        localPos = targetPos * baseMatrix.inverse()
        
        angleValues = pymel.core.angleBetween( v1=[1,0,0], v2=[localPos.x, localPos.y, localPos.z], er=1 )
        rotMtx = sgCmds.rotateToMatrix( angleValues )
        
        jointMatrix = sgCmds.matrixToList( rotMtx * baseMatrix )
        if beforeJnt:
            pymel.core.select( beforeJnt )
        else:
            pymel.core.select( d=1 )
        cuJoint = pymel.core.joint()
        pymel.core.xform( cuJoint, ws=1, matrix=jointMatrix )
        baseMatrix = sgCmds.listToMatrix( jointMatrix )
        joints.append( cuJoint )
        beforeJnt = cuJoint
    
    pymel.core.select( beforeJnt )
    endJnt = pymel.core.joint()
    pymel.core.xform( endJnt, ws=1, matrix= targets[-1].wm.get() )
    endJnt.r.set( 0,0,0 )
    joints.append( endJnt )
    
    return joints
    


def makeWaveJoint( inputTopJoint ): 
    
    topJoint = pymel.core.ls( inputTopJoint )[0]
    children = topJoint.listRelatives( c=1, type='transform' )
    joints = [topJoint]
    
    while children:
        joints.append( children[0] )
        children = children[0].listRelatives( c=1, type='transform' )
    
    joints = list( filter( lambda x : x.nodeType() == 'joint', joints ) )
    
    methodList = ['Sine', 'Rand', 'RandBig']
    axisList   = ['X', 'Y', 'Z']
    
    firstJnt = joints[0]
    sgCmds.addOptionAttribute( firstJnt, 'All' )
    sgCmds.addAttr( firstJnt, ln='move', k=1 )
    sgCmds.addAttr( firstJnt, ln='allWeight', min=0, dv=1, k=1 )
    sgCmds.addAttr( firstJnt, ln='allSpeed', min=0, dv=1, k=1 )
    for method in methodList:
        sgCmds.addOptionAttribute( firstJnt, '%s' % method )
        sgCmds.addAttr( firstJnt, ln='all%sWeight' % method, min=0, dv=1, k=1 )
        sgCmds.addAttr( firstJnt, ln='all%sSpeed' % method, min=0, dv=1, k=1 )
    sgCmds.addOptionAttribute( firstJnt, 'intervalValueAdd' )
    sgCmds.addAttr( firstJnt, ln='intervalValueAdd', min=0, dv=15, k=1 )
    
    for joint in joints:
        try:sgCmds.freezeJoint( joint )
        except:pass
    
    for method in methodList:
        dvOffset = 0
        dvInterval = -2
        
        sgCmds.addOptionAttribute( firstJnt, 'control%s' % method )
        sgCmds.addAttr( firstJnt, ln='interval%s' %(method), k=1, dv=dvInterval )
        sgCmds.addAttr( firstJnt, ln='offset%s' %(method), k=1, dv=dvOffset )
        for axis in axisList:    
            dvValue = 5
            sgCmds.addAttr( firstJnt, ln='value%s%s' %(method,axis), min=-90, max=90, k=1, dv = dvValue )
        for axis in axisList:
            if axis == 'Y':
                dvSpeed = 1.2
            else:
                dvSpeed = 0.8
            sgCmds.addAttr( firstJnt, ln='speed%s%s' %(method,axis), k=1, dv=dvSpeed )
            
    
    for axis in axisList:  
        randValues = []
        for j in range( 100 ):
            randValue = random.uniform( -1, 1 )
            randValues.append( randValue )
        
        for i in range( 1, len(joints)-1 ):
            methodAdd = pymel.core.createNode( 'plusMinusAverage' )
            globalAllMult = pymel.core.createNode( 'multDoubleLinear' )
            firstJnt.attr( 'allWeight' ) >> globalAllMult.input1
            methodAdd.output1D >> globalAllMult.input2
            
            joint = joints[i]
            methodIndex = 0
            
            for method in methodList:
                globalAllSpeedMult = pymel.core.createNode( 'multDoubleLinear' )
                firstJnt.attr( 'allSpeed' ) >> globalAllSpeedMult.input1
                globalSpeedMult = pymel.core.createNode( 'multDoubleLinear' )
                firstJnt.attr( 'all%sSpeed' % method ) >> globalSpeedMult.input1
                globalSpeedMult.output >> globalAllSpeedMult.input2
                
                animCurve = pymel.core.createNode( 'animCurveUU' )
                animCurve.preInfinity.set( 3 )
                animCurve.postInfinity.set( 3 )
                if method in ['Rand','RandBig']:
                    for j in range( len( randValues ) ):
                        randValue = randValues[j]
                        if j == 0 or j == 99:
                            pymel.core.setKeyframe( animCurve, f=j*10, v=0 )
                        else:
                            pymel.core.setKeyframe( animCurve, f=j*10, v=randValue )
                elif method == 'Sine':
                    pymel.core.setKeyframe( animCurve, f=0,  v= 1 )
                    pymel.core.setKeyframe( animCurve, f=5, v=-1 )
                    pymel.core.setKeyframe( animCurve, f=10, v= 1 )
                
                valueMult = pymel.core.createNode( 'multDoubleLinear' )
                speedMult = pymel.core.createNode( 'multDoubleLinear' )
                intervalMult = pymel.core.createNode( 'multDoubleLinear' )
                inputSum = pymel.core.createNode( 'plusMinusAverage' )
                firstJnt.attr( 'offset%s' %( method ) ) >> inputSum.input1D[0]
                firstJnt.attr( 'move' ) >> speedMult.input1
                firstJnt.attr( 'speed%s%s' %( method, axis ) ) >> speedMult.input2
                speedMult.output >> globalSpeedMult.input2
                globalAllSpeedMult.output >> inputSum.input1D[1]
                intervalMult.input1.set( i )
                firstJnt.attr( 'interval%s' %( method ) ) >> intervalMult.input2
                intervalMult.output >> inputSum.input1D[2]
                inputSum.output1D >> animCurve.input
                animCurve.output >> valueMult.input1
                firstJnt.attr( 'value%s%s' %(method,axis) ) >> valueMult.input2
                
                globalWeightMult = pymel.core.createNode( 'multDoubleLinear' )
                firstJnt.attr( 'all%sWeight' % method ) >> globalWeightMult.input1
                valueMult.output >> globalWeightMult.input2
                globalWeightMult.output >> methodAdd.input1D[methodIndex]
                methodIndex+=1
            
            intervalValueAddPercent = pymel.core.createNode( 'multDoubleLinear' )
            intervalValueAddMult = pymel.core.createNode( 'multDoubleLinear' )
            intervalValueAddAdd  = pymel.core.createNode( 'addDoubleLinear' )
            
            intervalValueAddPercent.input1.set( 0.01 * i )
            firstJnt.attr('intervalValueAdd') >> intervalValueAddPercent.input2
            intervalValueAddPercent.output >> intervalValueAddMult.input1
            globalAllMult.output >> intervalValueAddMult.input2
            globalAllMult.output >>intervalValueAddAdd.input1
            intervalValueAddMult.output >> intervalValueAddAdd.input2
            
            intervalValueAddAdd.output >> joint.attr( 'rotate%s' % axis )
            
            
                


def makeWaveGlobal( inputTopJoints, inputCtl ):
    
    topJoints = []
    for inputTopJoint in inputTopJoints:
        topJoints.append( pymel.core.ls( inputTopJoint )[0] )

    ctl = pymel.core.ls( inputCtl )[0]

    sgCmds.addOptionAttribute( ctl, 'control_offset' )
    sgCmds.addAttr( ctl, ln='offsetGlobalInterval', k=1, dv=1 )
    sgCmds.addAttr( ctl, ln='offsetGlobalRand', k=1, dv=1 )

    attrs = topJoints[0].listAttr( ud=1 )
    sgCmds.addOptionAttribute( ctl, 'wave' )
    for attr in attrs:
        sgCmds.copyAttribute( topJoints[0], ctl, attr.longName() )
    
    circleAttrs = ctl.listAttr( ud=1, k=1 )
    
    for topJoint in topJoints:
        for circleAttr in circleAttrs:
            if not pymel.core.attributeQuery( circleAttr.longName(), node=topJoint, ex=1 ): continue
            circleAttr >> topJoint.attr( circleAttr.longName() )
    
    index = 0
    for topJoint in topJoints:
        offsetRand = pymel.core.createNode( 'multDoubleLinear' )
        offsetInterval = pymel.core.createNode( 'multDoubleLinear' )
        offsetAll = pymel.core.createNode( 'addDoubleLinear' )
        offsetRand.input1.set( random.uniform( -5, 5 ) )
        ctl.attr( 'offsetGlobalRand' ) >> offsetRand.input2
        offsetInterval.input1.set( index )
        ctl.attr( 'offsetGlobalInterval' ) >> offsetInterval.input2
        offsetRand.output >> offsetAll.input1
        offsetInterval.output >> offsetAll.input2
        offsetAll.output >> topJoint.attr( 'offsetSine' )
        index += 1
        allWeightPlug = topJoint.allWeight.listConnections( s=1, d=0, p=1 )[0]
        sgCmds.addAttr( topJoint, ln='globalWeight', min=0, max=1, k=1, dv=1 )
        multGlobal = pymel.core.createNode( 'multDoubleLinear' )
        topJoint.globalWeight >> multGlobal.input1
        allWeightPlug >> multGlobal.input2
        multGlobal.output >> topJoint.allWeight



def createRandomTranslate( inputCtl, inputTarget ):
    
    ctl    = pymel.core.ls( inputCtl )[0]
    target = pymel.core.ls( inputTarget )[0]
    
    sgCmds.addOptionAttribute( ctl, 'translateRandom' )
    sgCmds.addAttr( ctl, ln='move', k=1 )
    sgCmds.addAttr( ctl, ln='speed', k=1, min=0, dv=1 )
    multMove = pymel.core.createNode( 'multDoubleLinear' )
    ctl.attr( 'move' )  >> multMove.input1
    ctl.attr( 'speed' ) >> multMove.input2
    
    for axis in ['X', 'Y', 'Z']:
        animCurve = pymel.core.createNode( 'animCurveUU' )
        animCurve.preInfinity.set( 3 )
        animCurve.postInfinity.set( 3 )
        for j in range( 100 ):
            randValue = random.uniform( -1, 1 )
            if j == 0 or j == 99:
                pymel.core.setKeyframe( animCurve, f=j*10, v=0 )
            else:
                pymel.core.setKeyframe( animCurve, f=j*10, v=randValue )
                print "set rand value : %f" % randValue

        multMove.output >> animCurve.input
        sgCmds.addAttr( ctl, ln='weight_%s' % axis, min=0, dv=0.5, k=1 )
        multWeight = pymel.core.createNode( 'multDoubleLinear' )
        ctl.attr( 'weight_%s' % axis ) >> multWeight.input1
        animCurve.output >> multWeight.input2
        multWeight.output >> target.attr( 'translate%s' % axis )



def makeUdAttrGlobal( inputTargets, inputCtl ):

    targets = []
    for inputTarget in inputTargets:
        targets.append( pymel.core.ls( inputTarget )[0] )

    ctl = pymel.core.ls( inputCtl )[0]

    attrs = targets[0].listAttr( ud=1 )
    for attr in attrs:
        sgCmds.copyAttribute( targets[0], ctl, attr.longName() )
    
    circleAttrs = ctl.listAttr( ud=1, k=1 )
    
    for target in targets:
        for circleAttr in circleAttrs:
            if not pymel.core.attributeQuery( circleAttr.longName(), node=target, ex=1 ): continue
            circleAttr >> target.attr( circleAttr.longName() )



def buildJointLineByVtxNum( mesh, vtxList, numJoints ):
    
    points = OpenMaya.MPointArray()
    
    for vtxIndex in vtxList:
        vtxPos = OpenMaya.MPoint( *cmds.xform( mesh + '.vtx[%d]' % vtxIndex, q=1, ws=1, t=1 )[:3] )
        points.append( vtxPos )
        #print "vtx pos[%d] : %5.3f, %5.3f, %5.3f " %( vtxIndex, vtxPos.x, vtxPos.y, vtxPos.z )
    
    curveData = OpenMaya.MFnNurbsCurveData()
    oData = curveData.create()
    fnCurve = OpenMaya.MFnNurbsCurve()
    
    fnCurve.createWithEditPoints( points, 3, fnCurve.kOpen, False, True, True, oData )
    
    newFnCurve = OpenMaya.MFnNurbsCurve( oData )
    
    eachLength = newFnCurve.length()/numJoints
    parentObj = None
    joints = []
    for i in range( numJoints+1 ):
        paramValue = newFnCurve.findParamFromLength( eachLength * i )
        point = OpenMaya.MPoint()
        newFnCurve.getPointAtParam( paramValue, point )
        
        if not parentObj:
            pymel.core.select( d=1 )
        else:
            pymel.core.select( parentObj )

        joint = pymel.core.joint()
        joints.append( joint )
        pymel.core.move( point.x, point.y, point.z, joint, ws=1 )
        parentObj = joint
    return joints[0]



class ParentedMove:
    
    offsetMatrixAttrName = 'parentedMove_offsetMatrix'
    parentTargetAttrName = 'parentedMove_parentTarget'
    expressionName       = 'ex_ParentedMove'
    
    @staticmethod
    def set( inputChildTarget, inputParentTarget ):
        
        childTarget  = pymel.core.ls( inputChildTarget )[0]
        parentTarget = pymel.core.ls( inputParentTarget )[0]
        
        sgCmds.addAttr( childTarget, ln=ParentedMove.offsetMatrixAttrName, at='matrix' )
        sgCmds.addAttr( childTarget, ln=ParentedMove.parentTargetAttrName, at='message' )
        
        try:parentTarget.message >> childTarget.attr( ParentedMove.parentTargetAttrName )
        except:pass
        
        localMatrix = sgCmds.getMMatrix( childTarget.wm ) * sgCmds.getMMatrix( parentTarget.wim )
        childTarget.attr( ParentedMove.offsetMatrixAttrName ).set( sgCmds.matrixToList( localMatrix ) )
    
    
    @staticmethod
    def reset( inputChildTarget ):
        
        childTarget = pymel.core.ls( inputChildTarget )[0]
        if not pymel.core.attributeQuery( ParentedMove.offsetMatrixAttrName, node=childTarget, ex=1 ) or\
           not pymel.core.attributeQuery( ParentedMove.parentTargetAttrName, node=childTarget, ex=1 ):
            pymel.core.error( "%s is not Parenting Move Object" % childTarget.name() )
        
        parentTargets = childTarget.attr( ParentedMove.parentTargetAttrName ).listConnections( s=1, d=0 )
        if not parentTargets:
            pymel.core.error( "%s is not Parenting Move Object" % childTarget.name() )
        
        localMatrix = sgCmds.getMMatrix( childTarget.wm ) * sgCmds.getMMatrix( parentTargets[0].wim )
        childTarget.attr( ParentedMove.offsetMatrixAttrName ).set( sgCmds.matrixToList( localMatrix ) )

    
    
    @staticmethod
    def run():
        attrs = pymel.core.ls( '*.' + ParentedMove.parentTargetAttrName )
        for attr in attrs:
            node = attr.node()
            parentTarget = attr.listConnections( s=1, d=0 )[0]
            parentMtx = sgCmds.getMMatrix( parentTarget.wm )
            localMtx = sgCmds.getMMatrix( node.attr( ParentedMove.offsetMatrixAttrName ) )
            worldMtxList = sgCmds.matrixToList( localMtx * parentMtx )
            pymel.core.xform( node, ws=1, matrix=worldMtxList )
    
    
    @staticmethod
    def createExpression():
        if pymel.core.ls( ParentedMove.expressionName + '*', type='expression' ): return None
        pymel.core.expression( s="python( \"from sgMaya import sgAnim;sgAnim.ParentedMove.run()\" )",  o="", ae=1, uc='all', n = ParentedMove.expressionName )
    
    
    @staticmethod
    def deleteExpression():
    
        if pymel.core.ls( ParentedMove.expressionName + '*', type='expression' ):
            pymel.core.delete( pymel.core.ls( ParentedMove.expressionName + '*', type='expression' ) )



class NetControlRig:
    
    groupAttrName = 'netControlGroup'
    rowAttrName   = 'netControlRow'
    columnAttrName = 'netControlColumn'
    bigControlAttrName = 'netControlBigTarget'


    def __init__(self, netGroupName ):
        
        self.baseName = netGroupName
        self.numRows = 0
        self.numColumns = 0
        self.targets = []


    def setRows( self, *inputOrderedTargets ):
        
        orderedTargets = [ pymel.core.ls( inputOrderedTarget )[0] for inputOrderedTarget in inputOrderedTargets ]
        for i in range( len( orderedTargets ) ):
            orderedTargets[i].rename( self.baseName + '_%02d' % i )
            sgCmds.addAttr( orderedTargets[i], ln=NetControlRig.groupAttrName, dt='string' )
            orderedTargets[i].attr( NetControlRig.groupAttrName ).set( self.baseName )
            sgCmds.addAttr( orderedTargets[i], ln=NetControlRig.rowAttrName, at='long' )
            orderedTargets[i].attr( NetControlRig.rowAttrName ).set( i )
            self.numRows += 1
            self.targets.append( orderedTargets[i] )


    def setBigConnect( self, *inputBigTargets ):
        
        bigTargets = [ pymel.core.ls( inputBigControl )[0] for inputBigControl in inputBigTargets ]
        
        for i in range( len( bigTargets ) ):
            closeTarget = sgCmds.getClosestTransform( bigTargets[i], self.targets )
            sgCmds.addAttr( closeTarget, ln=NetControlRig.bigControlAttrName, at='message' )
            bigTargets[i].message >> closeTarget.attr( NetControlRig.bigControlAttrName )
    
    
    def setParentContraint(self, circle=False, toParent=False ):
        
        def getBigControl( target ):
            return target.attr( NetControlRig.bigControlAttrName ).listConnections( s=1, d=0 )[0]
        
        if not self.numColumns:
            bigControlIndices = []
            
            for i in range( len( self.targets ) ):
                if not pymel.core.attributeQuery( NetControlRig.bigControlAttrName,
                                                  node = self.targets[i], ex=1 ):
                    continue
                bigControlIndices.append( i )

            for i in range( len( self.targets ) ):
                if toParent:
                    parentTarget = self.targets[i].getParent()
                else:
                    parentTarget = self.targets[i]

                if i in bigControlIndices:
                    bigControl = getBigControl(self.targets[i])
                    pymel.core.parentConstraint( bigControl, parentTarget, mo=1 )
                else:
                    twoSideBigControlsIndices = [None, None]
                    for j in range( len( bigControlIndices ) ):
                        if i < bigControlIndices[j]:
                            if j == 0:
                                if circle:
                                    twoSideBigControlsIndices = [ bigControlIndices[0], bigControlIndices[-1]]
                                else:
                                    twoSideBigControlsIndices = [ bigControlIndices[0], bigControlIndices[0]]
                            else:
                                twoSideBigControlsIndices = [bigControlIndices[j-1],bigControlIndices[j]]
                            break
                    
                    if twoSideBigControlsIndices[0] == None:
                        if circle:
                            twoSideBigControlsIndices = [bigControlIndices[-1], bigControlIndices[0]]
                        else:
                            twoSideBigControlsIndices = [bigControlIndices[-1], bigControlIndices[-1]]
                    
                    twoSideControls = [ getBigControl( self.targets[k] ) for k in twoSideBigControlsIndices ]
                    
                    first  = sgCmds.getMVector( twoSideControls[0] )
                    second = sgCmds.getMVector( twoSideControls[1] )
                    target = sgCmds.getMVector( self.targets[i] )
                    
                    baseVector = second - first
                    targetVector = target - first
                    
                    if baseVector.length() < 0.00001:
                        pymel.core.parentConstraint( twoSideControls[0], parentTarget, mo=1 )
                        continue
                    
                    projTargetToBase = baseVector * ( ( targetVector * baseVector )/baseVector.length()**2 )
                    
                    secondWeight = projTargetToBase.length() / baseVector.length()
                    if secondWeight > 1:
                        secondWeight = 1
                    firstWeight = 1.0 - secondWeight
                    
                    print firstWeight, secondWeight
                    
                    if firstWeight == 0:
                        constraint = pymel.core.parentConstraint( twoSideControls[1], parentTarget, mo=1 )
                    elif secondWeight == 0:
                        constraint = pymel.core.parentConstraint( twoSideControls[0], parentTarget, mo=1 )
                    else:
                        constraint = pymel.core.parentConstraint( twoSideControls[0], twoSideControls[1], parentTarget, mo=1 )
                        constraint.w0.set( firstWeight )
                        constraint.w1.set( secondWeight )
                    
                    
                    
class SplineRig:
    
    def __init__(self, topJoint ):
        
        self.topJoint = pymel.core.ls( topJoint )[0]
        self.jointH = self.topJoint.listRelatives( c=1, ad=1, type='joint' )
        self.jointH.append( self.topJoint )
        self.jointH.reverse()
    
    
    def createSplineCurve(self):
        
        poses = []
        for jnt in self.jointH:
            pos = pymel.core.xform( jnt, q=1, ws=1, t=1 )
            poses.append( pos )
        
        curve = pymel.core.curve( ep=poses, d=3 )
        return curve
    
    
    def assignToCurve(self, inputCurve ):
        
        curve = pymel.core.ls( inputCurve )[0]
        return pymel.core.ikHandle( sj=self.topJoint, ee=self.jointH[-1], sol="ikSplineSolver", ccv=False, pcv=False, curve=curve )[0]
        
        
        


class IkDetailJoint:

    def __init__( self, baseJoint, targetJoint ):
        
        self.baseJoint   = pymel.core.ls( baseJoint )[0]
        self.targetJoint = pymel.core.ls( targetJoint )[0]
        self.joints = []
    
        localMtx = sgCmds.getLocalMatrix( self.targetJoint.wm, self.baseJoint.wim )
        upVectorStart = pymel.core.createNode( 'vectorProduct' ); upVectorStart.op.set( 3 )
        upVectorEnd   = pymel.core.createNode( 'vectorProduct' ); upVectorEnd.op.set( 3 )
        directionIndex = sgCmds.getDirectionIndex( [localMtx.o.get().a30, localMtx.o.get().a31, localMtx.o.get().a32] )
        upVector = sgCmds.getVectorList()[(directionIndex+1)%6]
        upVectorStart.input1.set( upVector )
        upVectorEnd.input1.set( upVector )
        localMtx.o >> upVectorEnd.matrix
        
        self.aimIndex = ( directionIndex ) % 3
        self.upIndex  = ( directionIndex + 1 ) % 3
        self.crossIndex = ( directionIndex + 2 ) % 3
        self.upVectorStart = upVectorStart
        self.upVectorEnd   = upVectorEnd
        self.reverseVector = False
        if directionIndex >= 3:
            self.reverseVector = True


    def makeCurve(self):
        
        crvGrp = pymel.core.createNode( 'transform', n='CrvGrp_'+self.baseJoint )
        crv = pymel.core.curve( p=[[0,0,0],[0,0,0]], n='Crv_'+self.baseJoint, d=1 )
        crv.setParent( crvGrp )
        dcmp = sgCmds.getLocalDecomposeMatrix( self.targetJoint.wm, self.baseJoint.wim )
        dcmp.ot >> crv.getShape().controlPoints[1]
        sgCmds.constrain_all( self.baseJoint, crvGrp )
        self.baseGrp = crvGrp
        self.curve = crv



    def addJointAtParam(self, paramValue ):
        
        pointOnCurveInfo = pymel.core.createNode( 'pointOnCurveInfo' )
        self.curve.getShape().local >> pointOnCurveInfo.inputCurve
        pointOnCurveInfo.top.set( 1 )
        pymel.core.select( self.baseGrp )
        newJoint = pymel.core.joint()
        sgCmds.addAttr( newJoint, ln='param', min=0, max=1, dv=paramValue, k=1 )
        newJoint.attr( 'param' ) >> pointOnCurveInfo.parameter
        
        fbfMtx = pymel.core.createNode( 'fourByFourMatrix' )
        
        def getMultVector( outputAttr, reverse ):
            multVector = pymel.core.createNode( 'multiplyDivide' )
            outputAttr >> multVector.input1
            if reverse:
                multVector.input2.set( -1, -1, -1 )
            else:
                multVector.input2.set( 1,1,1 )
            return multVector
        
        aimMultVector = getMultVector( pointOnCurveInfo.tangent, self.reverseVector )
        
        aimMultVector.outputX >> fbfMtx.attr( 'in%d0' % self.aimIndex )
        aimMultVector.outputY >> fbfMtx.attr( 'in%d1' % self.aimIndex )
        aimMultVector.outputZ >> fbfMtx.attr( 'in%d2' % self.aimIndex )   
        
        blendColor = pymel.core.createNode( 'blendColors' )
        self.upVectorEnd.output >> blendColor.color1
        self.upVectorStart.output >> blendColor.color2
        newJoint.param >> blendColor.blender
        
        upMultVector = getMultVector( blendColor.output, self.reverseVector )
        
        upMultVector.outputX >> fbfMtx.attr( 'in%d0' % self.upIndex )
        upMultVector.outputY >> fbfMtx.attr( 'in%d1' % self.upIndex )
        upMultVector.outputZ >> fbfMtx.attr( 'in%d2' % self.upIndex )
        
        print self.aimIndex, self.upIndex, self.crossIndex
        
        crossVector = sgCmds.getCrossVectorNode( aimMultVector.output, upMultVector.output )
        
        crossVector.outputX >> fbfMtx.attr( 'in%d0' % self.crossIndex )
        crossVector.outputY >> fbfMtx.attr( 'in%d1' % self.crossIndex )
        crossVector.outputZ >> fbfMtx.attr( 'in%d2' % self.crossIndex )
        
        pointOnCurveInfo.positionX >> fbfMtx.in30
        pointOnCurveInfo.positionY >> fbfMtx.in31
        pointOnCurveInfo.positionZ >> fbfMtx.in32
        
        dcmp = sgCmds.getDecomposeMatrix( fbfMtx.output )
        dcmp.ot >> newJoint.t
        dcmp.outputRotate >> newJoint.r
        
        self.joints.append( newJoint )
    
    
    def renameJoints(self, name ):
        
        for i in range( len( self.joints ) ):
            self.joints[i].rename( name + '_%02d' % i )
            
            
        
        

def chainRig( mesh, curve, upObject, upVector, percentOfSpaceOfBlock=0.0, randomOffsetPercent=0 ):
    
    from maya import mel
    
    pymel.core.select( mesh )
    mel.eval( 'CenterPivot' )
    
    pivotMatrix = sgCmds.getPivotWorldMatrix( mesh )
    sgCmds.setPivotZero( mesh )
    sgCmds.setMatrixToTarget( pivotMatrix, mesh, pcp=1 )
    
    def getMeshStartAndEndPoint( mesh, curve ):
        param = sgCmds.getClosestParamAtPoint( mesh, curve )
        direction = sgCmds.getTangentAtParam( curve, param )
        localDirection = sgCmds.getMVector(direction) * sgCmds.listToMatrix( mesh.wim.get() )
        directionIndex = sgCmds.getDirectionIndex( localDirection )
        
        meshChildren = mesh.listRelatives( c=1 )
        bbmin = [10000000,10000000,1000000]
        bbmax = [-10000000,-10000000,-10000000]
        for child in meshChildren:
            cbbmin = child.attr( 'boundingBoxMin' ).get()
            cbbmax = child.attr( 'boundingBoxMax' ).get()
            for i in range( 3 ):
                bbmin[i] = min( bbmin[i], cbbmin[i] )
                bbmax[i] = max( bbmax[i], cbbmax[i] )
            
        meshStartPoint = [ 0,0,0 ]
        meshEndPoint = [ 0,0,0 ]
        meshStartPoint[ directionIndex%3 ] = bbmin[directionIndex%3]
        meshEndPoint[ directionIndex%3 ] = bbmax[directionIndex%3]
        meshStartPoint = sgCmds.getMPoint(meshStartPoint) * sgCmds.listToMatrix( mesh.wm.get() )
        meshEndPoint = sgCmds.getMPoint(meshEndPoint) * sgCmds.listToMatrix( mesh.wm.get() )
        return meshStartPoint, meshEndPoint, directionIndex
    
    paramMinValue = curve.getShape().minValue.get()
    paramMaxValue = curve.getShape().maxValue.get()
    
    startPoint, endPoint,  dirIndex = getMeshStartAndEndPoint( mesh, curve )
    direction = sgCmds.getVectorList()[dirIndex]
    param   = sgCmds.getClosestParamAtPoint( mesh, curve )
    closePoint = sgCmds.getPointAtParam( curve, param )
    tangent = sgCmds.getTangentAtParam( curve, param )
    
    startTr = pymel.core.createNode( 'transform' )
    rot = pymel.core.angleBetween( v1=direction, v2=[tangent.x, tangent.y, tangent.z], euler=1 )
    startTr.t.set( closePoint )
    startTr.r.set( rot )
    
    if mesh.getShape():
        sgCmds.setGeometryMatrixToTarget( mesh, startTr )
    else:
        sgCmds.setMatrixToTarget( startTr.wm.get(), mesh, pcp=1 )
    pymel.core.delete( startTr )
    
    curveLength = sgCmds.getCurveLength( curve )
    
    sizeOfBlock = startPoint.distanceTo( endPoint )
    spaceOfBlock = sizeOfBlock * percentOfSpaceOfBlock
    
    numBlock = int( curveLength/(sizeOfBlock + spaceOfBlock) )
    elseSpace = curveLength - ( sizeOfBlock + spaceOfBlock ) * numBlock
    
    spaceOfBlock += elseSpace / numBlock
    
    blockLength = ( spaceOfBlock + sizeOfBlock )
    eachParamLengthOfBlock = blockLength / curveLength * (paramMaxValue-paramMinValue)
    
    mainGrp = pymel.core.createNode( 'transform' )
    sgCmds.addAttr( mainGrp, ln='param', k=1 )
    
    duMeshPointers = []
    duMeshs = []
    
    for i in range( numBlock ):
        duMesh = pymel.core.duplicate( mesh )[0]
        if mesh.getShape():
            mesh.getShape().outMesh >> duMesh.getShape().inMesh
            sgCmds.copyShader( mesh, duMesh )
        randomOffset = random.uniform( -randomOffsetPercent*blockLength/2, randomOffsetPercent*blockLength/2 )
        duMesh.addAttr( 'offset', k=1, dv= randomOffset )
        
        duMeshPointer = pymel.core.createNode( 'transform' )
        pymel.core.xform( duMeshPointer, ws=1, matrix= duMesh.wm.get() )
        
        animCurve = pymel.core.createNode( 'animCurveUU' )
        animCurve.attr( 'preInfinity' ).set( 3 )
        animCurve.attr( 'postInfinity').set( 3 )

        offsetAdd = pymel.core.createNode( 'addDoubleLinear' )
        paramAdd = pymel.core.createNode( 'addDoubleLinear' )
        paramMult = pymel.core.createNode( 'multDoubleLinear' )
        mainGrp.attr( 'param' ) >> offsetAdd.input1
        duMesh.attr( 'offset' ) >> offsetAdd.input2
        offsetAdd.output >> paramMult.input1
        paramMult.input2.set( (paramMaxValue-paramMinValue)/curveLength )
        paramMult.output >> paramAdd.input1
        paramAdd.input2.set( eachParamLengthOfBlock * i + paramMinValue )
        paramAdd.output >> animCurve.input

        pymel.core.setKeyframe( animCurve, f=paramMinValue, v = paramMinValue )
        pymel.core.setKeyframe( animCurve, f=paramMaxValue, v = paramMaxValue )
        pymel.core.keyTangent( animCurve, itt='linear', ott='linear' )
        
        sgCmds.attachToCurve( duMeshPointer, curve )
        animCurve.output >> duMeshPointer.param
        sgCmds.constrain_parent( duMeshPointer, duMesh )
        duMeshPointers.append( duMeshPointer )
        duMeshs.append( duMesh )
        
        pymel.core.tangentConstraint( curve, duMeshPointer, aim=direction, u=upVector, wu=upVector, wut='objectrotation', wuo=upObject)
    
    pointersGrp   = pymel.core.group( duMeshPointers, n='conveyer_pointersGrp' )
    duMeshsGrp    = pymel.core.group( duMeshs, n='conveyer_duMeshsGrp' )
    mesh.v.set( 0 ); upObject.v.set( 0 ); pointersGrp.v.set( 0 );curve.v.set( 0 )
    pymel.core.parent( mesh, curve, upObject, pointersGrp, duMeshsGrp, mainGrp )
    pymel.core.select( mainGrp )
    
    


def conveyerBeltRig( mesh, curve, percentOfSpaceOfBlock=0.0 ):
    
    def getMeshStartAndEndPoint( mesh, curve ):
        param = sgCmds.getClosestParamAtPoint( mesh, curve )
        direction = sgCmds.getTangentAtParam( curve, param )
        localDirection = sgCmds.getMVector(direction) * sgCmds.listToMatrix( mesh.wim.get() )
        directionIndex = sgCmds.getDirectionIndex( localDirection )
        meshShape = sgCmds.getShape( mesh )
        bbmin = meshShape.attr( 'boundingBoxMin' ).get()
        bbmax = meshShape.attr( 'boundingBoxMax' ).get()
        meshStartPoint = [ 0,0,0 ]
        meshEndPoint = [ 0,0,0 ]
        meshStartPoint[ directionIndex%3 ] = bbmin[directionIndex%3]
        meshEndPoint[ directionIndex%3 ] = bbmax[directionIndex%3]
        meshStartPoint = sgCmds.getMPoint(meshStartPoint) * sgCmds.listToMatrix( mesh.wm.get() )
        meshEndPoint = sgCmds.getMPoint(meshEndPoint) * sgCmds.listToMatrix( mesh.wm.get() )
        return meshStartPoint, meshEndPoint, sgCmds.getVectorList()[directionIndex]
    
    paramMinValue = curve.getShape().minValue.get()
    paramMaxValue = curve.getShape().maxValue.get()
    
    startPoint, endPoint, direction = getMeshStartAndEndPoint( mesh, curve )
    param   = sgCmds.getClosestParamAtPoint( mesh, curve )
    tangent = sgCmds.getTangentAtParam( curve, param )    
    
    paramStartPoint = sgCmds.getClosestParamAtPoint( startPoint, curve )
    paramEndPoint   = sgCmds.getClosestParamAtPoint( endPoint, curve )
    sp = sgCmds.getPointAtParam( curve, paramStartPoint )
    ep = sgCmds.getPointAtParam( curve, paramEndPoint )
    startTr = pymel.core.createNode( 'transform', n='startTr' ); startTr.t.set( sp )
    endTr   = pymel.core.createNode( 'transform', n='endTr' ); endTr.t.set( ep )
    sgCmds.lookAt( endTr, startTr, direction )
    
    if mesh.getShape():
        sgCmds.setGeometryMatrixToTarget( mesh, startTr )
    else:
        sgCmds.setMatrixToTarget( mesh, startTr, pcp=1 )
    curveLength = sgCmds.getCurveLength( curve )
    
    sizeOfBlock = OpenMaya.MPoint( *pymel.core.xform( endTr, q=1, ws=1, t=1 ) ).distanceTo( OpenMaya.MPoint( *pymel.core.xform( startTr, q=1, ws=1, t=1 ) ) )
    spaceOfBlock = sizeOfBlock * percentOfSpaceOfBlock 
    
    numBlock = int( curveLength/(sizeOfBlock + spaceOfBlock) )
    elseSpace = curveLength - ( sizeOfBlock + spaceOfBlock ) * numBlock
    
    spaceOfBlock += elseSpace / numBlock
    
    eachParamLengthOfBlock = ( spaceOfBlock + sizeOfBlock ) / curveLength * (paramMaxValue-paramMinValue)
    
    mainGrp = pymel.core.createNode( 'transform' )
    sgCmds.addAttr( mainGrp, ln='param', k=1 )
    
    duMeshPointers = []
    duMeshs = []
    
    for i in range( numBlock+1 ):
        duMesh = pymel.core.duplicate( mesh )[0]
        mesh.getShape().outMesh >> duMesh.getShape().inMesh
        sgCmds.copyShader( mesh, duMesh )
        
        duMeshPointer = pymel.core.createNode( 'transform' )
        pymel.core.xform( duMeshPointer, ws=1, matrix= duMesh.wm.get() )
        
        animCurve = pymel.core.createNode( 'animCurveUU' )
        animCurve.attr( 'preInfinity' ).set( 3 )
        animCurve.attr( 'postInfinity').set( 3 )

        offsetAdd = pymel.core.createNode( 'addDoubleLinear' )
        offsetMult = pymel.core.createNode( 'multDoubleLinear' )
        mainGrp.attr( 'param' ) >> offsetMult.input1
        offsetMult.input2.set( (paramMaxValue-paramMinValue)/curveLength )
        offsetMult.output >> offsetAdd.input1
        offsetAdd.input2.set( eachParamLengthOfBlock * i + paramMinValue )
        offsetAdd.output >> animCurve.input

        pymel.core.setKeyframe( animCurve, f=paramMinValue, v = paramMinValue )
        pymel.core.setKeyframe( animCurve, f=paramMaxValue, v = paramMaxValue )
        pymel.core.keyTangent( animCurve, itt='linear', ott='linear' )
        
        sgCmds.attachToCurve( duMeshPointer, curve )
        animCurve.output >> duMeshPointer.param
        
        sgCmds.makeParent( duMeshPointer )
        sgCmds.constrain_parent( duMeshPointer, duMesh )
        duMeshPointers.append( duMeshPointer )
        duMeshs.append( duMesh )
    
    for i in range( numBlock ):
        sgCmds.lookAtConnect( duMeshPointers[(i+1)%(numBlock+1)], duMeshPointers[i], direction=tangent )
    pymel.core.delete( duMeshs[-1] )
    
    duMeshGrp    = pymel.core.group( duMeshs, n='conveyer_meshs' )
    duPointerGrp = pymel.core.group( duMeshPointers, n='conveyer_pointers' )




def conveyerBeltRig_deform( mesh, curve, upObject, upVector, numDetail=4 ):
    
    if numDetail < 3: numDetail = 3
    
    def editGeometryTransform( mesh, curve ):
        meshMtx = sgCmds.getPivotWorldMatrix( mesh )
        sgCmds.setGeometryMatrixToTarget( mesh, meshMtx )
        newTr = sgCmds.createNearestPointOnCurveObject( mesh, curve )
        newTrPos = newTr.t.get()
        pymel.core.delete( newTr )
        setMtx = sgCmds.matrixToList( meshMtx )
        setMtx = setMtx[:-4] + [newTrPos[0],newTrPos[1],newTrPos[2]] + [1]
        sgCmds.setGeometryMatrixToTarget( mesh, setMtx ) 
    
    editGeometryTransform( mesh, curve )
    
    curveLength = sgCmds.getCurveLength( curve )
    meshBB = pymel.core.exactWorldBoundingBox( mesh )
    bbmin = meshBB[:3]
    bbmax = meshBB[3:]
    
    sizeX = bbmax[0]-bbmin[0]
    sizeY = bbmax[1]-bbmin[1]
    sizeZ = bbmax[2]-bbmin[2]
    
    size = [ sizeX, sizeY, sizeZ ]
    
    closeParam = sgCmds.getClosestParamAtPoint( mesh, curve )
    paramMinValue = curve.getShape().minValue.get()
    paramMaxValue = curve.getShape().maxValue.get()
    
    tangent = sgCmds.getTangentAtParam( curve, closeParam )
    directionIndex = sgCmds.getDirectionIndex( tangent )
    
    sizeOfBlock = size[ directionIndex%3 ]
    spaceOfEachBlock = sizeOfBlock * 0.02
    
    numBlock = int( curveLength/(sizeOfBlock + spaceOfEachBlock) )
    elseSpace = curveLength - ( sizeOfBlock + spaceOfEachBlock ) * numBlock
    
    spaceOfEachBlock += elseSpace / numBlock
    
    eachParamLengthOfBlock = ( spaceOfEachBlock + sizeOfBlock ) / curveLength * (paramMaxValue-paramMinValue)
    
    mainGrp = pymel.core.createNode( 'transform', n='conveyer_allGrp' )
    sgCmds.addAttr( mainGrp, ln='param', k=1 )
    
    eachCurves = []
    baseCurves = []
    pointers = []
    duMeshs = []
    localMeshs = []
    for i in range( numBlock ):
        duMesh = pymel.core.duplicate( mesh )[0]
        mesh.getShape().outMesh >> duMesh.getShape().inMesh
        localOutMesh = pymel.core.duplicate( mesh )[0]
        duMesh.getShape().outMesh >> localOutMesh.inMesh
        
        offsetMin = -eachParamLengthOfBlock/2
        offsetMax =  eachParamLengthOfBlock/2
        
        eachPointers = []
        for j in range( numDetail ):
            addOffsetValue = ((offsetMax - offsetMin) / (numDetail-1)) * j + offsetMin
            
            animCurve = pymel.core.createNode( 'animCurveUU' )
            animCurve.attr( 'preInfinity' ).set( 3 )
            animCurve.attr( 'postInfinity').set( 3 )
    
            offsetAdd = pymel.core.createNode( 'addDoubleLinear' )
            offsetMult = pymel.core.createNode( 'multDoubleLinear' )
            mainGrp.attr( 'param' ) >> offsetMult.input1
            offsetMult.input2.set( (paramMaxValue-paramMinValue)/curveLength )
            offsetMult.output >> offsetAdd.input1
            offsetAdd.input2.set( eachParamLengthOfBlock * i + addOffsetValue + paramMinValue )
            offsetAdd.output >> animCurve.input
    
            pymel.core.setKeyframe( animCurve, f=paramMinValue, v = paramMinValue )
            pymel.core.setKeyframe( animCurve, f=paramMaxValue, v = paramMaxValue )
            pymel.core.keyTangent( animCurve, itt='linear', ott='linear' )
        
            pointer = pymel.core.createNode( 'transform' )
            sgCmds.attachToCurve( pointer, curve )
            animCurve.output >> pointer.param
            eachPointers.append( pointer )
        pointers += eachPointers

        eachCurve = sgCmds.makeCurveFromSelection( *eachPointers, d=2 )
        mainGrp.attr( 'param' ).set( (closeParam - eachParamLengthOfBlock * i + paramMinValue) * curveLength )
        wireNode = pymel.core.wire( duMesh, gw=False, en=1, ce=0, li=0, w=eachCurve, dds=[0,100000] )[0]
        baseCurve = wireNode.attr( 'baseWire' ).listConnections( s=1, d=0 )[0]
        
        eachCurves.append( eachCurve )
        baseCurves.append( baseCurve )
        duMeshs.append( duMesh )
        localMeshs.append( localOutMesh )
        
        pymel.core.refresh()
    
    eachCurveGrp  = pymel.core.group( eachCurves, n='conveyer_eachCurvesGrp' )
    baseCurveGrp  = pymel.core.group( baseCurves, n='conveyer_baseCurvesGrp' )
    pointersGrp   = pymel.core.group( pointers, n='conveyer_pointersGrp' )
    duMeshsGrp    = pymel.core.group( duMeshs, n='conveyer_duMeshsGrp' )
    localMeshsGrp = pymel.core.group( localMeshs, n='conveyer_localMeshsGrp' )
    mesh.v.set( 0 ); upObject.v.set( 0 ); eachCurveGrp.v.set( 0 ); baseCurveGrp.v.set( 0 ); pointersGrp.v.set( 0 ); duMeshsGrp.v.set( 0 );curve.v.set( 0 )
    pymel.core.parent( mesh, curve, upObject, eachCurveGrp, baseCurveGrp, pointersGrp, duMeshsGrp, localMeshsGrp, mainGrp )
    pymel.core.select( mainGrp )
    
    


def createDefaultPropRig( propGrp ):
    
    propGrp = pymel.core.ls( propGrp )[0]
    
    def makeParent( target ):
        targetP = pymel.core.createNode( 'transform' )
        pymel.core.xform( targetP, ws=1, matrix= target.wm.get() )
        pymel.core.parent( target, targetP )
        targetP.rename( 'P' + target.shortName() )
        return targetP
    
    worldCtl = pymel.core.ls( sgCmds.makeController( sgModel.Controller.circlePoints ).name() )[0]
    moveCtl  = pymel.core.ls( sgCmds.makeController( sgModel.Controller.crossPoints ).name() )[0]
    rootCtl  = pymel.core.ls( sgCmds.makeController( sgModel.Controller.circlePoints ).name() )[0]
    
    bb = cmds.exactWorldBoundingBox(propGrp.name())
    bbmin = bb[:3]
    bbmax = bb[3:]
    
    bbsize = max( bbmax[0] - bbmin[0], bbmax[2] - bbmin[2] )/2
    
    center     = ( ( bbmin[0] + bbmax[0] )/2, ( bbmin[1] + bbmax[1] )/2, ( bbmin[2] + bbmax[2] )/2 )
    floorPoint = ( ( bbmin[0] + bbmax[0] )/2, bbmin[1], ( bbmin[2] + bbmax[2] )/2 )
    
    worldCtl.t.set( *floorPoint )
    moveCtl.t.set( *floorPoint )
    rootCtl.t.set( *center )
    
    rootCtl.shape_sx.set( bbsize*1.2 )
    rootCtl.shape_sy.set( bbsize*1.2 )
    rootCtl.shape_sz.set( bbsize*1.2 )

    moveCtl.shape_sx.set( bbsize*1.3 )
    moveCtl.shape_sy.set( bbsize*1.3 )
    moveCtl.shape_sz.set( bbsize*1.3 )
    
    worldCtl.shape_sx.set( bbsize*1.5 )
    worldCtl.shape_sy.set( bbsize*1.5 )
    worldCtl.shape_sz.set( bbsize*1.5 )
    
    rootCtl.getShape().setAttr( 'overrideEnabled', 1 )
    rootCtl.getShape().setAttr( 'overrideColor', 29 )
    moveCtl.getShape().setAttr( 'overrideEnabled', 1 )
    moveCtl.getShape().setAttr( 'overrideColor', 20 )
    worldCtl.getShape().setAttr( 'overrideEnabled', 1 )
    worldCtl.getShape().setAttr( 'overrideColor', 17 )
    
    shortName = propGrp.shortName().split( '|' )[-1]
    rootCtl.rename( 'Ctl_%s_Root' % shortName )
    moveCtl.rename( 'Ctl_%s_Move' % shortName )
    worldCtl.rename( 'Ctl_%s_World' % shortName )
    
    pRootCtl  = makeParent( rootCtl )
    pMoveCtl  = makeParent( moveCtl )
    pWorldCtl = makeParent( worldCtl )
    
    pymel.core.parent( pRootCtl, moveCtl )
    pymel.core.parent( pMoveCtl, worldCtl )

    sgCmds.setMatrixToGeoGroup( rootCtl.wm.get(), propGrp.name() )
    sgCmds.constrain_all( rootCtl, propGrp )


    

def createSimplePlaneControl( inputTarget, **options ):
    
    target = pymel.core.ls( inputTarget )[0]
    
    points = sgModel.Controller.cubePoints
    moveCtlPoints = sgModel.Controller.pinPoints
    if options.has_key( 'typ' ) and options[ 'typ' ] == 'circle':
        points = sgModel.Controller.circlePoints
    
    worldCtl = sgCmds.makeController( points, makeParent=1 )
    moveCtl =  sgCmds.makeController( moveCtlPoints, makeParent=1 )
    
    bb = cmds.exactWorldBoundingBox(target.name())
    bbmin = bb[:3]
    bbmax = bb[3:]

    bbsize = ( bbmax[0] - bbmin[0], bbmax[1] - bbmin[1], bbmax[2] - bbmin[2] )
    center     = ( ( bbmin[0] + bbmax[0] )/2, ( bbmin[1] + bbmax[1] )/2, ( bbmin[2] + bbmax[2] )/2 )

    for ctl in [ worldCtl, moveCtl ]:
        ctlShape = ctl.getShape()
        ctlShape.setAttr( 'overrideEnabled', 1 )

    worlcCtlShape = worldCtl.getShape()
    moveCtlShape  = moveCtl.getShape()
    worlcCtlShape.setAttr( 'overrideColor', 17 )
    moveCtlShape.setAttr( 'overrideColor', 20 )
    worlcCtlShape.shape_sx.set(bbsize[0])
    worlcCtlShape.shape_sy.set(bbsize[1])
    worlcCtlShape.shape_sz.set(bbsize[2])
    for attr in [ 'shape_sx', 'shape_sy', 'shape_sz']:
        moveCtlShape.attr( attr ).set( max( bbsize ) * 0.5)
    
    worldCtl.rename( 'Ctl_%s_World' % target.name() )
    moveCtl.rename( 'Ctl_%s_Move' % target.name() )
    moveCtl.getParent().setParent( worldCtl )

    if options.has_key( 'directionBased' ):
        setMatrixToCenterPoint( target, True )
        trValue  = sgCmds.getTranslateFromMatrix(target.wm.get())
        rotValue = sgCmds.getRotateFromMatrix(target.wm.get())
        scaleValue = sgCmds.getScaleFromMatrix( target.wm.get() )
        worldCtl.getParent().t.set( trValue )
        worldCtl.getParent().r.set( rotValue )
        worlcCtlShape.shape_sx.set(scaleValue[0])
        worlcCtlShape.shape_sy.set(scaleValue[1])
        worlcCtlShape.shape_sz.set(scaleValue[2])
        for attr in ['shape_sx', 'shape_sy', 'shape_sz']:
            moveCtlShape.attr(attr).set(max(scaleValue) * 0.5)
    else:
        worldCtl.getParent().t.set( center )
    followTarget( target, moveCtl )

    worldCtl.getParent().rename('P' + worldCtl )
    moveCtl.getParent().rename('P' + moveCtl )

    return moveCtl, worldCtl




def makeLookAtSquashTransform( lookObject, baseObject, lookParentObject=None, baseParentObject=None, size=1 ):

    if not lookParentObject:
        lookParentObject = pymel.core.ls( lookObject )[0].getParent()
    if not baseParentObject:
        baseParentObject = pymel.core.ls( baseObject )[0].getParent()
        if not baseParentObject:
            baseParentObject = baseObject

    dcmpBase   = sgCmds.getDecomposeMatrix( sgCmds.getMultMatrix( lookParentObject + '.wm', baseParentObject + '.wim' ).o )
    dcmpSquash = sgCmds.getDecomposeMatrix( sgCmds.getMultMatrix( lookObject + '.wm', baseObject + '.wim' ).o )
    directionIndex = sgCmds.getDirectionIndex( dcmpBase.ot.get() )

    lookAtChild = sgCmds.makeLookAtChild( lookObject, baseObject )
    lookAtChild.rename( 'lookAtChild_' + baseObject )
    squashTransform = sgCmds.makeChild( lookAtChild, 'null' )
    squashTransform.rename( 'squashTr_' + baseObject )
    squashCenter = sgCmds.makeChild( squashTransform )
    sgCmds.addAttr( squashCenter, ln='positionParam', min=0, max=1, dv=0.5, k=1 )
    
    sgCmds.createControllerShape( sgModel.Controller.diamondPoints,squashCenter, size )
    centerTrMult = pymel.core.createNode( 'multiplyDivide' )
    dcmpBase.attr( ['otx', 'oty', 'otz'][ (directionIndex) % 3 ] ) >> centerTrMult.attr( ['input1X', 'input1Y', 'input1Z'][ (directionIndex) % 3 ] )
    squashCenter.attr( 'positionParam' ) >> centerTrMult.input2X
    squashCenter.attr( 'positionParam' ) >> centerTrMult.input2Y
    squashCenter.attr( 'positionParam' ) >> centerTrMult.input2Z
    centerTrMult.output >> squashCenter.t
    
    distBase   = sgCmds.getDistance( dcmpBase )
    distSquash = sgCmds.getDistance( dcmpSquash )
    
    scaleNode = pymel.core.createNode( 'multiplyDivide' )
    distSquash.distance >> scaleNode.input1X
    distBase.distance   >> scaleNode.input2X
    scaleNode.op.set( 2 )
    
    
    scaleNode.outputX >> squashTransform.attr( ['sx', 'sy', 'sz'][ directionIndex % 3 ] )
    
    sgCmds.addOptionAttribute( lookObject )
    sgCmds.addAttr( lookObject, ln='squash', k=1, dv=1 )
    
    squashAttr = sgCmds.createSquashAttr( scaleNode.outputX, lookObject + '.squash' )
    squashAttr >> squashTransform.attr( ['sx', 'sy', 'sz'][ (directionIndex+1) % 3 ] )
    squashAttr >> squashTransform.attr( ['sx', 'sy', 'sz'][ (directionIndex+2) % 3 ] )
    
    return squashCenter




def makeLookAtSquashBendTransform( lookObject, baseObject, lookParentObject=None, size=1 ):

    if not lookParentObject:
        lookParentObject = pymel.core.ls( lookObject )[0].getParent()

    dcmpBase   = sgCmds.getDecomposeMatrix( sgCmds.getMultMatrix( lookParentObject + '.wm', baseObject + '.wim' ).o )
    dcmpSquash = sgCmds.getDecomposeMatrix( sgCmds.getMultMatrix( lookObject + '.wm', baseObject + '.wim' ).o )
    directionIndex = sgCmds.getDirectionIndex( dcmpBase.ot.get() )

    centerBaseObject = sgCmds.makeChild( baseObject )
    centerBaseObject.rename( 'centerBase_' + baseObject )
    sgCmds.addAttr( centerBaseObject, ln='positionParam', min=0, max=1, dv=0.5, k=1 )
    multCenterNode = pymel.core.createNode( 'multiplyDivide' )
    dcmpSquash.attr( ['otx', 'oty', 'otz'][ (directionIndex) % 3 ] ) >> multCenterNode.attr( ['input1X', 'input1Y', 'input1Z'][ (directionIndex) % 3 ] )
    centerBaseObject.attr( 'positionParam' ) >> multCenterNode.attr('input2X')
    centerBaseObject.attr( 'positionParam' ) >> multCenterNode.attr('input2Y')
    centerBaseObject.attr( 'positionParam' ) >> multCenterNode.attr('input2Z')
    multCenterNode.output >> centerBaseObject.t

    lookAtChild = sgCmds.makeLookAtChild( lookObject, centerBaseObject )
    lookAtChild.rename( 'lookAtChild_' + centerBaseObject )
    squashTransform = sgCmds.makeChild( lookAtChild, 'null' )
    squashTransform.rename( 'squashTr_' + centerBaseObject )
    
    sgCmds.createControllerShape( sgModel.Controller.diamondPoints,squashTransform, size )
    
    distBase   = sgCmds.getDistance( dcmpBase )
    distSquash = sgCmds.getDistance( dcmpSquash )
    
    scaleNode = pymel.core.createNode( 'multiplyDivide' )
    distSquash.distance >> scaleNode.input1X
    distBase.distance   >> scaleNode.input2X
    scaleNode.op.set( 2 )
    
    scaleNode.outputX >> squashTransform.attr( ['sx', 'sy', 'sz'][ directionIndex % 3 ] )
    
    sgCmds.addOptionAttribute( lookObject )
    sgCmds.addAttr( lookObject, ln='squash', k=1, dv=1 )
    
    squashAttr = sgCmds.createSquashAttr( scaleNode.outputX, lookObject + '.squash' )
    squashAttr >> squashTransform.attr( ['sx', 'sy', 'sz'][ (directionIndex+1) % 3 ] )
    squashAttr >> squashTransform.attr( ['sx', 'sy', 'sz'][ (directionIndex+2) % 3 ] )
    
    return centerBaseObject
    
    
    
    
def createMatrixObjectFromGeo( target, typ='originalTransform' ):
    
    targetShapes = [ shape for shape in pymel.core.listRelatives( target, c=1, ad=1, type='mesh' ) if not shape.io.get() ]

    if typ == "directionBased":
        vectorDicts = {}
        xBaseVector = OpenMaya.MVector( 1,0,0 )
        yBaseVector = OpenMaya.MVector( 0,1,0 )
        zBaseVector = OpenMaya.MVector( 0,0,1 )
        
        for targetShape in targetShapes:
            dagPathMesh = sgCmds.getDagPath(targetShape)
            fnMesh = OpenMaya.MFnMesh( dagPathMesh )
            
            points = OpenMaya.MPointArray()
            fnMesh.getPoints( points, OpenMaya.MSpace.kWorld )

            for i in range( fnMesh.numEdges() ):
                util = OpenMaya.MScriptUtil()
                util.createFromList([0,0],2)
                int2Ptr = util.asInt2Ptr()
                fnMesh.getEdgeVertices( i, int2Ptr )
                index1 = util.getInt2ArrayItem( int2Ptr, 0, 0 )
                index2 = util.getInt2ArrayItem( int2Ptr, 0, 1 )
                
                point1 = points[ index1 ]
                point2 = points[ index2 ]
                
                vector = point2 - point1
                
                dotX = math.fabs( xBaseVector * vector )
                dotY = math.fabs( yBaseVector * vector )
                dotZ = math.fabs( zBaseVector * vector )
                
                if dotY == max( [ dotX, dotY, dotZ ] ):
                    continue
                
                if dotX > dotZ:
                    convertedVector = vector if xBaseVector * vector > 0 else -vector
                elif dotZ >= dotX:
                    convertedVector = vector if zBaseVector * vector > 0 else -vector
                
                key = "%.2f,%.2f,%.2f" %( convertedVector.x, convertedVector.y, convertedVector.z )
                if not vectorDicts.has_key( key ):
                    vectorDicts[ key ] = { "value":[convertedVector.x, 0, convertedVector.z], "length":convertedVector.length()}
                else:
                    vectorDicts[ key ]['length'] += convertedVector.length()
                    vectorDicts[ key ]['value'][0] +=  convertedVector.x
                    vectorDicts[ key ]['value'][1] +=  0
                    vectorDicts[ key ]['value'][2] +=  convertedVector.z
            
        maxLength = 0.0
        maxLengthKey = None
        for key in vectorDicts.keys():
            if maxLength < vectorDicts[ key ]['length']:
                maxLength = vectorDicts[ key ]['length']
                maxLengthKey = key
        
        horizonVector = OpenMaya.MVector( *vectorDicts[ maxLengthKey ][ 'value' ] ).normal()
        upVector      = OpenMaya.MVector( 0,1,0 )

        dotX = math.fabs( xBaseVector * horizonVector )
        dotZ = math.fabs( zBaseVector * horizonVector )
        
        if dotX > dotZ:
            xVector = horizonVector
            yVector = upVector
            zVector = horizonVector ^ upVector
        else:
            xVector = horizonVector
            yVector = upVector
            zVector = upVector ^ horizonVector

    elif typ == "originalTransform":
        targetMtx = sgCmds.getMMatrix( target.wm )
        xVector = OpenMaya.MVector(1,0, 0) * targetMtx
        yVector = OpenMaya.MVector(0,1, 0) * targetMtx
        zVector = OpenMaya.MVector(0,0, 1) * targetMtx
        xVector.normalize()
        yVector.normalize()
        zVector.normalize()
    else:
        xVector = OpenMaya.MVector( 1,0,0 )
        yVector = OpenMaya.MVector( 0,1,0 )
        zVector = OpenMaya.MVector( 0,0,1 )

    worldPivot = pymel.core.xform( target, q=1, ws=1, rotatePivot=1 )
    mtxList = [xVector.x, xVector.y, xVector.z,0, yVector.x, yVector.y, yVector.z,0, zVector.x, zVector.y, zVector.z,0, worldPivot[0],worldPivot[1],worldPivot[2],1]
    mtx = sgCmds.listToMatrix( mtxList )
    invMtx = mtx.inverse()
    bb = OpenMaya.MBoundingBox()
    
    pointsList = []
    for targetShape in targetShapes:
        dagPathMesh = sgCmds.getDagPath(targetShape)
        fnMesh = OpenMaya.MFnMesh( dagPathMesh )
        
        points = OpenMaya.MPointArray()
        fnMesh.getPoints( points, OpenMaya.MSpace.kWorld )
        pointsList.append( points )
    
    for points in pointsList:
        for i in range( points.length() ):
            bb.expand( points[i] * invMtx )
        
    bbCenter = bb.center() * mtx
    mtxList[12] = bbCenter.x;mtxList[13] = bbCenter.y;mtxList[14] = bbCenter.z
    
    tr = pymel.core.createNode( 'transform' )
    tr.dh.set( 1 )
    pymel.core.xform( tr, ws=1, matrix= mtxList )
    xSize = bb.max().x-bb.min().x
    ySize = bb.max().y-bb.min().y
    zSize = bb.max().z-bb.min().z
    tr.s.set( xSize, ySize, zSize )
    return tr




def setMatrixToCenterPoint( target, typ='originalTransform' ):
    
    trObject = createMatrixObjectFromGeo( target, typ=typ )
    trObjectMtxList = trObject.wm.get()
    trObjectMtx = sgCmds.listToMatrix( trObjectMtxList )
    pymel.core.delete( trObject )
    sgCmds.setMatrixToTarget( trObjectMtxList, target, pcp=1 )




def setMatrixToButtomPoint( target, typ='originalTransform' ):
    
    trObject = createMatrixObjectFromGeo( target, typ=typ )
    trObjectMtxList = trObject.wm.get()
    trObjectMtx = sgCmds.listToMatrix( trObjectMtxList )
    pymel.core.delete( trObject )
    point = OpenMaya.MPoint( 0, -0.5, 0 ) * trObjectMtx
    defaultMtx = sgCmds.getDefaultMatrix()
    defaultMtx[12] = point.x
    defaultMtx[13] = point.y
    defaultMtx[14] = point.z
    sgCmds.setMatrixToTarget( defaultMtx, target, pcp=1 )


        
    
def createPlaneController( target, typ='originalTransform' ):
    
    trObject = createMatrixObjectFromGeo( target, typ=typ )
    trObjectMtxList = trObject.wm.get()
    trObjectMtx = sgCmds.listToMatrix( trObjectMtxList )
    pymel.core.delete( trObject )
    
    vectorX = OpenMaya.MVector( trObjectMtx[0] )
    vectorY = OpenMaya.MVector( trObjectMtx[1] )
    vectorZ = OpenMaya.MVector( trObjectMtx[2] )
    point = OpenMaya.MPoint( 0, -0.5, 0 ) * trObjectMtx
    
    ctl = sgCmds.makeController( sgModel.Controller.planePoints, 1, makeParent=1 )
    ctlP = ctl.getParent()
    ctlShape = ctl.getShape()
    ctlShape.shape_sx.set( vectorX.length() )
    ctlShape.shape_sy.set( vectorY.length() )
    ctlShape.shape_sz.set( vectorZ.length() )
    ctlShape.scaleMult.set( 0.5 )
    
    pymel.core.xform( ctlP, ws=1, ro=sgCmds.getRotateFromMatrix( trObjectMtxList ) )
    pymel.core.xform( ctlP, ws=1, t=[point.x,point.y,point.z] )
    
    targetP = target.getParent()
    targetGrp = pymel.core.createNode( 'transform' )
    if targetP: targetGrp.setParent( targetP )
    sgCmds.constrain_all( ctl, targetGrp )
    target.setParent( targetGrp )
    pymel.core.select( ctl )
    sgCmds.setIndexColor( ctl, 22 )
    return ctl
    
    
    
def createCubeController_toCenter( target, typ='originalTransform' ):
    
    trObject = createMatrixObjectFromGeo( target, typ=typ )
    trObjectMtxList = trObject.wm.get()
    trObjectMtx = sgCmds.listToMatrix( trObjectMtxList )
    pymel.core.delete( trObject )
    
    vectorX = OpenMaya.MVector( trObjectMtx[0] )
    vectorY = OpenMaya.MVector( trObjectMtx[1] )
    vectorZ = OpenMaya.MVector( trObjectMtx[2] )
    point = OpenMaya.MPoint( 0, 0, 0 ) * trObjectMtx
    
    ctl = sgCmds.makeController( sgModel.Controller.cubePoints, 1, makeParent=1 )
    ctlP = ctl.getParent()
    ctlShape = ctl.getShape()
    ctlShape.shape_sx.set( vectorX.length() )
    ctlShape.shape_sy.set( vectorY.length() )
    ctlShape.shape_sz.set( vectorZ.length() )
    
    pymel.core.xform( ctlP, ws=1, ro=sgCmds.getRotateFromMatrix( trObjectMtxList ) )
    pymel.core.xform( ctlP, ws=1, t=[point.x,point.y,point.z] )
    
    targetP = target.getParent()
    targetGrp = pymel.core.createNode( 'transform' )
    if targetP: targetGrp.setParent( targetP )
    sgCmds.constrain_all( ctl, targetGrp )
    target.setParent( targetGrp )
    pymel.core.select( ctl )
    sgCmds.setIndexColor( ctl, 22 )
    return ctl



def createCubeController_toButtom( target, typ='originalTransform' ):
    
    trObject = createMatrixObjectFromGeo( target, typ=typ )
    trObjectMtxList = trObject.wm.get()
    trObjectMtx = sgCmds.listToMatrix( trObjectMtxList )
    pymel.core.delete( trObject )
    
    vectorX = OpenMaya.MVector( trObjectMtx[0] )
    vectorY = OpenMaya.MVector( trObjectMtx[1] )
    vectorZ = OpenMaya.MVector( trObjectMtx[2] )
    point = OpenMaya.MPoint( 0, -0.5, 0 ) * trObjectMtx
    
    ctl = sgCmds.makeController( sgModel.Controller.cubePoints, 1, makeParent=1 )
    ctlP = ctl.getParent()
    ctlShape = ctl.getShape()
    ctlShape.shape_sx.set( vectorX.length() )
    ctlShape.shape_sy.set( vectorY.length() )
    ctlShape.shape_sz.set( vectorZ.length() )
    ctlShape.shape_ty.set( vectorY.length() * 0.5 )
    
    pymel.core.xform( ctlP, ws=1, ro=sgCmds.getRotateFromMatrix( trObjectMtxList ) )
    pymel.core.xform( ctlP, ws=1, t=[point.x,point.y,point.z] )
    
    targetP = target.getParent()
    targetGrp = pymel.core.createNode( 'transform' )
    if targetP: targetGrp.setParent( targetP )
    sgCmds.constrain_all( ctl, targetGrp )
    target.setParent( targetGrp )
    pymel.core.select( ctl )
    sgCmds.setIndexColor( ctl, 22 )
    return ctl
    
    
    

def shadowEffect( lightTransform, projectTargets, projectBase ):
    
    children = pymel.core.listRelatives( projectTargets, c=1, ad=1, type='mesh' )
    projectTargets = [ child.getParent() for child in children if sgCmds.isVisible( child ) ]
    
    def getLocalGeometry( geometry, parentObject ):
        geometryShape = geometry.getShape()
        mm = pymel.core.createNode( 'multMatrix' )
        trGeo = pymel.core.createNode( 'transformGeometry' )
        newMeshShape = pymel.core.createNode( 'mesh' )
        
        geometry.wm >> mm.i[0]
        parentObject.wim >> mm.i[1]
        
        geometryShape.attr( 'outMesh' ) >> trGeo.inputGeometry
        mm.matrixSum >> trGeo.transform
        trGeo.outputGeometry >> newMeshShape.attr( 'inMesh' )
        return newMeshShape.getParent()
    
    def projectMesh( projTarget, projBase ):
        projTargetShape = projTarget.getShape()
        projBaseShape   = projBase.getShape()
        shrinkWrap = pymel.core.deformer( projTargetShape, type='shrinkWrap' )[0]
        shrinkWrap.attr( 'reverse' ).set( 1 )
        shrinkWrap.attr( 'projection' ).set( 2 )
        attrList = ['keepMapBorders','continuity','smoothUVs','keepBorder',
                    'boundaryRule','keepHardEdge','propagateEdgeHardness']
        for attr in attrList:
            projTargetShape.attr( attr ) >> shrinkWrap.attr( attr )
        projBaseShape.attr( 'worldMesh' ) >> shrinkWrap.attr( 'targetGeom' )
        return shrinkWrap

    def getOutMesh( targetMesh ):
        targetMeshShape = targetMesh.getShape()
        newMesh = pymel.core.createNode( 'mesh' )
        targetMeshShape.outMesh >> newMesh.inMesh
        return newMesh.getParent()

    
    def getProjectionTypeOutput( lightTransform ):
        sgCmds.addAttr( lightTransform, ln='projectionType', at='enum', en=':point:directionX:directionY:directionZ', k=1 )
        pmaNode = pymel.core.createNode( 'plusMinusAverage' )
        for i, outputValues in [ (0,[0,0,0]),(1,[1,0,0]),(2,[0,1,0]),(3,[0,0,1]) ]:
            condition = pymel.core.createNode( 'condition' )
            lightTransform.attr( 'projectionType' ) >> condition.firstTerm
            condition.attr( 'secondTerm' ).set( i )
            condition.colorIfTrue.set( *outputValues )
            condition.colorIfFalse.set( 0,0,0 )
            condition.outColor >> pmaNode.input3D[i]
        return pmaNode.attr( 'output3Dx' ), pmaNode.attr( 'output3Dy' ), pmaNode.attr( 'output3Dz' )
    
    def addOffsetAttribute( lightTransform, shrinkWrapNode ):
        sgCmds.addAttr( lightTransform, ln='offset', min=0, k=1 )
        lightTransform.attr( 'offset' ) >> shrinkWrapNode.attr( 'targetInflation' )

    constrainGrp = pymel.core.createNode( 'transform', n=lightTransform.nodeName() + '_shadowCoreGrp' )
    resultGrp    = pymel.core.createNode( 'transform', n=lightTransform.nodeName() + '_shadowResultGrp' )
    localProjBase = getLocalGeometry( projectBase, lightTransform )
    localProjBase.setParent( constrainGrp )
    localProjBase.attr( 'inheritsTransform' ).set( 0 )
    localProjBase.v.set( 0 )
    
    xOutput, yOutput, zOutput = getProjectionTypeOutput( lightTransform )
    
    localGeometrys = []
    resultObjects = []
    for projectTarget in projectTargets:
        localProjTarget = getLocalGeometry( projectTarget, lightTransform )
        localProjTarget.attr( 'inheritsTransform' ).set( 0 )
        localProjTarget.v.set( 0 )
        
        shrinkWrap = projectMesh( localProjTarget, localProjBase )
        resultObject = getOutMesh( localProjTarget )
        sgCmds.copyShader( projectTarget, resultObject )
        xOutput >> shrinkWrap.attr( 'alongX' )
        yOutput >> shrinkWrap.attr( 'alongY' )
        zOutput >> shrinkWrap.attr( 'alongZ' )
        addOffsetAttribute( lightTransform, shrinkWrap )
        
        pymel.core.parent( localProjTarget, resultObject, constrainGrp )
        localGeometrys.append( localProjTarget )
        resultObjects.append( resultObject )
    
    pymel.core.group( localGeometrys, n='LocalObjects' )
    pymel.core.parent( resultObjects, resultGrp )
    
    if not cmds.objExists( 'shadowEffectSurfaceShader' ):
        surfaceShader = cmds.shadingNode( 'surfaceShader', asShader=1, n='shadowEffectSurfaceShader' )
    else:
        surfaceShader = 'shadowEffectSurfaceShader'
    if not cmds.objExists( 'shadowEffectSurfaceShaderSG' ):
        surfaceShaderSG = cmds.sets( renderable=True, noSurfaceShader=True, empty=1, name=surfaceShader + 'SG' )
    else:
        surfaceShaderSG = 'shadowEffectSurfaceShaderSG'

    if not cmds.isConnected( surfaceShader + '.outColor', surfaceShaderSG + '.surfaceShader' ):
        cmds.connectAttr( surfaceShader + '.outColor', surfaceShaderSG + '.surfaceShader' )  
    cmds.sets( resultGrp.name(), forceElement=surfaceShaderSG )
    
    sgCmds.constrain_all( lightTransform, constrainGrp )
    sgCmds.constrain_all( lightTransform, resultGrp )




def createLatticeController( targets, numController=0, typ='originalTransform' ):

    numController = max([numController,2])
    deformer, lattice, latticeBase = pymel.core.lattice(  divisions=[2,numController,2], objectCentered=False,  ldv=[2,numController+1,2] )
    mtxObject = createMatrixObjectFromGeo( targets, typ=typ )
    pymel.core.parent( lattice, latticeBase, mtxObject )
    lattice.t.set( 0,0,0 ), lattice.r.set( 0,0,0 ), lattice.s.set( 1,1,1 )
    latticeBase.t.set( 0,0,0 ), latticeBase.r.set( 0,0,0 ), latticeBase.s.set( 1,1,1 )
    
    mtxObjectSize = mtxObject.sx.get() + mtxObject.sy.get() + mtxObject.sz.get()
    minSize = mtxObjectSize / 20.0
    mtxObject.sx.set( max( [minSize,mtxObject.sx.get()] ) )
    mtxObject.sy.set( max( [minSize,mtxObject.sy.get()] ) )
    mtxObject.sz.set( max( [minSize,mtxObject.sz.get()] ) )
    mtxObject.v.set( 0 )

    mainCtl = sgCmds.makeController( sgModel.Controller.cubePoints, 1, makeParent=1 );sgCmds.setIndexColor( mainCtl, 22 )
    pymel.core.xform( mainCtl, ws=1, matrix=mtxObject.wm.get() )

    sgCmds.constrain_all( mainCtl, mtxObject )

    dtCtlBase = pymel.core.createNode( 'transform' )
    sgCmds.constrain_parent( mainCtl, dtCtlBase )

    pointers = []
    for i in range( numController ):
        position = float(i)/(numController-1) - 0.5
        pointer = pymel.core.createNode( 'transform' )
        pointer.setParent( mainCtl )
        sgCmds.setTransformDefault( pointer )
        pointer.ty.set( position )
        pointers.append( pointer )
        sgCmds.constrain_scale( dtCtlBase, pointer )
    
    conditionNode = pymel.core.createNode( 'condition' )
    conditionNode.op.set( 4 )
    mtxObject.sx >> conditionNode.firstTerm
    mtxObject.sz >> conditionNode.secondTerm
    mtxObject.sx >> conditionNode.colorIfTrueR
    mtxObject.sz >> conditionNode.colorIfFalseR
    
    joints = []
    bindPres = []
    planeCtls = []
    
    beforeParent = dtCtlBase
    for pointer in pointers:
        moveCtl = sgCmds.makeController( sgModel.Controller.movePoints, 1, makeParent=1 );sgCmds.setIndexColor( moveCtl, 20 )
        conditionNode.outColorR >> moveCtl.scaleMult
        
        dcmp = sgCmds.getLocalDecomposeMatrix( pointer.wm, beforeParent.wim )
        planeCtl = sgCmds.makeController( sgModel.Controller.circlePoints, 0.5, makeParent=1 );sgCmds.setIndexColor( planeCtl, 18 )
        moveCtl.getParent().setParent( planeCtl )
        ctlShape = planeCtl.getShape()
        pPlaneCtl = planeCtl.getParent()
        pPlaneCtl.setParent( beforeParent )
        dcmp.ot >> pPlaneCtl.t
        dcmp.outputRotate >> pPlaneCtl.r
        mainCtl.sx >> ctlShape.shape_sx
        mainCtl.sy >> ctlShape.shape_sy
        mainCtl.sz >> ctlShape.shape_sz
        
        multSxMinus = pymel.core.createNode( 'multDoubleLinear' )
        multSxPlus = pymel.core.createNode( 'multDoubleLinear' )
        multSzMinus = pymel.core.createNode( 'multDoubleLinear' )
        multSzPlus = pymel.core.createNode( 'multDoubleLinear' )
        
        mainCtl.sx >> multSxMinus.input1; multSxMinus.input2.set( -0.5 )
        mainCtl.sx >> multSxPlus.input1; multSxPlus.input2.set( 0.5 )
        mainCtl.sz >> multSzMinus.input1; multSzMinus.input2.set( -0.5 )
        mainCtl.sz >> multSzMinus.input1; multSzMinus.input2.set( 0.5 )
        
        for i, position in [ (0,[multSxMinus,multSzMinus]), (1,[multSxMinus,multSzPlus]), 
                             (2,[multSxPlus,multSzMinus]), (3,[multSxPlus,multSzPlus]) ]:
            pymel.core.select( moveCtl )
            joint   = pymel.core.joint(); joint.drawStyle.set( 2 )
            bindPre = pymel.core.createNode( 'transform' )
            bindPre.setParent( pointer )
            sgCmds.setTransformDefault( bindPre )
            joints.append( joint )
            bindPres.append( bindPre )
            position[0].output >> joint.tx; position[1].output >> joint.tz
            position[0].output >> bindPre.tx; position[1].output >> bindPre.tz
        planeCtls.append( planeCtl )
        beforeParent = pointer
    
    for i in range( len( planeCtls )-1 ):
        planeCtls[i+1].getParent().setParent( planeCtls[i] )

    skinCluster = pymel.core.skinCluster( joints, lattice, dr=1000 )
    for i in range( len( joints ) ):
        sgCmds.setBindPreMatrix( joints[i], bindPres[i] )
    lattice.wm >> skinCluster.geomMatrix

    allGrp = pymel.core.createNode( 'transform' )
    pymel.core.parent( mainCtl.getParent(), mtxObject, dtCtlBase, allGrp )

    return mainCtl
    

def createPointConstrainedCam( targetObject ):
    
    targetObject = pymel.core.ls( targetObject )[0].name()
    
    cam = sgCmds.getCurrentCam().name()
    panel = cmds.getPanel( wf=1 )
    if not cam:
        cam = 'persp'
    duCam = cmds.duplicate( cam )[0]
    
    camGrp = cmds.group( em=1 )
    cmds.pointConstraint( targetObject, camGrp )
    
    cmds.parent( duCam, camGrp )
    
    if cmds.getPanel( to=panel ):
        print 'lookThroughModelPanel %s %s;' %( duCam, panel )
        mel.eval( 'lookThroughModelPanel %s %s;' %( duCam, panel ) )




class FkSet_type1:
    
    cubePoints = [[0.50000,0.50000,0.50000],
            [0.50000,-0.50000,0.50000],
            [-0.50000,-0.50000,0.50000],
            [-0.50000,0.50000,0.50000],
            [0.50000,0.50000,0.50000],
            [0.50000,0.50000,-0.50000],
            [-0.50000,0.50000,-0.50000],
            [-0.50000,0.50000,0.50000],
            [-0.50000,-0.50000,0.50000],
            [-0.50000,-0.50000,-0.50000],
            [-0.50000,0.50000,-0.50000],
            [0.50000,0.50000,-0.50000],
            [0.50000,-0.50000,-0.50000],
            [-0.50000,-0.50000,-0.50000],
            [-0.50000,-0.50000,0.50000],
            [0.50000,-0.50000,0.50000],
            [0.50000,-0.50000,-0.50000]]
    
    crossPinPoints = [[0.0, 0.0, 0.0],
            [0.0, 2.20212737358e-16, 0.991750001907],
            [0.0902799963951, 2.25583985035e-16, 1.01593995094],
            [0.156369999051, 2.40258936725e-16, 1.08203005791],
            [0.18055999279, 2.60307333084e-16, 1.17232000828],
            [0.156369999051, 2.80353505981e-16, 1.26259994507],
            [0.0902799963951, 2.95028457671e-16, 1.32869005203],
            [0.0, 3.00399705348e-16, 1.35288000107],
            [-0.0902799963951, 2.95028457671e-16, 1.32869005203],
            [-0.156369999051, 2.80353505981e-16, 1.26259994507],
            [-0.18055999279, 2.60307333084e-16, 1.17232000828],
            [-0.156369999051, 2.40258936725e-16, 1.08203005791],
            [-0.0902799963951, 2.25583985035e-16, 1.01593995094],
            [0.0, 2.20212737358e-16, 0.991750001907],
            [0.0, 0.0, 0.0],
            [-0.991750001907, 2.20212737358e-16, 7.70744607222e-16],
            [-1.01593995094, 2.25583985035e-16, 0.0902799963951],
            [-1.08203005791, 2.40258936725e-16, 0.156369999051],
            [-1.17232000828, 2.60307333084e-16, 0.18055999279],
            [-1.26259994507, 2.80353505981e-16, 0.156369999051],
            [-1.32869005203, 2.95028457671e-16, 0.0902799963951],
            [-1.35288000107, 3.00399705348e-16, 1.05139891578e-15],
            [-1.32869005203, 2.95028457671e-16, -0.0902799963951],
            [-1.26259994507, 2.80353505981e-16, -0.156369999051],
            [-1.17232000828, 2.60307333084e-16, -0.18055999279],
            [-1.08203005791, 2.40258936725e-16, -0.156369999051],
            [-1.01593995094, 2.25583985035e-16, -0.0902799963951],
            [-0.991750001907, 2.20212737358e-16, 7.70744607222e-16],
            [0.0, 0.0, 0.0],
            [5.61879782017e-16, 2.20212737358e-16, -0.991750001907],
            [-0.0902799963951, 2.25583985035e-16, -1.01593995094],
            [-0.156369999051, 2.40258936725e-16, -1.08203005791],
            [-0.18055999279, 2.60307333084e-16, -1.17232000828],
            [-0.156369999051, 2.80353505981e-16, -1.26259994507],
            [-0.0902799963951, 2.95028457671e-16, -1.32869005203],
            [7.66479372817e-16, 3.00399705348e-16, -1.35288000107],
            [0.0902799963951, 2.95028457671e-16, -1.32869005203],
            [0.156369999051, 2.80353505981e-16, -1.26259994507],
            [0.18055999279, 2.60307333084e-16, -1.17232000828],
            [0.156369999051, 2.40258936725e-16, -1.08203005791],
            [0.0902799963951, 2.25583985035e-16, -1.01593995094],
            [5.61879782017e-16, 2.20212737358e-16, -0.991750001907],
            [0.0, 0.0, 0.0],
            [0.991750001907, 2.20212737358e-16, 2.20212737358e-16],
            [1.01593995094, 2.25583985035e-16, -0.0902799963951],
            [1.08203005791, 2.40258936725e-16, -0.156369999051],
            [1.17232000828, 2.60307333084e-16, -0.18055999279],
            [1.26259994507, 2.80353505981e-16, -0.156369999051],
            [1.32869005203, 2.95028457671e-16, -0.0902799963951],
            [1.35288000107, 3.00399705348e-16, 3.00399705348e-16],
            [1.32869005203, 2.95028457671e-16, 0.0902799963951],
            [1.26259994507, 2.80353505981e-16, 0.156369999051],
            [1.17232000828, 2.60307333084e-16, 0.18055999279],
            [1.08203005791, 2.40258936725e-16, 0.156369999051],
            [1.01593995094, 2.25583985035e-16, 0.0902799963951],
            [0.991750001907, 2.20212737358e-16, 2.20212737358e-16],
            [0.0, 0.0, 0.0]]
    
    
    switchPoints = [[0.60013,0.24369,0.00000],
            [0.60013,0.48737,0.00000],
            [1.00023,0.00001,0.00000],
            [0.60013,-0.48737,0.00000],
            [0.60013,-0.24368,0.00000],
            [-0.60011,-0.24368,0.00000],
            [-0.60011,-0.48737,0.00000],
            [-1.00023,0.00001,0.00000],
            [-0.60011,0.48737,0.00000],
            [-0.60011,0.24369,0.00000],
            [0.60013,0.24369,0.00000],
            [0.60013,0.24369,0.00000]]
    
    
    @staticmethod
    def getMObject( inputTarget ):
        target = pymel.core.ls( inputTarget )[0]
        mObject = OpenMaya.MObject()
        selList = OpenMaya.MSelectionList()
        selList.add( target.name() )
        selList.getDependNode( 0, mObject )
        return mObject

    
    
    @staticmethod
    def makeParent( inputSel, **options ):
    
        sel = pymel.core.ls( inputSel )[0]
        if not options.has_key( 'n' ) and not options.has_key( 'name' ):
            options.update( {'n':'P'+ sel.nodeName()} )
        selP = sel.getParent()
        transform = pymel.core.createNode( 'transform', **options )
        if selP: pymel.core.parent( transform, selP )
        pymel.core.xform( transform, ws=1, matrix= sel.wm.get() )
        pymel.core.parent( sel, transform )
        pymel.core.xform( sel, os=1, matrix= [1,0,0,0, 0,1,0,0, 0,0,1,0 ,0,0,0,1] )
        return transform
    
    
    @staticmethod
    def getIndexColor( inputDagNode ):
    
        dagNode = pymel.core.ls( inputDagNode )[0]
        return dagNode.overrideColor.get()
    


    @staticmethod
    def setIndexColor( inputDagNode, index ):
        
        dagNode = pymel.core.ls( inputDagNode )[0]
        dagNode.overrideEnabled.set( 1 )
        dagNode.overrideColor.set( index )
        
        
    
    @staticmethod
    def copyShapeToTransform( inputShape, inputTransform ):
    
        shape = pymel.core.ls( inputShape )[0]
        transform = pymel.core.ls( inputTransform )[0]
        
        tempTr = pymel.core.createNode( 'transform' )
        oTarget = FkSet_type1.getMObject( tempTr )
        
        if shape.type() == 'mesh':
            oMesh = FkSet_type1.getMObject( shape )
            fnMesh = OpenMaya.MFnMesh( oMesh )
            fnMesh.copy( oMesh, oTarget )
        elif shape.type() == 'nurbsCurve':
            oCurve = FkSet_type1.getMObject( shape )
            fnCurve = OpenMaya.MFnNurbsCurve( oCurve )
            fnCurve.copy( oCurve, oTarget )
        elif shape.type() == 'nurbsSurface':
            oSurface = FkSet_type1.getMObject( shape )
            fnSurface = OpenMaya.MFnNurbsSurface( oSurface )
            fnSurface.copy( oSurface, oTarget )
        else:
            duShapeTr = pymel.core.duplicate( shape.getParent() )[0]
            pymel.core.parent( duShapeTr.getShape(), transform, add=1, shape=1 )
            pymel.core.delete( duShapeTr )
        
        if tempTr.getShape():
            FkSet_type1.setIndexColor( tempTr.getShape(), FkSet_type1.getIndexColor( shape ) )
            pymel.core.parent( tempTr.getShape(), transform, shape=1, add=1 )
        pymel.core.delete( tempTr )
        
    
    
    @staticmethod
    def addIOShape( inputShape ):
    
        shape = pymel.core.ls( inputShape )[0]
        
        if shape.type() == 'transform':
            targetShape = shape.getShape()
        else:
            targetShape = shape
        
        targetTr    = targetShape.getParent()
        newShapeTr = pymel.core.createNode( 'transform' )
        FkSet_type1.copyShapeToTransform( targetShape, newShapeTr )
        ioShape = newShapeTr.getShape()
        ioShape.attr( 'io' ).set( 1 )
        pymel.core.parent( ioShape, targetTr, add=1, shape=1 )
        pymel.core.delete( newShapeTr )
        ioShape = targetTr.listRelatives( s=1 )[-1]
        return ioShape
    
    
    @staticmethod
    def listToMatrix( mtxList ):
        if type( mtxList ) == OpenMaya.MMatrix:
            return mtxList
        matrix = OpenMaya.MMatrix()
        if type( mtxList ) == list:
            resultMtxList = mtxList
        else:
            resultMtxList = []
            for i in range( 4 ):
                for j in range( 4 ):
                    resultMtxList.append( mtxList[i][j] )
        
        OpenMaya.MScriptUtil.createMatrixFromList( resultMtxList, matrix )
        return matrix
    
    
    @staticmethod
    def getBlendTwoMatrix( inputMtx1, inputMtx2 ):
    
        mtx1 = FkSet_type1.listToMatrix( inputMtx1 )
        mtx2 = FkSet_type1.listToMatrix( inputMtx2 )
        
        return (mtx1 + mtx2) * 0.5


    @staticmethod
    def getRotateFromMatrix( mtxValue ):
    
        trMtx = OpenMaya.MTransformationMatrix( mtxValue )
        rotVector = trMtx.eulerRotation().asVector()
        
        return [math.degrees(rotVector.x), math.degrees(rotVector.y), math.degrees(rotVector.z)]
    
    
    
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


    
    @staticmethod
    def blendTwoMatrixConnect( inputFirst, inputSecond, inputThird, **options ):
    
        connectTrans = False
        connectRotate = False
        connectScale = False
        connectShear = False
        
        if options.has_key( 'ct' ):
            connectTrans = options['ct']
        if options.has_key( 'cr' ):
            connectRotate = options['cr']
        if options.has_key( 'cs' ):
            connectScale = options['cs']
        if options.has_key( 'csh' ):
            connectShear = options['csh']
        
        first  = pymel.core.ls( inputFirst )[0]
        second = pymel.core.ls( inputSecond )[0]
        third  = pymel.core.ls( inputThird )[0]
        
        FkSet_type1.addAttr( third, ln='blend', min=0, max=1, k=1, dv=0.5 )
        
        if options.has_key( 'local' ):
            wtAddMtx = pymel.core.createNode( 'wtAddMatrix' )
            dcmp = pymel.core.createNode( 'decomposeMatrix' )
            revNode = pymel.core.createNode( 'reverse' )
            third.blend >> revNode.inputX
            first.m >> wtAddMtx.i[0].m
            second.m >> wtAddMtx.i[1].m
            revNode.outputX >> wtAddMtx.i[0].w
            third.blend >> wtAddMtx.i[1].w
            wtAddMtx.matrixSum >> dcmp.imat
        else:
            wtAddMtx = pymel.core.createNode( 'wtAddMatrix' )
            multMtx = pymel.core.createNode( 'multMatrix' )
            dcmp = pymel.core.createNode( 'decomposeMatrix' )
            revNode = pymel.core.createNode( 'reverse' )
            third.blend >> revNode.inputX
            
            first.wm >> wtAddMtx.i[0].m
            second.wm >> wtAddMtx.i[1].m
            revNode.outputX >> wtAddMtx.i[0].w
            third.blend >> wtAddMtx.i[1].w
        
            wtAddMtx.matrixSum >> multMtx.i[0]
            third.pim >> multMtx.i[1]
        
            multMtx.matrixSum >> dcmp.imat
        
        if connectTrans:
            dcmp.ot >> third.t
        if connectRotate:
            dcmp.outputRotate >> third.r
        if connectScale:
            dcmp.outputScale >> third.s
        if connectShear:
            dcmp.outputShear >> third.sh



    @staticmethod
    def makeController( pointList, defaultScaleMult = 1, **options ):
        
        import copy
        newPointList = copy.deepcopy( pointList )
        
        options.update( {'p':newPointList, 'd':1} )
        
        typ = 'transform'
        if options.has_key( 'typ' ):
            typ = options.pop( 'typ' )
        
        mp = False
        if options.has_key( 'makeParent' ):
            mp = options.pop('makeParent')
        
        colorIndex = -1
        if options.has_key( 'colorIndex' ):
            colorIndex = options.pop('colorIndex')
        
        crv = pymel.core.curve( **options )
        crvShape = crv.getShape()
        
        if options.has_key( 'n' ):
            name = options['n']
        elif options.has_key( 'name' ):
            name = options['name']
        else:
            name = None
        
        jnt = pymel.core.ls( cmds.createNode( typ ) )[0]
        pJnt = None
        
        if mp:
            pJnt = pymel.core.ls( FkSet_type1.makeParent( jnt ) )[0]
        
        if name:
            jnt.rename( name )
            if pJnt:
                pJnt.rename( 'P' + name )
    
        pymel.core.parent( crvShape, jnt, add=1, shape=1 )
        pymel.core.delete( crv )
        crvShape = jnt.getShape()
        
        ioShape = FkSet_type1.addIOShape( jnt )
        ioShape = pymel.core.ls( ioShape )[0]
        
        crvShape.addAttr( 'shape_tx', dv=0 ); jnt.shape_tx.set( e=1, cb=1 )
        crvShape.addAttr( 'shape_ty', dv=0); jnt.shape_ty.set( e=1, cb=1 )
        crvShape.addAttr( 'shape_tz', dv=0); jnt.shape_tz.set( e=1, cb=1 )
        crvShape.addAttr( 'shape_rx', dv=0, at='doubleAngle' ); jnt.shape_rx.set( e=1, cb=1 )
        crvShape.addAttr( 'shape_ry', dv=0, at='doubleAngle' ); jnt.shape_ry.set( e=1, cb=1 )
        crvShape.addAttr( 'shape_rz', dv=0, at='doubleAngle' ); jnt.shape_rz.set( e=1, cb=1 )
        crvShape.addAttr( 'shape_sx', dv=1 ); jnt.shape_sx.set( e=1, cb=1 )
        crvShape.addAttr( 'shape_sy', dv=1 ); jnt.shape_sy.set( e=1, cb=1 )
        crvShape.addAttr( 'shape_sz', dv=1 ); jnt.shape_sz.set( e=1, cb=1 )
        crvShape.addAttr( 'scaleMult', dv=defaultScaleMult, min=0 ); jnt.scaleMult.set( e=1, cb=1 )
        composeMatrix = pymel.core.createNode( 'composeMatrix' )
        composeMatrix2 = pymel.core.createNode( 'composeMatrix' )
        multMatrix = pymel.core.createNode( 'multMatrix' )
        composeMatrix.outputMatrix >> multMatrix.i[0]
        composeMatrix2.outputMatrix >> multMatrix.i[1]
        crvShape.shape_tx >> composeMatrix.inputTranslateX
        crvShape.shape_ty >> composeMatrix.inputTranslateY
        crvShape.shape_tz >> composeMatrix.inputTranslateZ
        crvShape.shape_rx >> composeMatrix.inputRotateX
        crvShape.shape_ry >> composeMatrix.inputRotateY
        crvShape.shape_rz >> composeMatrix.inputRotateZ
        crvShape.shape_sx >> composeMatrix.inputScaleX
        crvShape.shape_sy >> composeMatrix.inputScaleY
        crvShape.shape_sz >> composeMatrix.inputScaleZ
        crvShape.scaleMult >> composeMatrix2.inputScaleX
        crvShape.scaleMult >> composeMatrix2.inputScaleY
        crvShape.scaleMult >> composeMatrix2.inputScaleZ
        trGeo = pymel.core.createNode( 'transformGeometry' )
        try:jnt.attr( 'radius' ).set( 0 )
        except:pass
        
        ioShape.local >> trGeo.inputGeometry
        multMatrix.matrixSum >> trGeo.transform
        
        trGeo.outputGeometry >> crvShape.create
        
        if colorIndex != -1:
            shape = jnt.getShape().name()
            cmds.setAttr( shape + '.overrideEnabled', 1 )
            cmds.setAttr( shape + '.overrideColor', colorIndex )
    
        return jnt
    
    
    @staticmethod
    def constrain( *inputs, **options ):
    
        def getOptionValue( keyName, returnValue, **options ):
            if options.has_key( keyName ):
                returnValue = options[ keyName ]
            return returnValue
        
        def createLocalMatrix( matrixAttr, inverseMatrixAttr ):
            matrixAttr = pymel.core.ls( matrixAttr )[0]
            inverseMatrixAttr = pymel.core.ls( inverseMatrixAttr )[0]
            multMatrixNode = pymel.core.createNode( 'multMatrix' )
            matrixAttr >> multMatrixNode.i[0]
            inverseMatrixAttr >> multMatrixNode.i[1]
            return multMatrixNode
    
        def getDecomposeMatrix( mtxAttr ):
            dcmp = pymel.core.createNode( 'decomposeMatrix' )
            mtxAttr >> dcmp.imat
            return dcmp
    
        srcs   = inputs[:-1]
        target = inputs[-1]
        
        ct = False
        cr = False
        cs = False
        csh = False
        
        ct = getOptionValue( 'ct', ct, **options )
        cr = getOptionValue( 'cr', cr, **options )
        cs = getOptionValue( 'cs', cs, **options )
        csh = getOptionValue( 'csh', csh, **options )
        
        if len( srcs ) == 1:
            mm = createLocalMatrix( srcs[0].wm, target.pim )
        else:
            addNode = pymel.core.createNode( 'plusMinusAverage' )
            conditionNode = pymel.core.createNode( 'condition' )
            addNode.output1D >> conditionNode.firstTerm
            addNode.output1D >> conditionNode.colorIfFalseR
            conditionNode.colorIfTrueR.set( 1 )
            
            wtAddMtx = pymel.core.createNode( 'wtAddMatrix' )
            mm = createLocalMatrix( wtAddMtx.matrixSum, target.pim )
            
            for i in range( len( srcs ) ):
                eachMM = pymel.core.createNode( 'multMatrix' )
                srcs[i].wm >> eachMM.i[0]
                FkSet_type1.addAttr( target, ln='blend_%d' % i, k=1, min=0, dv=1 )
                blendAttr = target.attr( 'blend_%d' % i )
                blendAttr >> addNode.input1D[i]
                divNode = pymel.core.createNode( 'multiplyDivide' ); divNode.op.set( 2 )
                blendAttr >> divNode.input1X
                conditionNode.outColorR >> divNode.input2X
                
                eachMM.o >> wtAddMtx.i[i].m
                divNode.outputX >> wtAddMtx.i[i].w
        resultDcmp = getDecomposeMatrix( mm.o )
        
        if ct  : resultDcmp.ot >> target.t
        if cr  : resultDcmp.outputRotate >> target.r
        if cs  : resultDcmp.os >> target.s
        if csh : resultDcmp.osh >> target.sh
    
    
    @staticmethod
    def lookAtConnect( lookTarget, baseTarget, rotTarget ):
        
        FkSet_type1.constrain( baseTarget, rotTarget, ct=1, cs=1 )
        mm1 = pymel.core.createNode( 'multMatrix' )
        dcmp1 = pymel.core.createNode( 'decomposeMatrix' )
        ab = pymel.core.createNode( 'angleBetween' )
        compose = pymel.core.createNode( 'composeMatrix' )
        mm2 = pymel.core.createNode( 'multMatrix' )
        dcmp2 = pymel.core.createNode( 'decomposeMatrix' )
        lookTarget.wm >> mm1.i[0]
        baseTarget.wim >> mm1.i[1]
        mm1.o >> dcmp1.imat
        ab.vector1.set( 1,0,0 )
        dcmp1.ot >> ab.vector2
        ab.euler >> compose.ir
        compose.outputMatrix >> mm2.i[0]
        baseTarget.wm >> mm2.i[1]
        rotTarget.pim >> mm2.i[2]
        mm2.o >> dcmp2.imat
        dcmp2.outputRotate >> rotTarget.r
    


    def __init__(self, topJoint ):
        
        joints = pymel.core.listRelatives( topJoint, c=1, ad=1, type='joint' )
        joints.append( pymel.core.ls( topJoint )[0] )
        joints.reverse()
        
        self.joints = joints
    
    
    
    def createMainControllers(self, size=1 ):
        
        startCtl = FkSet_type1.makeController( FkSet_type1.crossPinPoints, size, makeParent=1 )
        endCtl   = FkSet_type1.makeController( FkSet_type1.crossPinPoints, size, makeParent=1 )
        pymel.core.xform( startCtl.getParent(),  ws=1,  matrix=self.joints[0].wm.get() )
        pymel.core.xform( endCtl.getParent(),    ws=1,  matrix=self.joints[-1].wm.get() )
        
        interCtls = []
        for joint in self.joints[1:-1]:
            interCtl = FkSet_type1.makeController( FkSet_type1.crossPinPoints, size, makeParent=1 )
            interCtls.append( interCtl )
            pymel.core.xform( interCtl.getParent(), ws=1, matrix= joint.wm.get() )
        
        fkCtls = [ startCtl, endCtl ]
        for interCtl in interCtls:
            fkCtls.insert( -1, interCtl )
        [ fkCtl.getShape().shape_rz.set( 90 ) for fkCtl in fkCtls ]
        
        mainCtlsBase = pymel.core.createNode( 'transform' )
        for i in range( len( fkCtls ) -1 ):
            fkCtls[i+1].getParent().setParent( fkCtls[i] )
        mainCtlsBase.setParent( fkCtls[0].getParent() )
        return fkCtls, mainCtlsBase
    
    

    def createMoveControllers(self, size=1 ):
        
        moveCtls = []
        
        moveCtlGrp = pymel.core.createNode( 'transform' )
        pymel.core.xform( moveCtlGrp, ws=1, matrix= self.joints[0].wm.get() )
        
        for i in range( 1, len( self.joints )-1 ):
            moveCtl = FkSet_type1.makeController( FkSet_type1.switchPoints, size, makeParent=1 )
            moveCtl.getShape().shape_rx.set( 90 )
            moveCtl.getShape().shape_rz.set( 90 )
            moveCtls.append( moveCtl )
            pMoveCtl = moveCtl.getParent()
            offsetMoveCtl = FkSet_type1.makeParent( moveCtl )
            pymel.core.xform( pMoveCtl, ws=1, matrix= self.joints[i].wm.get() )
            blendTwoMatrix = FkSet_type1.getBlendTwoMatrix( self.joints[i].wm.get(), self.joints[-1].wm.get() )
            
            rot = FkSet_type1.getRotateFromMatrix( blendTwoMatrix )
            pymel.core.rotate( offsetMoveCtl, rot[0], rot[1], rot[2], ws=1 )
            pMoveCtl.setParent( moveCtlGrp )
        
        return moveCtls, moveCtlGrp
    
    
    @staticmethod
    def connectMoveToFk( moveCtls, fkCtls ):
        
        for i in range( len( fkCtls )-2 ):
            offsetCtl = moveCtls[i].getParent()
            pCtl = offsetCtl.getParent()
            FkSet_type1.constrain( fkCtls[i+1], pCtl, ct=1, cr=1, cs=1 )
            FkSet_type1.blendTwoMatrixConnect( fkCtls[i], fkCtls[i+1], offsetCtl, cr=1 )
    
    
    @staticmethod
    def connectJointToFk( joints, fkCtls ):
        
        for i in range( len( fkCtls )-1 ):
            FkSet_type1.lookAtConnect( fkCtls[i+1], fkCtls[i], joints[i] )
        
        FkSet_type1.constrain( fkCtls[-1], joints[-1], ct=1, cr=1, cs=1 )

    
    
    @staticmethod
    def createInterPointers( fkCtls, moveCtls, aimAxis='x' ):
        
        startCtl = fkCtls[0]
        endCtl = fkCtls[-1]
        
        def getMultMatrixDcmp( inputMtx1, inputMtx2 ):
            mm = pymel.core.createNode( 'multMatrix' )
            dcmp = pymel.core.createNode( 'decomposeMatrix' )
            inputMtx1 >> mm.i[0]
            inputMtx2 >> mm.i[1]
            mm.o >> dcmp.imat
            return dcmp
        
        def createInterPointer( targetCtl, baseCtl, axis ):
            pointer = pymel.core.createNode( 'transform' ); pointer.dh.set( 1 )
            pointer.setParent( baseCtl )
            pointer.t.set( 0,0,0 ); pointer.r.set( 0,0,0 )
            dcmp = getMultMatrixDcmp( targetCtl.wm, baseCtl.wim )
            FkSet_type1.addAttr( pointer,  ln='mult_inter', dv=0.333333, k=1 )
            distNode = pymel.core.createNode( 'distanceBetween' )
            multDirectionNode = pymel.core.createNode( 'multDoubleLinear' )
            dcmp.ot >> distNode.point1
            distNode.distance >> multDirectionNode.input1
            if dcmp.attr( 'ot' + axis ).get() > 0:
                multDirectionNode.input2.set( 1 )
            else:
                multDirectionNode.input2.set( -1 )
            multNode = pymel.core.createNode( 'multDoubleLinear' )
            multDirectionNode.output >> multNode.input1
            pointer.attr( 'mult_inter' ) >> multNode.input2
            multNode.output >> pointer.attr( 't' + axis )
            return pointer
        
        startPointer = createInterPointer( moveCtls[0], startCtl, aimAxis )
        endPointer   = createInterPointer( moveCtls[-1], endCtl, aimAxis )

        pointers = [ startCtl, startPointer ]
        for i in range( len( moveCtls ) ):
            if i == 0:
                beforeCtl = startCtl
            else:
                beforeCtl = moveCtls[i-1]
            
            if i==len( moveCtls )-1:
                afterCtl = endCtl
            else:
                afterCtl = moveCtls[i+1]
            
            beforePoint = createInterPointer( beforeCtl, moveCtls[i], aimAxis )
            afterPoint  = createInterPointer( afterCtl,  moveCtls[i], aimAxis )
            pointers += [ beforePoint, afterPoint ]
            
        pointers += [endPointer, endCtl]
        
        return pointers
            
    
    @staticmethod
    def createCurveFromPointers( pointers, **options ):
        
        sels = pointers
        for i in range( len( sels ) ):
            sels[i] = pymel.core.ls( sels[i] )[0]
    
        poses = []
        for sel in sels:
            pose = pymel.core.xform( sel, q=1, ws=1, t=1 )[:3]
            poses.append( pose )
        
        if len( pointers ) <= 3:
            options['d']= 2
        curve = pymel.core.ls( cmds.curve( p=poses, **options ) )[0]
        curveShape = curve.getShape()
        
        for i in range( len( sels ) ):
            dcmp = pymel.core.createNode( 'decomposeMatrix' )
            vp   = pymel.core.createNode( 'vectorProduct' ); vp.setAttr( 'op', 4 )
            sels[i].wm >> dcmp.imat
            dcmp.ot >> vp.input1
            curve.wim >> vp.matrix
            vp.output >> curveShape.controlPoints[i]
        
        return curve
                
        
    @staticmethod
    def createWeightedLookAt( lookTarget, rotTarget ):
    
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
        
        def createBlendTwoMatrixNode( inputFirstAttr, inputSecondAttr ):
        
            firstAttr  = pymel.core.ls( inputFirstAttr )[0]
            secondAttr = pymel.core.ls( inputSecondAttr )[0]
            
            wtAddMtx = pymel.core.createNode( 'wtAddMatrix' )
            wtAddMtx.addAttr( 'blend', min=0, max=1, dv=0.5, k=1 )
            
            revNode  = pymel.core.createNode( 'reverse' )
        
            firstAttr >> wtAddMtx.i[0].m
            secondAttr >> wtAddMtx.i[1].m
            
            wtAddMtx.blend >> revNode.inputX
            revNode.outputX >> wtAddMtx.i[0].w
            wtAddMtx.blend >> wtAddMtx.i[1].w
            
            return wtAddMtx
    
        mm = pymel.core.createNode( 'multMatrix' )
        dcmp = pymel.core.createNode( 'decomposeMatrix' )
        angleNode = pymel.core.createNode( 'angleBetween' )
        
        mm.o >> dcmp.imat
        
        lookTarget.wm >> mm.i[0]
        rotTarget.pim >> mm.i[1]
        
        angleNode.vector1.set( dcmp.ot.get() )
        dcmp.ot >> angleNode.vector2
        
        composeOrig = pymel.core.createNode( 'composeMatrix' )
        composeMove = pymel.core.createNode( 'composeMatrix' )
        angleNode.euler >> composeMove.ir
        
        blendMtx = sgCmds.createBlendTwoMatrixNode( composeOrig.outputMatrix, composeMove.outputMatrix )
        addAttr( rotTarget, ln='blend', min=0, max=1, k=1, dv=1 )
        rotTarget.attr( 'blend' ) >> blendMtx.attr( 'blend' )
        
        dcmpBlend = pymel.core.createNode( 'decomposeMatrix' )
        blendMtx.matrixSum >> dcmpBlend.imat
        
        dcmpBlend.outputRotate >> rotTarget.r
     
            
    
    @staticmethod
    def createBend( fkCtls, dvValue=0.5, size=1 ):
        
        def get_bend_mult_attr( bendAttr, ctl ):
            FkSet_type1.addAttr( ctl, ln='bend_mult', k=1,  dv=1 )
            node = pymel.core.createNode( 'multDoubleLinear' )
            bendAttr >> node.input1
            ctl.attr( 'bend_mult' ) >> node.input2
            return node.output
        
        def createMainCtl( lastFkCtl, size=1 ):
            cubeCtl = FkSet_type1.makeController( FkSet_type1.cubePoints, size, makeParent=1 )
            pymel.core.xform( cubeCtl.getParent(), ws=1, matrix= lastFkCtl.wm.get() )
            lockAttrs = ['rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v' ]
            for attr in lockAttrs:
                cubeCtl.attr( attr ).set( lock=1, k=0 )
            return cubeCtl
        
        def createLookAtObject( lookTarget, firstFkCtl ):
            
            def listToMatrix( mtxList ):
                if type( mtxList ) == OpenMaya.MMatrix:
                    return mtxList
                matrix = OpenMaya.MMatrix()
                if type( mtxList ) == list:
                    resultMtxList = mtxList
                else:
                    resultMtxList = []
                    for i in range( 4 ):
                        for j in range( 4 ):
                            resultMtxList.append( mtxList[i][j] )
                
                OpenMaya.MScriptUtil.createMatrixFromList( resultMtxList, matrix )
                return matrix
            
            def getDirectionIndex( inputVector ):
    
                import math
                
                if type( inputVector ) in [ list, tuple ]:
                    normalInput = OpenMaya.MVector(*inputVector).normal()
                else:
                    normalInput = OpenMaya.MVector(inputVector).normal()
                
                xVector = OpenMaya.MVector( 1,0,0 )
                yVector = OpenMaya.MVector( 0,1,0 )
                zVector = OpenMaya.MVector( 0,0,1 )
                
                xdot = xVector * normalInput
                ydot = yVector * normalInput
                zdot = zVector * normalInput
                
                xabs = math.fabs( xdot )
                yabs = math.fabs( ydot )
                zabs = math.fabs( zdot )
                
                dotList = [xdot, ydot, zdot]
                
                dotIndex = 0
                if xabs < yabs:
                    dotIndex = 1
                    if yabs < zabs:
                        dotIndex = 2
                elif xabs < zabs:
                    dotIndex = 2
                    
                if dotList[ dotIndex ] < 0:
                    dotIndex += 3
                
                return dotIndex
            
            def getLookAtAngleNode( inputLookTarget, inputRotTarget, **options ):

                def createLookAtMatrix( lookTarget, rotTarget ):
                    mm = pymel.core.createNode( 'multMatrix' )
                    compose = pymel.core.createNode( 'composeMatrix' )
                    mm2 = pymel.core.createNode( 'multMatrix' )
                    invMtx = pymel.core.createNode( 'inverseMatrix' )
                    
                    lookTarget.wm >> mm.i[0]
                    rotTarget.t >> compose.it
                    compose.outputMatrix >> mm2.i[0]
                    rotTarget.pm >> mm2.i[1]
                    mm2.matrixSum >> invMtx.inputMatrix
                    invMtx.outputMatrix >> mm.i[1]
                    return mm
                
                if options.has_key( 'direction' ) and options['direction']:
                    direction = options['direction']
                else:
                    direction = [1,0,0]
                
                lookTarget = pymel.core.ls( inputLookTarget )[0]
                rotTarget = pymel.core.ls( inputRotTarget )[0]
                
                dcmpLookAt = pymel.core.createNode( 'decomposeMatrix' )
                createLookAtMatrix( lookTarget, rotTarget ).matrixSum >> dcmpLookAt.imat
                
                abnodes = dcmpLookAt.listConnections( type='angleBetween' )
                if not abnodes:
                    node = cmds.createNode( 'angleBetween' )
                    cmds.setAttr( node + ".v1", *direction )
                    cmds.connectAttr( dcmpLookAt + '.ot', node + '.v2' )
                else:
                    node = abnodes[0]
                return node
            
            def lookAtConnect( inputLookTarget, inputRotTarget, **options ):
    
                if options.has_key( 'direction' ) and options['direction']:
                    direction = options['direction']
                else:
                    direction = None
                
                lookTarget = pymel.core.ls( inputLookTarget )[0]
                rotTarget  = pymel.core.ls( inputRotTarget )[0]
                
                if not direction:
                    wim = listToMatrix( rotTarget.wim.get() )
                    pos = OpenMaya.MPoint( *pymel.core.xform( lookTarget, q=1, ws=1, t=1 ) )
                    directionIndex = getDirectionIndex( pos*wim )
                    direction = [[1,0,0], [0,1,0], [0,0,1],[-1,0,0], [0,-1,0], [0,0,-1]][directionIndex]
                
                node = getLookAtAngleNode( lookTarget, rotTarget, direction=direction )
                cmds.connectAttr( node + '.euler', rotTarget + '.r' )

            lookAtObject = pymel.core.createNode( 'transform' )
            lookAtBase = FkSet_type1.makeParent( lookAtObject )
            pymel.core.xform( lookAtBase, ws=1, matrix=firstFkCtl.wm.get() )
            lookAtConnect( lookTarget, lookAtObject )
            lookAtPoint = pymel.core.createNode( 'transform' )
            lookAtPoint.setParent( lookAtObject )
            pymel.core.xform( lookAtPoint, ws=1, matrix=lookTarget.wm.get() )
            return lookAtPoint, lookAtBase
        
        mainCtl = createMainCtl( fkCtls[-1], size )
        FkSet_type1.addAttr( mainCtl, ln='______', at='enum', en='Options:', cb=1 )
        lookAtPoint, lookAtBase = createLookAtObject( mainCtl, fkCtls[0] )
        FkSet_type1.addAttr( mainCtl, ln='bend', k=1, min=0, max=1, dv=dvValue )
        eachWeight = 1.0/( len( fkCtls )-2 )
        bendTransformes = []
        currentParent = fkCtls[0].getParent()
        for i in range( len( fkCtls )-1 ):
            bendTarget = pymel.core.createNode( 'transform', n='bendTr_' + fkCtls[i].nodeName() )
            pBendTarget = FkSet_type1.makeParent( bendTarget )
            pBendTarget.setParent( currentParent )
            pymel.core.xform( pBendTarget, ws=1, matrix=fkCtls[i].wm.get() )
            FkSet_type1.createWeightedLookAt( lookAtPoint, bendTarget )
            bendValue = eachWeight * i
            blAttrNode = pymel.core.createNode( 'blendTwoAttr' )
            blAttrNode.input[0].set( 1 )
            blAttrNode.input[1].set( bendValue )
            mainCtl.attr( 'bend' ) >> blAttrNode.attr( 'ab' )
            blAttrNode.output >> bendTarget.attr( 'blend' )
            fkOffset = FkSet_type1.makeParent( fkCtls[i], n= 'bend_' + fkCtls[i].nodeName() )
            bendTarget.r >> fkOffset.r
            currentParent = bendTarget
            bendTransformes.append( pBendTarget )
        
        return mainCtl.getParent() , lookAtBase, bendTransformes[0]
    
    
    @staticmethod
    def createJointOnCurve( curve, upObjects, numJoints ):
        
        def getClosestParamAtPoint( inputTargetObj, inputCurve ):
            
            def getDagPath( inputTarget ):
                target = pymel.core.ls( inputTarget )[0]
                dagPath = OpenMaya.MDagPath()
                selList = OpenMaya.MSelectionList()
                selList.add( target.name() )
                try:
                    selList.getDagPath( 0, dagPath )
                    return dagPath
                except:
                    return None

            curve = pymel.core.ls( inputCurve )[0]
            if curve.nodeType() == 'transform':
                crvShape = curve.getShape()
            else:crvShape = curve
            
            if type( inputTargetObj ) in [ list, type( OpenMaya.MPoint() ), type( OpenMaya.MVector() ) ]:
                pointTarget = OpenMaya.MPoint( *pymel.core.xform( inputTargetObj, q=1, ws=1, t=1 ) )
            else:
                targetObj = pymel.core.ls( inputTargetObj )[0]
                dagPathTarget = getDagPath( targetObj )
                mtxTarget = dagPathTarget.inclusiveMatrix()
                pointTarget = OpenMaya.MPoint( mtxTarget[3] )
                
            dagPathCurve  = getDagPath( crvShape )
            mtxCurve  = dagPathCurve.inclusiveMatrix()
            pointTarget *= mtxCurve.inverse()
            
            fnCurve = OpenMaya.MFnNurbsCurve( getDagPath( crvShape ) )
            
            util = OpenMaya.MScriptUtil()
            util.createFromDouble( 0.0 )
            ptrDouble = util.asDoublePtr()
            fnCurve.closestPoint( pointTarget, 0, ptrDouble )
            
            paramValue = OpenMaya.MScriptUtil().getDouble( ptrDouble )
            return paramValue
        
        def createBlendTwoMatrixNode( inputFirstAttr, inputSecondAttr ):
    
            firstAttr  = pymel.core.ls( inputFirstAttr )[0]
            secondAttr = pymel.core.ls( inputSecondAttr )[0]
            
            wtAddMtx = pymel.core.createNode( 'wtAddMatrix' )
            wtAddMtx.addAttr( 'blend', min=0, max=1, dv=0.5, k=1 )
            
            revNode  = pymel.core.createNode( 'reverse' )
        
            firstAttr >> wtAddMtx.i[0].m
            secondAttr >> wtAddMtx.i[1].m
            
            wtAddMtx.blend >> revNode.inputX
            revNode.outputX >> wtAddMtx.i[0].w
            wtAddMtx.blend >> wtAddMtx.i[1].w
            return wtAddMtx
        
        jointBases = pymel.core.createNode( 'transform' )
        curveShape = curve.getShape()
        FkSet_type1.constrain( curve, jointBases, ct=1, cr=1, cs=1, csh=1 )
        
        fnCurve = OpenMaya.MFnNurbsCurve( FkSet_type1.getMObject( curveShape ) )
        
        curveLength = fnCurve.length()
        eachParams = []
        eachLength = curveLength / (numJoints-1)
        for i in range( numJoints ):
            eachParam = fnCurve.findParamFromLength( eachLength * i )
            eachParams.append( eachParam )
        
        upCtlsParams = []
        for upCtl in upObjects:
            upCtlsParams.append( getClosestParamAtPoint( upCtl, curve ) )

        for i in range( numJoints ):
            pymel.core.select( jointBases )
            newJoint = pymel.core.joint()
            info = pymel.core.createNode( 'pointOnCurveInfo' )
            curveShape.local >> info.inputCurve
            info.parameter.set( eachParams[i] )
            mm = pymel.core.createNode( 'multMatrix' )
            vp = pymel.core.createNode( 'vectorProduct' )
            vp.op.set( 4 )
            mm.o >> vp.matrix
            curveShape.wm >> mm.i[0]
            newJoint.pim >> mm.i[1]
            info.position >> vp.input1
            vp.output >> newJoint.t
            
            if i == 0:
                upMtxAttr = upObjects[0].wm
                upMtxInvAttr = upObjects[0].wim
            elif i == numJoints-1:
                upMtxAttr = upObjects[-1].wm
                upMtxInvAttr = upObjects[-1].wim
            else:
                for j in range( len(upCtlsParams) ):
                    if eachParams[i] < upCtlsParams[j]:
                        blendValue = (eachParams[i] - upCtlsParams[j-1])/(upCtlsParams[j] - upCtlsParams[j-1])
                        blendTwoMtxNode = createBlendTwoMatrixNode( upObjects[j-1].wm, upObjects[j].wm )
                        blendTwoMtxNode.attr( 'blend' ).set( blendValue )
                        invMtx = pymel.core.createNode( 'inverseMatrix' )
                        blendTwoMtxNode.matrixSum >> invMtx.inputMatrix
                        upMtxAttr = blendTwoMtxNode.matrixSum
                        upMtxInvAttr = invMtx.outputMatrix
                        break
                    else:
                        continue
            
            mm = pymel.core.createNode( 'multMatrix' )
            vp = pymel.core.createNode( 'vectorProduct' )
            vp.op.set( 3 )
            mm.o >> vp.matrix
            curveShape.wm >> mm.i[0]
            upMtxInvAttr >> mm.i[1]
            info.tangent >> vp.input1
            angleNode = pymel.core.createNode( 'angleBetween' )
            angleNode.vector1.set( 1,0,0 )
            vp.output >> angleNode.vector2
            
            compose = pymel.core.createNode( 'composeMatrix' )
            angleNode.euler >> compose.ir
            mm = pymel.core.createNode( 'multMatrix' )
            dcmp = pymel.core.createNode( 'decomposeMatrix' )
            compose.outputMatrix >> mm.i[0]
            upMtxAttr >> mm.i[1]
            curve.wim >> mm.i[2]
            mm.o >> dcmp.imat
            
            dcmp.outputRotate >> newJoint.r
            
        return jointBases
            
            
            
def followTarget( drivenObj, driverObj ):
    
    def getShape( inputTarget ):
    
        target = pymel.core.ls( inputTarget )[0]
        if target.nodeType() == 'transform':
            return target.getShape()
        else:
            return target
    
    
    def setMatrixPreventChildren( target, moveTarget ):
        
        def setPivotZero( target ):
            target.rotatePivot.set( 0,0,0 )
            target.scalePivot.set( 0,0,0 )
            target.rotatePivotTranslate.set( 0,0,0 )
            target.scalePivotTranslate.set( 0,0,0 )
        
        targetChildren = pymel.core.listRelatives( target, c=1, type='transform', f=1 )
        if not targetChildren: targetChildren = []
        poses = []
        for targetChild in targetChildren:
            pose = pymel.core.xform( targetChild, q=1, ws=1, matrix=1 )
            poses.append( pose )
        
        pymel.core.xform( target, ws=1, matrix= cmds.getAttr( moveTarget + '.wm' ) )
        
        for i in range( len( targetChildren ) ):
            pymel.core.xform( targetChildren[i], ws=1, matrix= poses[i] )
        
        setPivotZero( target )
    
    
    
    
    def getConstrainMatrix( inputFirst, inputTarget ):
        first = pymel.core.ls( inputFirst )[0]
        target = pymel.core.ls( inputTarget )[0]
        mm = pymel.core.createNode( 'multMatrix' )
        first.wm >> mm.i[0]
        target.pim >> mm.i[1]
        return mm
        
        
    def getDecomposeMatrix( matrixAttr ):
        
        matrixAttr = pymel.core.ls( matrixAttr )[0]
        cons = matrixAttr.listConnections( s=0, d=1, type='decomposeMatrix' )
        if cons: 
            pymel.core.select( cons[0] )
            return cons[0]
        decomposeMatrix = pymel.core.createNode( 'decomposeMatrix' )
        matrixAttr >> decomposeMatrix.imat
        return decomposeMatrix
    
    
    def constrain_all( first, target ):
        
        mm = getConstrainMatrix( first, target )
        dcmp = getDecomposeMatrix( mm.matrixSum )
        cmds.connectAttr( dcmp + '.ot',  target + '.t', f=1 )
        cmds.connectAttr( dcmp + '.or',  target + '.r', f=1 )
        cmds.connectAttr( dcmp + '.os',  target + '.s', f=1 )
        cmds.connectAttr( dcmp + '.osh',  target + '.sh', f=1 )
    
    
    
    def setGeometryMatrixToTarget( inputGeo, inputMatrixTarget ):
    
        def setPivotZero( target ):
            target.rotatePivot.set( 0,0,0 )
            target.scalePivot.set( 0,0,0 )
            target.rotatePivotTranslate.set( 0,0,0 )
            target.scalePivotTranslate.set( 0,0,0 )
    
        def getIndexColor( inputDagNode ):
            dagNode = pymel.core.ls( inputDagNode )[0]
            return dagNode.overrideColor.get()
        
        
        def setIndexColor( inputDagNode, index ):
            dagNode = pymel.core.ls( inputDagNode )[0]
            dagNode.overrideEnabled.set( 1 )
            dagNode.overrideColor.set( index )
            
        
        def getMObject( inputTarget ):
            target = pymel.core.ls( inputTarget )[0]
            mObject = OpenMaya.MObject()
            selList = OpenMaya.MSelectionList()
            selList.add( target.name() )
            selList.getDependNode( 0, mObject )
            return mObject
    
        def addIOShape( inputShape ):
            shape = pymel.core.ls( inputShape )[0]
            
            if shape.type() == 'transform':
                targetShape = shape.getShape()
            else:
                targetShape = shape
            
            targetTr    = targetShape.getParent()
            newShapeTr = pymel.core.createNode( 'transform' )
            copyShapeToTransform( targetShape, newShapeTr )
            ioShape = newShapeTr.getShape()
            ioShape.attr( 'io' ).set( 1 )
            pymel.core.parent( ioShape, targetTr, add=1, shape=1 )
            pymel.core.delete( newShapeTr )
            ioShape = targetTr.listRelatives( s=1 )[-1]
            return ioShape
        
        def copyShapeToTransform( inputShape, inputTransform ):
        
            shape = pymel.core.ls( inputShape )[0]
            transform = pymel.core.ls( inputTransform )[0]
            
            tempTr = pymel.core.createNode( 'transform' )
            oTarget = getMObject( tempTr )
            
            if shape.type() == 'mesh':
                oMesh = getMObject( shape )
                fnMesh = OpenMaya.MFnMesh( oMesh )
                fnMesh.copy( oMesh, oTarget )
            elif shape.type() == 'nurbsCurve':
                oCurve = getMObject( shape )
                fnCurve = OpenMaya.MFnNurbsCurve( oCurve )
                fnCurve.copy( oCurve, oTarget )
            elif shape.type() == 'nurbsSurface':
                oSurface = getMObject( shape )
                fnSurface = OpenMaya.MFnNurbsSurface( oSurface )
                fnSurface.copy( oSurface, oTarget )
            else:
                duShapeTr = pymel.core.duplicate( shape.getParent() )[0]
                pymel.core.parent( duShapeTr.getShape(), transform, add=1, shape=1 )
                pymel.core.delete( duShapeTr )
            
            if tempTr.getShape():
                setIndexColor( tempTr.getShape(), getIndexColor( shape ) )
                pymel.core.parent( tempTr.getShape(), transform, shape=1, add=1 )
            pymel.core.delete( tempTr )
    
        def listToMatrix( mtxList ):
            if type( mtxList ) == OpenMaya.MMatrix:
                return mtxList
            matrix = OpenMaya.MMatrix()
            if type( mtxList ) == list:
                resultMtxList = mtxList
            else:
                resultMtxList = []
                for i in range( 4 ):
                    for j in range( 4 ):
                        resultMtxList.append( mtxList[i][j] )
            
            OpenMaya.MScriptUtil.createMatrixFromList( resultMtxList, matrix )
            return matrix
        
        
        
        def matrixToList( matrix ):
            if type( matrix ) == list:
                return matrix
            
            mtxList = range( 16 )
            for i in range( 4 ):
                for j in range( 4 ):
                    mtxList[ i * 4 + j ] = matrix( i, j )
            return mtxList
        
        try:
            matrixTarget = pymel.core.ls( inputMatrixTarget )[0]
            targetMatrix = listToMatrix( pymel.core.xform( matrixTarget, q=1, ws=1, matrix=1 ) )
        except:
            targetMatrix = listToMatrix( inputMatrixTarget )
    
        geo = pymel.core.ls( inputGeo )[0]
        geoShapes = geo.listRelatives( s=1 )
        geoMatrix = listToMatrix( pymel.core.xform( geo, q=1, ws=1, matrix=1 ) )
        
        for shape in geoShapes:
            if shape.attr( 'io' ).get():
                pymel.core.delete( shape )
        
        geoShapes = geo.listRelatives( s=1 )
        
        for geoShape in geoShapes:
            if not geoShape.nodeType() in ['nurbsCurve', 'nurbsSurface', 'mesh']: continue
            cmds.select( geoShape.name() )
            cmds.CreateCluster()
            cmds.select( geoShape.name() )
            cmds.DeleteHistory()
            origShape = addIOShape( geoShape )
            
            outputAttr = None
            inputAttr = None
            
            if origShape.type() == 'mesh':
                outputAttr = 'outMesh'
                inputAttr = 'inMesh'
            elif origShape.type() in ['nurbsCurve','nurbsSurface']:
                outputAttr = 'local'
                inputAttr = 'create'
            
            trGeo = pymel.core.createNode( 'transformGeometry' )
            origShape.attr( outputAttr ) >> trGeo.inputGeometry
            trGeo.outputGeometry >> geoShape.attr( inputAttr )
            trGeo.transform.set( matrixToList(geoMatrix * targetMatrix.inverse()), type='matrix' )
            cmds.select( geoShape.name() )
            cmds.DeleteHistory()
        
        pymel.core.xform( geo, ws=1, matrix= matrixToList( targetMatrix ) )
        setPivotZero( geo )
    
    if getShape( drivenObj ):
        cmds.select( drivenObj.name() )
        cmds.DeleteHistory( drivenObj.name() )
        setGeometryMatrixToTarget( drivenObj, driverObj )
    else:
        setMatrixPreventChildren( drivenObj, driverObj )
    constrain_all( driverObj, drivenObj )
            
            
def duplicateMirror( target, h=True ):

    def listToMatrix(mtxList):
        if type(mtxList) == OpenMaya.MMatrix:
            return mtxList
        matrix = OpenMaya.MMatrix()
        if type(mtxList) == list:
            resultMtxList = mtxList
        else:
            resultMtxList = []
            for i in range(4):
                for j in range(4):
                    resultMtxList.append(mtxList[i][j])

        OpenMaya.MScriptUtil.createMatrixFromList(resultMtxList, matrix)
        return matrix

    def matrixToList(matrix):
        if type(matrix) == list:
            return matrix

        mtxList = range(16)
        for i in range(4):
            for j in range(4):
                mtxList[i * 4 + j] = matrix(i, j)
        return mtxList

    def getMirrorMatrix(mtxValue):

        if type(mtxValue) == list:
            mtxList = mtxValue
        else:
            mtxList = matrixToList(mtxValue)

        mtxList[1] *= -1
        mtxList[2] *= -1
        mtxList[5] *= -1
        mtxList[6] *= -1
        mtxList[9] *= -1
        mtxList[10] *= -1
        mtxList[12] *= -1

        return listToMatrix(mtxList)

    def setMirrorTransform(inputSrcTr, inputDstTr):
        srcTr = pymel.core.ls(inputSrcTr)[0]
        dstTr = pymel.core.ls(inputDstTr)[0]

        mirrorMtx = getMirrorMatrix( listToMatrix(srcTr.wm.get()) )

        pymel.core.xform(dstTr, ws=1, matrix=matrixToList(mirrorMtx))

    trTarget = pymel.core.ls( target )[0]
    mirrorTransform = pymel.core.createNode(trTarget.nodeType())
    mirrorTransform.rename( sgBase.getOtherSideStr(trTarget.nodeName()))
    mirrorTransform.dh.set(trTarget.dh.get())
    setMirrorTransform( trTarget, mirrorTransform )

    return mirrorTransform


def duplicateShadingNetwork(node, **options):
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

    options.update({'un': 1})
    try:
        duNodes = pymel.core.duplicate(node, **options)
    except:
        return node
    duNode = duNodes[0]

    origHistory = node.history()
    duHistory = duNode.history()

    for srcAttr, origAttr in disconnectedList:
        srcAttr >> origAttr
        historyIndex = origHistory.index(origAttr.node())
        pymel.core.connectAttr(srcAttr, duHistory[historyIndex] + '.' + origAttr.longName())
    return duNode



def copyRig( inputSource, inputTarget ):

    def getReplaceStringList( sourceName, targetName ):
        srcSplits = sourceName.split( '_' )
        trgSplits = targetName.split( '_' )
        replaceStringList = []
        for i in range( len( srcSplits ) ):
            if srcSplits[i] == trgSplits[i]: continue
            replaceStringList.append( [ '_' + srcSplits[i] + '_', '_' + trgSplits[i] + '_' ] )
        return replaceStringList


    def copyChildren( first, second, replaceStrList ):

        firstChildren = pymel.core.listRelatives( first, c=1, type='transform' )
        secondChildren = [ child for child in pymel.core.listRelatives( second, c=1, type='transform' ) ]
        for firstChild in firstChildren:
            targetChildName = firstChild.nodeName()
            for src, trg in replaceStrList:
                targetChildName = targetChildName.replace( src, trg )
            firstChildChildren = firstChild.listRelatives( c=1, type='transform' )
            if not targetChildName in secondChildren:
                if firstChildChildren : pymel.core.parent( firstChildChildren, w=1 )
                secondChild = pymel.core.duplicate( firstChild, n=targetChildName )[0]
                #print "f : ", firstChild, ', ', secondChild
                if firstChildChildren : pymel.core.parent( firstChildChildren, firstChild )
                secondChild.setParent( second )
                if secondChild.nodeType() == 'joint':
                    try:
                        secondChild.r.set( firstChild.r.get() )
                        secondChild.jo.set( firstChild.jo.get() )
                    except:pass
                pymel.core.xform( secondChild, os=1, matrix= firstChild.m.get() )
                targetChildName = secondChild.name()
            copyChildren( firstChild, targetChildName, replaceStrList)


    def copyConnections( first, second, replaceStrList ):

        def duplicateShadingNetwork(node, replaceStrList ):

            def isDoNotDeleteTarget(node):
                for attr in ['wm', 'expression']:
                    if pymel.core.attributeQuery(attr, node=node, ex=1): return True
                return False

            replacedNode = node.name()
            for src, trg in replaceStrList:
                replacedNode = replacedNode.replace( src, trg )

            if isDoNotDeleteTarget( node ) and pymel.core.objExists( replacedNode ):
                return pymel.core.ls(replacedNode)[0]

            checkNodes = node.history( pdo=1 )
            disconnectedList = []
            for checkNode in checkNodes:
                if isDoNotDeleteTarget(checkNode): continue
                nodeSrcCons = checkNode.listConnections(s=1, d=0, p=1, c=1)
                for origAttr, srcAttr in nodeSrcCons:
                    srcNode = srcAttr.node()
                    if not isDoNotDeleteTarget(srcNode): continue
                    srcAttr // origAttr
                    disconnectedList.append((srcAttr, origAttr))

            duNodes = pymel.core.duplicate(node, un=1)
            duNode = duNodes[0]

            origHistory = node.history( pdo=1 )
            duHistory = duNode.history( pdo=1 )

            for srcAttr, origAttr in disconnectedList:
                srcAttr >> origAttr
                historyIndex = origHistory.index(origAttr.node())
                replacedSrcAttr = srcAttr.name()
                for src, trg in replaceStrList:
                    replacedSrcAttr = replacedSrcAttr.replace( src, trg )
                pymel.core.connectAttr( replacedSrcAttr, duHistory[historyIndex].attr(origAttr.longName()) )
            return duNode

        cons = pymel.core.listConnections( first, s=1, d=0, p=1, c=1 )
        for origCon, srcCon in cons:
            duNode = duplicateShadingNetwork( srcCon.node(), replaceStrList )
            replacedOrigCon = origCon.name()
            for src, trg in replaceStrList:
                replacedOrigCon= replacedOrigCon.replace( src, trg )
            if pymel.core.isConnected( duNode.attr( srcCon.longName() ), replacedOrigCon ): continue
            pymel.core.connectAttr( duNode.attr( srcCon.longName() ), replacedOrigCon, f=1 )

        firstChildren  = cmds.listRelatives( first, c=1, f=1 )
        secondChildren = cmds.listRelatives( second, c=1, f=1 )

        if not firstChildren or not secondChildren: return
        firstChildren.sort()
        secondChildren.sort()
        for i in range( len( firstChildren ) ):
            copyConnections( firstChildren[i], secondChildren[i], replaceStrList )

    sourceName = inputSource if type( inputSource ) in [ unicode, str ] else inputSource.nodeName()
    targetName = inputTarget if type( inputTarget ) in [ unicode, str ] else inputTarget.nodeName()
    replaceStrList = getReplaceStringList( sourceName, targetName )

    copyChildren( sourceName, targetName, replaceStrList )
    copyConnections( sourceName, targetName, replaceStrList )


def mirrorConnect( leftObject, rightObject ):

    sels = pymel.core.ls( sl=1 )

    def rotateConnect( leftObject, rightObject ):
        mm = pymel.core.createNode( 'multMatrix' )
        dcmp = pymel.core.createNode( 'decomposeMatrix' )
        fbf = pymel.core.createNode( 'fourByFourMatrix' )

        leftObject.wm >> mm.i[0]
        fbf.output >> mm.i[1]
        rightObject.pim >> mm.i[2]
        mm.o >> dcmp.imat
        dcmp.outputRotate >> rightObject.r
        fbf.attr('i11').set(-1)
        fbf.attr('i22').set(-1)

    def translateConnect( leftObject, rightObject ):
        mm = pymel.core.createNode('multMatrix')
        dcmp = pymel.core.createNode('decomposeMatrix')
        fbf = pymel.core.createNode('fourByFourMatrix')

        leftObject.wm >> mm.i[0]
        fbf.output >> mm.i[1]
        rightObject.pim >> mm.i[2]
        mm.o >> dcmp.imat
        dcmp.outputTranslate >> rightObject.t
        fbf.attr('i00').set(-1)

    translateConnect(leftObject, rightObject)
    rotateConnect( leftObject, rightObject )
    pymel.core.select( sels )



def addIkScaleAndSlide(ikCtl, ikPointer, ikJntTop, ikBase ):

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

    def createMultMatrix(*matrixAttrList):

        mm = pymel.core.createNode('multMatrix')
        for i in range(len(matrixAttrList)):
            pymel.core.connectAttr(matrixAttrList[i], mm.i[i])
        return mm

    def getDirectionIndex(inputVector):

        import math

        if type(inputVector) in [list, tuple]:
            normalInput = OpenMaya.MVector(*inputVector).normal()
        else:
            normalInput = OpenMaya.MVector(inputVector).normal()

        xVector = OpenMaya.MVector(1, 0, 0)
        yVector = OpenMaya.MVector(0, 1, 0)
        zVector = OpenMaya.MVector(0, 0, 1)

        xdot = xVector * normalInput
        ydot = yVector * normalInput
        zdot = zVector * normalInput

        xabs = math.fabs(xdot)
        yabs = math.fabs(ydot)
        zabs = math.fabs(zdot)

        dotList = [xdot, ydot, zdot]

        dotIndex = 0
        if xabs < yabs:
            dotIndex = 1
            if yabs < zabs:
                dotIndex = 2
        elif xabs < zabs:
            dotIndex = 2

        if dotList[dotIndex] < 0:
            dotIndex += 3

        return dotIndex

    ikPointer = pymel.core.ls( ikPointer )[0]
    ikJntTop  = pymel.core.ls( ikJntTop )[0]
    ikJntGrp  = pymel.core.ls( ikBase )[0]
    ikJntMiddle = ikJntTop.listRelatives( c=1 )[0]
    ikJntEnd  = ikJntMiddle.listRelatives( c=1, type='joint' )[0]
    ikJntEndEffector = ikJntMiddle.listRelatives( c=1, type='ikEffector' )[0]
    ikHandle  = ikJntEndEffector.listConnections(s=0, d=1, type='ikHandle')[0]

    upperCon = ikJntMiddle.tx.listConnections(s=1, d=0, p=1)
    lowerCon = ikJntEnd.tx.listConnections(s=1, d=0, p=1)

    dirIndex = getDirectionIndex(ikJntMiddle.t.get())

    middleAttr = ikJntMiddle.attr(['tx', 'ty', 'tz'][dirIndex % 3] )
    endAttr    = ikJntEnd.attr(['tx', 'ty', 'tz'][dirIndex % 3] )

    if upperCon:
        upperCon = upperCon[0]
    else:
        addDoubleNode = pymel.core.createNode( 'addDoubleLinear' )
        addDoubleNode.input1.set( middleAttr.get() )
        srcCon = middleAttr.listConnections( s=1, d=0, p=1 )
        if srcCon: srcCon[0] >> addDoubleNode.input1
        upperCon = addDoubleNode.output

    if lowerCon:
        lowerCon = lowerCon[0]
    else:
        addDoubleNode = pymel.core.createNode('addDoubleLinear')
        addDoubleNode.input1.set( endAttr.get() )
        srcCon = endAttr.listConnections(s=1, d=0, p=1)
        if srcCon: srcCon[0] >> addDoubleNode.input1
        lowerCon = addDoubleNode.output

    ikCtl = pymel.core.ls( ikCtl )[0]
    addAttr(ikCtl, ln="______", at='enum', en='scaleIk:' )
    addAttr(ikCtl, ln='addScale', min=-1, max=1, k=1)
    addAttr(ikCtl, ln='slideScale', min=-1, max=1, k=1)
    addAttr(ikCtl, ln='stretch', min=0, max=1, k=1)

    powNode = pymel.core.createNode('multiplyDivide'); powNode.setAttr('op', 3)
    addUpper = pymel.core.createNode('addDoubleLinear')
    addLower = pymel.core.createNode('addDoubleLinear')
    lowerReverse = pymel.core.createNode('multDoubleLinear'); lowerReverse.setAttr('input2', -1)

    multUpper = pymel.core.createNode('multDoubleLinear')
    multLower = pymel.core.createNode('multDoubleLinear')

    powNode.input1X.set(2)
    ikCtl.addScale >> powNode.input2X
    powNode.outputX >> addUpper.input1
    powNode.outputX >> addLower.input1
    ikCtl.slideScale >> addUpper.input2
    ikCtl.slideScale >> lowerReverse.input1
    lowerReverse.output >> addLower.input2
    addUpper.output >> multUpper.input2
    addLower.output >> multLower.input2

    upperCon >> multUpper.input1
    lowerCon >> multLower.input1

    multUpper.output >> ikJntMiddle.attr( [ 'tx', 'ty', 'tz'][dirIndex % 3] )
    multLower.output >> ikJntEnd.attr( [ 'tx', 'ty', 'tz'][dirIndex % 3] )

    localMatrix = createMultMatrix(ikPointer.wm, ikJntGrp.wim)
    localDcmp = pymel.core.createNode( 'decomposeMatrix' )
    localMatrix.o >> localDcmp.imat
    distNode = pymel.core.createNode( 'distanceBetween')
    localDcmp.ot >> distNode.point1

    cuUpperAndLowerAdd = pymel.core.createNode('addDoubleLinear')
    cuUpperAndLowerDist = pymel.core.createNode('distanceBetween')
    multUpper.output >> cuUpperAndLowerAdd.input1
    multLower.output >> cuUpperAndLowerAdd.input2
    cuUpperAndLowerAdd.output >> cuUpperAndLowerDist.point1X

    distCondition = pymel.core.createNode('condition')
    distNode.distance >> distCondition.firstTerm
    cuUpperAndLowerDist.distance >> distCondition.secondTerm
    distCondition.op.set(2)

    distRate = pymel.core.createNode('multiplyDivide')
    distRate.op.set(2)
    distNode.distance >> distRate.input1X
    cuUpperAndLowerDist.distance >> distRate.input2X

    stretchedUpper = pymel.core.createNode('multDoubleLinear')
    stretchedLower = pymel.core.createNode('multDoubleLinear')

    multUpper.output >> stretchedUpper.input1
    multLower.output >> stretchedLower.input1
    distRate.outputX >> stretchedUpper.input2
    distRate.outputX >> stretchedLower.input2

    blendNodeUpper = pymel.core.createNode('blendTwoAttr')
    blendNodeLower = pymel.core.createNode('blendTwoAttr')
    ikCtl.stretch >> blendNodeUpper.ab
    ikCtl.stretch >> blendNodeLower.ab

    multUpper.output >> blendNodeUpper.input[0]
    multLower.output >> blendNodeLower.input[0]
    stretchedUpper.output >> blendNodeUpper.input[1]
    stretchedLower.output >> blendNodeLower.input[1]

    blendNodeUpper.output >> distCondition.colorIfTrueR
    blendNodeLower.output >> distCondition.colorIfTrueG
    multUpper.output >> distCondition.colorIfFalseR
    multLower.output >> distCondition.colorIfFalseG

    distCondition.outColorR >> ikJntMiddle.attr( [ 'tx', 'ty', 'tz'][dirIndex%3] )
    distCondition.outColorG >> ikJntEnd.attr( [ 'tx', 'ty', 'tz'][dirIndex%3] )

def addFlexibleControlToCurve(inputTargetCurve):

    def getDagPath(inputTarget):
        target = pymel.core.ls(inputTarget)[0]
        dagPath = OpenMaya.MDagPath()
        selList = OpenMaya.MSelectionList()
        selList.add(target.name())
        try:
            selList.getDagPath(0, dagPath)
            return dagPath
        except:
            return None

    def getMPoint(inputSrc):
        if type(inputSrc) in [type(OpenMaya.MVector()), type(OpenMaya.MPoint())]:
            return OpenMaya.MPoint(inputSrc)
        elif type(inputSrc) == list:
            return OpenMaya.MPoint(*inputSrc)
        return OpenMaya.MPoint(*pymel.core.xform(inputSrc, q=1, ws=1, t=1))


    def getClosestParamAtPoint(inputTargetObj, inputCurve):

        curve = pymel.core.ls(inputCurve)[0]

        if curve.nodeType() == 'transform':
            crvShape = curve.getShape()
        else:
            crvShape = curve

        if type(inputTargetObj) in [list, type(OpenMaya.MPoint()), type(OpenMaya.MVector())]:
            pointTarget = getMPoint(inputTargetObj)
        else:
            targetObj = pymel.core.ls(inputTargetObj)[0]
            dagPathTarget = getDagPath(targetObj)
            mtxTarget = dagPathTarget.inclusiveMatrix()
            pointTarget = OpenMaya.MPoint(mtxTarget[3])

        dagPathCurve = getDagPath(crvShape)
        mtxCurve = dagPathCurve.inclusiveMatrix()
        pointTarget *= mtxCurve.inverse()

        fnCurve = OpenMaya.MFnNurbsCurve(getDagPath(crvShape))

        util = OpenMaya.MScriptUtil()
        util.createFromDouble(0.0)
        ptrDouble = util.asDoublePtr()
        fnCurve.closestPoint(pointTarget, 0, ptrDouble)

        paramValue = OpenMaya.MScriptUtil().getDouble(ptrDouble)
        return paramValue


    def getConstrainMatrix(inputFirst, inputTarget):
        first = pymel.core.ls(inputFirst)[0]
        target = pymel.core.ls(inputTarget)[0]
        mm = pymel.core.createNode('multMatrix')
        first.wm >> mm.i[0]
        target.pim >> mm.i[1]
        return mm


    def getDecomposeMatrix(matrixAttr):

        matrixAttr = pymel.core.ls(matrixAttr)[0]
        cons = matrixAttr.listConnections(s=0, d=1, type='decomposeMatrix')
        if cons:
            pymel.core.select(cons[0])
            return cons[0]
        decomposeMatrix = pymel.core.createNode('decomposeMatrix')
        matrixAttr >> decomposeMatrix.imat
        return decomposeMatrix


    def constrain_parent(first, target):

        mm = getConstrainMatrix(first, target)
        dcmp = getDecomposeMatrix(mm.matrixSum)
        cmds.connectAttr(dcmp + '.ot', target + '.t', f=1)
        cmds.connectAttr(dcmp + '.or', target + '.r', f=1)

    def getDirectionIndex(inputVector):

        import math

        if type(inputVector) in [list, tuple]:
            normalInput = OpenMaya.MVector(*inputVector).normal()
        else:
            normalInput = OpenMaya.MVector(inputVector).normal()

        xVector = OpenMaya.MVector(1, 0, 0)
        yVector = OpenMaya.MVector(0, 1, 0)
        zVector = OpenMaya.MVector(0, 0, 1)

        xdot = xVector * normalInput
        ydot = yVector * normalInput
        zdot = zVector * normalInput

        xabs = math.fabs(xdot)
        yabs = math.fabs(ydot)
        zabs = math.fabs(zdot)

        dotList = [xdot, ydot, zdot]

        dotIndex = 0
        if xabs < yabs:
            dotIndex = 1
            if yabs < zabs:
                dotIndex = 2
        elif xabs < zabs:
            dotIndex = 2

        if dotList[dotIndex] < 0:
            dotIndex += 3

        return dotIndex


    targetCurve = pymel.core.ls(inputTargetCurve)[0]
    targetCurveShape = targetCurve.getShape()
    curveBase = targetCurve.getParent()

    blBase = None
    for parent in curveBase.getAllParents():
        if parent.nodeType() == 'transform':
            blBase = parent
            break
    if not blBase: return None


    point2Con = targetCurveShape.controlPoints[1].listConnections(s=1, d=0, p=1)

    lookAtObject = pymel.core.createNode('transform', n='lookAtObject')
    pymel.core.parent(lookAtObject, curveBase)
    lookAtObject.t.set(0, 0, 0)
    angleNode = pymel.core.createNode('angleBetween')

    ctl, circleNode = pymel.core.circle()
    ctlP = pymel.core.createNode('transform')
    ctlP.setParent(blBase)
    ctl.setParent(ctlP)
    ctl.t.set(0, 0, 0);
    ctl.r.set(0, 0, 0)
    constrain_parent(lookAtObject, ctlP)

    pointNode = pymel.core.createNode('multiplyDivide')
    baseVector = [[1,0,0],[0,1,0],[0,0,1],[-1,0,0],[0,-1,0],[0,0,-1]][ getDirectionIndex(point2Con[0].get()) ]
    angleNode.vector1.set(baseVector)
    point2Con[0] >> pointNode.input1
    point2Con[0] >> angleNode.vector2
    pointNode.input2.set(0.5, 0.5, 0.5)
    pointNode.output >> lookAtObject.t
    angleNode.euler >> lookAtObject.r

    circleNode.normal.set(baseVector)

    curvePoint1Mult = pymel.core.createNode('multDoubleLinear')
    curvePoint2Mult = pymel.core.createNode('multDoubleLinear')
    curvePoint1Compose = pymel.core.createNode('composeMatrix')
    curvePoint2Compose = pymel.core.createNode('composeMatrix')
    point2Con[0].getChildren()[0] >> curvePoint1Mult.input1
    point2Con[0].getChildren()[0] >> curvePoint2Mult.input1
    curvePoint1Mult.input2.set(-.3)
    curvePoint2Mult.input2.set(0.3)
    curvePoint1Mult.output >> curvePoint1Compose.itx
    curvePoint2Mult.output >> curvePoint2Compose.itx

    mmPoint1 = pymel.core.createNode('multMatrix')
    dcmpPoint1 = pymel.core.createNode('decomposeMatrix')
    curvePoint1Compose.outputMatrix >> mmPoint1.i[0]
    ctl.wm >> mmPoint1.i[1]
    targetCurve.getParent().wim >> mmPoint1.i[2]
    mmPoint1.o >> dcmpPoint1.imat
    mmPoint2 = pymel.core.createNode('multMatrix')
    dcmpPoint2 = pymel.core.createNode('decomposeMatrix')
    curvePoint2Compose.outputMatrix >> mmPoint2.i[0]
    ctl.wm >> mmPoint2.i[1]
    lookAtObject.getParent().wim >> mmPoint2.i[2]
    mmPoint2.o >> dcmpPoint2.imat

    pointAttrs = [None, dcmpPoint1.ot, dcmpPoint2.ot, point2Con[0]]

    newCurve = pymel.core.curve(p=[[0, 0, 0] for i in range(4)], d=3)
    newCurveShape = newCurve.getShape()
    for i in range(4):
        if not pointAttrs[i]: continue
        pointAttrs[i] >> newCurveShape.controlPoints[i]

    pymel.core.parent(newCurve, curveBase)
    newCurve.t.set(0, 0, 0)
    newCurve.r.set(0, 0, 0)

    for origCon, destCon in targetCurveShape.listConnections(s=0, d=1, p=1, c=1):
        attrName = origCon.attrName()
        newCurve.attr(attrName) >> destCon

    selShape = newCurveShape
    curveInfo = selShape.listConnections(s=0, d=1, type='curveInfo')[0]
    multNode = curveInfo.listConnections(d=1, s=0, type='multDoubleLinear')[0]
    joints = multNode.listConnections(s=0, d=1, type='joint')
    maxValue = selShape.maxValue.get()

    pointOnCurve = pymel.core.createNode('pointOnCurveInfo')
    selShape.local >> pointOnCurve.inputCurve
    jntAndCurveInfos = [[0.0, None, pointOnCurve]]

    for jnt in joints:
        paramValue = getClosestParamAtPoint(jnt, selShape.getParent()) / maxValue
        pointOnCurve = pymel.core.createNode('pointOnCurveInfo')
        selShape.local >> pointOnCurve.inputCurve
        pointOnCurve.parameter.set(paramValue)
        jntAndCurveInfos.append([paramValue, jnt, pointOnCurve])
    jntAndCurveInfos.sort()
    for i in range(1, len(jntAndCurveInfos)):
        beforeCurveInfo = jntAndCurveInfos[i - 1][2]
        param, jnt, curveInfo = jntAndCurveInfos[i]
        distNode = pymel.core.createNode('distanceBetween')
        beforeCurveInfo.position >> distNode.point1
        curveInfo.position >> distNode.point2
        eachMultNode = pymel.core.createNode('multDoubleLinear')
        eachMultNode.input2.set(1)
        distNode.distance >> eachMultNode.input1
        eachMultNode.output >> jnt.tx
        if multNode.input2.get() < 0:
            eachMultNode.input2.set(-1)
        eachMultNode.output >> jnt.tx

    pymel.core.delete(targetCurve)



def addBlendBySkinedWeight( skinedMesh, targetMesh ):

    def createBlendShape( skinedMesh, targetMesh ):
        skinNodes = sgCmds.getNodeFromHistory( skinedMesh, 'skinCluster' )
        if not skinNodes: return

        skinNode = skinNodes[0]
        joints = skinNode.matrix.listConnections( s=1, d=0 )

        meshs = []
        for joint in joints:
            meshShape = pymel.core.createNode( 'mesh' )
            mesh = meshShape.getParent()
            mesh.rename( 'blTarget_%s' % joint.name() )
            skinedMesh.getShape().outMesh >> meshShape.inMesh
            meshs.append( mesh )
        blNode = pymel.core.blendShape( meshs, targetMesh )[0]
        for origCon, dstCon in blNode.listConnections( s=1, d=0, type='mesh', p=1, c=1 ):
            dstCon.node().inMesh.listConnections( s=1, d=0, p=1 )[0] >> origCon
        pymel.core.delete( meshs )
        for i in range( len( joints ) ):
            sgCmds.addAttr( joints[i], ln='blend', min=0, max=1, k=1 )
            joints[i].attr( 'blend' ) >> blNode.w[i]
        return blNode, skinNode, [ joint.node() for joint in joints ]

    def getMatrixIndexToJointIndexMap( skinNode, joints ):
        cons = skinNode.matrix.listConnections( s=1, d=0, p=1, c=1 )
        localIndexToJointMap = {}
        for origCon, srcCon in cons:
            localIndexToJointMap[ origCon.logicalIndex() ] = joints.index( srcCon.node() )
        return localIndexToJointMap

    blNode, skinNode, joints = createBlendShape( skinedMesh, targetMesh )
    matrixIndexToJointIndexMap = getMatrixIndexToJointIndexMap( skinNode, joints )

    fnSkinNode = OpenMaya.MFnDependencyNode( sgCmds.getMObject( skinNode ) )
    plugWeightList = fnSkinNode.findPlug( 'weightList' )

    weightsMap = {}
    for i in range( plugWeightList.numElements() ):
        plugWeights = plugWeightList[i].child(0)
        for j in range( plugWeights.numElements() ):
            matrixIndex = plugWeights[j].logicalIndex()
            weightValue = plugWeights[j].asFloat()
            targetJointIndex = matrixIndexToJointIndexMap[ matrixIndex ]
            if weightsMap.has_key( targetJointIndex ):
                weightsMap[ targetJointIndex ][i] = weightValue
            else:
                weightsMap[ targetJointIndex ] = {}

    for jointIndex in weightsMap:
        for vtxIndex in range(plugWeightList.numElements()):
            blendShapeAttr = '%s.inputTarget[0].inputTargetGroup[%d].targetWeights[%d]' % ( blNode.name(), jointIndex, vtxIndex)
            pymel.core.setAttr(blendShapeAttr, 0)
        for vtxIndex in weightsMap[ jointIndex ]:
            blendShapeAttr = '%s.inputTarget[0].inputTargetGroup[%d].targetWeights[%d]' % ( blNode.name(), jointIndex, vtxIndex )
            pymel.core.setAttr( blendShapeAttr, weightsMap[ jointIndex ][ vtxIndex ] )






