"""
Customisized QTableWidget
"""
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class ShoppingList(QTableWidget):
    """
    List of products
    """
    sendList = pyqtSignal(object)

    def __init__(self, parent=None):
        """
        :param parent: the parent of this QWidget
        """
        super(ShoppingList, self).__init__(parent)
        self.setColumnCount(3)
        self.horizontalHeader().setVisible(False)  # No Header
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # No edit
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch) # setting only one column
        self.setShowGrid(False)  # deleting the grid

    def displayProduct(self, mylist):
        """
        :param mylist: its element containing three components: str, str, str
        :return: void
        """
        self.clear()
        index = 0
        if len(mylist) >0:
            self.setRowCount(len(mylist))
            for product in mylist:
                name = QTableWidgetItem(product[0])
                name.setFont(QFont('宋体', 20, 70))
                description = QTableWidgetItem(product[1])
                description.setFont(QFont('宋体', 20, 70))
                value = QTableWidgetItem(product[2])
                value.setTextAlignment(Qt.AlignRight)
                value.setFont(QFont('宋体', 20, 70))
                self.setItem(index, 0, name)
                self.setItem(index, 1, description)
                self.setItem(index, 2, value)
                index = index + 1
            self.sendList.emit(mylist)

