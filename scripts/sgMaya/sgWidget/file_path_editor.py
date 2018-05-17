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
        QFont, QGridLayout, QAbstractScrollArea
else:
    from PySide2 import QtGui, QtCore, QtWidgets
    import shiboken2 as shiboken
    from PySide2.QtWidgets import QListWidgetItem, QDialog, QListWidget, QMainWindow, QWidget, QVBoxLayout, QLabel, \
        QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QAbstractItemView, QMenu, QMessageBox, QSplitter, \
        QScrollArea, QSizePolicy, QTextEdit, QApplication, QFileDialog, QCheckBox, QSlider, \
        QTabWidget, QFrame, QTreeWidgetItem, QTreeWidget, QComboBox, QGroupBox, QAction, QGridLayout, QAbstractScrollArea

    from PySide2.QtGui import QColor, QCursor, QBrush, QDoubleValidator, QIntValidator, QImage, QPixmap, QTransform, \
        QPaintEvent, QFont



path_basedir = cmds.about(pd=1) + "/pingo/file_path_editor"


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




class Widget_TypeAttribute( QWidget, Cmds_file_control ):

    def __init__(self, *args, **kwargs ):

        self.attr_name = ""
        self.type_node = ""
        if kwargs.has_key( "attr_name" ):
            self.attr_name = kwargs.pop( "attr_name" )
        if kwargs.has_key( 'type_node' ):
            self.type_node = kwargs.pop( 'type_node' )

        self.path_uiInfo = path_basedir + "/attr_name_%s.json" % self.attr_name

        super( Widget_TypeAttribute, self ).__init__( *args, **kwargs )
        self.installEventFilter( self )

        mainLayout = QHBoxLayout( self ); mainLayout.setContentsMargins( 0,0,0,0 )
        checkBox = QCheckBox(); checkBox.setFixedWidth( 10 )
        checkBox.setChecked( True )
        label = QLabel( '%s ( *.%s )' % (self.type_node, self.attr_name ) )
        mainLayout.addWidget( checkBox )
        mainLayout.addWidget( label )
        self.setFixedHeight( 25 )
        self.checkBox = checkBox
        self.cmds_checkEvent = []

        self.load_check()
        QtCore.QObject.connect(checkBox, QtCore.SIGNAL("stateChanged(int)"), self.save_check)


    def save_check(self, *args ):
        self.save_checkBoxValue( self.checkBox, self.path_uiInfo )
        for cmd in self.cmds_checkEvent:
            try:cmd()
            except:pass

    def load_check(self):
        self.load_checkBoxValue( self.checkBox, self.path_uiInfo )



class Widget_TypeAttributeList( QWidget, Cmds_file_control ):

    url = "https://docs.google.com/spreadsheets/d/1Hor3OMI_WkR2f3cYHU8o_DXZk_Vhto4aALpVycoASYQ/edit?usp=sharing"
    csv = path_basedir + "/data_checkAttrs.csv"

    def __init__(self, *args, **kwargs ):

        super( Widget_TypeAttributeList, self ).__init__( *args, **kwargs )
        self.installEventFilter( self )

        mainLayout = QVBoxLayout( self ); mainLayout.setContentsMargins( 0,0,0,5 )

        groupBox = QGroupBox( "Search Attribute Types"); groupBoxLayout = QVBoxLayout()
        groupBox.setStyleSheet( "font-size:12px")
        groupBox.setLayout( groupBoxLayout ); groupBoxLayout.setContentsMargins(0,0,0,0)
        scrollArea = QScrollArea(); scrollArea.setStyleSheet("font-size:11px")
        scrollAreaWidget = QWidget();
        scrollAreaLayout = QVBoxLayout(scrollAreaWidget)
        scrollArea.setWidgetResizable( True )
        scrollArea.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored) ;
        scrollArea.setWidget( scrollAreaWidget ); scrollAreaLayout.setContentsMargins(5,0,5,0)
        scrollArea.resize( scrollArea.sizeHint() )
        groupBoxLayout.addWidget( scrollArea )

        self.get_csv_form_google_spreadsheets(Widget_TypeAttributeList.url, Widget_TypeAttributeList.csv)
        dict_list = self.get_dictList_from_csvPath(Widget_TypeAttributeList.csv)

        self.w_typeAttrs = []
        for dict_data in dict_list:
            w_typeAttr = Widget_TypeAttribute( attr_name =dict_data['attr_name'], type_node= dict_data['type_node'] )
            scrollAreaLayout.addWidget( w_typeAttr )
            self.w_typeAttrs.append(w_typeAttr)

        empty = QLabel(); empty.setMinimumHeight( 0 )
        scrollAreaLayout.addWidget( empty )
        mainLayout.addWidget( groupBox )

        self.resize( 0, 100 )


    def appendCheckEventCommands(self, cmd ):
        for w_typeAttr in self.w_typeAttrs:
            w_typeAttr.cmds_checkEvent.append( cmd )


