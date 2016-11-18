import pygame
import random
import math
import queue
from game_tile import GameTile
import copy


colors = {"Key": (255, 0, 128),
          "Background Dark Blue": (4, 5, 36),
          "Background Medium Blue": (10, 15, 55),
          "Background Light Blue": (16, 29, 81),
          "Agent Green": (85, 215, 70),
          "Market Red": (180, 56, 56),
          "Road 1": (17, 17, 31),
          "Road 2": (23, 23, 41),
          "Road 3": (31, 31, 55),
          # "Road 1": (255, 255, 255),
          # "Road 2": (255, 255, 255),
          # "Road 3": (255, 255, 255),
          "Train Station": (217, 72, 214),
          "Subtle Rail": (23, 23, 41),
          "Rail": (255, 105, 46),
          "Settled 1": (76, 58, 74),
          "Settled 2": (182, 153, 119),
          "Settled 3": (231, 217, 154),
          "Settled 4": (255, 246, 186),
          "Settled 5": (253, 250, 235)}


settlement_colors = {1: "Settled 1",
                     2: "Settled 2",
                     3: "Settled 3",
                     4: "Settled 4",
                     5: "Settled 5"}


road_colors = {1: "Road 1",
               2: "Road 2",
               3: "Road 3"}


# Constant Parameters
"""ROAD_THRESHOLD: Higher number means more visitors are required before a tile becomes a road
and is eligible for upgrades

STATION_THRESHOLD: Same as road threshold but for train station objects instead of road tiles

Min_STATION_DISTANCE: For a new train station to generate, the new station must be at least
this many tiles away from any existing stations.  Prevents station redundancy in market radii

RAIL_CONNECTION_THRESHOLD: How many times a visiter must visit a station after passing through
another station on the same trip before a rail link is constructed between the two.  A lower
number encourages branching.

NUMBER_OF_AGENTS: Number of Agents to generate at runtime

NUMBER_OF_MARKETS: Number of Markets to generate at runtime"""

ROAD_THRESHOLD = 10
STATION_THRESHOLD = 10
MIN_STATION_DISTANCE = 30
RAIL_CONNECTION_THRESHOLD = 3
NUMBER_OF_AGENTS = 20
NUMBER_OF_MARKETS = 1


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

    def get_target(self, map_object, markets):
        if not self.target_market:
            self.target_market = random.choice(markets)
        assert self.target_market
        x_variance = 30
        y_variance = 30
        target_chosen = False
        while not target_chosen:
            x_rolls = []
            y_rolls = []
            number_of_x_rolls = 4
            number_of_y_rolls = 4
            for ii in range(number_of_x_rolls):
                x_rolls.append(random.randint(-x_variance, x_variance))
            for ii in range(number_of_y_rolls):
                y_rolls.append(random.randint(-y_variance, y_variance))
            x = self.target_market.x + get_smallest(x_rolls)
            y = self.target_market.y + get_smallest(y_rolls)
            my_tile = get_tile(map_object, self.x, self.y)
            if within_map(x, y, map_object):
                tile = get_tile(map_object, x, y)
                if tile not in get_adjacent_tiles(my_tile, map_object):
                    target_chosen = True
        # print("Market: {0}, target: {1}".format((target_market.x, target_market.y), (x, y)))
        return (x, y)

    def clear_vector(self):
        self.vector = (0, 0)

    def set_vector(self, a, b, x, y):
        # A B pair is Target Coordinates
        # X Y pair is Agent Coordinates
        speed = 1
        distance_to_target = distance(a, b, x, y)
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

    def pave(self, map_object, road_group):
        tile = get_tile(map_object, self.x, self.y)
        tile.visitors += 1
        if tile.visitors > ROAD_THRESHOLD:
            if tile.road:
                tile.road.grow()
                road_group.display_layer.update(tile.road)
            else:
                road_group.new_road(tile)

    def move(self, map_object):
        new_tile = self.path.steps.pop(0)
        self.x = new_tile.column
        self.y = new_tile.row
        self.clear_vector()

    def visit(self, map_object, station_group, rail_group, road_group):
        tile = get_tile(map_object, self.x, self.y)
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
        if tile.visitors > STATION_THRESHOLD and not tile.train_station:
            station_group.new_station(tile)

    def find_closest_station(self, target, station_group):
        closest_station = (None, None)
        for each in station_group.members:
            distance_from_target = distance(self.target[0], self.target[1], each.x, each.y)
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
                self.path = get_path((self.x, self.y), map_object, self.target)
        else:
            print("Less than two stations")
            self.path = get_path((self.x, self.y), map_object, self.target)

    def station_to_station(self, map_object, station_a, station_b, target):
        aggregate_path = Path()
        path_to_station = get_path((round(self.x), round(self.y)), map_object, (station_a.x, station_a.y))
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
        path_from_station = get_path((station_b.x, station_b.y), map_object, target)
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
        if len(self.path.steps) < 1:
            assert (round(self.x), round(self.y)) == self.target
            self.clear_target()
            self.path = None
            self.settle(settlement_group, get_tile(map_object, self.x, self.y))

    def tick_cycle(self, map_object, markets, settlement_group, road_group, station_group, rail_group):
        if not self.target or not self.target_market:
            self.target = self.get_target(map_object, markets)
            # self.plot_course(map_object, road_group, station_group, rail_group)
            self.path = get_path((self.x, self.y), map_object, self.target)
            assert self.path
            assert self.path.steps
        assert self.target_market and self.target
        assert self.path
        assert self.path.steps
        self.pave(map_object, road_group)
        assert self.path
        assert self.path.steps
        assert (self.path.steps[0].column, self.path.steps[0].row) != (self.x, self.y)
        self.vector = self.set_vector(self.path.steps[0].column, self.path.steps[0].row, self.x, self.y)
        assert self.path
        assert self.path.steps
        self.move(map_object)
        # self.visit(map_object, station_group, rail_group, road_group)
        self.check_target(map_object, settlement_group)
        if self.path:
            assert self.path.steps


