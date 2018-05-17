import maya.cmds as cmds
from functools import partial

import maya.cmds as cmds
from functools import partial
import os


def getValueFromDict(argDict, *dictKeys):
    items = argDict.items()

    for item in items:
        if item[0] in dictKeys: return item[1]

    return None


class PopupFieldUI:

    def __init__(self, label, popupLabel='Load Selected', typ='single', addCommend=[], **options):

        self._label = label
        self._popup = popupLabel
        self._position = getValueFromDict(options, 'position')
        self._textWidth = getValueFromDict(options, 'textWidth')
        self._olnyAddCommand = getValueFromDict(options, 'olnyAddCmd')
        self._addCommand = addCommend
        if self._textWidth == None: self._textWidth = 120
        self._field = ''
        self._type = typ
        self._cmdPopup = [self.cmdLoadSelected]

    def cmdLoadSelected(self):

        if self._olnyAddCommand:
            if type(self._addCommand) in [type(()), type([])]:
                for command in self._addCommand: command()
            else:
                self._addCommand()
            return None

        sels = cmds.ls(sl=1, sn=1)
        if not sels: return None

        if self._type == 'single':
            cmds.textField(self._field, e=1, tx=sels[-1])
        else:
            popupTxt = ''
            for sel in sels:
                popupTxt += sel + ' '
            cmds.textField(self._field, e=1, tx=popupTxt[:-1])

        if self._addCommand:
            if type(self._addCommand) in [type(()), type([])]:
                for command in self._addCommand: command()
            else:
                self._addCommand()

    def cmdPopup(self, *args):
        for cmd in self._cmdPopup: cmd()

    def getFieldText(self):
        return cmds.textField(self._field, q=1, tx=1)

    def getFieldTexts(self):

        texts = cmds.textField(self._field, q=1, tx=1)
        splits = texts.split(' ')
        returnTexts = []

        splits2 = []

        for split in splits:
            splits2 += split.split(',')

        for split in splits2:
            split = split.strip()
            if split:
                returnTexts.append(split)
        return returnTexts

    def create(self):

        form = cmds.formLayout()
        text = cmds.text(l=self._label, al='right', h=20, width=self._textWidth)
        field = cmds.textField(h=21)
        cmds.popupMenu()
        cmds.menuItem(l=self._popup, c=self.cmdPopup)

        cmds.formLayout(form, e=1,
                        af=[(text, 'top', 0), (text, 'left', 0),
                            (field, 'top', 0), (field, 'right', 0)],
                        ac=[(field, 'left', 0, text)])

        if self._position:
            cmds.formLayout(form, e=1,
                            ap=[(text, 'right', 0, self._position)])

        cmds.setParent('..')

        self._text = text
        self._field = field
        self._form = form

        return form


