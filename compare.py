import json
import jieba            
import numpy as np
from collections import Counter
from gensim import corpora, models, similarities
from collections import defaultdict

stopwords = {}.fromkeys([',', '.', ';',':'])

with open("world_settings.json", "r") as json_file:
    data = json.load(json_file)
    town_areas = data["town_areas"]

building_description = {}
for k, v in town_areas.items():
    building_description[k] = [i for i in jieba.cut(v, cut_all=False) if i != ' ' and i not in stopwords]
    


def similarity(text1, text2):
    """
    Calculate sentence similarity and give a score.
    Args:
        text_1: target text
        text2: Compare text
    RETURNS:
        a score that is float
    """
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
  
    
    
    
def place_compare(llama_2_place, llama_index_place, plan):
    """
    Compare locations based on similarity and then choose the best 
    result between normal and RAG models.
    
    RETURNS:
        rag or basic
    """
    llama_2_lst = "{} on {}".format(plan, llama_2_place)
    llama_index_lst = "{} on {}".format(plan, llama_index_place)
        
    llama_2_lst = [i for i in jieba.cut(llama_2_lst, cut_all=False) if i != ' ' and i not in stopwords]
    llama_index_lst = [i for i in jieba.cut(llama_index_lst, cut_all=False) if i != ' ' and i not in stopwords]
    
    llama2_result = similarity(building_description[llama_2_place], llama_2_lst)
    llamaIndex_result = similarity(building_description[llama_index_place], llama_index_lst)
     
    if llama2_result > llamaIndex_result:
        return "basic"
    else:
        return "rag"  
    
    
def action_compare(llama_2_action, llama_index_action, plan):
    """
    Compare actions based on similarity and then choose the best 
    result between normal and RAG models.
    
    RETURNS:
        rag or basic, text
    """
    plan = [i for i in jieba.cut(plan, cut_all=False) if i != ' ' and i not in stopwords]
    
    llama_2_actions = [i for i in jieba.cut(llama_2_action, cut_all=False) if i != ' ' and i not in stopwords]
    llama_index_actions = [i for i in jieba.cut(llama_index_action, cut_all=False) if i != ' ' and i not in stopwords]
    
    llama2_result = similarity(plan, llama_2_actions)
    llamaIndex_result = similarity(plan, llama_index_actions)
    
    if llama2_result > llamaIndex_result:
        return "basic", llama_2_action
    elif llama2_result == llamaIndex_result:
        return "same", np.random.choice([llama_2_action, llama_index_action], 1)[0]
    else:
        return "rag", llama_index_action
    
    
# def calculate_memory_consistency(summary, plan):
#     """
#     Compare text based on similarity and then choose the best 
#     result between normal and RAG models.
    
#     RETURNS:
#         float number
#     """
#     embedding_1= sentence_model.encode(summary, convert_to_tensor=True)
#     embedding_2 = sentence_model.encode(plan, convert_to_tensor=True)
#     score = util.pytorch_cos_sim(embedding_1, embedding_2).tolist()[0][0]
#     return score

    
    