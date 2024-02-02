from person import *
from world import *
from global_methods import *

def run_simulation(hours_to_run=16, continue_simulation = False):
    if not continue_simulation:
        filename = generate_simulation_filename() #Generate unique file name for new simulation
        world = World() #Initialize new world and agents
        for resident in world.residents:
            world.residents[resident].plan() # Start first daily plan for the person 
    else:
        filename = select_simulation_file() #User selects a existing simulation
        if filename:
            world = load_simulation_state(filename)
        else:
            print("Starting a new simulation.")
            filename = generate_simulation_filename()
            world = World()
            for resident in world.residents:
                world.residents[resident].plan() # start first daily plan for the person 
    
    #the current time is 8
    for _ in range(hours_to_run):
        for resident in world.residents:
            world.residents[resident].action()
        world.cur_time += 1
        save_simulation_state(world, filename) # save state at the end of each hour
    
    return world
    

if __name__ == '__main__':
    run_simulation()

#     while True:
#         count = input("Enter iteration to run: ")
#         while count > 0:
#             run_simulation()
#             count -= 1

