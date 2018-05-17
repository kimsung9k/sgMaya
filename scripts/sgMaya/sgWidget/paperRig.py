import pymel.core
from maya import OpenMaya, cmds, OpenMayaUI
import copy, os, json, ntpath

class Controller:

    circlePoints = [[0.00000, 0.00000, -1.00000],
                    [-0.17365, 0.00000, -0.98481],
                    [-0.34202, 0.00000, -0.93969],
                    [-0.50000, 0.00000, -0.86603],
                    [-0.64279, 0.00000, -0.76604],
                    [-0.76604, 0.00000, -0.64279],
                    [-0.86603, 0.00000, -0.50000],
                    [-0.93969, 0.00000, -0.34202],
                    [-0.98481, 0.00000, -0.17365],
                    [-1.00000, 0.00000, -0.00000],
                    [-0.98481, -0.00000, 0.17365],
                    [-0.93969, -0.00000, 0.34202],
                    [-0.86603, -0.00000, 0.50000],
                    [-0.76604, -0.00000, 0.64279],
                    [-0.64279, -0.00000, 0.76604],
                    [-0.50000, -0.00000, 0.86603],
                    [-0.34202, -0.00000, 0.93969],
                    [-0.17365, -0.00000, 0.98481],
                    [-0.00000, -0.00000, 1.00000],
                    [0.17365, -0.00000, 0.98481],
                    [0.34202, -0.00000, 0.93969],
                    [0.50000, -0.00000, 0.86603],
                    [0.64279, -0.00000, 0.76604],
                    [0.76604, -0.00000, 0.64279],
                    [0.86603, -0.00000, 0.50000],
                    [0.93969, -0.00000, 0.34202],
                    [0.98481, -0.00000, 0.17365],
                    [1.00000, -0.00000, 0.00000],
                    [0.98481, 0.00000, -0.17365],
                    [0.93969, 0.00000, -0.34202],
                    [0.86603, 0.00000, -0.50000],
                    [0.76604, 0.00000, -0.64279],
                    [0.64279, 0.00000, -0.76604],
                    [0.50000, 0.00000, -0.86603],
                    [0.34202, 0.00000, -0.93969],
                    [0.17365, 0.00000, -0.98481],
                    [0.00000, 0.00000, -1.00000]]

    pinPoints = [[0.00000, 0.00000, 0.00000],
                 [0.00000, 0.99175, 0.00000],
                 [0.09028, 1.01594, 0.00000],
                 [0.15637, 1.08203, 0.00000],
                 [0.18056, 1.17232, 0.00000],
                 [0.15637, 1.26260, 0.00000],
                 [0.09028, 1.32869, 0.00000],
                 [0.00000, 1.35288, 0.00000],
                 [-0.09028, 1.32869, 0.00000],
                 [-0.15637, 1.26260, 0.00000],
                 [-0.18056, 1.17232, 0.00000],
                 [-0.15637, 1.08203, 0.00000],
                 [-0.09028, 1.01594, 0.00000],
                 [0.00000, 0.99175, 0.00000]]

    crossPoints = [[0.333333, 0.000000, -0.999999],
                   [0.333333, 0.000000, -0.333333],
                   [0.999999, 0.000000, -0.333333],
                   [0.999999, -0.000000, 0.333333],
                   [0.333333, -0.000000, 0.333333],
                   [0.333333, -0.000000, 0.999999],
                   [-0.333333, -0.000000, 0.999999],
                   [-0.333333, -0.000000, 0.333333],
                   [-0.999999, -0.000000, 0.333333],
                   [-0.999999, 0.000000, -0.333333],
                   [-0.333333, 0.000000, -0.333333],
                   [-0.333333, 0.000000, -0.999999],
                   [0.333333, 0.000000, -0.999999]]

    planePoints = [[-1.00000, 0.00000, -1.00000],
                   [-1.00000, 0.00000, 1.00000],
                   [1.00000, 0.00000, 1.00000],
                   [1.00000, 0.00000, -1.00000],
                   [-1.00000, 0.00000, -1.00000]]

    spherePoints = [[0.00000, 1.00000, 0.00000],
                    [-0.00000, 0.92388, 0.38268],
                    [-0.00000, 0.70711, 0.70711],
                    [-0.00000, 0.38268, 0.92388],
                    [-0.00000, 0.00000, 1.00000],
                    [-0.00000, -0.38260, 0.92388],
                    [-0.00000, -0.70710, 0.70711],
                    [-0.00000, -0.92380, 0.38268],
                    [0.00000, -1.00000, 0.00000],
                    [0.00000, -0.92380, -0.38260],
                    [0.00000, -0.70710, -0.70710],
                    [0.00000, -0.38260, -0.92380],
                    [0.00000, 0.00000, -1.00000],
                    [0.00000, 0.38268, -0.92380],
                    [0.00000, 0.70711, -0.70710],
                    [0.00000, 0.92388, -0.38260],
                    [0.00000, 1.00000, 0.00000],
                    [-0.38260, 0.92388, -0.00000],
                    [-0.70710, 0.70711, -0.00000],
                    [-0.92380, 0.38268, -0.00000],
                    [-1.00000, 0.00000, -0.00000],
                    [-0.92380, 0.00000, -0.38260],
                    [-0.70710, 0.00000, -0.70710],
                    [-0.38260, 0.00000, -0.92380],
                    [0.00000, 0.00000, -1.00000],
                    [0.38268, 0.00000, -0.92380],
                    [0.70711, 0.00000, -0.70710],
                    [0.92388, 0.00000, -0.38260],
                    [1.00000, 0.00000, 0.00000],
                    [0.92388, 0.00000, 0.38268],
                    [0.70711, 0.00000, 0.70711],
                    [0.38268, 0.00000, 0.92388],
                    [-0.00000, 0.00000, 1.00000],
                    [-0.38260, 0.00000, 0.92388],
                    [-0.70710, 0.00000, 0.70711],
                    [-0.92380, 0.00000, 0.38268],
                    [-1.00000, 0.00000, -0.00000],
                    [-0.92380, -0.38260, -0.00000],
                    [-0.70710, -0.70710, -0.00000],
                    [-0.38260, -0.92380, -0.00000],
                    [0.00000, -1.00000, 0.00000],
                    [0.38268, -0.92380, 0.00000],
                    [0.70711, -0.70710, 0.00000],
                    [0.92388, -0.38260, 0.00000],
                    [1.00000, 0.00000, 0.00000],
                    [0.92388, 0.38268, 0.00000],
                    [0.70711, 0.70711, 0.00000],
                    [0.38268, 0.92388, 0.00000],
                    [0.00000, 1.00000, 0.00000]]

