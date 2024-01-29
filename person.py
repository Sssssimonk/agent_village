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
        response = generate_response(prompt)

        self.daily_plan = response

        print("The daily plan for " + self.name + "is : " + self.daily_plan)

    def retrieve(self):
        pass 

    def reflect(self):
        pass 

    def action(self, task="move"):

        if task == "move":
            prompt = generate_prompt("action", self, self.world)
            response = generate_response(prompt)

            return response
        
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




        


