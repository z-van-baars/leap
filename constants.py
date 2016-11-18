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
          "Settled 1": (55, 48, 30),
          "Settled 2": (95, 95, 55),
          "Settled 3": (130, 105, 65),
          "Settled 4": (225, 195, 135),
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

TRIPS_FOR_NEW_AGENT: Number of trips that must be completed in a market's radius before a new
Agent is produced at the market.

NUMBER_OF_AGENTS: Number of Agents to generate at runtime

NUMBER_OF_MARKETS: Number of Markets to generate at runtime"""
NUMBER_OF_AGENTS = 50
NUMBER_OF_MARKETS = 1

ROAD_THRESHOLD = 1
STATION_THRESHOLD = 10
MIN_STATION_DISTANCE = 30
RAIL_CONNECTION_THRESHOLD = 3
TRIPS_FOR_NEW_AGENT = 5000
REDEVELOP_VALUE = 60

OPEN_SPACE_WEIGHT = 10
CENTRAL_PLACE_WEIGHT = 1
FUZZINESS = 1000
CENTRAL_FUZZINESS = 100
