import networkx as nx
import json
from person import Person

class World:
    def __init__(self) -> None:
        self.town_areas = None
        self.world_graph = self.initialize_world()
        self.residents = {}
        self.cur_time = 8
        
        self.initialize_agents()
        
    


    def initialize_world(self) -> nx.Graph:
        with open("world_settings.json", "r") as json_file:
            data = json.load(json_file)
            town_areas = data["town_areas"]

        self.town_areas = town_areas
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
        
        print("World Initialized")

        return world_graph
    
    def initialize_agents(self) -> None:
        with open("world_settings.json", "r") as json_file:
            data = json.load(json_file)
            residents = data["town_residents"]

        for resident in residents.keys():
            self.residents[resident] = Person(residents[resident]["Name"], 
                                             residents[resident]["Description"], 
                                             residents[resident]["Personality"],
                                             self)

        print("Agent Initialized")
        
        
        
if __name__ == "__main__":
    world = World()
    nx.draw(world.world_graph, with_labels=True)
