import json
from person import Person
import numpy as np
from llm import generate_index

class World:
    def __init__(self):
        self.town_areas = None
        self.world_graph = self.initialize_world()
        self.residents = {}
        self.cur_time = 8
        self.date = ""
        self.weather = -1
        self.date_index = -1
        
        self.initialize_agents()
        print("World Initialized")
    
    def initialize_agents(self):
        # instantiate person and add them to the self.residents
        with open("world_settings.json", "r") as json_file:
            data = json.load(json_file)
            residents = data["town_residents"]
            town_areas = data["town_areas"]

        self.town_areas = town_areas

        for resident in residents.keys():
            # create default agents
            self.residents[resident] = Person(residents[resident]["Name"], 
                                             residents[resident]["Description"], 
                                             residents[resident]["Personality"],
                                             self)
            description = residents[resident]['Description']
            # create index for agents
            self.residents[resident].index = generate_index(description)

        print("Agent Initialized")
        
    def reset_date(self):
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday","Saturday", "Sunday"]
        weather = ["Sunny", "Rain", "Cloudy"]
        if self.date_index < 0:
            self.date_index = np.random.randint(len(days))
        else:
            self.date_index = 0 if self.date_index >= len(days) - 1 else self.date_index + 1
        self.date = days[self.date_index]
        self.weather = weather[np.random.choice(len(weather), p=[0.5, 0.2, 0.3])]
        print("****************************")
        print("Today is {}, it's {}.\n".format(self.date, self.weather))   
        
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
        

    
