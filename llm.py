from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from transformers import BitsAndBytesConfig

import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, ServiceContext, Document
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.core import PromptTemplate

from sentence_transformers import SentenceTransformer, util


# ==================== Initialzied HF model ==================== # 
basic_llama = None 
llama_index = None
sentence_model = None
bnb_config = BitsAndBytesConfig(load_in_4bit=True,
                                bnb_4bit_use_double_quant=True,
                                bnb_4bit_quant_type="nf4",
                                bnb_4bit_compute_dtype=torch.bfloat16
)

# use llama2 model in transfomers
BASIC_TOKEN = "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"
# MODEL_NAME = "lmsys/vicuna-7b-v1.5"
# MODEL_NAME = "mistralai/Mistral-7B-v0.1"
MODEL_NAME = "meta-llama/Llama-2-7b-chat-hf"


def generate_model():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, 
                                              token=BASIC_TOKEN
                                             )
    BASIC_MODEL = AutoModelForCausalLM.from_pretrained(MODEL_NAME,
                                                 quantization_config=bnb_config,
                                                 token=BASIC_TOKEN,
                                                 device_map="auto"
                                                )
    
    pipe = pipeline(task="text-generation",
                    model=BASIC_MODEL, 
                    tokenizer=tokenizer
                    #PretrainedConfig = xxx
                   )
    print("hf_model_initialized")
    
    llm = HuggingFaceLLM(
        context_window=4096,
        max_new_tokens=1024,
        generate_kwargs={"temperature": 0.7, "do_sample": False},
        model_name=MODEL_NAME,
        tokenizer_name=MODEL_NAME,
        query_wrapper_prompt=PromptTemplate("<|USER|>{query_str}<|ASSISTANT|>"),
        model_kwargs={"token": BASIC_TOKEN, "quantization_config": bnb_config},
        tokenizer_kwargs={"token": BASIC_TOKEN, "max_length": 4096},
        device_map="auto",
    )

    service_context = ServiceContext.from_defaults(llm=llm, embed_model="local:BAAI/bge-small-en-v1.5")
    print("llama_index_model_initialized")
    
    sentence_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    return pipe, service_context, sentence_model


basic_llama, llama_index, sentence_model = generate_model()

def generate_prompt(task, person, world):
    # from prompt file task.txt, read the prompt template and then out put a str prompt.
    prompt_template = "prompt_templates" + "/"+ task + ".txt"

    file = open(prompt_template, "r")
    prompt = file.read()
    file.close()

    if task == "daily_plan":
        if person.special_event != None:
            person.description = person.description + " " + "I plan to " + person.special_event + " Today." 
        prompt = prompt.format(person.name, 
                               person.description, 
                               person.personality,
                               world.date,
                               world.weather
                              )
        
    if task == "place":                          
        plan_action = "{} plan to{}".format(person.name.split(" ")[0], 
                                            person.plan_lst["{}:00".format(world.cur_time)][0]
                                           )    
        prompt = prompt.format(person.name, 
                               person.description, 
                               ", ".join(list(world.town_areas.keys())),
                               "\n".join(list(world.town_areas.values())),
                               plan_action,
                               world.cur_time
                              )
    
    if task == "action":
        plan_action = "I plan to {}at {}:00.".format(person.plan_lst["{}:00".format(world.cur_time)][0],
                                                     world.cur_time
                                                    )
#         if world.cur_time > 8:
#             plan_action += "I already {}at {}:00.".format(person.plan_lst["{}:00".format(world.cur_time - 1)][0],
#                                                           world.cur_time - 1
#                                                          )
        prompt = prompt.format(person.name,
                               person.description,
                               person.location,
                               plan_action,
#                                before_action,
                               world.cur_time)
    if task == "if_chat":
        target_name = []
        target_description = []
        target_action = []
        for i in person.meet:
            target_name.append(person.world.residents[i].name)
            target_description.append(person.world.residents[i].description)
            target_action.append(person.world.residents[i].memory[-1].replace("I will",
                                                                              "{} will".format(person.world.residents[i].name)
                                                                             ))
        prompt = prompt.format(person.name,
                               person.description,
                               person.location,
                               world.cur_time,
                               person.memory[-1],
                               ", ".join(target_name),
                               " ".join(target_description),
                               " ".join(target_action),
                               world.date,
                               world.weather
                               )
    if task == "chat":
        prompt = prompt.format(person,
                               world
                               )
    
    if task == "summary_memory":
        prompt = prompt.format(person.name,
                               person.description,
                               "\n".join(person.memory),
                               person.daily_plan,
                               world.date,
                               world.weather
                               )
        
    if task == "interact":
        prompt = prompt.format(person,
                               world
                               )
        
    if task == "interaction":
        location = world.residents[person[0]].location
        now_time = world.cur_time
        action_intro = "{} meet on {}. ".format(", ".join(person), location)
        action_intro += " ".join([world.residents[i].get_plan() for i in person])
        prompt = prompt.format(person,
                               location,
                               now_time,
                               action_intro,
                               world.date,
                               world.weather
                               )
    return prompt

def generate_response(prompt, max_new_tokens=100, min_new_tokens=50):
    response = basic_llama(prompt, max_new_tokens=max_new_tokens, min_new_tokens=min_new_tokens)
    return response[0]['generated_text']


def generate_index(description):
    document = Document(text=description)
    index = VectorStoreIndex.from_documents([document], service_context=llama_index)
    return index

def rag_response(prompt, person):
    query_engine = person.index.as_query_engine() 
    response = query_engine.query(prompt)

    return response
    
    
def calculate_memory_consistency(summary, plan):
    """
    Compare text based on similarity and then choose the best 
    result between normal and RAG models.
    
    RETURNS:
        float number
    """
    embedding_1= sentence_model.encode(summary, convert_to_tensor=True)
    embedding_2 = sentence_model.encode(plan, convert_to_tensor=True)
    score = util.pytorch_cos_sim(embedding_1, embedding_2).tolist()[0][0]
    return score
    
    
    
    
    