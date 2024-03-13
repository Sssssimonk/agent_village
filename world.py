import networkx as nx
import json
from person import Person
import numpy as np
from llm import generate_index, generate_prompt, generate_response, rag_response
from compare import place_compare, action_compare, calculate_memory_consistency

def process_answer(text):
    """
    Confirm the valid text format and delete prompt words or text irrelevant to the results.
    Args:
        text: Text generated by HuggingFace and RAG
    RETURNS: 
        text that have already remove useless junk text
    """
    stop_labels = ["|>", "<|", "<", ">", "Note:", "ASSISTANT", 
                   "USER", "Other Agents:", "Other Agents", "\n",
                  "have a conversation:"]
    result = []
    for i in text.split("\n"):
        if np.sum(np.array([True if j in i else False for j in stop_labels])) == 0:
            result.append(i)
    return "\n".join(result).strip()


class World:
    def __init__(self) -> None:
        self.town_areas = None
        self.world_graph = self.initialize_world()
        self.residents = {}
        self.cur_time = 8
        self.date = ""
        self.weather = -1
        self.date_index = -1
        self.index= None
        self.plan = {}
        
        self.initialize_agents()
        
        
        # this variable will contains the compare value between basic model and rag model
        self.results = {
            "frequency":[],
            "points": {
                "basic_model": [],
                "rag_model": []
            },
            "plan":{
                "basic_model": [],
                "rag_model": []
            }, 
            "summary":{
                "basic_model": [],
                "rag_model": []
            }, 
        }
        
    


    def initialize_world(self) -> nx.Graph:
        """
        initialize town areas and world graph
        """
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
        """
        instantiate person and add them to the self.residents
        """
        with open("world_settings.json", "r") as json_file:
            data = json.load(json_file)
            residents = data["town_residents"]
        
        agent_introduction = "\n".join([residents[i]["Description"] for i in residents])
        for resident in residents.keys():
            self.residents[resident] = Person(residents[resident]["Name"], 
                                             residents[resident]["Description"], 
                                             residents[resident]["Personality"],
                                             self)
            description = residents[resident]['Description']
            self.residents[resident].index = generate_index(description)
        
        town_introduction = '\n'.join(list(self.town_areas.values()))
        introduction = agent_introduction + '\n' + town_introduction
        self.index = generate_index(introduction)
        print("Agent Initialized")
#         print(self.town_areas)
        
    def reset_date(self):
        """
        When a day passes, the environment automatically switches to tomorrow and then updates the weather
        """
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday","Saturday", "Sunday"]
        weather = ["Sunny", "Rain", "Cloudy"]
        if self.date_index < 0:
            self.date_index = np.random.randint(len(days))
        else:
            self.date_index = 0 if self.date_index >= len(days) - 1 else self.date_index + 1
        self.date = days[self.date_index]
        self.weather = weather[np.random.choice(len(weather), p=[0.5, 0.2, 0.3])]
        print("===== Today is {} and it's {}. =====".format(self.date, self.weather))
        
    def agent_meet(self, agents):
        """
        When more than one agent is active in this place, it will be determined 
        whether multiple agents will conduct common activities and conversations 
        here, and then generate new memories.
        
        Args:
            agents: List of agents stored in list form
        """
        best_result, chat_result = None, None
        action_intro = " ".join([self.residents[i].get_plan() for i in agents])
        
        prompt = generate_prompt("interaction", agents, self)
        response = generate_response(prompt, max_new_tokens=500, min_new_tokens=100)
        response = response.split("<Output>:")[1].split("<Information Given>")[0]
        rag_respones = str(rag_response(prompt, self)).split("<Information Given>")[0]
        
        response = process_answer(response)
        rag_respones = process_answer(rag_respones)
        
        action_basic_compare = calculate_memory_consistency(action_intro, response)
        action_rag_compare = calculate_memory_consistency(action_intro, rag_respones)
        if action_basic_compare > action_rag_compare:
            print("The Basic model is better, under content is Basic Intercation.")
            best_result = response
            self.results["frequency"].append("basic")
        else:
            print("The RAG model is better, under content is RAG Intercation.")
            best_result = rag_respones
            self.results["frequency"].append("rag")
            
        print(best_result)

        
         ### Dialogue generation decision
        if_prompt = generate_prompt("interact", agents, response)
        if_response = generate_response(if_prompt, max_new_tokens=1, min_new_tokens=1)
        if_response = if_response.split("<Output>:")[1]
        if_rag_respones = str(rag_response(if_prompt, self))

        chat_response = "They DO NOT have conversion."
        chat_rag_respones = "They DO NOT have conversion."
        
       
        if "yes" in if_response.lower() or "yes" in if_rag_respones.lower():
            ### Dialogue generation
            chat_prompt = generate_prompt("chat", agents, response)
            chat_response = generate_response(chat_prompt, max_new_tokens=500, min_new_tokens=30)
            chat_response = chat_response.split("<Output>:")[1].split("<Information Given>")[0]
            chat_rag_respones = str(rag_response(chat_prompt, self)).split("<Information Given>")[0]

            chat_response = process_answer(chat_response)
            chat_rag_respones = process_answer(chat_rag_respones)
            
            chat_basic_compare = calculate_memory_consistency(action_intro, chat_response)
            chat_rag_compare = calculate_memory_consistency(action_intro, chat_rag_respones)
            self.results["points"]["basic_model"].append(chat_basic_compare)
            self.results["points"]["rag_model"].append(chat_rag_compare)
        
            if chat_basic_compare > chat_rag_compare:
                print("The Basic model is better, under content is Basic conversion.")
                chat_result = chat_response
                self.results["frequency"].append("basic")
                print(chat_response)
            else:
                print("The Rag model is better, under content is RAG conversion.")
                chat_result = chat_rag_respones
                self.results["frequency"].append("rag")
                print(chat_rag_respones)
                
        else:
            chat_result = "They do not have interaction, they just work alone"
        
    
        self.results["points"]["basic_model"].append(action_basic_compare)
        self.results["points"]["rag_model"].append(action_rag_compare)
        
        ### Store the results generated by different models in corresponding elements
        for agent in agents:
            self.residents[agent].memory.append(" ".join([i for i in best_result.split("\n") if agent in i]))
            self.residents[agent].memory[-1] += '\n'
            self.residents[agent].memory[-1] += chat_result
            
            self.residents[agent].basic_memory.append(" ".join([i for i in response.split("\n") if agent in i]))
            self.residents[agent].basic_memory[-1] += '\n'
            self.residents[agent].basic_memory[-1] += chat_response
            
            self.residents[agent].rag_memory.append(" ".join([i for i in rag_respones.split("\n") if agent in i]))
            self.residents[agent].rag_memory[-1] += '\n'
            self.residents[agent].rag_memory[-1] += chat_rag_respones
        
        
if __name__ == "__main__":
    world = World()
    
