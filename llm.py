from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig 
import torch 

import logging
import sys

from llama_index.core import VectorStoreIndex, ServiceContext, Document
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.core import PromptTemplate

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))


# ==================== Initialzied HF model ==================== # 
pipe = None 
service_context = None
bnb_config = BitsAndBytesConfig(load_in_4bit=True,
                                bnb_4bit_use_double_quant=True,
                                bnb_4bit_quant_type="nf4",
                                bnb_4bit_compute_dtype=torch.bfloat16
)

BASIC_TOKEN = "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"
# MODEL_NAME = "lmsys/vicuna-7b-v1.5"
# MODEL_NAME = "mistralai/Mistral-7B-v0.1"
MODEL_NAME = "meta-llama/Llama-2-7b-chat-hf"


def generate_model():
    global pipe 
    global service_context
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
        max_new_tokens=256,
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

generate_model()

def generate_index(description):
    document = Document(text=description)
    index = VectorStoreIndex.from_documents([document], service_context=service_context)
    return index



def generate_prompt(task, person, world):
    # from prompt file task.txt, read the prompt template and then out put a str prompt.
    prompt_template = "prompt_templates" + "/"+ task + ".txt"

    file = open(prompt_template, "r")
    prompt = file.read()
    file.close()

    if task == "daily_plan":
        prompt = prompt.format(person.name, 
                               person.description, 
                               person.personality,
                               world.date,
                               world.weather
                              )
        
    if task == "place":
        plan_action = ""
        if "{}:00".format(world.cur_time) in person.plan_lst.keys():
            plan_action = "{} plan to {}".format(person.name.split(" ")[0], 
                                                 person.plan_lst["{}:00".format(world.cur_time)]
                                                )
        else:
            before_action = ""
            if world.cur_time == 8:
                before_action = "just wake up!"
            else:
                before_action = person.memory[-1]
            plan_action = before_action.replace("I will ", "I already ")
            
        prompt = prompt.format(person.name, 
                               person.description, 
                               ", ".join(list(world.town_areas.keys())),
                               plan_action,
                               world.cur_time
                              )
    
    if task == "action":
        before_action = ""
        if world.cur_time == 8:
            before_action = "I just wake up!"
        else:
            if len(person.memory) <= 5:
                before_action = "\n".join(person.memory)
            else:
                before_action = "\n".join(person.memory[-5:])
        plan_action = ""
        if "{}:00".format(world.cur_time) in person.plan_lst.keys():
            plan_action = person.plan_lst["{}:00".format(world.cur_time)]
        else:
            plan_action = before_action
        
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
    if task == "summary_memory":
        prompt = prompt.format(person.name,
                               person.description,
                               "\n".join(person.memory),
                               person.daily_plan,
                               world.date,
                               world.weather
                               )
    return prompt



def generate_response(prompt, max_new_tokens=100, min_new_tokens=50):
    response = pipe(prompt, max_new_tokens=max_new_tokens, min_new_tokens=min_new_tokens)[0]['generated_text']
    return response


def generate_index(description):
    document = Document(text=description)
    index = VectorStoreIndex.from_documents([document], service_context=service_context)
    return index

def rag_response(prompt, person):
    query_engine = person.index.as_query_engine() 
    response = query_engine.query(prompt)

    return response
    
    
    
    
    
    