class PopupFieldUI_b:

    def __init__(self, label, **options):

        import sgBFunction_value

        popupLabel = getValueFromDict(options, *['popupLabel', 'popLabel'])
        typ = getValueFromDict(options, *['type', 'typ'])
        addCommand = getValueFromDict(options, *['addCommand', 'addCmd'])
        globalForm = getValueFromDict(options, *['globalForm', 'form'])
        globalField = getValueFromDict(options, *['globalField', 'field'])

        if not popupLabel: popupLabel = 'Load Selected'
        if not typ: typ = 'single'
        if not addCommand: addCommand = []

        self._label = label
        self._popup = popupLabel
        self._position = getValueFromDict(options, 'position')
        self._textWidth = getValueFromDict(options, 'textWidth')
        self._olnyAddCommand = getValueFromDict(options, 'olnyAddCmd')
        self._addCommand = addCommand
        if self._textWidth == None: self._textWidth = 120
        self._field = ''
        self._type = typ
        self._cmdPopup = [self.cmdLoadSelected]
        self._globalForm = globalForm
        self._globalField = globalField

    def cmdLoadSelected(self):

        if self._olnyAddCommand:
            if type(self._addCommand) in [type(()), type([])]:
                for command in self._addCommand: command()
            else:
                self._addCommand()
            return None

        sels = cmds.ls(sl=1, sn=1)
        if not sels: return None

        if self._type == 'single':
            cmds.textField(self._field, e=1, tx=sels[-1])
        else:
            popupTxt = ''
            for sel in sels:
                popupTxt += sel + ' '
            cmds.textField(self._field, e=1, tx=popupTxt[:-1])

        if self._addCommand:
            if type(self._addCommand) in [type(()), type([])]:
                for command in self._addCommand: command()
            else:
                self._addCommand()

    def cmdPopup(self, *args):
        for cmd in self._cmdPopup: cmd()

    def getFieldText(self):
        return cmds.textField(self._field, q=1, tx=1)

    def getFieldTexts(self):

        texts = cmds.textField(self._field, q=1, tx=1)
        splits = texts.split(' ')
        returnTexts = []

        splits2 = []

        for split in splits:
            splits2 += split.split(',')

        for split in splits2:
            split = split.strip()
            if split:
                returnTexts.append(split)
        return returnTexts

    def create(self):

        form = cmds.formLayout()
        text = cmds.text(l=self._label, al='right', h=20, width=self._textWidth)
        field = cmds.textField(h=21)
        cmds.popupMenu()
        cmds.menuItem(l=self._popup, c=self.cmdPopup)

        cmds.formLayout(form, e=1,
                        af=[(text, 'top', 0), (text, 'left', 0),
                            (field, 'top', 0), (field, 'right', 0)],
                        ac=[(field, 'left', 0, text)])

        if self._position:
            cmds.formLayout(form, e=1,
                            ap=[(text, 'right', 0, self._position)])

        cmds.setParent('..')

        self._text = text
        self._field = field
        self._form = form

        self._globalForm = form
        self._globalField = field

        return form


def updatePathPopupMenu(textField, popupMenu, addCommand=None, *args):
    targetExtensions = ['mb', 'ma', 'fbx', 'obj']

    try:
        path = cmds.textFieldGrp(textField, q=1, tx=1)
    except:
        path = cmds.textField(textField, q=1, tx=1)

    splitPath = path.replace('\\', '/').split('/')
    if not os.path.isfile(path) and not os.path.isdir(path):
        path = '/'.join(splitPath[:-1])

    cmds.popupMenu(popupMenu, e=1, dai=1)
    cmds.setParent(popupMenu, menu=1)
    cmds.menuItem(l='Open File Browser', c=partial(sgBFunction_base.openFileBrowser, path))
    cmds.menuItem(d=1)

    def backToUpfolder(path, *args):
        print "back to folder"
        path = path.replace('\\', '/')

        if os.path.isdir(path):
            path = '/'.join(path.split('/')[:-1])
        else:
            path = '/'.join(path.split('/')[:-2])
        try:
            cmds.textFieldGrp(textField, e=1, tx=path)
        except:
            cmds.textField(textField, e=1, tx=path)
        updatePathPopupMenu(textField, popupMenu, addCommand)

    if os.path.isfile(path) or os.path.isdir(path):
        splitPath = path.replace('\\', '/').split('/')
        if splitPath and splitPath[-1] != '':
            cmds.menuItem(l='Back', c=partial(backToUpfolder, path))
    cmds.menuItem(d=1)

    path = path.replace('\\', '/')
    if os.path.isfile(path):
        path = '/'.join(path.split('/')[:-1])

    def updateTextField(path, *args):
        try:
            cmds.textFieldGrp(textField, e=1, tx=path)
        except:
            cmds.textField(textField, e=1, tx=path)
        updatePathPopupMenu(textField, popupMenu, addCommand)

    for root, dirs, names in os.walk(path):
        dirs.sort()
        for dir in dirs:
            cmds.menuItem(l=dir, c=partial(updateTextField, root + '/' + dir))
        names.sort()
        for name in names:
            extension = name.split('.')
            if len(extension) == 1: continue
            extension = extension[1]
            if not extension.lower() in targetExtensions: continue
            cmds.menuItem(l=name, c=partial(updateTextField, root + '/' + name))
        break

    if addCommand != None: addCommand()

    try:
        cmds.textField(textField, e=1, ec=partial(updatePathPopupMenu, textField, popupMenu, addCommand))
        cmds.textField(textField, e=1, cc=partial(updatePathPopupMenu, textField, popupMenu, addCommand))
    except:
        cmds.textFieldGrp(textField, e=1, ec=partial(updatePathPopupMenu, textField, popupMenu, addCommand))
        cmds.textFieldGrp(textField, e=1, cc=partial(updatePathPopupMenu, textField, popupMenu, addCommand))


