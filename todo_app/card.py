class Card:
    def __init__(self, name, idList, idCard=None, idBoard=None):
        self.name = name
        self.idList = idList
        self.id = idCard
        self.idBoard = idBoard

    def setIdBoard(self, idBoard):
        self.idBoard = idBoard

    def setIdList(self, idList):
        self.idList = idList

    def json(self):
        result = {
            "name": self.name,
            "id": self.id,
            "idList": self.idList
        }
        return result