class Dialog_deleteUnused( QDialog, Cmds_file_control ):

    objectName = 'sg_pingo_file_path_editor_dialog_deleteUnused'
    title = "Delete unused"
    defaultWidth = 300
    defaultHeight = 300

    def __init__(self, *args, **kwargs):

        super( Dialog_deleteUnused, self ).__init__( *args, **kwargs )
        self.installEventFilter( self )
        self.setObjectName( Dialog_deleteUnused.objectName )
        self.setWindowTitle( Dialog_deleteUnused.title )
        self.resize(Dialog_deleteUnused.defaultWidth, Dialog_deleteUnused.defaultHeight)

        mainLayout = QVBoxLayout(self)
        label_download = QLabel("The following files will be deleted. Continue?".decode('utf-8'))
        label_download.setMaximumHeight(30)
        scrollArea = QScrollArea()
        fileList = QListWidget()
        scrollArea.setWidget(fileList)
        scrollArea.setWidgetResizable(True)
        hLayout_buttons = QHBoxLayout()
        button_delete = QPushButton("Delete All".decode('utf-8'))
        button_cancel = QPushButton("Cancel".decode('utf-8'))
        hLayout_buttons.addWidget(button_delete)
        hLayout_buttons.addWidget(button_cancel)
        mainLayout.addWidget(label_download)
        mainLayout.addWidget(scrollArea)
        mainLayout.addLayout(hLayout_buttons)

        self.fileList = fileList
        self.button_delete = button_delete

        QtCore.QObject.connect(button_delete, QtCore.SIGNAL('clicked()'), self.cmd_deleteSelected )
        QtCore.QObject.connect(button_cancel, QtCore.SIGNAL('clicked()'), self.cmd_cancel )
        QtCore.QObject.connect( self.fileList, QtCore.SIGNAL("itemSelectionChanged()"), self.cmd_setButtonCondition )

        self.fileList.setSelectionMode( QAbstractItemView.ExtendedSelection )


    def cmd_setButtonCondition(self):

        if self.fileList.selectedItems():
            self.button_delete.setText( "Delete Selected" )
        else:
            self.button_delete.setText( "Delete All" )


    def updateFileList(self, paths ):
        self.fileList.clear()
        for path in paths:
            self.fileList.addItem( path )


    def show(self, *args, **kwargs ):
        super( Dialog_deleteUnused, self ).show( *args, **kwargs )
        diffWidth = self.fileList.sizeHint().width() - self.fileList.width()
        self.resize(self.width() - diffWidth, self.height())
        self.move(self.pos().x() + diffWidth * 0.5, self.pos().y())


    def cmd_deleteAll(self):
        for item in [ self.fileList.item( i ) for i in range( self.fileList.count() ) ]:
            os.remove( item.text() )
        self.deleteLater()
        self.parentWidget().loadList()


    def cmd_deleteSelected(self):
        selItems = self.fileList.selectedItems()
        if not selItems:
            selItems = [ self.fileList.item(i) for i in range( self.fileList.count() ) ]
        for item in selItems:
            os.remove( item.text() )
        self.deleteLater()
        self.parentWidget().loadList()


    def cmd_cancel(self):
        self.deleteLater()




