from person import *
from world import *

def run_simulation():
    world = World() # world and agent will be initialized
    for resident in world.residents:
        world.residents[resident].plan() # start first daily plan for the person 

    # we need a log system to load existing file and continue the simulation  use pickle?

    

if __name__ == '__main__':
    world = World()
    
    
    print(generate_prompt("daily_plan", world.residents["Tom"], world))
#     while True:
#         count = input("Enter iteration to run: ")
#         while count > 0:
#             run_simulation()
#             count -= 1

