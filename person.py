from llm import generate_prompt, generate_response, rag_generate_response, index_insert, calculate_memory_consistency
import numpy as np
import re
from compare import place_compare, action_compare

class Person:

    def __init__(self, name, description, personality, world) -> None:
        self.name = name
        self.description = description
        self.special_event = None
        
        self.basic_memory = []
        self.rag_memory = []
        self.memory_label = []
        
        self.location = "Town Square"
        self.personality = personality
        self.world = world
        self.daily_plan = None
        self.plan_lst = {}
        self.meet = []
        self.summary = []
        self.index = None

        self.memory_consistency = []


    
    def other_meet(self, agents):
        meet_agent = [self.world.residents[agent].name for agent in agents] # list of name of agents in current location
        meet_agent.remove(self.name) #
        self.memory[-1] += " I see {} on {}.".format(", ".join(meet_agent), self.location)

    def plan(self):
        # create daily plan whenever the new day starts
        prompt = generate_prompt("daily_plan", self, self.world)
        response = generate_response(prompt, max_new_tokens=500, min_new_tokens=100)
        
        
        daily_plan = response.split("<Output>:")[1]     # delete prompt template provided
        self.daily_plan = daily_plan
        
        for plan_value in self.daily_plan.split('\n'):
            if " - " in plan_value:
                key = plan_value.split(":")[0]
                value = plan_value.split(" - ")[1].lower()
                self.plan_lst["{}:00".format(key)] = value
                
                if "23:00" in self.plan_lst.keys():
                    break
        

#         print("The daily plan for " + self.name + " is : " + self.daily_plan)

    def retrieve(self):
        print(self.name + " is summarizing today's memory")
        # summarize today's memory, add to seld.summary, clear memory
        prompt = generate_prompt("summarize_action", self, self.world)
        response = generate_response(prompt, max_new_tokens=200, min_new_tokens=50)

#TODO
        summary = response.split("<Output>:")[1]   #.split('\n')

        plan = str(self.plan_lst).replace("'","")
        self.memory_consistency.append(calculate_memory_consistency(summary, plan))

        rag_respones = rag_response(prompt, self)
        summary = response.split("<Output>:")[1].split('\n')
        
        plan_temp = self.daily_plan.replace(" - ", " ")
        plan_temp = plan_temp.replace('\n', ' ')
        
# TODO 
        
        
        basic_summary = ""
        for i in summary:
            if len(i) != 0:
                basic_summary = i
                break
        label, summary_result = action_compare(basic_summary, str(rag_respones), plan_temp)
        self.memory_label.append(label)
        self.memory.append(summary_result)
        
        self.daily_plan = None
        self.plan_lst = {}
        self.meet = []
        self.memory = []
    def move(self):
        prompt = generate_prompt("move", self, self.world)
        response = generate_response(prompt, max_new_tokens=500, min_new_tokens=10)
        rag_respones = rag_response(prompt, self)

        action = response.split("<Output>:")[1]  
        for i in action.split('\n'):
            if "I will " in i:
                action = i
                break
        rag, default = self.change_place("place")        
        basic_action = "At {}:00, I am {} on {}. {}".format(self.world.cur_time,
                                                            self.name,
                                                            default,
                                                            action
                                                            )
        
        rag_action = "At {}:00, I am {} on {}. {}".format(self.world.cur_time,
                                                            self.name,
                                                            rag,
                                                            rag_respones
                                                            )
        self.basic_memory.append(basic_action)
        self.rag_memory.append(rag_action)
        
        
        plan_action = ""
        if "{}:00".format(self.world.cur_time) in self.plan_lst.keys():
            plan_action = self.plan_lst["{}:00".format(self.world.cur_time)]
            plan_Action = "I plan to {} at {}".format(self.plan_lst["{}:00".format(self.world.cur_time)],
                                                        "{}:00".format(self.world.cur_time)
                                                        )
        else:
            plan_action = self.memory[-1]
        label, action_result = action_compare(basic_action, rag_action, plan_action)
        
        if label != 'same':
            self.memory_label.append(label)
        self.memory.append(action_result)

    def change_place(self):
        prompt = generate_prompt("place", self, self.world)
        response = generate_response(prompt, max_new_tokens=10, min_new_tokens=1)
        place = response.split("<Output>:")[1]

        rag_respones = rag_response(prompt, self)
        rag_str_respones = str(rag_respones)
        
        for building in self.world.town_areas.keys():
            if building.lower() in place.lower():
                place = building
            
            if building.lower() in rag_str_respones.lower():
                rag_str_respones = building
        
        if place not in list(self.world.town_areas.keys()):
            place = "Housing Area"
            
        if rag_str_respones not in list(self.world.town_areas.keys()):
            rag_str_respones = "Housing Area"


        if rag_str_respones == place:
            self.location = rag_str_respones
        else:
            action_check = ""
            if "{}:00".format(self.world.cur_time) in self.plan_lst.keys():
                action_check = self.plan_lst["{}:00".format(self.world.cur_time)]
            else:
                action_check = self.memory[-1]
            compare_result = place_compare(place, rag_str_respones, action_check)
            if compare_result == "rag":
                self.location = rag_str_respones
            else:
                self.location = place
            self.memory_label.append(compare_result)
        return rag_str_respones, place

    def chat(self):
        prompt = generate_prompt("chat", self, self.world)
        response = generate_response(prompt, max_new_tokens=500, min_new_tokens=100)
        chat = response.split("<Output>:")[1]
        chat_result = chat.split('\n<')[0].replace('\n\n', '\n')
        return re.sub(r'\n\n+', '', chat_result)
    
    def if_chat(self):
        prompt = generate_prompt("if_chat", self, self.world)
        response = generate_response(prompt, max_new_tokens=5, min_new_tokens=1)
        check_chat = response.split("<Output>:")[1]
        check_chat = np.float64(check_chat) if any(i.isdigit() for i in check_chat) else 0
        if check_chat >= 7:
            return True
        return False
    
    def action(self, task="move"):
        if task == "move":
            self.move()

        if task == "place": 
            self.change_place()
            
        if task == "chat":
            return self.chat()

        if task == "if_chat":
            return self.if_chat()

        

