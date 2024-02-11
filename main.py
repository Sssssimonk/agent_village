from person import *
from world import *
from global_methods import *
import numpy as np

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday","Saturday", "Sunday"]
weather = ["Sunny", "Rain", "Cloudy"]

def run_simulation(hours_to_run=16, continue_simulation = False):
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
    
    #the current time is 8
    for _ in range(hours_to_run):
        place_dict = {}
        date_index = -1
        if world.cur_time == 8:
            world.weather = weather[np.random.choice(len(weather), p=[0.5, 0.2, 0.3])]
            
            for resident in world.residents:
                world.residents[resident].plan()
                print(world.residents[resident].plan_lst)
                print(world.residents[resident].daily_plan)
            if type(world.date) == str:
                date_index = np.random.randint(len(days))
                world.date = days[date_index]
            else:
                date_index = 0 if date_index >= len(days) - 1 else date_index + 1
                world.date = days[date_index]
                
            print("****************************")
            print("Today is {}, it's {}.\n".format(world.date, world.weather))    
        
        if world.cur_time > 23:
            print("=== Today is over and a new day will begin soon. ===\n")
            print("****************************")
            for resident in world.residents:
                world.residents[resident].retrieve()
                world.cur_time = 8
            
            continue
        
        
        print("Current is on {}:00.".format(world.cur_time))
        
        for resident in world.residents:
            world.residents[resident].action("place")
            world.residents[resident].action()
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
                    meet_agent = [world.residents[index].name for index in value_agent]
                    meet_agent.remove(world.residents[people].name)
                    world.residents[people].memory[-1] += " I see {} on {}".format(", ".join(meet_agent),
                                                                                   key_place
                                                                                  )
                more_agent_action = [". ".join(world
                                              .residents[agent_name]
                                              .memory[-1]
                                              .split(".")[1:])
                                     .replace(" I ",
                                              " {} ".format(world.residents[agent_name].name)) for agent_name in value_agent]
                print("{} are on {}.\n{}.".format(", ".join([world.residents[agent_name].name for agent_name in value_agent]),
                                                key_place,
                                                ".\n".join(more_agent_action)
                                               ))
                chat_if_result = main_agent.action("if_chat")
                if chat_if_result:
                    chat_result = main_agent.action("chat")
                    print(chat_result)
                    for people in value_agent:
                        world.residents[people].memory[-1] += ", and we have a conversion that content is:"
                        world.residents[people].memory[-1] += chat_result
                else:
                    world.residents[people].memory[-1] += "."
                    
        
        print()
        print("====== This hour is end, new hour will start. ======")
        print()
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