def createWaningWindow(parentWindowName, message, conntinueCommand, continueLabel='Continue'):
    pTitle = cmds.window(parentWindowName, q=1, title=1)

    winName = 'warning_window'
    title = '%s Warning' % pTitle

    def cmdContinue(*args):
        conntinueCommand()
        cmds.deleteUI(winName)

    def cmdClose(*args):
        cmds.deleteUI(winName)

    if cmds.window(winName, ex=1): cmds.deleteUI(winName)
    cmds.window(winName, title=title)

    wh = cmds.window(parentWindowName, q=1, wh=1)
    tlc = cmds.window(parentWindowName, q=1, tlc=1)
    width = wh[0] - 4

    cmds.columnLayout()
    cmds.rowColumnLayout(nc=1, cw=[(1, width)])
    cmds.text(l=message, al='center')
    cmds.setParent('..')

    halfWidth = (width) * 0.5
    otherWidth = (width) - halfWidth
    cmds.rowColumnLayout(nc=2, cw=[(1, halfWidth), (2, otherWidth)])
    cmds.button(l=continueLabel, c=cmdContinue)
    cmds.button(l='Close', c=cmdClose)

    cmds.showWindow(winName)
    cmds.window(winName, e=1, wh=[width, 50], tlc=[tlc[0] + wh[1] + 38, tlc[1]], rtf=1)


class Slider:

    def __init__(self, **options):
        self.options = options

    def create(self):
        form = cmds.formLayout()
        slider = cmds.floatSliderGrp(**self.options)
        cmds.setParent('..')

        cmds.formLayout(form, e=1,
                        af=[(slider, 'top', 0), (slider, 'left', 0), (slider, 'right', 0)])

        self.form = form
        self.slider = slider

        return form


class Buttons_two:

    def __init__(self, label1='', label2='', h=25):
        self.label1 = label1
        self.label2 = label2
        self.height = h

    def create(self):
        form = cmds.formLayout()
        button1 = cmds.button(l=self.label1, h=self.height)
        button2 = cmds.button(l=self.label2, h=self.height)
        cmds.setParent('..')

        cmds.formLayout(form, e=1,
                        af=[(button1, 'top', 0), (button1, 'left', 0),
                            (button2, 'top', 0), (button2, 'right', 0)],
                        ap=[(button1, 'right', 0, 50),
                            (button2, 'left', 0, 50)])

        self.button1 = button1
        self.button2 = button2

        return form


class Button_changedCondition:

    def __init__(self, labels, colors=None, commands=None, **options):

        self.labels = labels
        self.commands = commands
        self.colors = colors
        self.button = None
        self.currentIndex = 0

        self.options = options

    def create(self):

        self.button = cmds.button(l=self.labels[0], c=self.cmdButton, **self.options)
        if self.colors: cmds.button(self.button, e=1, bgc=self.colors[0])

        return self.button

    def setCommands(self, commands):

        self.commands = commands

    def cmdButton(self, *args):

        if self.commands:
            self.commands[self.currentIndex]()
        cmds.button(self.button, e=1, label=self.labels[self.currentIndex])

    def gotoCondition(self, index):

        cmds.button(self.button, e=1, label=self.labels[index])
        if self.colors: cmds.button(self.button, e=1, bgc=self.colors[index])
        self.currentIndex = index


class OptionMenu:

    def __init__(self, label, nameItems):

        self._label = label
        self._nameItems = nameItems

        self._items = []
        self._menu = ''

    def create(self, cw=[80, 80]):

        self._menu = cmds.optionMenuGrp(l=self._label, cw2=cw)

        for nameItem in self._nameItems:
            self._items.append(cmds.menuItem(l=nameItem))

    def resetMenu(self, nameItems):

        for item in self._items:
            cmds.deleteUI(item)

        self._items = []

        for nameItem in nameItems:
            self._items.append(cmds.menuItem(l=nameItem, p=(self._menu + '|OptionMenu')))


