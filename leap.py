import pygame
from game_tile import GameTile
import utilities
import groups
import buildings
import constants
import display_layer


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
            print("Making the road tile cheaper!")
            print(game_tile.cost)


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


def tick_processing(map_object, settlement_group, station_group, road_group, rail_group, market_group, agent_group):
    for each in agent_group.members:
        each.tick_cycle(map_object, market_group, settlement_group, road_group, station_group, rail_group)
    for each in market_group.members:
        each.check_trips(agent_group)


key_mapping = {pygame.K_a: "Draw Agents",
               pygame.K_c: "Draw Settlements",
               pygame.K_l: "Draw Rails",
               pygame.K_m: "Draw Markets",
               pygame.K_r: "Draw Roads",
               pygame.K_t: "Draw Train Stations"}


def key_handler(event, bools):
    index = key_mapping.get(event.key, None)
    if index is not None:
        bools[index] = not bools[index]


def mouse_handler(map_object, pos, event, market_group):
    if event.button == 1:
        market_group.new_market(map_object, pos[0], pos[1])


def main():
    fps = 0
    pygame.init()
    pygame.display.set_caption("One Giant Leap V 0.1")
    clock = pygame.time.Clock()
    screen_width = 1000
    screen_height = 800
    screen = pygame.display.set_mode([screen_width, screen_height])
    game_map = GameMap(screen_width, screen_height)
    background = display_layer.Background(screen_width, screen_height)
    settlement_group = groups.SettlementGroup(screen_width, screen_height)
    road_group = groups.RoadGroup(screen_width, screen_height)
    agent_group = groups.AgentGroup(screen_width, screen_height)
    market_group = groups.MarketGroup(screen_width, screen_height)
    station_group = groups.TrainStationGroup(screen_width, screen_height)
    rail_group = groups.RailGroup(screen_width, screen_height)

    utilities.generate_random_markets(game_map, screen_width, screen_height, market_group, constants.NUMBER_OF_MARKETS)
    print("Markets generated and placed")
    # utilities.generate_random_agents(screen_width, screen_height, agent_group, constants.NUMBER_OF_AGENTS)
    # utilities.generate_agents_at_random_markets(agent_group, constants.NUMBER_OF_AGENTS, market_group)
    utilities.generate_agents_at_one_market(agent_group, constants.NUMBER_OF_AGENTS, market_group)
    print("Agents generated and placed")

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
                      "Agents": agent_group.members,
                      "Markets": market_group.members}
    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                key_handler(event, bools)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_handler(game_map, mouse_pos, event, market_group)

        tick_processing(game_map, settlement_group, station_group, road_group, rail_group, market_group, agent_group)
        draw_to_screen(screen, visual_objects, bools)
        clock.tick(60)
        if fps != round(clock.get_fps()):
            fps = round(clock.get_fps())
            print("FPS: {0}  Agents: {1}".format(fps, len(agent_group.members)))

main()
