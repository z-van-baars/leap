import tile_operations
import constants
import utilities
import queue


class Path(object):
    def __init__(self):
        self.tiles = []
        self.steps = []
        self.cost = 0


def process_tile_data(game_map, previous_tile, current_tile, new_cost, target_tile, closest_tile, frontier):
    tile_neighbors = tile_operations.get_adjacent_tiles(current_tile, game_map)
    for each in tile_neighbors:
        distance_to_target = utilities.distance(each.column, each.row, target_tile.column, target_tile.row)
        priority = distance_to_target + new_cost + each.cost
        frontier.put((priority, each, current_tile))
    distance_to_target = utilities.distance(current_tile.column, current_tile.row, target_tile.column, target_tile.row)
    if distance_to_target < closest_tile[0]:
        closest_tile = [distance_to_target, current_tile]
    return(new_cost, previous_tile)


def new_explore_frontier_to_target(game_map, visited, target_tile, closest_tile, frontier):
    while not frontier.empty():
        priority, current_tile, previous_tile = frontier.get()
        new_cost = visited[previous_tile][0] + 1
        if current_tile not in visited or new_cost < visited[current_tile][0]:
            visited[current_tile] = process_tile_data(game_map, previous_tile, current_tile, new_cost, target_tile, closest_tile, frontier)
        if target_tile in visited:
            break
    return visited, closest_tile


def explore_frontier_to_target(game_map, visited, target_tile, closest_tile, frontier):
    while not frontier.empty():
        priority, current_tile, previous_tile = frontier.get()
        new_cost = visited[previous_tile][0] + 1
        if current_tile not in visited or new_cost < visited[current_tile][0]:
            tile_neighbors = tile_operations.get_adjacent_tiles(current_tile, game_map)
            for each in tile_neighbors:
                distance_to_target = utilities.distance(each.column, each.row, target_tile.column, target_tile.row)
                priority = (distance_to_target * each.cost) + new_cost + each.cost
                frontier.put((priority, each, current_tile))
            distance_to_target = utilities.distance(current_tile.column, current_tile.row, target_tile.column, target_tile.row)
            if distance_to_target < closest_tile[0]:
                closest_tile = [distance_to_target, current_tile]
            visited[current_tile] = (new_cost, previous_tile)
        if target_tile in visited:
            break
    return visited, closest_tile


def get_path(my_position, game_map, target_coordinates):
    target_tile = game_map.game_tile_rows[target_coordinates[1]][target_coordinates[0]]
    start_tile = game_map.game_tile_rows[my_position[1]][my_position[0]]
    visited = {start_tile: (0, None)}
    tile_neighbors = tile_operations.get_adjacent_tiles(start_tile, game_map)
    frontier = queue.PriorityQueue()
    closest_tile = [99999, start_tile]
    for each in tile_neighbors:
        frontier.put((each.cost, each, start_tile))
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