class WinA_Global:
    winName = 'sgWindow_joint_slider'
    title = 'Joint Position Slider'
    width = 450
    height = 50
    txf_topJoint = ''
    txf_endJoint = ''
    slider_joint = ''
    button_set = ''

    slider_form = ''

    num_original = ''
    num_separate = ''
    frame = ''
    bt_setEqually = ''
    bt_setNormally = ''

    windowPtr = None

    globalValueAttr = 'sgJointSliderValueAttr'


class WinA_field_popup:

    def __init__(self, firstLabel, secondLabel):
        self.fieldPopup_first = PopupFieldUI(firstLabel, textWidth=120)
        self.fieldPopup_second = PopupFieldUI(secondLabel, textWidth=120)

    def create(self):
        print "field popup create"
        form = cmds.formLayout()
        fieldPopupFirst_form = self.fieldPopup_first.create()
        fieldPopupSecond_form = self.fieldPopup_second.create()
        cmds.setParent('..')

        cmds.formLayout(form, e=1,
                        af=[(fieldPopupFirst_form, 'top', 0), (fieldPopupFirst_form, 'left', 0),
                            (fieldPopupSecond_form, 'top', 0), (fieldPopupSecond_form, 'right', 0)],
                        ap=[(fieldPopupFirst_form, 'right', 0, 50),
                            (fieldPopupSecond_form, 'left', 0, 50)])

        self.form = form

        WinA_Global.txf_topJoint = self.fieldPopup_first._field
        WinA_Global.txf_endJoint = self.fieldPopup_second._field

        return form


class WinA_frame:

    def __init__(self):
        pass

    def create(self):
        frame = cmds.frameLayout(l='Separate Joint', cl=1, cll=1, cc=self.cmdCollapse)
        form = cmds.formLayout()
        tx_origin = cmds.text(l='Current Joint Number : ', h=25, al='right')
        inf_origin = cmds.intField(w=50)
        bt_equally = cmds.button(l='Separate Equally')
        bt_normally = cmds.button(l='Separate Normally')
        cmds.setParent('..')
        cmds.setParent('..')

        cmds.formLayout(form, e=1,
                        af=[(tx_origin, 'top', 0), (tx_origin, 'left', 0),
                            (inf_origin, 'top', 0),
                            (bt_equally, 'top', 0), (bt_equally, 'left', 0),
                            (bt_normally, 'top', 0), (bt_normally, 'right', 0)],
                        ap=[(tx_origin, 'right', 0, 50), (inf_origin, 'left', 0, 50),
                            (bt_equally, 'right', 0, 50), (bt_normally, 'left', 0, 50)],
                        ac=[(bt_equally, 'top', 0, tx_origin), (bt_normally, 'top', 0, tx_origin)])

        self.frame = frame
        WinA_Global.num_original = inf_origin
        WinA_Global.bt_setEqually = bt_equally
        WinA_Global.bt_setNormally = bt_normally

        return frame

    def cmdCollapse(self, *args):
        cmds.window(WinA_Global.winName, e=1, h=50, rtf=1)