class Widget_FileTree( QWidget, Cmds_file_control ):

    path_uiInfo = path_basedir + '/Widget_FileTree/uiInfo.json'
    url = "https://docs.google.com/spreadsheets/d/175Kc_LVWd1K25fjIRo0CIDsjvzCV91natlhD9MhIuik/edit?usp=sharing"
    csv = path_basedir + "/data_extension.csv"

    def __init__(self, *args, **kwargs ):

        self.get_csv_form_google_spreadsheets(Widget_FileTree.url, Widget_FileTree.csv)
        self.dict_extensionList = self.get_dictList_from_csvPath(Widget_FileTree.csv)

        super( Widget_FileTree, self ).__init__( *args, **kwargs )
        self.installEventFilter( self )

        mainLayout = QVBoxLayout( self ); mainLayout.setContentsMargins(0,5,0,0)

        w_basePath = QWidget(); lay_basePath = QHBoxLayout( w_basePath )
        w_basePath.setStyleSheet("font-size:12px")
        lay_basePath.setContentsMargins(5,0,3,0)
        label_basePath = QLabel( "Base Path : " )
        lineEdit_basePath = QLineEdit(); lineEdit_basePath.setMinimumHeight( 22 )
        lineEdit_basePath.setReadOnly( True )
        lay_basePath.addWidget( label_basePath )
        lay_basePath.addWidget( lineEdit_basePath )
        w_tree = QTreeWidget()
        w_tree.setColumnCount(2)
        headerItem = w_tree.headerItem()
        headerItem.setText(0, "File Path" )
        headerItem.setText(1, "Target Node" )
        w_tree.itemExpanded.connect( self.setContentsWidth )
        w_tree.itemCollapsed.connect( self.setContentsWidth )
        w_tree.setSelectionMode( QAbstractItemView.ExtendedSelection )

        self.w_typeAttrList = Widget_TypeAttributeList()

        w_tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        QtCore.QObject.connect(w_tree, QtCore.SIGNAL('customContextMenuRequested(QPoint)'),
                               self.loadContextMenu)

        w_check = QWidget()
        lay_check = QHBoxLayout( w_check ); lay_check.setContentsMargins(5,5,0,10); lay_check.setSpacing(0)
        checkBox = QCheckBox(); checkBox.setFixedWidth( 30 )
        label = QLabel( "Show Unused files in folder");label.setStyleSheet("font-size:12px")
        lay_check.addWidget( checkBox )
        lay_check.addWidget( label )

        mainLayout.addWidget( w_basePath )
        mainLayout.addWidget( w_tree )
        mainLayout.addWidget( w_check )

        self.w_tree = w_tree
        self.checkBox = checkBox
        self.lineEdit = lineEdit_basePath

        self.load_checkBoxValue( checkBox, Widget_FileTree.path_uiInfo )

        QtCore.QObject.connect( checkBox, QtCore.SIGNAL( "stateChanged(int)" ), self.saveCheckBoxValue )
        QtCore.QObject.connect( w_tree,   QtCore.SIGNAL("itemSelectionChanged()"), self.selectItem )


    def saveCheckBoxValue(self, *args ):
        self.save_checkBoxValue( self.checkBox, Widget_FileTree.path_uiInfo )
        self.loadList()


    def loadContextMenu(self, *args):

        menu = QMenu( self.w_tree )
        path = self.w_tree.currentItem().text( 0 )
        if os.path.isdir( path ):
            dirPath = path
        else:
            dirPath = os.path.dirname(path)
        if os.path.exists( dirPath ): menu.addAction(unicode("Open Folder", errors='replace'), self.openFolder)
        menu.addAction( unicode("Copy Path", errors='replace'), self.copyPath )
        separator = QAction( self.w_tree ); separator.setSeparator(True); menu.addAction( separator )
        menu.addAction( unicode("Replace Path", errors='replace'), self.replacePath )
        separator = QAction(self.w_tree);separator.setSeparator(True);menu.addAction(separator)
        if self.unusedExists() : menu.addAction(unicode("Remove Unused Files", errors='replace'), self.removeUnused )
        pos = QCursor.pos()
        point = QtCore.QPoint(pos.x() + 10, pos.y())
        menu.exec_(point)


    def unusedExists(self):

        selectedPaths = []
        for item in self.w_tree.selectedItems():
            if item.childCount():
                for child in [item.child(i) for i in range(item.childCount())]:
                    if child.attrs: continue
                    selectedPaths += [child.text(0)]
            else:
                if item.attrs: continue
                selectedPaths += [item.text(0)]
        if selectedPaths: return True
        return False


    def removeUnused(self):

        selectedPaths = []
        for item in self.w_tree.selectedItems():
            if item.childCount():
                for child in [ item.child(i) for i in range( item.childCount() ) ]:
                    if child.attrs: continue
                    selectedPaths += [ child.text( 0 ) ]
            else:
                if item.attrs: continue
                selectedPaths += [ item.text( 0 ) ]

        dialog = Dialog_deleteUnused( self )
        dialog.updateFileList( selectedPaths )
        dialog.show()


    def copyPath(self):

        import subprocess
        path = self.w_tree.currentItem().text( 0 )
        def copy2clip(txt):
            cmd = 'echo ' + txt.strip() + '|clip'
            return subprocess.check_call(cmd, shell=True)
        copy2clip( path )
        QMessageBox.information( self, self.tr( "Info" ), "The path has been copied.".decode( "utf-8" ), QMessageBox.Ok )


    def openFolder(self):

        import subprocess
        path = self.w_tree.currentItem().text(0)
        if os.path.isdir( path ):
            targetDir = path
        else:
            targetDir = os.path.dirname(path)
        subprocess.call( 'explorer /object, "%s"' % targetDir.replace('/', '\\').encode('cp949') )


    def replacePath(self):

        dirItems = []
        fileItems = []
        if self.w_tree.selectedItems():
            for item in self.w_tree.selectedItems():
                if not item.text(1):
                    dirItems.append( item )
                else:
                    fileItems.append( item )

        dialog_replacePath = Dialog_ReplacePath( self.w_tree.parentWidget() )
        dialog_replacePath.w_tree = self.w_tree
        dialog_replacePath.show()
        if dirItems:
            dialog_replacePath.setPaths( [ dirItem.text(0) for dirItem in dirItems ] )
        elif fileItems:
            dialog_replacePath.setPaths( [ os.path.dirname( fileItems[0].text(0) ) ] )


    def selectItem(self):

        targets = []
        for item in self.w_tree.selectedItems():
            if item.childCount():
                for child in [ item.child(i) for i in range( item.childCount() ) ]:
                    if not child.attrs: continue
                    nodes = [ attr.node() for attr in child.attrs ]
                    targets += nodes
            else:
                if not item.attrs: continue
                nodes = [ attr.node() for attr in item.attrs ]
                targets += nodes
        pymel.core.select( targets, ne=1 )


    def setContentsWidth(self):

        self.w_tree.resizeColumnToContents(0)
        self.w_tree.resizeColumnToContents(1)
        self.w_tree.setColumnWidth( 0, self.w_tree.columnWidth( 0 ) + 10 )


    def loadList(self):

        brush_notExists = QBrush(QColor(255, 150, 120))
        brush_unUsed = QBrush(QColor(120, 180, 255))
        brush_unUsed_and_notExists = QBrush(QColor(225, 120, 225))
        brush_notExists_file = QBrush(QColor(255, 100, 100 ))
        brush_unUsed_file = QBrush(QColor(100, 150, 255 ))

        extensionList = [ dict1['extension'] for dict1 in self.dict_extensionList ]
        extensionList_with_dot = [ '.' + str1 for str1 in extensionList ]

        def cmdByExtension( first, second ):
            firstSplit = os.path.splitext( first )
            secondSplit = os.path.splitext( second )
            if len( firstSplit ) < 2 or len( secondSplit ) < 2:
                return cmp( first, second )
            if not firstSplit[-1] or not secondSplit[-1]: return cmp( first, second )
            if firstSplit[-1][0] != '.' or secondSplit[-1][0] != '.': return cmp( first, second )
            if not firstSplit[-1].lower() in extensionList_with_dot: return cmp(first, second)
            if not secondSplit[-1].lower() in extensionList_with_dot: return cmp(first, second)
            if firstSplit[-1].lower() > secondSplit[-1].lower():
                return 1
            elif firstSplit[-1].lower() < secondSplit[-1].lower():
                return -1
            return cmp( first, second )

        from maya import cmds
        basePath = os.path.dirname( cmds.file( q=1, sceneName=1 ) )
        self.lineEdit.setText( basePath )

        self.w_tree.clear()
        dict_attrs = {}
        for w_typeAttr in self.w_typeAttrList.w_typeAttrs:
            if not w_typeAttr.checkBox.isChecked(): continue
            targetAttrs = pymel.core.ls( '*.%s' % w_typeAttr.attr_name )
            for targetAttr in targetAttrs:
                dirName = os.path.dirname( os.path.normpath( targetAttr.get().strip().lower() ) )
                if not dict_attrs.has_key( dirName ):
                    dict_attrs[ dirName ] = [ targetAttr ]
                else:
                    dict_attrs[ dirName ].append( targetAttr )

        showUnusedDir = self.checkBox.isChecked()
        for dirName in dict_attrs:
            filesInDir = []
            for root, dirs, names in os.walk( dirName ):
                for name in names:
                    targetPath = os.path.normpath( root + '/' + name ).strip().lower()
                    try:ext = os.path.splitext( targetPath )[-1]
                    except:continue
                    if not ext[1:].lower() in extensionList: continue
                    filesInDir.append( targetPath )
                break

            attrList = dict_attrs[ dirName ]
            itemBase = QTreeWidgetItem( self.w_tree )
            itemBase.setText( 0, os.path.normpath( dirName ).strip().lower() )

            notExistsList = []
            unusedList = []

            attrs_from_paths = {}
            for attr in attrList:
                path = os.path.normpath(attr.get().strip().lower())
                if attrs_from_paths.has_key( path ):
                    attrs_from_paths[ path ].append( attr )
                else:
                    attrs_from_paths[ path ] = [ attr ]

            keys_attrs_from_paths = attrs_from_paths.keys()
            keys_attrs_from_paths.sort(cmdByExtension)

            for path in keys_attrs_from_paths:
                item = QTreeWidgetItem( itemBase )
                item.setText( 0, path )
                attrs = attrs_from_paths[ path ]
                attrName = attrs[0].name()
                if len( attrs ) > 1: attrName += '...'
                item.setText(1, attrName )
                item.attrs = attrs

                if not os.path.exists( path ):
                    item.setForeground( 0, brush_notExists_file )
                    notExistsList.append( path )

                if path in filesInDir:
                    filesInDir.remove( path )

            if showUnusedDir:
                for fileInDir in filesInDir:
                    item = QTreeWidgetItem(itemBase)
                    path = os.path.normpath( fileInDir ).strip().lower()
                    item.setText(0, path )
                    item.setForeground( 0, brush_unUsed_file )
                    item.attrs = None
                    unusedList.append( path )

            if unusedList and notExistsList:
                itemBase.setForeground( 0, brush_unUsed_and_notExists )
            elif unusedList:
                itemBase.setForeground( 0, brush_unUsed )
            elif notExistsList:
                itemBase.setForeground( 0, brush_notExists )

        self.w_tree.resizeColumnToContents(0)
        self.w_tree.setColumnWidth(0, self.w_tree.columnWidth(0) + 10)


