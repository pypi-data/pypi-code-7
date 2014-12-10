
from PySide.QtGui import QTreeView, QStandardItemModel, QStandardItem
from PySide.QtCore import Qt

from karmadbg.uicore.basewidgets import NativeDataViewWidget
from karmadbg.uicore.async import async

class ProcessExplorerWidget(NativeDataViewWidget):
    
    def __init__(self, widgetSettings, uimanager):
        super(ProcessExplorerWidget,self).__init__(uimanager)
        self.uimanager = uimanager

        self.treeView = QTreeView()
        self.treeView.setHeaderHidden(True)

        self.setWidget(self.treeView)

        self.uimanager.mainwnd.addDockWidget(Qt.TopDockWidgetArea, self)

    def dataUnavailable(self):
        self.treeModel.clear()

    @async
    def dataUpdate(self):
        treeModel = QStandardItemModel(0,1)
        from karmadbg.scripts.proclist import getProcessThreadList
        proclst = yield( self.uimanager.callFunction(getProcessThreadList) )
        for pid, exe, threadLst in proclst:

            processItem = QStandardItem( "Pid: %x" % pid )
            processItem.setEditable(False)
            
            processNameItem = QStandardItem( "Name: %s" % exe )
            processNameItem.setEditable(False)
            processItem.appendRow(processNameItem)

            threadsItem = QStandardItem( "Threads: %d" % len(threadLst))
            for thread in threadLst:
                tidItem = QStandardItem("Id: %x" % thread)
                tidItem.setEditable(False)
                threadsItem.appendRow(tidItem)
            processItem.appendRow(threadsItem)
            treeModel.appendRow(processItem)

        self.treeModel = treeModel
        self.treeView.setModel(self.treeModel)


