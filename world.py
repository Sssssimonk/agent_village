import networkx as nx
import json
from person import Person
import numpy as np
from llm import generate_index

class World:
    def __init__(self) -> None:
        self.town_areas = None
        self.world_graph = self.initialize_world()
        self.residents = {}
        self.cur_time = 8
        self.date = ""
        self.weather = -1
        self.date_index = -1
        
        self.initialize_agents()
        
    


    def initialize_world(self) -> nx.Graph:
        # initialize town areas and world graph
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
        # instantiate person and add them to the self.residents
        with open("world_settings.json", "r") as json_file:
            data = json.load(json_file)
            residents = data["town_residents"]

        for resident in residents.keys():
            self.residents[resident] = Person(residents[resident]["Name"], 
                                             residents[resident]["Description"], 
                                             residents[resident]["Personality"],
                                             self)
            description = residents[resident]['Description']
            self.residents[resident].index = generate_index(description)

        print("Agent Initialized")
        
    def rest_date(self):
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday","Saturday", "Sunday"]
        weather = ["Sunny", "Rain", "Cloudy"]
        if self.date_index < 0:
            self.date_index = np.random.randint(len(days))
        else:
            self.date_index = 0 if self.date_index >= len(days) - 1 else self.date_index + 1
        self.date = days[self.date_index]
        self.weather = weather[np.random.choice(len(weather), p=[0.5, 0.2, 0.3])]
        
    def agent_meet(self, agents, building):
        sentence = {}
        for people in agents:
            content = self.residents[people].memory[-1].split('.')[1:]
            content = ". ".join(content)
            content = content.replace(" I ", " {} ".format(self.residents[people].name))
            sentence[self.residents[people].name] = content
        
        return "{} are on {}.\n{}".format(", ".join(list(sentence.keys())), 
                                          building, 
                                          ".\n".join(list(sentence.values()))
                                         )
        
if __name__ == "__main__":
    world = World()
    
