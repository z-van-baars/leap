

class GameTile(object):
    def __init__(self, column, row):
        self.row = row
        self.column = column
        self.road = None
        self.settlement = None
        self.train_station = None
        self.visitors = 0
        self.cost = 1000
        self.destinations = {}

    def __lt__(self, other):
        return False



