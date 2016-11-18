import random
import constants
import utilities
import tile_operations
from constants import colors
import pygame
import queue


class Market(object):
    def __init__(self, map_object, x, y):
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = pygame.Surface([1, 1])
        self.sprite.image.fill(colors["Market Red"])
        self.sprite.image = self.sprite.image.convert_alpha()
        self.trips_completed = 0
        self.x = x
        self.y = y
        self.settled_tiles = [tile_operations.get_tile(map_object, x, y)]
        self.core_tiles = self.set_central_places()
        self.frontier = queue.PriorityQueue()
        self.update_frontier(map_object)

    def check_trips(self, agent_group):
        if self.trips_completed >= constants.TRIPS_FOR_NEW_AGENT:
            agent_group.new_agent(self.x, self.y)
            self.trips_completed -= constants.TRIPS_FOR_NEW_AGENT

    def update_settled_tiles(self, tile):
        self.settled_tiles.append(tile)

    def set_central_places(self):
        central_tiles = queue.PriorityQueue()
        for each in self.settled_tiles:
            if each.settlement and each.settlement.size < 5:
                distance_from_center = utilities.distance(self.x, self.y, each.column, each.row)
                priority = distance_from_center * (random.randint(0, constants.CENTRAL_FUZZINESS))
                central_tiles.put((priority, each))
        return central_tiles

    def update_frontier(self, map_object):
        # floats.  closer to zero is a heavier weighting, greater than 0 is a higher weighting

        evaluated_tiles = {}
        self.frontier = queue.PriorityQueue()
        # print(len(self.settled_tiles))
        for settled_tile in self.settled_tiles:
            neighbors = tile_operations.get_adjacent_tiles(settled_tile, map_object)

            for neighbor_tile in neighbors:
                if neighbor_tile not in evaluated_tiles:
                    if not neighbor_tile.settlement:
                        neighboring_settlements = 0
                        new_neighbors = tile_operations.get_adjacent_tiles(neighbor_tile, map_object)
                        for each in new_neighbors:
                            if each.settlement:
                                neighboring_settlements += 1
                        distance_from_center = utilities.distance(self.x, self.y, neighbor_tile.column, neighbor_tile.row)
                        central_place_score = distance_from_center * constants.CENTRAL_PLACE_WEIGHT * (random.randint(1, constants.FUZZINESS))
                        open_space_score = (neighboring_settlements + 1) * constants.OPEN_SPACE_WEIGHT
                        total_score = open_space_score + central_place_score
                        self.frontier.put((total_score, neighbor_tile))
                        evaluated_tiles[neighbor_tile] = True
                    else:
                        evaluated_tiles[neighbor_tile] = False
        # self.get_prime_real_estate(map_object, CENTRAL_PLACE_WEIGHT)
        # print(self.frontier.qsize())


class Settlement(object):
    def __init__(self, x, y):
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = pygame.Surface([1, 1])
        self.sprite.image.fill(colors["Settled 1"])
        self.size = 1
        self.x = x
        self.y = y

    def grow(self):
        if self.size < 5:
            self.size += 1
            self.sprite.image.fill(colors[constants.settlement_colors[self.size]])


class Road(object):
    def __init__(self, x, y):
        self.size = 0
        self.level = 1
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = pygame.Surface([1, 1])
        self.sprite.image.fill(colors["Road 2"])
        self.x = x
        self.y = y

    def old_grow(self):
        if self.size < (self.level + 1) * (self.level + 1):
            self.size += 1
        else:
            if self.level < 4:
                self.level += 1
                self.size = 0
                self.sprite.image.fill(colors[constants.road_colors[self.level]])

    def grow(self):
        if self.size < 50:
            self.size += 1
        else:
            self.sprite.image.fill(colors["Road 3"])


class TrainStation(object):
    def __init__(self, x, y):
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = pygame.Surface([1, 1])
        self.sprite.image.fill(colors["Train Station"])
        self.x = x
        self.y = y
        self.passed_through = {}
        self.connections = {}

    def add_connection(self, map_object, rail_group, new_station):
        new_rail_path = tile_operations.get_path((self.x, self.y), map_object, (new_station.x, new_station.y))
        rail_group.new_rail(self, new_station, new_rail_path)
        self.connections[new_station] = new_rail_path

    def connection_check(self, map_object, rail_group):
        for each in self.passed_through:
            if self.passed_through[each] > constants.RAIL_CONNECTION_THRESHOLD and each not in self.connections:
                self.add_connection(map_object, rail_group, each)
                each.add_connection(map_object, rail_group, self)


class Rail(object):
    def __init__(self, screen_width, screen_height, a, b, path):
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = pygame.Surface([screen_width, screen_height])
        self.sprite.image.fill(colors["Key"])
        self.a = a
        self.b = b
        self.path = path

        rail_tile = pygame.Surface([1, 1])
        rail_tile.fill(colors["Rail"])
        for each in self.path.steps:
            self.sprite.image.blit(rail_tile, [each.column, each.row])
        self.sprite.image.set_colorkey(colors["Key"])
