import utilities
import display_layer
import constants
import agent
import buildings


class ObjectGroup(object):
    def __init__(self, width, height):
        self.members = []
        self.width = width
        self.height = height
        self.display_layer = display_layer.DisplayLayer(width, height)


class RailGroup(ObjectGroup):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.display_layer = display_layer.RailLayer(width, height)

    def new_rail(self, a, b, path):
        new_rail = buildings.Rail(self.width, self.height, a, b, path)
        self.members.append(new_rail)
        self.display_layer.update(new_rail)


class AgentGroup(ObjectGroup):
    def __init__(self, width, height):
        super().__init__(width, height)

    def new_agent(self, x, y):
        self.members.append(agent.Agent(x, y))


class RoadGroup(ObjectGroup):
    def __init__(self, width, height):
        super().__init__(width, height)

    def new_road(self, tile):
        new_road = buildings.Road(tile.column, tile.row)
        tile.road = new_road
        tile.cost = 1
        self.members.append(new_road)
        self.display_layer.update(new_road)


class MarketGroup(ObjectGroup):
    def __init__(self, width, height):
        super().__init__(width, height)

    def new_market(self, map_object, x, y):
        self.members.append(buildings.Market(map_object, x, y))


class SettlementGroup(ObjectGroup):
    def __init__(self, width, height):
        super().__init__(width, height)

    def new_settlement(self, tile):
        new_settlement = buildings.Settlement(tile.column, tile.row)
        tile.settlement = new_settlement
        self.members.append(new_settlement)
        self.display_layer.update(new_settlement)


class TrainStationGroup(ObjectGroup):
    def __init__(self, width, height):
        super().__init__(width, height)

    def new_station(self, tile):
        closest_station = 10000
        for each in self.members:
            station_distance = utilities.distance(tile.column, tile.row, each.x, each.y)
            if station_distance < closest_station:
                closest_station = station_distance
        if closest_station >= constants.MIN_STATION_DISTANCE:
            new_station = buildings.TrainStation(tile.column, tile.row)
            tile.train_station = new_station
            self.members.append(new_station)
