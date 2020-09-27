import sqlite3
import json

# Дополнительные функции
def getCountMatrix(database, table):
    # Подключение к БД
    db = sqlite3.connect(database)
    sql = db.cursor()

    sql.execute("SELECT * FROM '%s'" % table)
    data = sql.fetchall()

    try:
        rowCount = len(data)
        columnCount = len(data[0])
    except:
        rowCount = 1
        columnCount = 1

    db.close()

    return rowCount, columnCount, data



def push(database, table, data):
    # Подключение к БД
    db = sqlite3.connect(database)
    sql = db.cursor()

    countCol = len(data[0])
    insertCountCol = []
    for i in range(countCol):
        insertCountCol.append('?')
    insertCountCol = ','.join(insertCountCol)

    sql.execute("DELETE FROM '%s'" % table)
    sql.executemany(f"INSERT INTO '%s' VALUES ({insertCountCol})" % table, data)
    db.commit()
    db.close()


def importFromJson(path):

    with open(path, "r") as file:
        data = json.load(file)

    return data


def exportToJson(database, table, path):
    _, _, data = getCountMatrix(database, table)

    with open(path, "w") as file:
        json.dump(data, file, indent=4)