class sgCmds_copyed:

    @staticmethod
    def getIndexColor(inputDagNode):

        dagNode = pymel.core.ls(inputDagNode)[0]
        return dagNode.overrideColor.get()

    @staticmethod
    def setIndexColor(inputDagNode, index):

        dagNode = pymel.core.ls(inputDagNode)[0]
        dagNode.overrideEnabled.set(1)
        dagNode.overrideColor.set(index)

    @staticmethod
    def getMObject(inputTarget):
        target = pymel.core.ls(inputTarget)[0]
        mObject = OpenMaya.MObject()
        selList = OpenMaya.MSelectionList()
        selList.add(target.name())
        selList.getDependNode(0, mObject)
        return mObject

    @staticmethod
    def copyShapeToTransform(inputShape, inputTransform):

        shape = pymel.core.ls(inputShape)[0]
        transform = pymel.core.ls(inputTransform)[0]

        tempTr = pymel.core.createNode('transform')
        oTarget = sgCmds_copyed.getMObject(tempTr)

        if shape.type() == 'mesh':
            oMesh = sgCmds_copyed.getMObject(shape)
            fnMesh = OpenMaya.MFnMesh(oMesh)
            fnMesh.copy(oMesh, oTarget)
        elif shape.type() == 'nurbsCurve':
            oCurve = sgCmds_copyed.getMObject(shape)
            fnCurve = OpenMaya.MFnNurbsCurve(oCurve)
            fnCurve.copy(oCurve, oTarget)
        elif shape.type() == 'nurbsSurface':
            oSurface = sgCmds_copyed.getMObject(shape)
            fnSurface = OpenMaya.MFnNurbsSurface(oSurface)
            fnSurface.copy(oSurface, oTarget)
        else:
            duShapeTr = pymel.core.duplicate(shape.getParent())[0]
            pymel.core.parent(duShapeTr.getShape(), transform, add=1, shape=1)
            pymel.core.delete(duShapeTr)

        if tempTr.getShape():
            sgCmds_copyed.setIndexColor(tempTr.getShape(), sgCmds_copyed.getIndexColor(shape))
            pymel.core.parent(tempTr.getShape(), transform, shape=1, add=1)
        pymel.core.delete(tempTr)


    @staticmethod
    def makeParent(inputSel, **options):

        sel = pymel.core.ls(inputSel)[0]
        if not options.has_key('n') and not options.has_key('name'):
            options.update({'n': 'P' + sel.nodeName()})
        selP = sel.getParent()
        transform = pymel.core.createNode('transform', **options)
        if selP: pymel.core.parent(transform, selP)
        pymel.core.xform(transform, ws=1, matrix=sel.wm.get())
        pymel.core.parent(sel, transform)
        pymel.core.xform(sel, os=1, matrix=[1,0,0,0, 0,1,0,0, 0,0,1,0 ,0,0,0,1])
        return transform


    @staticmethod
    def addIOShape(inputShape):

        shape = pymel.core.ls(inputShape)[0]

        if shape.type() == 'transform':
            targetShape = shape.getShape()
        else:
            targetShape = shape

        targetTr = targetShape.getParent()
        newShapeTr = pymel.core.createNode('transform')
        sgCmds_copyed.copyShapeToTransform(targetShape, newShapeTr)
        ioShape = newShapeTr.getShape()
        ioShape.attr('io').set(1)
        pymel.core.parent(ioShape, targetTr, add=1, shape=1)
        pymel.core.delete(newShapeTr)
        ioShape = targetTr.listRelatives(s=1)[-1]
        return ioShape


    @staticmethod
    def getMultMatrix(*matrixAttrList):
        mm = pymel.core.createNode('multMatrix')
        for i in range(len(matrixAttrList)):
            pymel.core.connectAttr(matrixAttrList[i], mm.i[i])
        return mm


    @staticmethod
    def constrain(*inputs, **options):

        def getOptionValue(keyName, returnValue, **options):
            if options.has_key(keyName):
                returnValue = options[keyName]
            return returnValue

        src = inputs[0]
        targets = inputs[1:]

        ct = True
        cr = True
        cs = False
        csh = False

        ct = getOptionValue('ct', ct, **options)
        cr = getOptionValue('cr', cr, **options)
        cs = getOptionValue('cs', cs, **options)
        csh = getOptionValue('csh', csh, **options)

        for target in targets:
            mm = sgCmds_copyed.getMultMatrix( src.wm, target.pim )
            dcmp = pymel.core.createNode( 'decomposeMatrix' )
            mm.o >> dcmp.imat

            if ct: dcmp.ot >> target.t
            if cr: dcmp.outputRotate >> target.r
            if cs: dcmp.os >> target.s
            if csh: dcmp.osh >> target.sh


    @staticmethod
    def setBindPreMatrix(inputJnt, inputBindPre):

        jnt = pymel.core.ls(inputJnt)[0]
        bindPre = pymel.core.ls(inputBindPre)[0]

        targetAttrs = jnt.wm.listConnections(s=0, d=1, type='skinCluster', p=1)
        if not targetAttrs: return None

        for targetAttr in targetAttrs:
            node = targetAttr.node()
            try:
                index = targetAttr.index()
            except:
                continue
            bindPre.wim >> node.bindPreMatrix[index]


    @staticmethod
    def getDecomposeMatrix(matrixAttr):

        matrixAttr = pymel.core.ls(matrixAttr)[0]
        cons = matrixAttr.listConnections(s=0, d=1, type='decomposeMatrix')
        if cons:
            pymel.core.select(cons[0])
            return cons[0]
        decomposeMatrix = pymel.core.createNode('decomposeMatrix')
        matrixAttr >> decomposeMatrix.imat
        return decomposeMatrix

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

    @staticmethod
    def getLookAtChildMatrixAttr(lookTargetMatrix, baseMatrix, baseVector):

        baseInverse = pymel.core.createNode('inverseMatrix')
        baseMatrix >> baseInverse.inputMatrix
        dcmp = sgCmds_copyed.getDecomposeMatrix(sgCmds_copyed.getMultMatrix(lookTargetMatrix, baseInverse.outputMatrix).matrixSum)
        angleNode = pymel.core.createNode('angleBetween')

        lookTargetMVector = OpenMaya.MVector(*dcmp.ot.get())
        baseMVector = OpenMaya.MVector(*baseVector)

        if lookTargetMVector * baseMVector < 0:
            baseVector = [-value for value in baseVector]

        angleNode.vector1.set(baseVector)
        dcmp.ot >> angleNode.vector2

        compose = pymel.core.createNode('composeMatrix')
        angleNode.euler >> compose.ir

        mm = pymel.core.createNode('multMatrix')
        compose.outputMatrix >> mm.i[0]
        baseMatrix >> mm.i[1]

        return mm.matrixSum


    @staticmethod
    def getNodeFromHistory(target, nodeType):

        pmTarget = pymel.core.ls(target)[0]
        hists = pmTarget.history()
        targetNodes = []
        for hist in hists:
            if hist.type() == nodeType:
                targetNodes.append(hist)
        return targetNodes

    @staticmethod
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


    @staticmethod
    def createBlendTwoMatrixNode(inputFirstAttr, inputSecondAttr):

        firstAttr = pymel.core.ls(inputFirstAttr)[0]
        secondAttr = pymel.core.ls(inputSecondAttr)[0]

        wtAddMtx = pymel.core.createNode('wtAddMatrix')
        wtAddMtx.addAttr('blend', min=0, max=1, dv=0.5, k=1)

        revNode = pymel.core.createNode('reverse')

        firstAttr >> wtAddMtx.i[0].m
        secondAttr >> wtAddMtx.i[1].m

        wtAddMtx.blend >> revNode.inputX
        revNode.outputX >> wtAddMtx.i[0].w
        wtAddMtx.blend >> wtAddMtx.i[1].w

        return wtAddMtx


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
                sgCmds_copyed.addAttr(dst, ln=srcAttr.longName(), sn=srcAttr.nodeName(), at=srcAttr.type(), en=enumStr, dv=defaultList[0])
            else:
                sgCmds_copyed.addAttr(dst, ln=srcAttr.longName(), sn=srcAttr.nodeName(), at=srcAttr.type(), dv=defaultList[0])
        except:
            try:
                sgCmds_copyed.addAttr(dst, ln=srcAttr.longName(), sn=srcAttr.nodeName(), dt=srcAttr.type(), dv=defaultList[0])
            except:
                pass

        sgCmds_copyed.addAttr(dst, ln=replaceAttrName)
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
    def replaceObject(inputSrc, inputDst):

        src = pymel.core.ls(inputSrc)[0]
        dst = pymel.core.ls(inputDst)[0]

        attrs = src.listAttr(ud=1)
        for attr in attrs:
            sgCmds_copyed.copyAttribute(src, dst, attr.longName())

        srcCons = src.listConnections(s=1, d=0, p=1, c=1)
        dstCons = src.listConnections(s=0, d=1, p=1, c=1)

        dst.setParent(src.getParent())

        for origCon, srcCon in srcCons:
            srcCon >> dst.attr(origCon.attrName())
        for origCon, dstCon in dstCons:
            dst.attr(origCon.attrName()) >> dstCon

        pymel.core.xform(dst, ws=1, matrix=src.wm.get())

        children = src.listRelatives(c=1, type='transform')
        for child in children:
            child.setParent(dst)
        return dst

    @staticmethod
    def blendTwoMatrixConnect(inputFirst, inputSecond, inputThird, **options):

        connectTrans = True
        connectRotate = True
        connectScale = True
        connectShear = True

        if options.has_key('ct'):
            connectTrans = options['ct']
        if options.has_key('cr'):
            connectRotate = options['cr']
        if options.has_key('cs'):
            connectScale = options['cs']
        if options.has_key('csh'):
            connectShear = options['csh']

        first = pymel.core.ls(inputFirst)[0]
        second = pymel.core.ls(inputSecond)[0]
        third = pymel.core.ls(inputThird)[0]

        sgCmds_copyed.addAttr(third, ln='blend', min=0, max=1, k=1, dv=0.5)

        if options.has_key('local'):
            wtAddMtx = pymel.core.createNode('wtAddMatrix')
            dcmp = pymel.core.createNode('decomposeMatrix')
            revNode = pymel.core.createNode('reverse')
            third.blend >> revNode.inputX
            first.m >> wtAddMtx.i[0].m
            second.m >> wtAddMtx.i[1].m
            revNode.outputX >> wtAddMtx.i[0].w
            third.blend >> wtAddMtx.i[1].w
            wtAddMtx.matrixSum >> dcmp.imat
        else:
            wtAddMtx = pymel.core.createNode('wtAddMatrix')
            multMtx = pymel.core.createNode('multMatrix')
            dcmp = pymel.core.createNode('decomposeMatrix')
            revNode = pymel.core.createNode('reverse')
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
    def makeController(pointList, defaultScaleMult=1, **options):

        newPointList = copy.deepcopy(pointList)

        options.update({'p': newPointList, 'd': 1})

        typ = 'transform'
        if options.has_key('typ'):
            typ = options.pop('typ')

        mp = False
        if options.has_key('makeParent'):
            mp = options.pop('makeParent')

        colorIndex = -1
        if options.has_key('colorIndex'):
            colorIndex = options.pop('colorIndex')

        crv = pymel.core.curve(**options)
        crvShape = crv.getShape()

        if options.has_key('n'):
            name = options['n']
        elif options.has_key('name'):
            name = options['name']
        else:
            name = None

        jnt = pymel.core.ls(cmds.createNode(typ))[0]
        pJnt = None

        if mp:
            pJnt = pymel.core.ls(sgCmds_copyed.makeParent(jnt))[0]

        if name:
            jnt.rename(name)
            if pJnt:
                pJnt.rename('P' + name)

        pymel.core.parent(crvShape, jnt, add=1, shape=1)
        pymel.core.delete(crv)
        crvShape = jnt.getShape()

        ioShape = sgCmds_copyed.addIOShape(jnt)
        ioShape = pymel.core.ls(ioShape)[0]

        crvShape.addAttr('shape_tx', dv=0);
        jnt.shape_tx.set(e=1, cb=1)
        crvShape.addAttr('shape_ty', dv=0);
        jnt.shape_ty.set(e=1, cb=1)
        crvShape.addAttr('shape_tz', dv=0);
        jnt.shape_tz.set(e=1, cb=1)
        crvShape.addAttr('shape_rx', dv=0, at='doubleAngle');
        jnt.shape_rx.set(e=1, cb=1)
        crvShape.addAttr('shape_ry', dv=0, at='doubleAngle');
        jnt.shape_ry.set(e=1, cb=1)
        crvShape.addAttr('shape_rz', dv=0, at='doubleAngle');
        jnt.shape_rz.set(e=1, cb=1)
        crvShape.addAttr('shape_sx', dv=1);
        jnt.shape_sx.set(e=1, cb=1)
        crvShape.addAttr('shape_sy', dv=1);
        jnt.shape_sy.set(e=1, cb=1)
        crvShape.addAttr('shape_sz', dv=1);
        jnt.shape_sz.set(e=1, cb=1)
        crvShape.addAttr('scaleMult', dv=defaultScaleMult, min=0);
        jnt.scaleMult.set(e=1, cb=1)
        composeMatrix = pymel.core.createNode('composeMatrix')
        composeMatrix2 = pymel.core.createNode('composeMatrix')
        multMatrix = pymel.core.createNode('multMatrix')
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
        trGeo = pymel.core.createNode('transformGeometry')
        try:
            jnt.attr('radius').set(0)
        except:
            pass

        ioShape.local >> trGeo.inputGeometry
        multMatrix.matrixSum >> trGeo.transform

        trGeo.outputGeometry >> crvShape.create

        if colorIndex != -1:
            shape = jnt.getShape().name()
            cmds.setAttr(shape + '.overrideEnabled', 1)
            cmds.setAttr(shape + '.overrideColor', colorIndex)

        return jnt


