
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
