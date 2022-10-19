import json
from typing import List
import datetime

DAYS = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'doming']

class JsonManager():

    def __init__(self) -> None:
        self.json_path = r'F:\rasa_chat\data\people.json'
        self.loadJson()

    
    def loadJson(self):
        with open(self.json_path, 'r') as file:
            self.data = json.load(file)

    def saveJson(self, newData):
        with open(self.json_path, 'w') as file:
            json.dump(newData, file)

    def changePath(self, newPath):
        self.json_path = newPath
    
    def getById(self, id):
        idData = self.data.get(str(id))

        return idData

    def saveById(self, id, data):
        self.data.update({str(id): data})
        self.saveJson(self.data)

    def getDataByKey(self, id, keyData):
        data = self.data.get(str(id))
        if not data:
            return
        
        return data.get(keyData)
    
    def saveDataByKey(self, id, key, data):
        info = self.data.get(str(id))
        if info:
            info.update({ key: data })
            self.data.update({ str(id): info })
            self.saveJson(self.data)
        return

class TimeManager():
    
    def __init__(self) -> None:
        self.date = datetime.datetime

    def getNowDate(self):
        return self.date.now()

    def getDay(self):
        dayNum = self.getNowDate().weekday()
        return DAYS[dayNum]

    def getHour(self):
        return self.getNowDate().hour


