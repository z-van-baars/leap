import random
import math


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


def check_old_markets(market_group, new_coordinates):
    for each in market_group.members:
        if new_coordinates == (each.x, each.y):
            return True
    return False


def generate_random_markets(map_object, screen_width, screen_height, market_group, number_of_markets):
    for z in range(number_of_markets):
        placed = False
        while not placed:
            x = random.randint(1, screen_width - 1)
            y = random.randint(1, screen_height - 1)
            if not check_old_markets(market_group, (x, y)):
                market_group.new_market(map_object, x, y)
                placed = True


def generate_random_agents(screen_width, screen_height, agent_group, number_of_agents):
    for z in range(number_of_agents):
        x = random.randint(1, screen_width - 1)
        y = random.randint(1, screen_height - 1)
        agent_group.new_agent(x, y)


def generate_agents_at_one_market(agent_group, number_of_agents, market_group):
    start_market = random.choice(market_group.members)
    for z in range(number_of_agents):
        x = start_market.x
        y = start_market.y
        agent_group.new_agent(x, y)


def generate_agents_at_random_markets(agent_group, number_of_agents, market_group):
    for z in range(number_of_agents):
        start_market = random.choice(market_group.members)
        x = start_market.x
        y = start_market.y
        agent_group.new_agent(x, y)