class Main_Commands:

    @staticmethod
    def paperRig(target, div=[5, 5]):

        import math
        bb = pymel.core.exactWorldBoundingBox(target)
        bbmin = OpenMaya.MVector(*bb[:3])
        bbmax = OpenMaya.MVector(*bb[3:])

        bbc = [(bbmin[i] + bbmax[i]) / 2.0 for i in range(3)]

        startPoint = OpenMaya.MVector(bbmin.x, (bbmin.y + bbmax.y) / 2, bbmin.z)

        xInterval = (bbmax.x - bbmin.x) / (div[0] - 1)
        zInterval = (bbmax.z - bbmin.z) / (div[1] - 1)
        xSize = (bbmax.x - bbmin.x)
        zSize = (bbmax.z - bbmin.z)

        worldCtl = sgCmds_copyed.makeController(Controller.circlePoints, 1, makeParent=1, n='Ctl_World')
        moveCtl = sgCmds_copyed.makeController(Controller.crossPoints, 1, makeParent=1, n='Ctl_Move')
        rootCtl = sgCmds_copyed.makeController(Controller.planePoints, 1, makeParent=1, n='Ctl_Root')
        pWorldCtl = worldCtl.getParent()
        pMoveCtl = moveCtl.getParent()
        pRootCtl = rootCtl.getParent()
        pWorldCtl.t.set(bbc)
        pMoveCtl.t.set(bbc)
        pRootCtl.t.set(bbc)
        worldCtl.scaleMult.set(xSize / 2.0 * 1.6)
        moveCtl.scaleMult.set(xSize / 2.0 * 1.4)
        rootCtl.scaleMult.set(xSize / 2.0 * 1.1)

        pMoveCtl.setParent(worldCtl)
        pRootCtl.setParent(moveCtl)

        sgCmds_copyed.setIndexColor(worldCtl, 17)
        sgCmds_copyed.setIndexColor(moveCtl, 20)
        sgCmds_copyed.setIndexColor(rootCtl, 15)

        joints = []
        ctls = []
        fkCtls = []

        lines_horizon = [[None for j in range(div[0])] for i in range(div[1])]
        lines_vertical = [[None for i in range(div[1])] for j in range(div[0])]

        for i in range(div[0]):
            xValue = startPoint.x + xInterval * i
            yValue = startPoint.y
            fkCtl = sgCmds_copyed.makeController(Controller.planePoints, 1, makeParent=1, n='Ctl_Fk_%d' % i)
            pFkCtl = fkCtl.getParent()
            pFkCtl.t.set(xValue, yValue, bbc[2])
            fkCtl.shape_sz.set(zSize / 2.0)
            fkCtl.shape_rz.set(90)
            if fkCtls:
                pFkCtl.setParent(fkCtls[-1])
            fkCtls.append(fkCtl)
            sgCmds_copyed.setIndexColor(fkCtl, 23)

            baseCtl = sgCmds_copyed.makeController(Controller.pinPoints, 1, makeParent=1, n='Ctl_Base_%d' % i)
            sgCmds_copyed.setIndexColor(baseCtl, 18)
            pBaseCtl = baseCtl.getParent()
            pBaseCtl.t.set(xValue, yValue, bbc[2])
            pBaseCtl.setParent(fkCtl)

            eachJnts = []
            eachCtls = []
            for j in range(div[1]):
                zValue = startPoint.z + zInterval * j
                eachCtl = sgCmds_copyed.makeController(Controller.spherePoints, .6, makeParent=1,
                                                n='Ctl_Each_%d_%d' % (i, j))
                pEachCtl = eachCtl.getParent()
                pEachCtl.t.set(xValue, yValue, zValue)
                jnt = pymel.core.createNode('joint')
                sgCmds_copyed.constrain(eachCtl, jnt, ct=1, cr=1, cs=1, csh=1)
                pEachCtl.setParent(baseCtl)
                eachJnts.append(jnt)
                eachCtls.append(eachCtl)
                sgCmds_copyed.setIndexColor(eachCtl, 31)

                lines_vertical[i][j] = eachCtl
                lines_horizon[j][i] = eachCtl

            joints.append(eachJnts)
            ctls.append(eachCtls)

        fkCtls[0].getParent().setParent(rootCtl)
        bindJoints = []
        for eachJoints in joints:
            bindJoints += eachJoints

        bindJntGrp = pymel.core.group(bindJoints, n='bindJnts')

        initObj = pymel.core.createNode('transform', n='initObj')
        pymel.core.xform(initObj, ws=1, t=bbc)
        initBase = pymel.core.createNode('transform', n='initBase')
        pymel.core.xform(initBase, ws=1, matrix=initObj.wm.get())
        initObj.t >> initBase.t
        initObj.r >> initBase.r

        bindPres = []
        for eachJoints in joints:
            eachBindPres = []
            for bindJnt in eachJoints:
                bindPre = pymel.core.createNode('transform')
                bindPre.dh.set(1)
                pymel.core.xform(bindPre, ws=1, matrix=bindJnt.wm.get())
                sgCmds_copyed.setBindPreMatrix(bindJnt, bindPre)
                eachBindPres.append(bindPre)
            pymel.core.parent(eachBindPres, initBase)
            bindPres.append(eachBindPres)

        # bindPre setting
        beforeAverageNode = None
        for i in range(len(joints)):
            eachBindPres = bindPres[i]
            eachJoints = joints[i]
            eachCtls = ctls[i]
            fkCtl = fkCtls[i]

            bindPreControls = []
            for eachBindPre in eachBindPres:
                bindPreControl = pymel.core.createNode('transform')
                pymel.core.xform(bindPreControl, ws=1, matrix=eachBindPre.wm.get())
                bindPreControl.setParent(initObj)
                sgCmds_copyed.constrain(bindPreControl, eachBindPre)
                bindPreControls.append(bindPreControl)

            averageNode = pymel.core.createNode('plusMinusAverage')
            averageNode.op.set(3)
            eachBindPres[0].t >> averageNode.input3D[0]
            eachBindPres[-1].t >> averageNode.input3D[1]

            if not beforeAverageNode:
                averageNode.output3D >> fkCtl.getParent().t
            else:
                minusNode = pymel.core.createNode('plusMinusAverage')
                minusNode.op.set(2)
                averageNode.output3D >> minusNode.input3D[0]
                beforeAverageNode.output3D >> minusNode.input3D[1]
                minusNode.output3D >> fkCtl.getParent().t

            beforeAverageNode = averageNode

            for i in range(len(eachBindPres)):
                minusNode = pymel.core.createNode('plusMinusAverage')
                minusNode.op.set(2)
                eachBindPres[i].t >> minusNode.input3D[0]
                averageNode.output3D >> minusNode.input3D[1]
                minusNode.output3D >> eachCtls[i].getParent().t
        sgCmds_copyed.constrain(initObj, pWorldCtl)

        # shapeSetting
        for i in range(len(joints)):
            eachBindPres = bindPres[i]
            fkCtl = fkCtls[i]
            minusNode = pymel.core.createNode('plusMinusAverage');
            minusNode.op.set(2)
            multHalf = pymel.core.createNode('multDoubleLinear')
            eachBindPres[-1].t >> minusNode.input3D[0]
            eachBindPres[0].t >> minusNode.input3D[1]
            minusNode.output3Dz >> multHalf.input1
            multHalf.input2.set(0.5)
            multHalf.output >> fkCtl.shape_sz

        initObj.v.set(0)
        initBase.v.set(0)

        for targetCtl in [rootCtl, moveCtl, worldCtl]:
            initObj.sx >> targetCtl.shape_sx
            initObj.sy >> targetCtl.shape_sy
            initObj.sz >> targetCtl.shape_sz

        pymel.core.group(target, pWorldCtl, bindJntGrp, initObj, initBase, n='SET')
        '''
        curves_horizon = []
        for line in lines_horizon:
            pointers = sgCmds_copyed.makeInterPointer(line)
            [pointer.v.set(0) for pointer in pointers]
            pointers.insert(0, line[0])
            pointers.append(line[-1])
            curve = sgCmds_copyed.makeCurveFromSelection(*pointers)
            curves_horizon.append(curve)

        curves_vertical = []
        for line in lines_vertical:
            pointers = sgCmds_copyed.makeInterPointer(line)
            [pointer.v.set(0) for pointer in pointers]
            pointers.insert(0, line[0])
            pointers.append(line[-1])
            curve = sgCmds_copyed.makeCurveFromSelection(*pointers)
            curves_vertical.append(curve)

        pointers_horizon = []
        for i in range(len(curves_horizon)):
            curve = curves_horizon[i]
            pointers = sgCmds_copyed.createPointOnCurve(curve, div[0] * 2 - 1)
            sgCmds_copyed.tangentConstraintByGroup(curve, pointers, lines_horizon[i], [1, 0, 0])
            pointers_horizon.append(pointers)

        pointers_vertical = []
        for i in range(len(curves_vertical)):
            curve = curves_vertical[i]
            pointers = sgCmds_copyed.createPointOnCurve(curve, div[1] * 2 - 1)
            sgCmds_copyed.tangentConstraintByGroup(curve, pointers, lines_vertical[i], [0, 0, 1])
            pointers_vertical.append(pointers)

        samePositionTargets = []
        elseTargets = []
        for i in range(len(pointers_horizon)):
            for j in range(len(pointers_vertical)):
                firstTarget = pointers_horizon[i][j * 2]
                secondTarget = pointers_vertical[j][i * 2]
                samePositionTargets.append([firstTarget, secondTarget])
                if i != 0:
                    elseTargets.append(pointers_vertical[j][i * 2 - 1])
                if j != 0:
                    elseTargets.append(pointers_horizon[i][j * 2 - 1])

        joints = []
        for first, second in samePositionTargets:
            newJoint = pymel.core.createNode('joint')
            sgCmds_copyed.blendTwoMatrixConnect(first, second, newJoint, ct=1, cr=1)
            joints.append(newJoint)

        elseTargets = list(set(elseTargets))
        for elseTarget in elseTargets:
            newJoint = pymel.core.createNode('joint')
            sgCmds_copyed.replaceObject(elseTarget, newJoint)
            joints.append(newJoint)

        resultPointers = []
        for pointers in pointers_horizon:
            resultPointers += pointers
        for pointers in pointers_vertical:
            resultPointers += pointers
        '''
        #curveGrp = pymel.core.createNode('transform', n='curveGrp')
        #pointersGrp = pymel.core.createNode('transform', n='pointersGrp')
        #pymel.core.parent(curves_vertical, curves_horizon, curveGrp)
        #pymel.core.parent(resultPointers, pointersGrp)
        #pymel.core.parent(curveGrp, pointersGrp, jointsGrp, rootCtl)
        #curveGrp.v.set( 0 )
        #pointersGrp.v.set( 0 )


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


    def save_lineEdit_text(self, lineEdits, path ):

        data = self.readData( path )
        for i in range( len( lineEdits ) ):
            lineEdit = lineEdits[i]
            data['lineEdit_%02d' % i ] = lineEdit.text()
        self.writeData( data, path )


    def load_lineEdit_text(self, lineEdits, path ):

        data = self.readData( path )
        for i in range( len( lineEdits ) ):
            lineEdit = lineEdits[i]
            key = 'lineEdit_%02d' % i
            if not data.has_key( key ): continue
            lineEdit.setText( data[ key ] )