class Market(object):
    def __init__(self, x, y):
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = pygame.Surface([1, 1])
        self.sprite.image.fill(colors["Market Red"])
        self.sprite.image = self.sprite.image.convert_alpha()
        self.x = x
        self.y = y


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
            self.sprite.image.fill(colors[settlement_colors[self.size]])


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
                self.sprite.image.fill(colors[road_colors[self.level]])

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
        new_rail_path = get_path((self.x, self.y), map_object, (new_station.x, new_station.y))
        rail_group.new_rail(self, new_station, new_rail_path)
        self.connections[new_station] = new_rail_path

    def connection_check(self, map_object, rail_group):
        for each in self.passed_through:
            if self.passed_through[each] > RAIL_CONNECTION_THRESHOLD and each not in self.connections:
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


class GameMap(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.number_of_columns = width
        self.number_of_rows = height
        self.game_tile_rows = []

        self.generate_game_tiles()

    def generate_game_tiles(self):
        for y_row in range(self.number_of_rows):
            this_row = []
            for x_column in range(self.number_of_columns):
                this_row.append(GameTile(x_column, y_row))
            self.game_tile_rows.append(this_row)

    def set_costs(self, road_group, rail_group):
        for rail in rail_group.members:
            for tile in rail.path.steps:
                game_tile = self.game_tile_rows[tile.row][tile.column]
                game_tile.cost = 1
        for road in road_group.members:
            game_tile = self.game_tile_rows[road.y][road.x]
            if game_tile.cost > 999:
                game_tile.cost -= 999
            print("Making the road tile cheaper!")
            print(game_tile.cost)


class Background(pygame.sprite.Sprite):
    def __init__(self, width, height):
        super().__init__()
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = pygame.Surface([width, height])
        self.sprite.image.fill(colors["Background Dark Blue"])
        self.sprite.image = self.sprite.image.convert_alpha()
        self.sprite.rect = self.sprite.image.get_rect()


class ObjectLayer(Background):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.sprite.image.fill(colors["Key"])
        self.sprite.image.set_colorkey(colors["Key"])
        self.sprite.image = self.sprite.image.convert_alpha()

    def update(self, new_item):
        self.sprite.image.blit(new_item.sprite.image, [new_item.x, new_item.y])


class RailLayer(ObjectLayer):
    def __init__(self, width, height):
        super().__init__(width, height)

    def update(self, rail):
        self.sprite.image.blit(rail.sprite.image, [0, 0])


class ObjectGroup(object):
    def __init__(self, width, height):
        self.members = []
        self.width = width
        self.height = height
        self.display_layer = ObjectLayer(width, height)


class RailGroup(ObjectGroup):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.display_layer = RailLayer(width, height)

    def new_rail(self, a, b, path):
        new_rail = Rail(self.width, self.height, a, b, path)
        self.members.append(new_rail)
        self.display_layer.update(new_rail)


class RoadGroup(ObjectGroup):
    def __init__(self, width, height):
        super().__init__(width, height)

    def new_road(self, tile):
        new_road = Road(tile.column, tile.row)
        tile.road = new_road
        tile.cost = 1
        self.members.append(new_road)
        self.display_layer.update(new_road)


class SettlementGroup(ObjectGroup):
    def __init__(self, width, height):
        super().__init__(width, height)

    def new_settlement(self, tile):
        new_settlement = Settlement(tile.column, tile.row)
        tile.settlement = new_settlement
        self.members.append(new_settlement)
        self.display_layer.update(new_settlement)


class TrainStationGroup(ObjectGroup):
    def __init__(self, width, height):
        super().__init__(width, height)

    def new_station(self, tile):
        closest_station = 10000
        for each in self.members:
            station_distance = distance(tile.column, tile.row, each.x, each.y)
            if station_distance < closest_station:
                closest_station = station_distance
        if closest_station >= MIN_STATION_DISTANCE:
            new_station = TrainStation(tile.column, tile.row)
            tile.train_station = new_station
            self.members.append(new_station)


def distance(a, b, x, y):
    a1 = abs(a - x)
    b1 = abs(b - y)
    c = math.sqrt((a1 * a1) + (b1 * b1))
    return c


def get_smallest(values):
    smallest = (9999, None)
    for each in values:
        if abs(each) < smallest[0]:
            smallest = (abs(each), each)
    return smallest[1]


def get_tile(map_object, x, y):
    x = round(x)
    y = round(y)
    tile = map_object.game_tile_rows[y][x]
    return tile


def within_map(x, y, map_object):
    return 0 <= x <= len(map_object.game_tile_rows[0]) - 1 and 0 <= y <= len(map_object.game_tile_rows) - 1


def get_adjacent_tiles(tile, map_object):
    initial_x = tile.column - 1
    initial_y = tile.row - 1
    adjacent_tiles = []
    for tile_y in range(initial_y, initial_y + 3):
        for tile_x in range(initial_x, initial_x + 3):
            if within_map(tile_x, tile_y, map_object):
                adjacent_tiles.append(map_object.game_tile_rows[tile_y][tile_x])
    return adjacent_tiles


class Path(object):
    def __init__(self):
        self.tiles = []
        self.steps = []
        self.cost = 0


def explore_frontier_to_target(game_map, visited, target_tile, closest_tile, frontier):
    while not frontier.empty():
        priority, current_tile, previous_tile = frontier.get()
        new_steps = visited[previous_tile][0] + 1
        if current_tile not in visited or new_steps < visited[current_tile][0]:
            tile_neighbors = get_adjacent_tiles(current_tile, game_map)
            for each in tile_neighbors:
                distance_to_target = distance(each.column, each.row, target_tile.column, target_tile.row)
                priority = distance_to_target + new_steps + each.cost
                frontier.put((priority, each, current_tile))
            distance_to_target = distance(current_tile.column, current_tile.row, target_tile.column, target_tile.row)
            if distance_to_target < closest_tile[0]:
                closest_tile = [distance_to_target, current_tile]
            visited[current_tile] = (new_steps, previous_tile)
        if target_tile in visited:
            break
    return visited, closest_tile


def get_path(my_position, game_map, target_coordinates):
    target_tile = game_map.game_tile_rows[target_coordinates[1]][target_coordinates[0]]
    start_tile = game_map.game_tile_rows[my_position[1]][my_position[0]]
    visited = {start_tile: (0, None)}
    tile_neighbors = get_adjacent_tiles(start_tile, game_map)
    frontier = queue.PriorityQueue()
    closest_tile = [99999, start_tile]
    for each in tile_neighbors:
        frontier.put((0, each, start_tile))
    visited, closest_tile = explore_frontier_to_target(game_map, visited, target_tile, closest_tile, frontier)

    new_path = Path()
    new_path.tiles.append(target_tile)
    new_path.tiles.append(closest_tile[1])
    new_path.steps.append(target_tile)
    new_path.steps.append(visited[closest_tile[1]][1])
    while start_tile not in new_path.tiles:
        next_tile = new_path.steps[-1]
        if next_tile != start_tile:
            new_path.steps.append(visited[next_tile][1])
            new_path.cost += next_tile.cost
        new_path.tiles.append(next_tile)
    new_path.tiles.reverse()
    # removes the start tile from the tiles list and the steps list in the path object
    new_path.tiles.pop(0)
    new_path.steps.reverse()
    new_path.steps.pop(0)
    return new_path


def draw_to_screen(screen, objects, bools):
    screen.blit(objects["Background"].sprite.image, [0, 0])
    if bools["Draw Roads"]:
        screen.blit(objects["Roads"].sprite.image, [0, 0])
    if bools["Draw Rails"]:
        screen.blit(objects["Rails"].sprite.image, [0, 0])
    if bools["Draw Settlements"]:
        screen.blit(objects["Settlements"].sprite.image, [0, 0])
    if bools["Draw Train Stations"]:
        for each in objects["Train Stations"]:
            screen.blit(each.sprite.image, [each.x, each.y])
    if bools["Draw Agents"]:
        for each in objects["Agents"]:
            screen.blit(each.sprite.image, [round(each.x), round(each.y)])
    if bools["Draw Markets"]:
        for each in objects["Markets"]:
            screen.blit(each.sprite.image, [each.x, each.y])
    pygame.display.flip()


def check_old_markets(markets, new_coordinates):
    for each in markets:
        if new_coordinates == (each.x, each.y):
            return True
    return False


def generate_random_markets(screen_width, screen_height, markets, number_of_markets):
    for z in range(number_of_markets):
        placed = False
        while not placed:
            x = random.randint(1, screen_width - 1)
            y = random.randint(1, screen_height - 1)
            if not check_old_markets(markets, (x, y)):
                new_market = Market(x, y)
                markets.append(new_market)
                placed = True


def generate_random_agents(screen_width, screen_height, agents, number_of_agents):
    for z in range(number_of_agents):
        x = random.randint(1, screen_width - 1)
        y = random.randint(1, screen_height - 1)
        new_agent = Agent(x, y)
        agents.append(new_agent)


def tick_processing(map_object, settlement_group, station_group, road_group, rail_group, markets, agents):
    for each in agents:
        each.tick_cycle(map_object, markets, settlement_group, road_group, station_group, rail_group)


def c_key(bools):
    bools["Draw Settlements"] = not bools["Draw Settlements"]


def a_key(bools):
    bools["Draw Agents"] = not bools["Draw Agents"]


def l_key(bools):
    bools["Draw Rails"] = not bools["Draw Rails"]


def m_key(bools):
    bools["Draw Markets"] = not bools["Draw Markets"]


def r_key(bools):
    bools["Draw Roads"] = not bools["Draw Roads"]


def t_key(bools):
    bools["Draw Train Stations"] = not bools["Draw Train Stations"]


def invalid_key(bools):
    pass


key_functions = {pygame.K_a: a_key,
                 pygame.K_c: c_key,
                 pygame.K_l: l_key,
                 pygame.K_m: m_key,
                 pygame.K_r: r_key,
                 pygame.K_t: t_key}


def key_handler(event, bools):
    key_functions.get(event.key, invalid_key)(bools)


def mouse_handler(pos, event, markets):
    if event.button == 1:
        new_market = Market(pos[0], pos[1])
        markets.append(new_market)


def main():
    fps = 0
    pygame.init()
    pygame.display.set_caption("One Giant Leap V 0.1")
    clock = pygame.time.Clock()
    screen_width = 1000
    screen_height = 800
    screen = pygame.display.set_mode([screen_width, screen_height])
    game_map = GameMap(screen_width, screen_height)
    background = Background(screen_width, screen_height)
    settlement_group = SettlementGroup(screen_width, screen_height)
    road_group = RoadGroup(screen_width, screen_height)
    agents = []
    markets = []
    station_group = TrainStationGroup(screen_width, screen_height)
    rail_group = RailGroup(screen_width, screen_height)

    generate_random_markets(screen_width, screen_height, markets, NUMBER_OF_MARKETS)
    generate_random_agents(screen_width, screen_height, agents, NUMBER_OF_AGENTS)

    bools = {"Draw Agents": True,
             "Draw Markets": True,
             "Draw Rails": True,
             "Draw Settlements": True,
             "Draw Train Stations": True,
             "Draw Roads": True}
    visual_objects = {"Background": background,
                      "Settlements": settlement_group.display_layer,
                      "Roads": road_group.display_layer,
                      "Rails": rail_group.display_layer,
                      "Train Stations": station_group.members,
                      "Agents": agents,
                      "Markets": markets}

    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                key_handler(event, bools)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_handler(mouse_pos, event, markets)

        tick_processing(game_map, settlement_group, station_group, road_group, rail_group, markets, agents)
        draw_to_screen(screen, visual_objects, bools)
        clock.tick(60)
        if fps != round(clock.get_fps()):
            fps = round(clock.get_fps())
            print("FPS: {0}".format(fps))


main()