class WinA_Cmd:

    def __init__(self, ptr_window):

        import maya.OpenMaya
        import math

        self.openMaya = maya.OpenMaya
        self.ptr_w = ptr_window
        self.oCurve = None
        self.numPoints = 0
        self.jntH = []
        self.sin = math.sin
        self.maxRadValue = math.pi / 2.0

        self.dragOn = False
        self.beforeValue = 0

        cmds.scriptJob(e=['Undo', self.setUndo], p=self.ptr_w.winName)
        cmds.scriptJob(e=['Redo', self.setRedo], p=self.ptr_w.winName)

        self.setGlobalValue(0)

    def getGlobalAttr(self):

        globalValueAttrs = cmds.ls('*.' + WinA_Global.globalValueAttr)
        if not globalValueAttrs:
            cmds.undoInfo(swf=1)
            node = cmds.createNode('addDoubleLinear')
            cmds.addAttr(node, ln=WinA_Global.globalValueAttr)
            globalValueAttrs = [node + '.' + WinA_Global.globalValueAttr]
        return globalValueAttrs[0]

    def getGlobalValue(self):

        return cmds.getAttr(self.getGlobalAttr())

    def setGlobalValue(self, value):

        return cmds.setAttr(self.getGlobalAttr(), value)

    def updateJointNum(self, *args):

        topJoint = cmds.textField(WinA_Global.txf_topJoint, q=1, tx=1)
        endJoint = cmds.textField(WinA_Global.txf_endJoint, q=1, tx=1)

        endJoint = cmds.ls(endJoint, l=1)[0]
        jntChildren = cmds.listRelatives(topJoint, c=1, ad=1, f=1)
        jntChildren.append(topJoint)
        jntChildren.reverse()

        if not endJoint in jntChildren:
            cmds.frameLayout(WinA_Global.frame, e=1, en=0)
            cmds.floatSliderGrp(WinA_Global.slider_joint, e=1, v=0)
            return False

        index = jntChildren.index(endJoint)
        self.jntH = jntChildren[:index + 1]
        self.numPoints = len(self.jntH)

        cmds.intField(WinA_Global.num_original, e=1, v=self.numPoints)

    def setEditMode(self, topJoint, endJoint, curveEdit=True):

        self.dragOn = False

        endJoint = cmds.ls(endJoint, l=1)[0]
        jntChildren = cmds.listRelatives(topJoint, c=1, ad=1, f=1)
        jntChildren.append(topJoint)
        jntChildren.reverse()

        if not endJoint in jntChildren:
            cmds.frameLayout(WinA_Global.frame, e=1, en=0)
            cmds.floatSliderGrp(WinA_Global.slider_joint, e=1, v=0)
            return False

        index = jntChildren.index(endJoint)
        self.jntH = jntChildren[:index + 1]
        self.numPoints = len(self.jntH)

        cmds.intField(WinA_Global.num_original, e=1, v=self.numPoints)
        cmds.floatSliderGrp(WinA_Global.slider_joint, e=1, v=0)

        self.editCurveByPosition()
        self.setGlobalValue(self.getGlobalValue())

        return True

    def editCurveByPosition(self):

        fnCurve = self.openMaya.MFnNurbsCurve()
        fnCurveData = self.openMaya.MFnNurbsCurveData()
        self.oCurve = fnCurveData.create()

        points = self.openMaya.MPointArray()
        points.setLength(self.numPoints)
        for i in range(points.length()):
            points.set(self.openMaya.MPoint(*cmds.xform(self.jntH[i], q=1, ws=1, t=1)), i)

        fnCurve.createWithEditPoints(points, 3, 1, 0, 0, 1, self.oCurve)
        fnCurve.setObject(self.oCurve)

        self.fnCurve = fnCurve

    def getPositionFromCurve(self, numPoint, equally=False):

        crvLength = self.fnCurve.length()
        originParam = self.fnCurve.findParamFromLength(crvLength)

        points = []

        if equally:
            eacheLengthValue = crvLength / float(numPoint - 1)

            for i in range(numPoint):
                point = self.openMaya.MPoint()
                paramValue = self.fnCurve.findParamFromLength(eacheLengthValue * i)
                self.fnCurve.getPointAtParam(paramValue, point)
                points.append(point)
        else:
            eacheParamValue = originParam / float(numPoint - 1)

            for i in range(numPoint):
                point = self.openMaya.MPoint()
                paramValue = eacheParamValue * i
                self.fnCurve.getPointAtParam(paramValue, point)
                points.append(point)

        return points

    def setJointNum(self, topJoint, endJoint, num, equally):

        import maya.OpenMaya as om
        import pymel.core
        topJointNode = pymel.core.ls(topJoint)[0]
        endJointNode = pymel.core.ls(endJoint)[0]

        def getMObject(nameString):

            selList = om.MSelectionList()
            selList.add(nameString)
            oNode = om.MObject()
            selList.getDependNode(0, oNode)
            return oNode

        jntFnH = [None for i in self.jntH]

        sels = cmds.ls(sl=1)

        originLength = len(jntFnH)
        for i in range(originLength):
            jntFnH[i] = om.MFnDagNode(getMObject(self.jntH[i]))

        diff = num - originLength
        if diff < 0:
            for jntFn in jntFnH[diff - 1:-1]:
                jntChildren = cmds.listRelatives(jntFn.fullPathName(), c=1, f=1)
                for child in jntChildren:
                    cmds.parent(child, w=1)
                cmds.delete(jntFn.fullPathName())
            jntFnH = jntFnH[:diff - 1] + [jntFnH[-1]]
            cmds.parent(jntFnH[-1].fullPathName(), jntFnH[-2].fullPathName())
        elif diff > 0:
            cmds.select(jntFnH[-2].fullPathName())
            rad = cmds.getAttr(jntFnH[-2].fullPathName() + '.radius')
            for i in range(diff):
                jntFnH.insert(-1, om.MFnDagNode(sgBFunction_dag.getMObject(cmds.joint(rad=rad))))
            cmds.parent(jntFnH[-1].fullPathName(), jntFnH[-2].fullPathName())

        positions = self.getPositionFromCurve(num, equally)

        for i in range(1, len(jntFnH) - 1):
            cmds.move(positions[i].x, positions[i].y, positions[i].z, jntFnH[i].fullPathName(), ws=1, pcp=1)

        self.setEditMode(topJointNode.name(), endJointNode.name())
        self.setGlobalValue(self.getGlobalValue())

        if sels:
            existObjs = []
            for sel in sels:
                if cmds.objExists(sel):
                    existObjs.append(sel)
            cmds.select(existObjs)

    def setPositionByValue(self, value, drag=False):

        # poweredValues.append( self.numPoints-1 )
        if drag and not self.dragOn:
            self.dragOn = True
            cmds.undoInfo(swf=0)

        if not drag and self.dragOn:
            self.setValueOlny(self.getGlobalValue())
            self.dragOn = False
            cmds.undoInfo(swf=1)
            self.setGlobalValue(value)

        self.setValueOlny(value)

    def setValueOlny(self, value):

        divValue = float(self.numPoints - 1)
        eacheRadValue = self.maxRadValue / divValue

        poweredValues = []

        for i in range(self.numPoints):
            cuRadValue = i * eacheRadValue
            eacheValue = self.sin(cuRadValue) * divValue
            origValue = i
            poweredValues.append(eacheValue * value + origValue * (1 - value))

        for i in range(1, self.numPoints - 1):
            point = self.openMaya.MPoint()
            self.fnCurve.getPointAtParam(poweredValues[i], point)
            cmds.move(point.x, point.y, point.z, self.jntH[i], ws=1, pcp=1)

    def setUndo(self, *args):

        cmds.floatSliderGrp(self.ptr_w.slider.slider, e=1, v=self.getGlobalValue())
        self.updateJointNum()
        self.editCurveByPosition()

    def setRedo(self, *args):

        cmds.floatSliderGrp(self.ptr_w.slider.slider, e=1, v=self.getGlobalValue())
        self.updateJointNum()
        self.editCurveByPosition()

    def set(self):

        pass


