import json
from nltk.translate.bleu_score import sentence_bleu
import jieba           
import difflib              
from fuzzywuzzy import fuzz   
import numpy as np
from collections import Counter

stopwords = {}.fromkeys([',', '.', ';',':'])

with open("world_settings.json", "r") as json_file:
    data = json.load(json_file)
    town_areas = data["town_areas"]
    
building_description = {}
for k, v in town_areas.items():
    building_description[k] = [i for i in jieba.cut(v, cut_all=False) if i != ' ' and i not in stopwords]
    

def BLUE_Compare(text_1, text_2):
    return sentence_bleu(text_1, text_2)

def FUZZ_Compare(text_1, text_2):
    return round(fuzz.ratio(text_1, text_2)/100,3)*100

def similarity(text1, text2):        
    cos_text1 = (Counter(text1))
    cos_text2 = (Counter(text2))
    similarity_text1 = []
    similarity_text2 = []
    for i in set(text1 + text2):
        similarity_text1.append(cos_text1[i])
        similarity_text2.append(cos_text2[i])
    similarity_text1 = np.array(similarity_text1)
    similarity_text2 = np.array(similarity_text2)
    return similarity_text1.dot(similarity_text2) / (np.sqrt(similarity_text1.dot(similarity_text1)) * np.sqrt(similarity_text2.dot(similarity_text2)))
    
def DIFF_LIB_Compare(text_1, text_2):
    return difflib.SequenceMatcher(None, text_1, text_2).quick_ratio()    
    
    
    
def place_compare(llama_2_place, llama_index_place, plan, method="sim"):
    llama_2_lst = "{} on {}".format(plan, llama_2_place)
    llama_index_lst = "{} on {}".format(plan, llama_index_place)
        
    llama_2_lst = [i for i in jieba.cut(llama_2_lst, cut_all=False) if i != ' ' and i not in stopwords]
    llama_index_lst = [i for i in jieba.cut(llama_index_lst, cut_all=False) if i != ' ' and i not in stopwords]
    
    if method == "blue":
        llama2_result = BLUE_Compare(building_description[llama_2_place], llama_2_lst)
        llamaIndex_result = BLUE_Compare(building_description[llama_index_place], llama_index_lst)
        
    elif method == "fuzz":
        llama2_result = FUZZ_Compare(building_description[llama_2_place], llama_2_lst)
        llamaIndex_result = FUZZ_Compare(building_description[llama_index_place], llama_index_lst)
        
    elif method == "sim":
        llama2_result = similarity(building_description[llama_2_place], llama_2_lst)
        llamaIndex_result = similarity(building_description[llama_index_place], llama_index_lst)
        
    elif method == "diff":
        llama2_result = DIFF_LIB_Compare(building_description[llama_2_place], llama_2_lst)
        llamaIndex_result = DIFF_LIB_Compare(building_description[llama_index_place], llama_index_lst)
        
    
#     print(llama2_result, llamaIndex_result)     
    if llama2_result > llamaIndex_result:
        return "basic"
    else:
        return "rag"  
    
    
def action_compare(llama_2_action, llama_index_action, plan, method="sim"):
    plan = [i for i in jieba.cut(plan, cut_all=False) if i != ' ' and i not in stopwords]
    
    llama_2_actions = [i for i in jieba.cut(llama_2_action, cut_all=False) if i != ' ' and i not in stopwords]
    llama_index_actions = [i for i in jieba.cut(llama_index_action, cut_all=False) if i != ' ' and i not in stopwords]
    
    if method == "blue":
        llama2_result = BLUE_Compare(plan, llama_2_actions)
        llamaIndex_result = BLUE_Compare(plan, llama_index_actions)
        
    elif method == "fuzz":
        llama2_result = FUZZ_Compare(plan, llama_2_actions)
        llamaIndex_result = FUZZ_Compare(plan, llama_index_actions)
        
    elif method == "sim":
        llama2_result = similarity(plan, llama_2_actions)
        llamaIndex_result = similarity(plan, llama_index_actions)
        
    elif method == "diff":
        llama2_result = DIFF_LIB_Compare(plan, llama_2_actions)
        llamaIndex_result = DIFF_LIB_Compare(plan, llama_index_actions)
    
    if llama2_result > llamaIndex_result:
        return "basic", llama_2_action
    elif llama2_result == llamaIndex_result:
        return "same", np.random.choice([llama_2_action, llama_index_action], 1)[0]
    else:
        return "rag", llama_index_action
    
    
    