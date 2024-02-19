from llm import generate_prompt, generate_response, rag_response
import numpy as np
import re
from compare import place_compare, action_compare

class Person:

    def __init__(self, name, description, personality, world) -> None:
        self.name = name
        self.description = description
        self.memory = []
        self.memory_label = []
        self.location = "Town Square"
        self.personality = personality
        # hard code self.world?
        self.world = world
        self.daily_plan = None
        self.plan_lst = {}
        self.meet = []
        self.summary = []
        self.index = None


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
    
    def retrieve(self, method):
        prompt = generate_prompt("summary_memory", self, self.world)
        response = generate_response(prompt, max_new_tokens=200, min_new_tokens=50)[0]['generated_text']
        rag_respones = rag_response(prompt, self)
        summary = response.split("<Output>:")[1].split('\n')
        
        plan_temp = self.daily_plan.replace(" - ", " ")
        plan_temp = plan_temp.replace('\n', ' ')
        
        basic_summary = ""
        for i in summary:
            if len(i) != 0:
                basic_summary = i
                break
        label, summary_result = action_compare(basic_summary, str(rag_respones), plan_temp, method)
        self.memory_label.append(label)
        self.memory.append(summary_result)
        
        self.daily_plan = None
        self.plan_lst = {}
        self.meet = []
        self.memory = []
        
        

    def reflect(self):
        # TODO: process memory, remove anything useless
        pass 

    def action(self, task="move", method="sim"):

        if task == "move":
            prompt = generate_prompt("action", self, self.world)
            response = generate_response(prompt, max_new_tokens=500, min_new_tokens=10)[0]['generated_text']
            rag_respones = rag_response(prompt, self)

            action = response.split("<Output>:")[1]  # delete prompt template provided
            for i in action.split('\n'):
                if "I will " in i:
                    action = i
                    break
                    
            basic_action = "At {}:00, I am {} on {}. {}".format(self.world.cur_time,
                                                                self.name,
                                                                self.location,
                                                                action
                                                               )
            
            rag_action = "At {}:00, I am {} on {}. {}".format(self.world.cur_time,
                                                              self.name,
                                                              self.location,
                                                              rag_respones
                                                             )
            plan_action = ""
            if "{}:00".format(self.world.cur_time) in self.plan_lst.keys():
                plan_action = self.plan_lst["{}:00".format(self.world.cur_time)]
                plan_Action = "I plan to {} at {}".format(self.plan_lst["{}:00".format(self.world.cur_time)],
                                                          "{}:00".format(self.world.cur_time)
                                                         )
            else:
                plan_action = self.memory[-1]
            label, action_result = action_compare(basic_action, rag_action, plan_action, method)
            self.memory_label.append(label)
            self.memory.append(action_result)
            # print("The action for " + self.name + "is : " + response)
            #return response
        
            #TODO: adjust generation config, make the output more stable 
            #TODO: enable agent to move to another space

        if task == "some other action":
            #TODO
            pass
        
        if task == "place":
            prompt = generate_prompt("place", self, self.world)
            response = generate_response(prompt, max_new_tokens=10, min_new_tokens=1)[0]['generated_text']
            rag_respones = rag_response(prompt, self)
            place = response.split("<Output>:")[1]
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
                compare_result = place_compare(place, rag_str_respones, action_check, method)
                if compare_result == "rag":
                    self.location = rag_str_respones
                else:
                    self.location = place
                self.memory_label.append(compare_result)
            
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
        




        


