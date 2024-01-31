from person import *
from world import *

def run_simulation(hours_to_run=16):
    world = World() # world and agent will be initialized
    for resident in world.residents:
        world.residents[resident].plan() # start first daily plan for the person 

    # the current time is 8
    for _ in range(hours_to_run):
        for resident in world.residents:
            world.residents[resident].action()
        world.cur_time += 1
        
    return world
    

if __name__ == '__main__':
    run_simulation()

#     while True:
#         count = input("Enter iteration to run: ")
#         while count > 0:
#             run_simulation()
#             count -= 1