path_baseDir = cmds.about(pd=1) + "/pingo/paper_rig"

class Widget_numController( QWidget, Cmds_file_control ):

    path_uiInfo = path_baseDir + '/numController.json'
    def __init__(self, *args, **kwargs ):
        super( Widget_numController, self ).__init__()
        self.installEventFilter( self )
        mainLayout = QHBoxLayout( self ); mainLayout.setContentsMargins( 5, 0, 5, 0 )

        validator = QIntValidator()

        label = QLabel( "Num Controller" )
        lineEdit_width = QLineEdit(); lineEdit_width.setValidator( validator )
        lineEdit_height = QLineEdit(); lineEdit_height.setValidator( validator )
        lineEdit_width.setText('5')
        lineEdit_height.setText('5')
        mainLayout.addWidget( label )
        mainLayout.addWidget( lineEdit_width )
        mainLayout.addWidget( lineEdit_height )

        self.lineEdit_width  = lineEdit_width
        self.lineEdit_height = lineEdit_height
        self.load_lineEdit_text( [self.lineEdit_width, self.lineEdit_height], Widget_numController.path_uiInfo )

        QtCore.QObject.connect(self.lineEdit_width, QtCore.SIGNAL("returnPressed()"), self.save_info)
        QtCore.QObject.connect(self.lineEdit_height, QtCore.SIGNAL("returnPressed()"), self.save_info)

    def save_info(self):
        self.save_lineEdit_text( [self.lineEdit_width, self.lineEdit_height], Widget_numController.path_uiInfo )




