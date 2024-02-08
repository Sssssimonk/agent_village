from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from transformers import BitsAndBytesConfig
from sentence_transformers import SentenceTransformer, util



# ==================== Initialzied HF model ==================== # 
bnb_config = BitsAndBytesConfig(load_in_4bit=True,
                                bnb_4bit_use_double_quant=True,
                                bnb_4bit_quant_type="nf4",
                                bnb_4bit_compute_dtype=torch.bfloat16
)

# use llama2 model in transfomers
access_token = "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"
model_id = "lmsys/vicuna-7b-v1.5"
# model_id = "meta-llama/Llama-2-7b-chat-hf"
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

sentence_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
print("hf_model_initialized")


def generate_prompt(task, person, world, **kwargs):
    # from prompt file task.txt, read the prompt template and then out put a str prompt.
    prompt_template = "prompt_templates" + "/"+ task + ".txt"

    file = open(prompt_template, "r")
    prompt = file.read()
    file.close()

    if task == "daily_plan":
        prompt = prompt.format(person.name, 
                            person.description, 
                            person.personality, 
                            world.town_areas.keys(), 
                            person.location)
    
    if task == "action":
        prompt = prompt.format(person.name,
                               person.description,
                               person.personality,
                               world.town_areas.keys(),
                               person.location,
                               person.daily_plan,
                               world.cur_time)
    if task == "update_location":
        prompt = prompt.format(person.name,
                               person.description, 
                               person.daily_plan,
                               world.cur_time,
                               person.location,
                               kwargs['action'], 
                               world.town_areas.keys(),
                               )

    if task == "summarize_action":
        prompt = prompt.format(person.name,
                               kwargs['memory'])
    return prompt

def generate_response(prompt, max_new_tokens=100, min_new_tokens=50):
    # given the prompt provided, create output from the pipeline
    response = pipe(prompt, 
                    max_new_tokens=max_new_tokens, 
                    min_new_tokens=min_new_tokens)[0]['generated_text']

    return response

def calculate_sentence_similarity(daily_plan, summarize_action):
    embedding_1= sentence_model.encode(daily_plan, convert_to_tensor=True)
    embedding_2 = sentence_model.encode(summarize_action, convert_to_tensor=True)
    similarity_score = util.pytorch_cos_sim(embedding_1, embedding_2).tolist()[0][0]
    return similarity_score