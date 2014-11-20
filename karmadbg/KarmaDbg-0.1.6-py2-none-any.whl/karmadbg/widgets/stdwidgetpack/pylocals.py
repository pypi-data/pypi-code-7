
from PySide.QtCore import Qt
from PySide.QtGui import QStandardItemModel, QStandardItem, QTreeView

from karmadbg.uicore.async import async
from karmadbg.uicore.basewidgets import PythonDataViewWidget

class PythonLocalsWidget(PythonDataViewWidget):

    def __init__(self, widgetSettings, uimanager): 
        super(PythonLocalsWidget,self).__init__(uimanager)

        self.uimanager = uimanager
        self.treeView = QTreeView()
        self.treeView.setModel(self.buildModel())

        self.setWidget(self.treeView)

        self.uimanager.mainwnd.addDockWidget(Qt.TopDockWidgetArea, self)

    def dataUnavailable(self):
        self.treeView.setModel(self.buildModel())

    @async
    def dataUpdate(self):
        model = self.buildModel()
        localvars= yield( self.uimanager.debugClient.getPythonLocalsAsync( () ) )
        for var in localvars:
            row = [ QStandardItem(var[0]), QStandardItem(var[1]) ]
            subitems = yield( self.uimanager.debugClient.getPythonLocalsAsync( (var[0],) ))
            for subitem in subitems:
                row[0].appendRow( [ QStandardItem(subitem[0]), QStandardItem(subitem[1]) ] )
            model.appendRow(row)
        self.treeView.setModel(model)

    
    def buildModel(self):
        treeViewModel = QStandardItemModel(0,2)
        for section, title in { 0 : "Name", 1 : "Value"}.items():
             treeViewModel.setHorizontalHeaderItem( section, QStandardItem(title) )
        return treeViewModel
