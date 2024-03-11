from person import *
from world import *
from global_methods import *
import sys

def check_continue_simulation(continue_simulation=False):
    if not continue_simulation:
        filename = generate_simulation_filename() #Generate unique file name for new simulation
        world = World() #Initialize new world and agents
    else:
        filename = select_simulation_file() #User selects a existing simulation
        if filename:
            world = load_simulation_state(filename)
        else:
            print("Starting a new simulation.")
            filename = generate_simulation_filename()
            world = World()

    return world, filename

def if_meet(world, place_dict):
    
    for key_place, value_agent in place_dict.items():
        if len(value_agent) == 1: # if current place only have one agent, agent will do its own action
            agent = value_agent[0]
            world.residents[agent].action()
            print(world.residents[agent].memory[-1].split(":00, ")[-1])
        
        else: # if current place have at least 2 agents, they will start a conversation
            world.agent_meet(value_agent)
    

def run_simulation(hours_to_run=4, continue_simulation=False):
    world, filename = check_continue_simulation(continue_simulation=continue_simulation)

    for _ in range(hours_to_run):
        # end of the day
        if world.cur_time > 23: 
            print("=== Today is over and a new day will begin soon. ===\n")
            print("****************************")
            for resident in world.residents:
                world.residents[resident].retrieve()  # summarize memory then reset it
                world.cur_time = 8
            
            continue
        
        
        if world.cur_time == 8:
            world.reset_date()
#             agent = list(world.residents.keys())
#             element = input("Do yu need Special Event on that day? y/n \t")      
#             while element == 'y':
#                 name_special = input("Which will agent will have? {}\t".format(", ".join(agent)))
#                 if name_special not in agent:
#                     name_special = input("Please enter a name from {}\t".format(", ".join(agent)))
#                 else:
#                     agent.remove(name_special)
                
#                 special_event = input("---")
#                 world.residents[name_special].special_event = str(special_event)
#                 if len(agent) == 0:
#                     break
#                 element = input("Do yu need Special Event on that day? y/n \t")   
#                 world.residents[name_special].special_event = special_event 
            for resident in world.residents:
                world.residents[resident].plan()
        
        print("Current time is {}:00.".format(world.cur_time))
        
        place_dict = {}
        """
        Example: {"School":['Tom', 'Jack'], "Shop":['David'], "Police Office":[]}
        """
        for resident in world.residents:
            place = world.residents[resident].action("place")
            name = world.residents[resident].name.split(" ")[0]
            if place in place_dict.keys():
                place_dict[place].append(name)
            else: 
                place_dict[place] = [name]
        
        print(place_dict)
        if_meet(world, place_dict)
                    
        print("====== This hour is end, new hour will start. ======")
        world.cur_time += 1
        save_simulation_state(world, filename) # save state at the end of each hour
    
    return world



if __name__ == '__main__':
    if len(sys.argv) > 1: # continue on previous simulation
        run_simulation(int(sys.argv[1]), bool(sys.argv[2]))
    else: # start a new simulation
        run_simulation(int(sys.argv[1]))