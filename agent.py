import random
import constants
import utilities
import tile_operations
from constants import colors
import navigate
import pygame


class Agent(object):
    def __init__(self, x, y):
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = pygame.Surface([1, 1])
        self.sprite.image.fill(colors["Agent Green"])
        self.sprite.image = self.sprite.image.convert_alpha()
        self.vector = (0, 0)
        self.x = x
        self.y = y
        self.target = None
        self.target_market = None
        self.stations_visited_this_trip = []

    def clear_target(self):
        self.target = None
        change_market_odds = 30
        if random.randint(0, 100) < change_market_odds:
            self.target_market = None

    def set_target(self, x, y):
        self.target = (x, y)

    def random_variance_target(self, map_object, target_market, x_variance, y_variance):
        x_rolls = []
        y_rolls = []
        number_of_x_rolls = 8
        number_of_y_rolls = 8
        for ii in range(number_of_x_rolls):
            x_rolls.append(random.randint(-x_variance, x_variance))
        for ii in range(number_of_y_rolls):
            y_rolls.append(random.randint(-y_variance, y_variance))
        x = self.target_market.x + utilities.get_smallest(x_rolls)
        y = self.target_market.y + utilities.get_smallest(y_rolls)
        my_tile = tile_operations.get_tile(map_object, self.x, self.y)
        if within_map(x, y, map_object):
            tile = tile_operations.get_tile(map_object, x, y)
            return True, (x, y)
        return False, (x, y)

    def weighted_frontier_target(self, map_object, target_market):
        if target_market.core_tiles.qsize() > 0:
            chance_to_redevelop = random.randint(0, 100)
            if chance_to_redevelop >= constants.REDEVELOP_VALUE:
                (priority, target_tile) = target_market.core_tiles.get()
                target_market.core_tiles.put((priority, target_tile))
            else:
                (priority, target_tile) = target_market.frontier.get()
                target_market.frontier.put((priority, target_tile))
        else:
            (priority, target_tile) = target_market.frontier.get()
            target_market.frontier.put((priority, target_tile))
        x = target_tile.column
        y = target_tile.row
        if tile_operations.within_map(x, y, map_object):
            return True, (x, y)
        return False, (x, y)

    def get_target(self, map_object, markets):
        if not self.target_market:
            self.target_market = random.choice(markets)
        assert self.target_market
        target_chosen = False
        while not target_chosen:
            # target_chosen = self.random_variance_target(map_object, self.target_market, x_variance, y_variance)
            target_chosen, (x, y) = self.weighted_frontier_target(map_object, self.target_market)
        # print("Market: {0}, target: {1}".format((target_market.x, target_market.y), (x, y)))
        return (x, y)

    def clear_vector(self):
        self.vector = (0, 0)

    def set_vector(self, a, b, x, y):
        # A B pair is Target Coordinates
        # X Y pair is Agent Coordinates
        speed = 1
        distance_to_target = utilities.distance(a, b, x, y)
        factor = distance_to_target / speed
        x_dist = a - x
        y_dist = b - y
        change_x = x_dist / factor
        change_y = y_dist / factor

        return (change_x, change_y)

    def settle(self, settlement_group, tile):
        if tile.settlement:
            tile.settlement.grow()
            settlement_group.display_layer.update(tile.settlement)
        else:
            settlement_group.new_settlement(tile)
            self.target_market.update_settled_tiles(tile)
        self.target_market.core_tiles = self.target_market.set_central_places()

    def pave(self, map_object, road_group):
        tile = tile_operations.get_tile(map_object, self.x, self.y)
        tile.visitors += 1
        if tile.visitors > constants.ROAD_THRESHOLD:
            if tile.road:
                tile.road.grow()
                road_group.display_layer.update(tile.road)
            else:
                road_group.new_road(tile)

    def path_move(self):
        new_tile = self.path.steps.pop(0)
        self.x = new_tile.column
        self.y = new_tile.row

    def vector_move(self):
        self.x += self.vector[0]
        self.y += self.vector[1]
        self.clear_vector()

    def visit(self, map_object, station_group, rail_group, road_group):
        tile = tile_operations.get_tile(map_object, self.x, self.y)
        tile.visitors += 1
        if tile.train_station:
            if self.stations_visited_this_trip:
                previous_station = self.stations_visited_this_trip[-1]
                if previous_station in tile.train_station.passed_through:
                    tile.train_station.passed_through[previous_station] += 1
                else:
                    if previous_station != tile.train_station:
                        tile.train_station.passed_through[previous_station] = 1
                    else:
                        print("Can't visit the same station twice!!")
            self.stations_visited_this_trip.append(tile.train_station)
            tile.train_station.connection_check(map_object, rail_group)
            map_object.set_costs(road_group, rail_group)
        if tile.visitors > constants.STATION_THRESHOLD and not tile.train_station:
            station_group.new_station(tile)

    def find_closest_station(self, target, station_group):
        closest_station = (None, None)
        for each in station_group.members:
            distance_from_target = utilities.distance(self.target[0], self.target[1], each.x, each.y)
            if not closest_station[0]:
                closest_station = (each, distance_from_target)
            if closest_station[0] and distance_from_target < closest_station[1]:
                closest_station = (each, distance_from_target)
        return closest_station

    def plot_course(self, map_object, road_group, station_group, rail_group):
        closest_station_to_target = self.find_closest_station(self.target, station_group)
        closest_station_to_me = self.find_closest_station((self.x, self.y), station_group)
        if closest_station_to_me[0] and closest_station_to_target[0]:
            if closest_station_to_target[0] in closest_station_to_me[0].connections:
                aggregate_path = self.station_to_station(map_object, closest_station_to_me[0], closest_station_to_target[0], self.target)
                self.path = aggregate_path
                print("Station to station1")
            else:
                closest_connection = self.find_closest_station(self.target, closest_station_to_me[0].connections)
                for each in station_group:
                    if closest_station_to_target[0] in each.connections:
                        aggregate_path = self.station_to_station(map_object, closest_station_to_me[0], closest_connection, (each.x, each.y))
                print("Stations don't connect")
                print(closest_station_to_me[0].connections)
                self.path = navigate.get_path((self.x, self.y), map_object, self.target)
        else:
            # print("Less than two stations")
            self.path = navigate.get_path((self.x, self.y), map_object, self.target)

    def station_to_station(self, map_object, station_a, station_b, target):
        aggregate_path = navigate.Path()
        path_to_station = navigate.get_path((round(self.x), round(self.y)), map_object, (station_a.x, station_a.y))
        aggregate_path.tiles.extend(path_to_station.tiles)
        aggregate_path.steps.extend(path_to_station.steps)
        rail_path = station_a.connections[station_b]
        if aggregate_path.tiles[-1] == rail_path.tiles[0]:
            print("DUPLICATE TILE DETECTED IN RAIL LINE")
            aggregate_path.tiles.extend(rail_path.tiles[1:])
            aggregate_path.steps.extend(rail_path.steps[1:])
        else:
            aggregate_path.tiles.extend(rail_path.tiles)
            aggregate_path.steps.extend(rail_path.steps)
        path_from_station = navigate.get_path((station_b.x, station_b.y), map_object, target)
        if aggregate_path.tiles[-1] == path_from_station.tiles[0]:
            print("DUPLICATE TILE DETECTED AFTER RAIL LINE")
            aggregate_path.tiles.extend(path_from_station.tiles[1:])
            aggregate_path.steps.extend(path_from_station.steps[1:])
        else:
            aggregate_path.tiles.extend(path_from_station.tiles)
            aggregate_path.steps.extend(path_from_station.steps)
        second_to_last = aggregate_path.steps[-2]
        last = aggregate_path.steps[-1]
        if second_to_last == last:
            aggregate_path.steps.pop(-1)
            aggregate_path.tiles.pop(-1)
        previous = None
        for each in aggregate_path.steps:
            # print("x:{0}, y:{1}".format(each.column, each.row))
            if previous == each:
                print("DUPLICATE DETECTED AFTER COMPLETION")
            previous = each
        return aggregate_path

    def check_target(self, map_object, settlement_group):
        if (round(self.x), round(self.y)) == self.target:
            self.target_market.trips_completed += 1

            self.settle(settlement_group, tile_operations.get_tile(map_object, self.x, self.y))
            self.target_market.update_frontier(map_object)
            self.clear_target()
            self.path = None

    def tick_cycle(self, map_object, market_group, settlement_group, road_group, station_group, rail_group):
        if not self.target or not self.target_market:
            self.target = self.get_target(map_object, market_group.members)
            # self.plot_course(map_object, road_group, station_group, rail_group)
            self.path = navigate.get_path((self.x, self.y), map_object, self.target)
        self.pave(map_object, road_group)
        # self.vector = self.set_vector(self.target[0], self.target[1], self.x, self.y)
        # self.vector_move()
        self.path_move()
        # self.visit(map_object, station_group, rail_group, road_group)
        self.check_target(map_object, settlement_group)
