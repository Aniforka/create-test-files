from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets, uic
from PyQt5.Qt import QTextCursor
import glob
import sys
import os

PATH_DATA = "func_tests/data" # путь к тестам относительно main.c


class Ui(QtWidgets.QMainWindow, QtWidgets.QWidget): #класс основого интерфейса программы
    resized = QtCore.pyqtSignal()

    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('ui/MainWindow.ui', self)
        #self.resize(self.minimumSize())

        self.initialization_file_tree()

        self.root = prepare_path(PATH_DATA)
        self.load_files_tree()

        self.show()

        self.loadBrowserButton.clicked.connect(self.open_url)
        self.treeWidget.itemClicked.connect(lambda item, column: self.open_file(item, column))
        self.fileEdit.textChanged.connect(self.change_file)
        self.createPositiveButton.clicked.connect(lambda x: self.add_files("pos"))
        self.createNegativeButton.clicked.connect(lambda x: self.add_files("neg"))
        self.clearFilesButton.clicked.connect(self.clear_files)
        #self.browserWidget.tabBarDoubleClicked.connect(lambda index: self.browserWidget.removeTab(index))

        #self.browserWidget.setTabsClosable(True)
        #self.browserWidget.tabCloseRequested.connect(self.close_tab)


    def initialization_file_tree(self):
        tree = self.treeWidget

        tree.clear()

        tree.setColumnCount(2)
        tree.setHeaderLabels(["Имя", "Тип"])
        tree.header().resizeSection(0, 175)

        tree.insertTopLevelItems(0,
            [QtWidgets.QTreeWidgetItem(["Позитивные тесты"]), QtWidgets.QTreeWidgetItem(["Негативные тесты"])]
        )

        tree.topLevelItem(0).setExpanded(True)
        tree.topLevelItem(1).setExpanded(True)


    def open_url(self):
        url = self.url.text() if self.url.text().startswith("http") else "https://" + self.url.text()
        self.url.setText(url)
        self.browserWidget.load(QtCore.QUrl(url))


    def load_files_tree(self):
        check_and_create_folders(self.root)
        files = get_files(self.root)
        tree = self.treeWidget

        for file in files:
            file_name = file.split('/')[-1].split('.')[0]
            file_type = "Пустой" if is_empty_file(file) else "Заполненный"
            item = tree.topLevelItem(0) if file_name.startswith("pos") else tree.topLevelItem(1)
            
            is_added = False
            child = QtWidgets.QTreeWidgetItem([file_name, file_type])

            for i in range(item.childCount()):
                cur_child = item.child(i)

                if cur_child.text(0) == file_name:
                    is_added = True
                    child = cur_child
                    break

            if is_added:
                child.setText(1, file_type)
            else:
                item.addChild(child)


    def open_file(self, item, column):
        text = item.text(0)

        if text.startswith("pos") or text.startswith("neg"):
            file = open(f"{self.root}{text}.txt", "r").read()
            self.fileEdit.setReadOnly(False)
            self.fileEdit.setText(file)
            self.fileEdit.setFocus()

            cursor = self.fileEdit.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.fileEdit.setTextCursor(cursor)

        else: item.setExpanded(not item.isExpanded())


    def change_file(self):
        text = self.fileEdit.toPlainText()
        item = self.treeWidget.selectedItems()[0]

        with open(f"{self.root}{item.text(0)}.txt", "w") as file:
            file.write(text)
        
        self.load_files_tree()


    def add_files(self, type_test):
        files = get_files(self.root)
        count = 0

        for file in files:
            file_name = file.split('/')[-1].split('.')[0]

            if file_name.startswith(type_test): count += 1

        number = str((count // 2) + 1).zfill(2)

        open(f"{self.root}{type_test}_{number}_in.txt", 'w').close()
        open(f"{self.root}{type_test}_{number}_out.txt", 'w').close()

        self.load_files_tree()


    def clear_files(self):
        files = get_files(self.root)

        for file in files:
            os.remove(file)

        self.fileEdit.clear()
        self.fileEdit.setReadOnly(True)
        self.setFocus()

        self.initialization_file_tree()


    def close_tab(self, index):
        if self.browserWidget.count() > 1:
            self.browserWidget.removeTab(index)



def is_empty_file(file):
    return os.stat(file).st_size == 0


def prepare_path(path_data):
    path_data = path_data.replace('\\\\', '/')
    path_data = path_data.replace('\\', '/')

    if path_data.endswith('/'): path_data = path_data[:-1]
    if path_data.startswith('/'): path_data = path_data[1:]

    path = os.path.abspath(__file__)

    path = path.replace("\\\\", '/')
    path = path.replace("\\", '/')

    path = "/".join(path.split('/')[:-1])

    if path.endswith('/'): path = path[:-1]

    root = path + f"/{path_data}/"

    return root


def check_and_create_folders(root):
    if not os.path.exists(root):
        os.makedirs(root)


def get_files(root):
    os.chdir(root)
    types = (f"*.txt") # the tuple of file types
    files_grabbed = list()

    for files in types:
        raw_files = glob.glob(files)

        for file in raw_files:
            if not file.startswith('.'):
                files_grabbed.append(root + file)

    return files_grabbed



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv) #создание приложения
    window = Ui() #получение экземпляра основного интерфейса
    app.exec() #запуск основого интерфейса
