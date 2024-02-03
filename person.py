from llm import generate_prompt, generate_response

class Person:

    def __init__(self, name, description, personality, world) -> None:
        self.name = name
        self.description = description
        self.memory = []
        self.location = "Town Square"
        self.personality = personality
        # hard code self.world?
        self.world = world
        self.daily_plan = None


    def perceive(self, world):
        # perceive current environment and memorize into memory
        pass 

    def plan(self):
        # create daily plan whenever the new day starts
        prompt = generate_prompt("daily_plan", self, self.world)
        response = generate_response(prompt, 
                                     max_new_tokens=300, 
                                     min_new_tokens=100)
        
        daily_plan = response.split("<Output>:")[1]     # delete prompt template provided
        
        # update memory
        self.daily_plan = daily_plan
        self.memory.append(daily_plan)
        
        print("The daily plan for " + self.name + " is : " + self.daily_plan)

    def retrieve(self):
        pass 

    def reflect(self):
        # TODO: process memory, remove anything useless
        pass 

    def action(self, task="move"):

        if task == "move":
            prompt = generate_prompt("action", self, self.world)
            response = generate_response(prompt, max_new_tokens=80, min_new_tokens=30)
            action = response.split("<Output>:")[1]  # delete prompt template provided
            
            self.memory.append("Current Time is " + str(self.world.cur_time) + action)

            print(action)
            # ========== update location ========== #

            prompt = generate_prompt("change_location", self, self.world)
            response = generate_response(prompt, max_new_tokens=50, action=action)

            location = response.split(":")[-1].strip()      # retrieve the location generated
            while location not in self.world.town_areas: 
                prompt = generate_prompt("change_location", self, self.world)
                response = generate_response(prompt, max_new_tokens=50, action=action)
                location = response.split(":")[-1].strip()

            self.location = location
        
            #TODO: adjust generation config, make the output more stable 
            #TODO: enable agent to move to another space
        if task == "chat":
            #TODO
            pass

        if task == "some other action":
            #TODO
            pass

# ===================================== Agent action with RAG ======================================#

    def rag_plan(self):
        # given memory in vector database, create daily plan
        pass 

    def rag_retreive(self):
        # perceive current environment and memorize into vector database(memory)
        pass

    def rag_action(self):
        pass




        


