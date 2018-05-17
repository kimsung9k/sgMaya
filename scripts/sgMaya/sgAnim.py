from maya import cmds, OpenMaya, OpenMayaAnim
import pymel.core

class KeyValues:

    def __init__(self, animCurveNode ):

        import math

        def getMObject(inputTarget):
            target = pymel.core.ls(inputTarget)[0]
            mObject = OpenMaya.MObject()
            selList = OpenMaya.MSelectionList()
            selList.add(target.name())
            selList.getDependNode(0, mObject)
            return mObject

        self.animCurveNode = pymel.core.ls( animCurveNode )[0]
        self.fnAnimCurve = OpenMayaAnim.MFnAnimCurve( getMObject( self.animCurveNode.name() ) )

        self.times = []
        self.values = []
        self.tangent_ints = []
        self.tangent_outs = []

        for i in range( self.animCurveNode.numKeys() ):
            self.times.append( self.animCurveNode.getTime( i ).real )
            value = self.animCurveNode.getValue( i )
            value = math.degrees(value) if self.animCurveNode.output.type() == 'doubleAngle' else value
            self.values.append( value )
            self.tangent_ints.append( self.animCurveNode.getTangent(i, True ) )
            self.tangent_outs.append( self.animCurveNode.getTangent(i, False ) )
        print self.times

    def _getValueAtTime( self, time):
        import math
        value = self.fnAnimCurve.evaluate(OpenMaya.MTime(time, OpenMaya.MTime.uiUnit()))
        value = math.degrees(value) if self.animCurveNode.output.type() == 'doubleAngle' else value
        return value


    def getValusesInRange(self, min, max ):

        import math

        value_start = self._getValueAtTime( min )
        value_end   = self._getValueAtTime( max )

        newDictList = {}
        for time, value in [[min,value_start],[max, value_end]]:
            newDictList[ time ] = {}
            newDictList[ time ]['value']  = value
            newDictList[ time ]['tanIn']  = None
            newDictList[ time ]['tanOut'] = None

        for i in range( len(self.times) ):
            time = self.times[i]
            if time < min: continue
            if time > max: break
            newDictList[time] = {}
            newDictList[time]['value']  = self.values[i]
            newDictList[time]['tanIn']  = self.tangent_ints[i]
            newDictList[time]['tanOut'] = self.tangent_outs[i]
        return newDictList


    def setKeyframeByDictList(self, keyDictList, targetAttr ):

        for time in keyDictList:
            pymel.core.setKeyframe( targetAttr, t=time, v=keyDictList[time]['value'] )
            inTangent = keyDictList[time]['tanIn']
            outTangent = keyDictList[time]['tanOut']
            if inTangent:
                pymel.core.keyTangent(targetAttr, t=time, ix=inTangent[0])
                pymel.core.keyTangent(targetAttr, t=time, iy=inTangent[1])
            if outTangent:
                pymel.core.keyTangent(targetAttr, t=time, ox=outTangent[0])
                pymel.core.keyTangent(targetAttr, t=time, oy=outTangent[1])