class WinA:

    def __init__(self):

        self.winName = WinA_Global.winName
        self.title = WinA_Global.title
        self.width = WinA_Global.width
        self.height = WinA_Global.height

        self.jointTxfPopup = WinA_field_popup('Top Joint : ', 'End Joint : ')
        self.frame = WinA_frame()
        self.slider = Slider(min=-1, max=1, v=0, pre=2, f=1)

        WinA_Global.windowPtr = self

    def create(self):

        if cmds.window(self.winName, ex=1):
            cmds.deleteUI(self.winName, wnd=1)
        cmds.window(self.winName, title=self.title)

        self.cmd = WinA_Cmd(self)

        form = cmds.formLayout()
        fieldForm = self.jointTxfPopup.create()
        frame = self.frame.create()
        sliderForm = self.slider.create()
        button = cmds.button(l='SET')
        cmds.setParent('..')
        cmds.formLayout(form, e=1,
                        af=[(fieldForm, 'top', 5), (fieldForm, 'left', 0), (fieldForm, 'right', 0),
                            (sliderForm, 'left', 0), (sliderForm, 'right', 0),
                            (frame, 'left', 0), (frame, 'right', 0),
                            (button, 'left', 0), (button, 'right', 0)],
                        ac=[(frame, 'top', 5, fieldForm),
                            (sliderForm, 'top', 0, frame),
                            (button, 'top', 0, sliderForm)])

        cmds.window(self.winName, e=1, wh=[self.width, self.height], rtf=1)
        cmds.showWindow(self.winName)

        WinA_Global.slider_joint = self.slider.slider

        WinA_Global.slider_form = sliderForm
        self.buttonForm = button

        self.conditionControl('default')

        cmds.button(button, e=1, c=self.cmdSet)
        cmds.floatSliderGrp(self.slider.slider, e=1, cc=self.cmdSetPointByChangeValue)
        cmds.floatSliderGrp(self.slider.slider, e=1, dc=self.cmdSetPointByDragValue)

        cmds.button(WinA_Global.bt_setEqually, e=1, c=self.cmdButtonSetEqually)
        cmds.button(WinA_Global.bt_setNormally, e=1, c=self.cmdButtonSetNormally)

        self.jointTxfPopup.fieldPopup_first._addCommand.append(self.updateFirstJoint)
        self.jointTxfPopup.fieldPopup_second._addCommand.append(self.updateSecondJoint)

    def cmdButtonSetEqually(self, *args):

        topJoint = cmds.textField(WinA_Global.txf_topJoint, q=1, tx=1)
        endJoint = cmds.textField(WinA_Global.txf_endJoint, q=1, tx=1)
        num = cmds.intField(WinA_Global.num_original, q=1, v=1)
        self.cmd.setJointNum(topJoint, endJoint, num, True)

    def cmdButtonSetNormally(self, *args):

        topJoint = cmds.textField(WinA_Global.txf_topJoint, q=1, tx=1)
        endJoint = cmds.textField(WinA_Global.txf_endJoint, q=1, tx=1)
        num = cmds.intField(WinA_Global.num_original, q=1, v=1)
        self.cmd.setJointNum(topJoint, endJoint, num, False)

    def cmdSet(self, *args):

        self.conditionControl('edit')
        self.cmdSetEditMode()

    def cmdSetEditMode(self):

        topJnt = cmds.textField(WinA_Global.txf_topJoint, q=1, tx=1)
        endJnt = cmds.textField(WinA_Global.txf_endJoint, q=1, tx=1)
        if not topJnt: return None
        if not cmds.objExists(topJnt): return None
        if not endJnt: return None
        if not cmds.objExists(endJnt): return None
        return self.cmd.setEditMode(topJnt, endJnt)

    def cmdSetPointByChangeValue(self, *args):

        value = cmds.floatSliderGrp(WinA_Global.slider_joint, q=1, v=1)
        self.cmd.setPositionByValue(value)

    def cmdSetPointByDragValue(self, *args):

        value = cmds.floatSliderGrp(WinA_Global.slider_joint, q=1, v=1)
        self.cmd.setPositionByValue(value, True)

    def conditionControl(self, mode='edit', *args):

        if mode == 'default':
            cmds.floatSliderGrp(WinA_Global.slider_joint, e=1, v=0)
            cmds.formLayout(WinA_Global.slider_form, e=1, en=0)
        elif mode == 'edit':
            cmds.floatSliderGrp(WinA_Global.slider_joint, e=1, v=0)
            cmds.formLayout(WinA_Global.slider_form, e=1, en=1)

    def updateFirstJoint(self):

        lastJnt = cmds.listRelatives(cmds.ls(sl=1), c=1, ad=1, f=1)[0]
        cmds.textField(WinA_Global.txf_endJoint, e=1, tx=cmds.ls(lastJnt)[0])
        cmds.intField(WinA_Global.num_original, e=1, v=1)
        self.cmdSetEditMode()
        self.conditionControl('edit')

    def updateSecondJoint(self):

        if self.cmdSetEditMode():
            self.conditionControl('edit')


def show( evt=0 ):
    WinA().create()

if __name__ == '__main__':
    show()
