from person import *
from world import *
from global_methods import *
import sys
from llm import initialize_model, rate_plan

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

# TODO add rag compatible
def if_meet(world, place_dict):
    for key_place, value_agent in place_dict.items():
        if len(value_agent) == 1: # if current place only have one agent, agent will do its own action
            print(world.residents[value_agent[0]].basic_memory[-1].split(',')[1])
        else: # if current place have at least 2 agents, they will start a conversation
            main_agent = world.residents[value_agent[0]]
            target_agent = value_agent[1:]
            main_agent.meet = target_agent
                
            for people in value_agent:
                world.residents[people].other_meet(value_agent) # add "I meet xx on xxx" to memory
                   
            print(world.agent_meet(value_agent, key_place))
                
            chat_if_result = main_agent.action("if_chat")
            if chat_if_result:
                chat_result = main_agent.action("chat")
                print(chat_result)
                for people in value_agent:
                    world.residents[people].basic_memory[-1] += ", and we have a conversion that content is:"
                    world.residents[people].basic_memory[-1] += chat_result
            else:
                world.residents[people].basic_memory[-1] += "."
    

def run_simulation(hours_to_run=4, continue_simulation=False):
    initialize_model('both')
    # world, filename = check_continue_simulation(continue_simulation=continue_simulation)
    world_rag = World()
    world_basic = World() 

    for _ in range(hours_to_run):
        # end of the day
        if world_basic.cur_time > 24: 
            print("=== Today is over and a new day will begin soon. ===\n")
            print("****************************")
            for resident in world_basic.residents:
                world_basic.residents[resident].retrieve()  # summarize memory then reset it
                world_basic.cur_time = 8
            
            for resident in world_rag.residents:
                world_rag.residents[resident].rag_retrieve()
                world_rag.cur_time = 8

            continue
        
        # start of the day
        if world_basic.cur_time == 8:
            make_plans(world_rag, world_basic)    
        
                    # element = input("Do yu need Special Event on that day? y/n")      
            # if element == 'y':
            #     pass
#                 name_special = input("Which will agent will have? {}".format(", ".join(list(agent.keys()))))
#                 special_event = input("---")
#                 world.residents[name_special].special_event = special_event
            
                
        print("Current time is {}:00.".format(world_basic.cur_time))

        # Now the iteration actually starts 
        place_dict_basic = {}
        place_dict_rag = {}

        """
        Example: {"School":['Tom', 'Jack'], "Shop":['David'], "Police Office":[]}
        """
        for resident in world_basic.residents:
#             world.residents[resident].action("place")
            world_basic.residents[resident].action("move")
            # check if agent's location in the dict
            if world_basic.residents[resident].location in place_dict_basic.keys():
                name = world_basic.residents[resident].name.split(" ")[0]
                place_dict_basic[world_basic.residents[resident].location].append(name)
            else: # if agent's location not in the dict, add to the dict
                name = world_basic.residents[resident].name.split(" ")[0]
                place_dict_basic[world_basic.residents[resident].location] = [name]

        if_meet(world_basic, place_dict_basic)

        for resident in world_rag.residents:
#             world.residents[resident].action("place")
            world_rag.residents[resident].rag_action("move")
            # check if agent's location in the dict
            if world_rag.residents[resident].location in place_dict_rag.keys():
                name = world_rag.residents[resident].name.split(" ")[0]
                place_dict_rag[world_rag.residents[resident].location].append(name)
            else: # if agent's location not in the dict, add to the dict
                name = world_rag.residents[resident].name.split(" ")[0]
                place_dict_rag[world_rag.residents[resident].location] = [name]
        
        if_meet(world_rag, place_dict_rag)

                    
        print("====== This hour is end, new hour will start. ======")
        world_basic.cur_time += 1
        world_rag.cur_time += 1

        #save_simulation_state(world, filename) # save state at the end of each hour

    return world_basic, world_rag

def make_plans(world_rag, world_basic):
        # create daily plans for basic world residents
    for resident in world_basic.residents:
        world_basic.residents[resident].plan()
            
            # print(world.residents[resident].plan_lst)
            #print(world_basic.residents[resident].daily_plan)

    for resident in world_rag.residents: # plans for rag world residents
        world_rag.residents[resident].rag_plan()

        # rate which plan is better 
    for resident in world_basic.residents:
        name = resident.name.split(' ')[0]       # name will be Tom Jackson, etc.  out put is Tom
        plan1 = world_basic[name].daily_plan
        plan2 = world_rag[name].daily_plan
        score = rate_plan(plan1, plan2)     # score is ['78', '95']
        if float(score[0]) > float(score[1]):
            world_rag[name].daily_plan = world_basic[name].daily_plan 
        else:
            world_basic[name].daily_plan = world_rag[name].daily_plan

    world_basic.reset_date()
    world_rag.reset_date()    
    print("****************************")
    print("Today is {}, it's {}.\n".format(world_basic.date, world_basic.weather))

if __name__ == '__main__':
    if len(sys.argv) > 1: # continue on previous simulation
        run_simulation(int(sys.argv[1]), bool(sys.argv[2]))
    else: # start a new simulation
        run_simulation(int(sys.argv[1]))


