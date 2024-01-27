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
        pass 

    def plan(self):
        prompt = generate_prompt("daily_plan", self, self.world)
        response = generate_response(prompt)

        self.daily_plan = response

    def retrieve(self):
        pass 

    def reflect(self):
        pass 

    def action(self):
        prompt = generate_prompt("action", self, self.world)

        pass


