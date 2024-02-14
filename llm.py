from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from transformers import BitsAndBytesConfig



# ==================== Initialzied HF model ==================== # 
bnb_config = BitsAndBytesConfig(load_in_4bit=True,
                                bnb_4bit_use_double_quant=True,
                                bnb_4bit_quant_type="nf4",
                                bnb_4bit_compute_dtype=torch.bfloat16
)

# use llama2 model in transfomers
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

print("hf_model_initialized")


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
                before_action = person.memory
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
    # given the prompt provided, create output from the pipeline
    response = pipe(prompt, max_new_tokens=max_new_tokens, min_new_tokens=min_new_tokens)

    return response