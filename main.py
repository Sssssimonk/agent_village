from person import *
from world import *
from global_methods import *

def run_simulation(hours_to_run=16, continue_simulation = False):
    if not continue_simulation:
        delete_saved_state() #Delete existing saved state when starting new simulation
        world = World() #initialize world and agents
        for resident in world.residents:
            world.residents[resident].plan() # start first daily plan for the person 
    else:
        world = load_simulation_state() # Attempt to load the saved state
        if world is None:
            world = World() # Initialize a new world if no saved state is found
            for resident in world.residents:
                world.residents[resident].plan() # start first daily plan for the person 
    
    #the current time is 8
    for _ in range(hours_to_run):
        for resident in world.residents:
            world.residents[resident].action()
        world.cur_time += 1
        save_simulation_state(world) # save state at the end of each hour
    
    return world
    

if __name__ == '__main__':
    run_simulation()

#     while True:
#         count = input("Enter iteration to run: ")
#         while count > 0:
#             run_simulation()
#             count -= 1

