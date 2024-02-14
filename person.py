from llm import generate_prompt, generate_response
import numpy as np
import re

class Person:

    def __init__(self, name, description, personality, world) -> None:
        self.name = name
        self.description = description
        self.memory = []
        self.location = "Town Square"
        self.personality = personality
        self.world = world
        self.daily_plan = None
        self.plan_lst = {}
        self.meet = []
        self.summary = []

    def initialize_index():
        pass

    def perceive(self, world):
        # perceive current environment and memorize into memory
        pass 
    
    def other_meet(self, agents):
        meet_agent = [self.world.residents[index].name for index in agents]
        meet_agent.remove(self.name)
        self.memory[-1] += " I see {} on {}.".format(", ".join(meet_agent), self.location)

    def plan(self):
        # create daily plan whenever the new day starts
        prompt = generate_prompt("daily_plan", self, self.world)
        response = generate_response(prompt, max_new_tokens=500, min_new_tokens=100)[0]['generated_text']
        
        
        daily_plan = response.split("<Output>:")[1]     # delete prompt template provided
        
        # update memory
        self.daily_plan = daily_plan
#         print(self.daily_plan)
        
        for plan_value in self.daily_plan.split('\n'):
            if " - " in plan_value:
                key = plan_value.split(":")[0]
                value = plan_value.split(" - ")[1].lower()
                self.plan_lst["{}:00".format(key)] = value
                
                if "23:00" in self.plan_lst.keys():
                    break
        

#         print("The daily plan for " + self.name + " is : " + self.daily_plan)
    
    def retrieve(self):
        prompt = generate_prompt("summary_memory", self, self.world)
        response = generate_response(prompt, max_new_tokens=200, min_new_tokens=50)[0]['generated_text']
        summary = response.split("<Output>:")[1].split('\n')
        for i in summary:
            if len(i) != 0:
                self.summary.append(i)
                break
        
        self.daily_plan = None
        self.plan_lst = {}
        self.meet = []
        self.memory = []
        
        

    def reflect(self):
        # TODO: process memory, remove anything useless
        pass 

    def action(self, task="move"):

        if task == "move":
            prompt = generate_prompt("action", self, self.world)
            response = generate_response(prompt, max_new_tokens=500, min_new_tokens=10)[0]['generated_text']
            action = response.split("<Output>:")[1]  # delete prompt template provided
            for i in action.split('\n'):
                if "I will " in i:
                    action = i
                    break
            self.memory.append("At {}:00, I am {} on {}. {}".format(self.world.cur_time,
                                                                    self.name,
                                                                    self.location,
                                                                    action
                                                                   ))
            
            # print("The action for " + self.name + "is : " + response)

        if task == "place":
            prompt = generate_prompt("place", self, self.world)
            response = generate_response(prompt, max_new_tokens=10, min_new_tokens=1)[0]['generated_text']
            place = response.split("<Output>:")[1]
#             print(place)
            for building in self.world.town_areas.keys():
                if building.lower() in place.lower():
                    self.location = building
                    break
            
        if task == "chat":
            prompt = generate_prompt("chat", self, self.world)
            response = generate_response(prompt, max_new_tokens=500, min_new_tokens=100)[0]['generated_text']
            chat = response.split("<Output>:")[1]
            chat_result = chat.split('\n<')[0].replace('\n\n', '\n')
            return re.sub(r'\n\n+', '', chat_result)
        
        if task == "if_chat":
            prompt = generate_prompt("if_chat", self, self.world)
            response = generate_response(prompt, max_new_tokens=5, min_new_tokens=1)[0]['generated_text']
            check_chat = response.split("<Output>:")[1]
            check_chat = np.float64(check_chat) if any(i.isdigit() for i in check_chat) else 0
            if check_chat >= 7:
                return True
            return False
        

# ===================================== Agent action with RAG ======================================#

    def rag_plan(self):
        # given memory in vector database, create daily plan
        pass 

    def rag_retreive(self):
        # perceive current environment and memorize into vector database(memory)
        pass

    def rag_action(self):
        pass




        


