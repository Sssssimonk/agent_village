import networkx as nx
import json

class World:
    def __init__(self) -> None:

        self.world_graph = self.initialize_world()
        self.resident = {}
        self.cur_time = 8

        
    


    def initialize_world(self) -> nx.Graph:
        with open("world_settings", "r") as json_file:
            data = json.load(json_file)
            town_areas = data["town_areas"]

        world_graph = nx.Graph()
        for town_area in town_areas.keys():
            world_graph.add_node(town_area)

        world_graph.add_edge("Town Square", "SuperMarket")
        world_graph.add_edge("Town Square", "City Hall")
        world_graph.add_edge("Town Square", "Coffee Shop")
        world_graph.add_edge("Coffee Shop", "Police Station")
        world_graph.add_edge("Town Square", "School")
        world_graph.add_edge("School", "Village Park")
        world_graph.add_edge("Village Park", "Housing Area")
        world_graph.add_edge("Housing Area", "Police Office")

        return world_graph