class Cmds_copy():

    @staticmethod
    def replace( origPaths, replacedPaths, **options ):
        import shutil
        for i in range( len( origPaths ) ):
            if not os.path.exists( origPaths[i] ): continue
            dirname = os.path.dirname( replacedPaths[i] )
            if not os.path.exists( dirname ): os.makedirs( dirname )
            if options.has_key( 'doNotReplace' ):
                if options[ 'doNotReplace' ] and os.path.exists( replacedPaths[i] ): continue
            #print "copy file : ", origPaths[i], replacedPaths[i]
            if origPaths[i] == replacedPaths[i]: continue
            shutil.copy2( origPaths[i], replacedPaths[i] )
        return replacedPaths




class Dialog_ReplacePath_last( QDialog, Cmds_file_control ):

    objectName = "sg_pingo_file_path_editor_last"
    title = "Confirm"
    defaultWidth = 300
    defaultHeight = 100

    def __init__(self, *args, **kwargs ):

        existing_widgets = args[0].findChildren(QDialog, Dialog_ReplacePath_last.objectName)
        if existing_widgets: map(lambda x: x.deleteLater(), existing_widgets)

        super( Dialog_ReplacePath_last, self ).__init__( *args, **kwargs )
        self.installEventFilter( self )
        self.setObjectName( Dialog_ReplacePath_last.objectName )
        self.setWindowTitle( Window.title )
        mainLayout = QVBoxLayout( self )

        w_msg = QLabel( "0 Items aleady exists. Do you want to replace it?" )
        w_list = QListWidget()
        w_buttons = QWidget()
        lay_buttons = QHBoxLayout( w_buttons )
        button_replace = QPushButton( "Replace All" )
        button_noReplace = QPushButton( "Do not Replace" )
        button_cancel = QPushButton("Cancel")
        lay_buttons.addWidget( button_replace ); button_replace.setFixedWidth( 120 )
        lay_buttons.addWidget( button_noReplace )
        lay_buttons.addWidget( button_cancel )

        mainLayout.addWidget( w_msg )
        mainLayout.addWidget( w_list )
        mainLayout.addWidget( w_buttons )

        self.button_replace = button_replace
        self.w_list = w_list
        self.w_msg = w_msg
        self.w_list.setSelectionMode(QAbstractItemView.ExtendedSelection)

        QtCore.QObject.connect(button_replace, QtCore.SIGNAL("clicked()"), self.cmd_replace )
        QtCore.QObject.connect(button_noReplace, QtCore.SIGNAL("clicked()"), self.cmd_noReplace)
        QtCore.QObject.connect(button_cancel, QtCore.SIGNAL("clicked()"), self.deleteLater )
        QtCore.QObject.connect( self.w_list, QtCore.SIGNAL("itemSelectionChanged()"), self.changeButtonCondition )
        self.items = []


    def changeButtonCondition(self):

        if self.w_list.selectedItems():
            self.button_replace.setText( "Replace Selected" )
        else:
            self.button_replace.setText( "Replace All" )



    def addItem(self, sourcePath, destPath, pmAttributes ):

        import ntpath
        dirName, fileName = ntpath.split( sourcePath )
        self.items.append( [sourcePath, destPath, pmAttributes] )

        if  os.path.exists( destPath ):
            wigetItem = QListWidgetItem(fileName)
            wigetItem.sourcePath = sourcePath
            wigetItem.destPath = destPath
            wigetItem.pmAttributes = pmAttributes
            self.w_list.addItem( wigetItem )
        self.w_msg.setText( '%d Items aleady exists at \n[%s] \nDo you want to replace it?' % (self.w_list.count(), os.path.dirname( destPath ) ) )


    def cmd_replace(self):
        selItems = self.w_list.selectedItems()
        cmds.undoInfo(ock=1)

        sourcePaths = []
        destPaths = []
        for sourcePath, destPath, pmAttributes in self.items:
            sourcePaths.append( sourcePath )
            destPaths.append( destPath )
        Cmds_copy.replace( sourcePaths, destPaths )
        for sourcePath, destPath, pmAttributes in self.items:
            if not pmAttributes: continue
            [ attr.set( destPath ) for attr in pmAttributes ]
        cmds.undoInfo(cck=1)
        self.deleteLater()
        self.parentWidget().loadList()


    def cmd_noReplace(self):
        selItems = self.w_list.selectedItems()
        if not selItems:
            selItems = [self.w_list.item(i) for i in range(self.w_list.count())]

        sourcePaths = []
        destPaths = []
        for item in selItems:
            sourcePaths.append(item.sourcePath)
            destPaths.append(item.destPath)
        Cmds_copy.replace(sourcePaths, destPaths, doNotReplace=True )
        cmds.undoInfo( ock=1 )
        if self.items:
            for sourcePath, destPath, pmAttributes in self.items:
                if not pmAttributes: continue
                [ attr.set( destPath ) for attr in pmAttributes ]
            cmds.undoInfo(cck=1)
        self.deleteLater()
        self.parentWidget().loadList()




