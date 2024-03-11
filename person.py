from llm import generate_prompt, generate_response, rag_response
import numpy as np
import pandas as pd
import re
from compare import place_compare, action_compare, calculate_memory_consistency
import emojis
import emoji

def extract_emojis(s):
      return ''.join(c for c in s if c not in emoji.EMOJI_DATA)
    
def get_emoji(text):
    dic = {}
    for i in text.split('\n'):
        if ":00" in i:
            key = i.split(":00")[0].split(" ")[-1]
            value = ''.join(c for c in i if c in emoji.EMOJI_DATA)
            if (key in dic.keys()) or (int(key) <= 7):
                key = str(int(key) + 12 )
            dic[key] = value
    return dic

def last_steps(person):
    if "{}:00".format(person.world.cur_time) in person.plan_lst.keys():
        return "I plan to{} at {}".format(person.plan_lst["{}:00".format(person.world.cur_time)],
                                           "{}:00".format(person.world.cur_time)
                                          )
    else:
        return person.memory[-1].replace("I plan to", "I already")

def pd_merge(basic, rag):
    dic = {}
    dic["basic"] = get_emoji(basic)
    dic["rag"] = get_emoji(rag)
    result = pd.DataFrame(dic)
    return result

class Person:

    def __init__(self, name, description, personality, world) -> None:
        self.name = name
        self.description = description
        self.special_event = None
        
        self.basic_memory = []
        self.rag_memory = []
        self.memory = []
        
        self.location = "Housing Area"
        self.personality = personality

        self.world = world
        self.daily_plan = None
        self.plan_lst = {}
        self.summary = []
        self.index = None
       
        
        
    def get_plan(self):
        current_time = "{}:00".format(self.world.cur_time)
        introduction = "{} is {}. ".format(self.name, self.personality)
        if current_time in self.plan_lst.keys():
            return "{}{} plan to{} on {}.".format(introduction, 
                                                   self.name, 
                                                   self.plan_lst[current_time], 
                                                   current_time)
        else:
            return introduction + self.memory[-1]

    def plan(self):
        # create daily plan whenever the new day starts
        prompt = generate_prompt("daily_plan", self, self.world)
        response = generate_response(prompt, max_new_tokens=1000, min_new_tokens=100)
        rag_respones = rag_response(prompt, self)
        rag_respones = str(rag_respones)
        
        daily_plan = response.split("<Output>:")[1]     # delete prompt template provided
        