# ===================================== Agent action with RAG ======================================#

    def rag_plan(self):
        prompt = generate_prompt("daily_plan", self, self.world)
        response = rag_response(prompt, self)

        index_insert(self, response) # insert the generated document back to index
        self.daily_plan = response 

        for plan_value in self.daily_plan.split('\n'):
            if " - " in plan_value:
                key = plan_value.split(":")[0]
                value = plan_value.split(" - ")[1].lower()
                self.plan_lst["{}:00".format(key)] = value
                
                if "23:00" in self.plan_lst.keys():
                    break

        # print("RAG response is + : " + response)
        # daily_plan = response.split("<Output>:")[1]     
        # self.daily_plan = daily_plan




    def rag_retreive(self):
        # summarize today's memory, add to seld.summary, clear memory
        prompt = generate_prompt("summarize_action", self, self.world)
        response = rag_generate_response(prompt, self)


        # !!!!!!!!!!!!!!!!!!!!!!!!!!! TODO 
        prompt = generate_prompt("summary_memory", self, self.world)
        response = rag_response(prompt, self)

        index_insert(self, response)
        summary = response
        for i in summary:
            if len(i) != 0:
                self.summary.append(i)
                break
        
        self.daily_plan = None
        self.plan_lst = {}
        self.meet = []
        self.memory = []

    def rag_action(self, task="move"):
        if task == "move":
            prompt = generate_prompt("action", self, self.world)
            response = rag_response(prompt,self)
            index_insert(self, response)
            action = response
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

        if task == "place": # generate a location in the town areas
            
            prompt = generate_prompt("place", self, self.world)
            response = rag_response(prompt, self)
            index_insert(self, response)
            place = response
            for building in self.world.town_areas.keys():
                if building.lower() in place.lower():
                    self.location = building
                    break
            
        if task == "chat":
            prompt = generate_prompt("chat", self, self.world)
            response = rag_response(prompt, self)
            index_insert(self, response)
            chat = response
            chat_result = chat.split('\n<')[0].replace('\n\n', '\n')
            return re.sub(r'\n\n+', '', chat_result)
        
        if task == "if_chat":
            prompt = generate_prompt("if_chat", self, self.world)
            response = rag_response(prompt, self)
            # index_insert(self, response)
            check_chat = response
            check_chat = np.float64(check_chat) if any(i.isdigit() for i in check_chat) else 0
            if check_chat >= 7:
                return True
            return False




        


