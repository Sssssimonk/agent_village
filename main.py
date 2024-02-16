from person import *
from world import *
from global_methods import *
import numpy as np
import sys
from llm import initialize_model

def check_continue_simulation(continue_simulation=False, rag=False):
    if not continue_simulation:
        filename = generate_simulation_filename() #Generate unique file name for new simulation
        world = World(rag) #Initialize new world and agents
    else:
        filename = select_simulation_file() #User selects a existing simulation
        if filename:
            world = load_simulation_state(filename)
        else:
            print("Starting a new simulation.")
            filename = generate_simulation_filename()
            world = World(rag)

    return world, filename

def rag_simulation(hours_to_run=4, continue_simulation=False):
    initialize_model('rag')
    world, filename = check_continue_simulation(continue_simulation=continue_simulation, rag=True)

    for _ in range(hours_to_run):
        place_dict = {}
        if world.cur_time == 8:  # start of the day
            # create daily plans
            for resident in world.residents:
                world.residents[resident].rag_plan() # start first daily plan for the person 
                print(world.residents[resident].plan_lst)
                print(world.residents[resident].daily_plan)

            world.rest_date() 
            print("****************************")
            print("Today is {}, it's {}.\n".format(world.date, world.weather))    

        if world.cur_time > 23: # end of the day
            print("=== Today is over and a new day will begin soon. ===\n")
            print("****************************")
            for resident in world.residents:
                world.residents[resident].retrieve()  # summarize memory then reset it
                world.cur_time = 8
            
            continue

        print("Current is on {}:00.".format(world.cur_time))

        
        # for resident in world.residents:
        #     world.residents[resident].action("place") # update resident's location
        #     world.residents[resident].action("move")
        #     if world.residents[resident].location in place_dict.keys():
        #         name = world.residents[resident].name.split(" ")[0]
        #         place_dict[world.residents[resident].location].append(name)
        #     else:
        #         name = world.residents[resident].name.split(" ")[0]
        #         place_dict[world.residents[resident].location] = [name]


        # save_simulation_state(world, filename) # save state at the end of each hour

    return world


def run_simulation(hours_to_run=16, continue_simulation=False, rag=False):
    if rag == True:
        rag_simulation(hours_to_run=hours_to_run, continue_simulation=continue_simulation)
        return 
    
    initialize_model('default')
    world, filename = check_continue_simulation(continue_simulation=continue_simulation)
    
    for _ in range(hours_to_run):
        place_dict = {}
        if world.cur_time == 8:  # start of the day
            # create daily plans
            for resident in world.residents:
                world.residents[resident].plan()
                print(world.residents[resident].plan_lst)
                print(world.residents[resident].daily_plan)
            world.rest_date()    
            print("****************************")
            print("Today is {}, it's {}.\n".format(world.date, world.weather))    
        

        if world.cur_time > 23: # end of the day
            print("=== Today is over and a new day will begin soon. ===\n")
            print("****************************")
            for resident in world.residents:
                world.residents[resident].retrieve()  # summarize memory then reset it
                world.cur_time = 8
            
            continue
        
        
        print("Current is on {}:00.".format(world.cur_time))
        
        for resident in world.residents:
            world.residents[resident].action("place") # update resident's location
            world.residents[resident].action("move")
            if world.residents[resident].location in place_dict.keys():
                name = world.residents[resident].name.split(" ")[0]
                place_dict[world.residents[resident].location].append(name)
            else:
                name = world.residents[resident].name.split(" ")[0]
                place_dict[world.residents[resident].location] = [name]
        
        for key_place, value_agent in place_dict.items():
            if len(value_agent) == 1:
                print(world.residents[value_agent[0]].memory[-1].split(',')[1])
            else:
                
                main_agent = world.residents[value_agent[0]]
                target_agent = value_agent[1:]
                main_agent.meet = target_agent
                
                for people in value_agent:
                    world.residents[people].other_meet(value_agent)
                    
                print(world.agent_meet(value_agent, key_place))
                
                chat_if_result = main_agent.action("if_chat")
                if chat_if_result:
                    chat_result = main_agent.action("chat")
                    print(chat_result)
                    for people in value_agent:
                        world.residents[people].memory[-1] += ", and we have a conversion that content is:"
                        world.residents[people].memory[-1] += chat_result
                else:
                    world.residents[people].memory[-1] += "."
                    
        print("====== This hour is end, new hour will start. ======")
        world.cur_time += 1
        save_simulation_state(world, filename) # save state at the end of each hour
    
    return world
    

if __name__ == '__main__':
    if len(sys.argv) > 1: # continue on previous simulation
        run_simulation(int(sys.argv[1]), bool(sys.argv[2]))
    else: # start a new simulation
        run_simulation(int(sys.argv[1]))