#         print("basic: \n", daily_plan, "\nrag:\n", rag_respones)
#         print("{}'s daily plan compare list between baisc model and rag model: ".format(self.name.split(" ")[0]))
#         print(pd_merge(daily_plan, rag_respones))
        
        
        ### This part will compare the result between basic model and rag model, the best one will be use
        if self.special_event == None:
            sentence_1_result = calculate_memory_consistency(self.description, extract_emojis(daily_plan))
            sentence_2_result = calculate_memory_consistency(self.description, extract_emojis(rag_respones))
        else:
            special_event = "I plan to " + self.special_event + " Today."
            sentence_1_result = calculate_memory_consistency(special_event, extract_emojis(daily_plan))
            sentence_2_result = calculate_memory_consistency(special_event, extract_emojis(rag_respones))
        
        self.world.results['plan']['basic_model'].append(sentence_1_result)
        self.world.results['plan']['rag_model'].append(sentence_2_result)
        
        if sentence_1_result > sentence_2_result:
            print("The Basic Model is more better!")
            self.daily_plan = extract_emojis(daily_plan)
            self.world.results["frequency"].append("basic")
        
        else:
            print("The RAG Model is more better!")
            self.daily_plan = extract_emojis(rag_respones)
            self.world.results["frequency"].append("rag")
        
        for text in self.daily_plan.split('\n'):
            plan_value = extract_emojis(text)

            if ":00 " in text:
                key = plan_value.split(":00 ")[0].split(" ")[-1]
                value = plan_value.split(":00 ")[1].lower().replace("-", "")
                value = extract_emojis(value)
                
                if (key in self.plan_lst.keys()) or (int(key) <= 7):
                    key = str(int(key) + 12 )   
                self.plan_lst["{}:00".format(key)] = value
                
                if not key.isnumeric():
                    break
    
    def retrieve(self):
        prompt = generate_prompt("summary_memory", self, self.world)
        response = generate_response(prompt, max_new_tokens=200, min_new_tokens=50)
        rag_respones = rag_response(prompt, self)
        summary = response.split("<Output>:")[1].split('\n')
        
        basic_summary = ""
        for i in summary:
            if len(i) != 0:
                basic_summary = i
                break
        
        summary_1_result = calculate_memory_consistency(self.daily_plan, basic_summary)
        summary_2_result = calculate_memory_consistency(self.daily_plan, rag_respones)
        
        self.world.results['summary']['basic_model'].append(summary_1_result)
        self.world.results['summary']['rag_model'].append(summary_2_result)
        if summary_1_result > summary_2_result:
            self.world.results["frequency"].append("basic")
            self.summary.append(basic_summary)
            
        else:
            self.world.results["frequency"].append("rag")
            self.summary.append(rag_summary)
        
        self.daily_plan = None
        self.plan_lst = {}
        self.memory = []


    def action(self, task="move"):
        if task == "move":
            if "{}:00".format(self.world.cur_time) not in list(self.plan_lst.keys()):
                last_plan_time = self.memory[-1].split(":00")[0].split(" ")[0]
                last_memory = self.memory[-1].replace(str(last_plan_time), str(self.world.cur_time))
                last_memory = self.memory[-1].replace("I plan to", "I already")
                self.memory.append(last_memory)
                return 
            
            prompt = generate_prompt("action", self, self.world)
            response = generate_response(prompt, max_new_tokens=500, min_new_tokens=10)
            rag_respones = rag_response(prompt, self)

            action = response.split("<Output>:")[1]  # delete prompt template provided
            for i in action.split('\n'):
                if "I will " in i:
                    action = i
                    break      

            plan_action = last_steps(self)
            rag_respones = str(rag_respones)
            
            basic_result = calculate_memory_consistency(plan_action, action)
            rag_result = calculate_memory_consistency(plan_action, rag_respones)
            
            self.world.results['points']['basic_model'].append(basic_result)
            self.world.results['points']['rag_model'].append(rag_result)
            
            basic_action = "At {}:00, I am {} on {} and I plan to{}. {}".format(self.world.cur_time,
                                                              self.name,
                                                              self.location,
                                                              self.plan_lst["{}:00".format(self.world.cur_time)],
                                                              action
                                                             )
            
            rag_action = "At {}:00, I am {} on {} and I plan to{}. {}".format(self.world.cur_time,
                                                              self.name,
                                                              self.location,
                                                              self.plan_lst["{}:00".format(self.world.cur_time)],
                                                              rag_respones
                                                             )
            self.basic_memory.append(basic_action)
            self.rag_memory.append(rag_action)
            
            if basic_result > rag_result:
                self.memory.append(basic_action)
                self.world.results["frequency"].append("basic")

            else:
                self.memory.append(rag_action)
                self.world.results["frequency"].append("rag")

        
        if task == "place":
            if "{}:00".format(self.world.cur_time) not in list(self.plan_lst.keys()):
                return self.location
            
            prompt = generate_prompt("place", self, self.world)
            response = generate_response(prompt, max_new_tokens=10, min_new_tokens=1)
            rag_respones = rag_response(prompt, self)
            
            place = response.split("<Output>:")[1]
            rag_str_respones = str(rag_respones)
            
            for building in self.world.town_areas.keys():
                if building.lower() in place.lower():
                    place = building
                
                if building.lower() in rag_str_respones.lower():
                    rag_str_respones = building
            
            print(rag_str_respones, place)
            if place not in list(self.world.town_areas.keys()):
                place = "Housing Area"
                
            if rag_str_respones not in list(self.world.town_areas.keys()):
                rag_str_respones = "Housing Area"

            if rag_str_respones == place:
                self.location = rag_str_respones
            else:
                action_check = last_steps(self)
                
                compare_result = place_compare(place, rag_str_respones, action_check)
                if compare_result == "rag":
                    self.location = rag_str_respones
                else:
                    self.location = place
                
                self.world.results['frequency'].append(compare_result)
            return self.location




        


