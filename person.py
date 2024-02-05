from llm import generate_prompt, generate_response, calculate_sentence_similarity

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
        """ create daily plan whenever the new day starts """
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
        """summarize the daily actions and calculate semantic simlarity between daily plan and summarized actions"""
        actions_done = " ".join(self.memory[-16:])      # retrieve today's memory and type cast into a string
        prompt = generate_prompt("summarize_action", self, self.world, memory=actions_done)
        response = generate_response(prompt, max_new_tokens=500, min_new_tokens=200)
        summary = response.split("<Output>:")[1]

        print("Summarizing today's memory")
        print(summary)

        # ======== calculate semantic similarity ======= #
        daily_plan = self.memory[self.world.days_passed * 16]
        score = calculate_sentence_similarity(daily_plan, summary)

        print("The semantic memory similarity for " + self.name + " is " + str(score))


        

        

    def action(self, task="move"):

        if task == "move":
            prompt = generate_prompt("action", self, self.world)
            response = generate_response(prompt, 
                                         max_new_tokens=80, 
                                         min_new_tokens=30)
            action = response.split("<Output>:")[1]  # delete prompt template provided
            
            self.memory.append("The Current Time is " + str(self.world.cur_time) + " :00 " + action)

            print("The Current Time is " + str(self.world.cur_time) + " :00 " + action)
            # ========== update location ========== #
            #TODO: Output not working, need improvements
            # prompt = generate_prompt("update_location", 
            #                          self, 
            #                          self.world,
            #                          action=action)

            
            # response = generate_response(prompt, 
            #                              max_new_tokens=20)

            # print(response)
            # location = response.split(":")[-1].strip()      # retrieve the location generated
            # print("The generated loaction to move is : " + location)
            # while location not in self.world.town_areas: 
            #     prompt = generate_prompt("update_location", self, self.world, action=action)
            #     response = generate_response(prompt, max_new_tokens=20)
            #     location = response.split(":")[-1].strip()
            #     print("Location not working, genreated a new location : " + location)

            # self.location = location
        
            #TODO: adjust generation config, make the output more stable 

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




        