class Dialog_ReplacePath( QDialog, Cmds_file_control ):

    objectName = "sg_pingo_file_path_editor_replacePath"
    title = "Replace Path"
    defaultWidth = 400
    defaultHeight = 100

    def __init__(self, *args, **kwargs ):

        existing_widgets = args[0].findChildren(QDialog, Dialog_ReplacePath.objectName )
        if existing_widgets: map(lambda x: x.deleteLater(), existing_widgets)

        super( Dialog_ReplacePath, self ).__init__( *args, **kwargs )
        self.installEventFilter( self )
        self.setObjectName(Dialog_ReplacePath.objectName)
        self.setWindowTitle( Window.title )
        mainLayout = QVBoxLayout( self )

        w_path = QWidget()
        lay_path = QHBoxLayout( w_path )
        comboBox = QComboBox(); comboBox.setEditable( True )
        comboBox.setSizeAdjustPolicy( QComboBox.AdjustToContents )
        button_search = QPushButton( "..." ); button_search.setFixedWidth( 30 )
        lay_path.addWidget( comboBox ); lay_path.addWidget( button_search )

        button_replace = QPushButton( "Replace Path" )

        mainLayout.addWidget(w_path)
        mainLayout.addWidget(button_replace)

        self.resize( self.defaultWidth, self.defaultHeight )
        self.comboBox = comboBox

        QtCore.QObject.connect(button_search, QtCore.SIGNAL("clicked()"), self.searchFolder)
        QtCore.QObject.connect(button_replace, QtCore.SIGNAL("clicked()"), self.replaceAndMovePath)
        self.w_tree = Widget_FileTree()


    def searchFolder(self):

        def getFolderFromBrowser(parent, defaultPath=''):
            dialog = QFileDialog(parent)
            dialog.setDirectory(defaultPath)
            choosedFolder = dialog.getExistingDirectory()
            return choosedFolder.replace('\\', '/')

        resultPath = getFolderFromBrowser(self, self.comboBox.currentText() )
        if os.path.exists(resultPath):
            self.comboBox.setCurrentText( resultPath )


    def replaceAndMovePath(self):

        from maya import cmds
        import ntpath

        cmds.undoInfo(ock=1)

        currentText = self.comboBox.currentText().strip()
        if not os.path.normpath(currentText).strip().lower():
            QMessageBox.warning(self, self.tr("Warning"), "The path is invalid.".decode("utf-8"), QMessageBox.Ok)
            return

        selItem = self.w_tree.selectedItems()[0]
        targetItems = []
        if selItem.text(1):
            targetItems = self.w_tree.selectedItems()
        else:
            for topLevelItem in self.w_tree.selectedItems():
                if os.path.normpath(topLevelItem.text(0)) == os.path.normpath(currentText): continue
                for j in range(topLevelItem.childCount()):
                    targetItems.append(topLevelItem.child(j))

        origPaths = []
        destPaths = []
        sameExists= False
        for item in targetItems:
            origPath = os.path.normpath(item.text(0).strip().lower())
            destPath = os.path.normpath( (currentText + '/' + ntpath.split(origPath)[-1]).lower() )
            origPaths.append( origPath )
            destPaths.append( destPath )
            if os.path.exists( destPath ): sameExists=True

        if sameExists:
            dialog_replacePath_last = Dialog_ReplacePath_last(self.parentWidget())
            for item in targetItems:
                origPath = os.path.normpath(item.text(0).strip().lower())
                destPath = os.path.normpath((currentText + '/' + ntpath.split(origPath)[-1]).lower())
                dialog_replacePath_last.addItem(origPath, destPath, item.attrs)
            self.deleteLater()
            dialog_replacePath_last.show()
        else:
            Cmds_copy.replace( origPaths, destPaths )
            cmds.undoInfo(ock=1)
            for item in targetItems:
                origPath = os.path.normpath(item.text(0).strip().lower())
                destPath = os.path.normpath((currentText + '/' + ntpath.split(origPath)[-1]).lower())
                if not item.attrs: continue
                [ attr.set( destPath ) for attr in item.attrs ]
            cmds.undoInfo(cck=1)
            self.deleteLater()
            self.parentWidget().loadList()

    def setPaths(self, paths ):
        for path in paths:
            self.comboBox.addItem( os.path.normpath(path.strip().lower()) )
        diffWidth = self.comboBox.sizeHint().width() - self.comboBox.width()
        self.resize( self.width() + diffWidth, self.height() )
        self.move( self.pos().x() - diffWidth * 0.5, self.pos().y() )