class Window( QDialog, Cmds_file_control ):

    mayaWin = shiboken.wrapInstance( long( OpenMayaUI.MQtUtil.mainWindow() ), QWidget )
    objectName = 'sg_pingo_paperRig'
    title = 'PINGO - Paper Rig'
    defaultWidth = 400
    defaultHeight = 400
    path_uiInfo = path_baseDir + '/Window.json'

    def __init__(self, *args, **kwargs ):
        existing_widgets = Window.mayaWin.findChildren(QDialog, Window.objectName)
        if existing_widgets: map(lambda x: x.deleteLater(), existing_widgets)

        super(Window, self).__init__(Window.mayaWin)
        self.installEventFilter(self)
        self.setObjectName(Window.objectName)
        self.setWindowTitle(Window.title)

        mainLayout = QVBoxLayout( self )
        w_numController = Widget_numController()
        button = QPushButton( "Create" )
        mainLayout.addWidget( w_numController )
        mainLayout.addWidget( button )

        self.load_shapeInfo( Window.path_uiInfo)

        self.w_numController = w_numController
        QtCore.QObject.connect( button, QtCore.SIGNAL( "clicked()" ), self.create )

    def create(self):

        widthValue = int( self.w_numController.lineEdit_width.text() )
        heightValue = int( self.w_numController.lineEdit_height.text() )

        selTarget = pymel.core.ls( sl=1 )[0]

        cmds.undoInfo( ock=1 )
        Main_Commands.paperRig( selTarget, [widthValue, heightValue] )
        cmds.undoInfo( cck=1 )

    def eventFilter(self, *args, **kwargs ):
        event = args[1]
        if event.type() in [ QtCore.QEvent.Resize, QtCore.QEvent.Move ]:
            try:self.save_shapeInfo( Window.path_uiInfo )
            except:pass



def show():
    Window().show()

if __name__ == '__main__':
    show()
