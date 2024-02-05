from person import *
from world import *
from global_methods import *

def run_simulation(hours_to_run=16, continue_simulation = False):

    # ====================== Load or Start New Simulation ====================== #
    # Start a new simulation
    if not continue_simulation:
        filename = generate_simulation_filename() #Generate unique file name for new simulation
        world = World()                           #Initialize new world and agents
        for resident in world.residents:          #Start first daily plan for each person 
            world.residents[resident].plan()    
    # Conitnue on previous simulation  
    else: 
        filename = select_simulation_file()       #User selects a existing simulation
        if filename:                              # if filename existing in the folder, load the simulation and continue
            world = load_simulation_state(filename)
        else:                                     # filename not existed, start a new simulation
            print("Starting a new simulation.")
            filename = generate_simulation_filename()
            world = World()
            for resident in world.residents:
                world.residents[resident].plan()  


    
    #the current time is 8
    for _ in range(hours_to_run): 
        for resident in world.residents:
            world.residents[resident].action()
        world.cur_time += 1
        save_simulation_state(world, filename) # save state at the end of each hour

        if world.cur_time == 24: # End of a day
            for resident in world.residents:
                world.residents[resident].reflect()
           
    
    return world
    

if __name__ == '__main__':
    run_simulation()



