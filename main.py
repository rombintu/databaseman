# by Nickolsky
import sys
import form
import os
import sqlite3
import functions

from PyQt5 import QtWidgets



class App(QtWidgets.QMainWindow, form.Ui_MainWindow):
    def __init__(self):
        super(App, self).__init__()
        self.setupUi(self)

        # Меню бар (открыть файл)
        self.action.triggered.connect(self.openFiles)
        # Функции - кнопки
        self.pushButton.clicked.connect(self.addData)
        self.pushButton_2.clicked.connect(self.delData)
        self.pushButton_3.clicked.connect(self.saveChanged)
        # Опции - кнопки
        self.pushButton_4.clicked.connect(self.importData)
        self.pushButton_5.clicked.connect(self.exportData)
        # +\- Таблица
        self.addTableButton.clicked.connect(self.addTable)
        self.delTableButton.clicked.connect(self.delTable)

        # Изменение вывода при выборе таблицы
        self.listWidget.itemActivated.connect(self.showTable)


    def openFiles(self):
        self.lineEdit_2.setText('Таблица')
        self.listWidget.clear()
        DB = QtWidgets.QFileDialog.getOpenFileName(self, 'Выбери файл', os.path.abspath(os.curdir), '*.db')[0]
        if '.db' in DB:
            self.lineEdit.setText(f'{DB}')

            # Подключение к БД
            db = sqlite3.connect(DB)
            sql = db.cursor()
            sql.execute("SELECT * FROM sqlite_master WHERE TYPE='table'")
            tables = sql.fetchall()

            arrTablesNames = []
            for table in tables:
                # Получаем имена таблиц
                nameTable = table[1]
                arrTablesNames.append(nameTable)

            for table in arrTablesNames:
                self.listWidget.addItem(table)
        else:
            errorWin = QtWidgets.QErrorMessage(self)
            errorWin.showMessage('Ожидается файл *.db')


    def showTable(self, item):

        DB = self.lineEdit.text()
        tableName = item.text()

        # вытаскиваем названия колонок

        db = sqlite3.connect(DB)
        sql = db.cursor()

        ColumnsNames = []
        sql.execute("SELECT * FROM '%s'" % tableName)
        columns = sql.description
        for nameColumn in columns:
            col = nameColumn[0]
            ColumnsNames.append(str(col))

        self.lineEdit_2.setText(tableName)
        rowCount, columnCount, data = functions.getCountMatrix(DB, tableName)

        # Создание таблицы
        self.tableWidget.setRowCount(rowCount)
        self.tableWidget.setColumnCount(columnCount)
        self.tableWidget.setHorizontalHeaderLabels(ColumnsNames)

        row = 0
        for element in data:
            col = 0
            for item in element:
                oneCell = QtWidgets.QTableWidgetItem(item)
                self.tableWidget.setItem(row, col, oneCell)
                col += 1
            row += 1


    # Работа с данными
    def addTable(self):
        if self.lineEdit.text() == 'База данных не выбрана':
            errorWin = QtWidgets.QErrorMessage(self)
            errorWin.showMessage('База данных не выбрана')
            return False
        tableName, yes = QtWidgets.QInputDialog.getText(self, 'Новая таблица', 'Название таблицы:')
        Cols, yes2 = QtWidgets.QInputDialog.getText(self, 'Колонки', 'Название колонок через запятую:')
        if yes and yes2:
            DB = self.lineEdit.text()
            # Подключение к БД
            db = sqlite3.connect(DB)
            sql = db.cursor()
            try:
                data = []
                insertCountCol = []
                countCol = len(Cols.split(','))

                for i in range(countCol):
                    data.append('NULL')
                    insertCountCol.append('?')

                insertCountCol = ','.join(insertCountCol)

                sql.execute(f"CREATE TABLE '%s' ({Cols})" % tableName)
                sql.executemany(f"INSERT INTO '%s' VALUES ({insertCountCol})" % tableName, [data])
                db.commit()
                self.listWidget.addItem(tableName)
            except:
                errorWin = QtWidgets.QErrorMessage(self)
                errorWin.showMessage('Таблица уже создана')
                return False


    def delTable(self):
        table = self.lineEdit_2.text()
        try:
            self.lineEdit_2.setText('Таблица')
            DB = self.lineEdit.text()
            # Подключение к БД
            db = sqlite3.connect(DB)
            sql = db.cursor()
            sql.execute("DROP TABLE '%s'" % table)
            db.commit()

            errorWin = QtWidgets.QErrorMessage(self)
            errorWin.showMessage('Таблица удалена')

            index = self.listWidget.currentRow()
            self.listWidget.takeItem(index)


        except:
            errorWin = QtWidgets.QErrorMessage(self)
            errorWin.showMessage('Не удалось удалить таблицу')
            return False

    # Добавить строку
    def addData(self):

        rows = self.tableWidget.rowCount()
        columns = self.tableWidget.columnCount()

        self.tableWidget.setRowCount(rows + 1)
        self.tableWidget.setColumnCount(columns)


    def saveChanged(self):
        if self.lineEdit.text() == 'База данных не выбрана':
            return False
        DB = self.lineEdit.text()
        tableName = self.lineEdit_2.text()

        rows = self.tableWidget.rowCount()
        columns = self.tableWidget.columnCount()

        newData = []
        for rowCount in range(rows):
            buff = []
            for colCount in range(columns):
                try:
                    buff.append(self.tableWidget.item(rowCount, colCount).text())
                except:
                    buff.append('NULL')
            newData.append(buff)

        try:
            functions.push(DB, tableName, newData)
        except:
            errorWin = QtWidgets.QErrorMessage(self)
            errorWin.showMessage('Таблица не выбрана, изменять нечего')


    def delData(self):
        # Получаем выбранные ячейки
        selectedItems = self.tableWidget.selectedItems()
        try:
            row = selectedItems[0].row()
        except:
            row = self.tableWidget.rowCount() - 1

        self.tableWidget.removeRow(row)


    # Экспорт - импорт
    def importData(self):
        if self.lineEdit.text() == 'База данных не выбрана':
            return False


        newFile = QtWidgets.QFileDialog.getOpenFileName(self, 'Выбери импортируемый файл', os.path.abspath(os.curdir), '*.json')

        try:
            data = functions.importFromJson(newFile[0])
        except:
            errorWin = QtWidgets.QErrorMessage(self)
            errorWin.showMessage('Произошла ошибка')

        oldRows = self.tableWidget.rowCount()
        oldCols = self.tableWidget.columnCount()
        newRows = len(data)
        newCols = len(data[0])

        if oldCols != newCols:
            errorWin = QtWidgets.QErrorMessage(self)
            errorWin.showMessage('Колонок меньше или больше')
            return False

        self.tableWidget.setRowCount(oldRows + newRows)

        row = oldRows - 1
        for element in data:
            col = oldCols
            for item in element:
                oneCell = QtWidgets.QTableWidgetItem(item)
                self.tableWidget.setItem(row, col, oneCell)
                col += 1
            row += 1

    def exportData(self):
        if self.lineEdit.text() == 'База данных не выбрана':
            return False

        DB = self.lineEdit.text()
        tableName = self.lineEdit_2.text()

        newFile = QtWidgets.QFileDialog.getSaveFileName(self, 'Выбери куда сохранить файл', os.path.abspath(os.curdir), '*.json')

        try:
            functions.exportToJson(DB, tableName, newFile[0])
        except:
            errorWin = QtWidgets.QErrorMessage(self)
            errorWin.showMessage('Произошла ошибка')



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = App()
    win.show()
    app.exec_()