class Widget_splitter( QSplitter, Cmds_file_control ):

    path_uiInfo = path_basedir + '/Widget_splitter/uiInfo.json'

    def __init__(self, *args, **kwargs ):

        super( Widget_splitter, self ).__init__( *args, **kwargs )
        QtCore.QObject.connect(self, QtCore.SIGNAL('splitterMoved(int,int)'), self.saveSplitterPosition )
        self.setSizes( [100,100] )

    def saveSplitterPosition(self, posX, posY ):
        self.save_splitterPosition( self, Widget_splitter.path_uiInfo )

    def loadSplitterPosition(self):
        self.load_splitterPosition(self, Widget_splitter.path_uiInfo)



class Widget_Separator( QFrame ):

    def __init__(self, *args, **kwargs ):
        super( Widget_Separator, self ).__init__( *args, **kwargs )
        self.setFrameShape(QFrame.HLine)



class Window(QDialog, Cmds_file_control ):

    mayaWin = shiboken.wrapInstance(long(maya.OpenMayaUI.MQtUtil.mainWindow()), QWidget)
    objectName = "sg_pingo_file_path_editor"
    title = "PINGO - File Path Editor"
    defaultWidth = 400
    defaultHeight = 400
    path_uiInfo = path_basedir + "/uiInfo.json"

    def __init__(self, *args, **kwrgs):

        existing_widgets = Window.mayaWin.findChildren( QDialog, Window.objectName )
        if existing_widgets: map( lambda x: x.deleteLater(), existing_widgets )

        super( Window, self ).__init__( *args, **kwrgs )

        self.installEventFilter( self )
        self.setObjectName( Window.objectName )
        self.setWindowTitle( Window.title )
        mainLayout = QVBoxLayout( self )

        w_splitter = Widget_splitter( QtCore.Qt.Vertical )
        w_typeAttrList = Widget_TypeAttributeList()
        w_fileTree = Widget_FileTree()
        button_refresh = QPushButton("REFRESH".decode('utf-8'))
        button_refresh.setStyleSheet("font-size:13px")

        w_splitter.addWidget( w_typeAttrList )
        w_splitter.addWidget( w_fileTree )

        mainLayout.addWidget(w_splitter)
        mainLayout.addWidget( button_refresh )
        button_refresh.setFocus()

        self.w_typeAttrList = w_typeAttrList
        self.w_fileTree = w_fileTree

        self.resize( Window.defaultWidth, Window.defaultHeight )
        self.load_shapeInfo( Window.path_uiInfo )

        QtCore.QObject.connect( button_refresh, QtCore.SIGNAL("clicked()"), self.w_fileTree.loadList )
        self.w_fileTree.w_typeAttrList = self.w_typeAttrList
        self.w_fileTree.loadList()

        self.w_typeAttrList.appendCheckEventCommands( self.w_fileTree.loadList )
        w_splitter.loadSplitterPosition()


    def eventFilter(self, *args, **kwargs ):
        event = args[1]
        if event.type() in [ QtCore.QEvent.Resize, QtCore.QEvent.Move ]:
            try:self.save_shapeInfo( Window.path_uiInfo )
            except:pass



def show():
    try: cmds.deleteUI( Window.objectName, wnd=1 )
    except:pass
    Window(Window.mayaWin).show()


if __name__ == '__main__':
    show()