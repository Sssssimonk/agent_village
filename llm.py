import logging
import sys
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from transformers import BitsAndBytesConfig
from llama_index import VectorStoreIndex, SimpleDirectoryReader, ServiceContext
from llama_index.llms import HuggingFaceLLM
from llama_index.prompts import PromptTemplate
from llama_index.readers import StringIterableReader

# Declare pipe and service_context as global variable, so that they can be accessed at later functions
pipe = None 
service_context = None 

def initialize_model(mnemonics='default'):
    if mnemonics == 'default':
        # ==================== Initialzied HF model ==================== # 
        global pipe
        bnb_config = BitsAndBytesConfig(load_in_4bit=True,
                                        bnb_4bit_use_double_quant=True,
                                        bnb_4bit_quant_type="nf4",
                                        bnb_4bit_compute_dtype=torch.bfloat16
        )

        access_token = "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"
        model_id = "meta-llama/Llama-2-7b-chat-hf"
        # model_id = "lmsys/vicuna-7b-v1.5"
        # model_id = "mistralai/Mistral-7B-v0.1"
        tokenizer = AutoTokenizer.from_pretrained(model_id, 
                                                token=access_token)
        model = AutoModelForCausalLM.from_pretrained(model_id,
                                                    quantization_config=bnb_config,
                                                    token=access_token,
                                                    device_map="auto")
        pipe = pipeline(task="text-generation", 
                model=model, 
                tokenizer=tokenizer
                #PretrainedConfig = xxx
                )
        
        print("huggingface model initialized")

    else:
        # ==================== Initialzied Llama-index ==================== # 
        global service_context
        system_prompt = """<|SYSTEM|># StableLM Tuned (Alpha version)
        - StableLM is a helpful and harmless open-source AI language model developed by StabilityAI.
        - StableLM is excited to be able to help the user, but will refuse to do anything that could be considered harmful to the user.
        - StableLM is more than just an information source, StableLM is also able to write poetry, short stories, and make jokes.
        - StableLM will refuse to participate in anything that could harm a human.
        """


        query_wrapper_prompt = PromptTemplate("<|USER|>{query_str}<|ASSISTANT|>")

        llm = HuggingFaceLLM(
            context_window=4096,
            max_new_tokens=256,
            generate_kwargs={"temperature": 0.7, "do_sample": False},
            system_prompt=system_prompt,
            query_wrapper_prompt=query_wrapper_prompt,
            tokenizer_name="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",
            model_name="meta-llama/Llama-2-7b-chat-hf",
            device_map="auto",
            stopping_ids=[50278, 50279, 50277, 1, 0],
            tokenizer_kwargs={"max_length": 4096},
            # uncomment this if using CUDA to reduce memory usage
            # model_kwargs={"torch_dtype": torch.float16}
        )
        service_context = ServiceContext.from_defaults(chunk_size=1024, llm=llm)
        print("hf_RAG_model_initialized")

initialize_model()

#put world_setting and daily plan into initialization
def generate_index(text):
    documents = StringIterableReader().load_data(texts=[text])
    index = VectorStoreIndex.from_documents(documents, service_context=service_context)
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
        prompt = prompt.format(person.name, 
                               person.description, 
                               ", ".join(list(world.town_areas.keys())),
                               "{} plan to {}".format(person.name.split(" ")[0], 
                                                      person.plan_lst["{}:00".format(world.cur_time)]),
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
        prompt = prompt.format(person.name,
                               person.description,
                               person.location,
                               person.plan_lst["{}:00".format(world.cur_time)],
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
    # given the prompt provided, create output from the pipeline
    response = pipe(prompt, max_new_tokens=max_new_tokens, min_new_tokens=min_new_tokens)

    return response

def generate_response_rag(prompt, index, max_new_tokens=100, min_new_tokens=50):
    # given the prompt provided, create output from the pipeline
    # response = pipe(prompt, max_new_tokens=max_new_tokens, min_new_tokens=min_new_tokens)
    query_engine = index.as_query_engine()
    response = query_engine.query(prompt)

    return response