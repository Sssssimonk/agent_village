import warnings
warnings.filterwarnings("ignore")

from person import *
from world import *
from global_methods import *
import sys
import pandas as pd
import matplotlib.pyplot as plt

def plot_data(world, hours_to_run):
    """
    When the technology is run on this project, drawings will 
    be made based on the generated data to compare the differences 
    between the ordinary model and the RAG model.
    
    Args:
        world: environment
    """
    frequency_data = {'basic': world.results['frequency'].count("basic"), 
                      'rag': world.results['frequency'].count("rag")}
    names = list(frequency_data.keys())
    values = list(frequency_data.values())
    summary = "In this time, the project run total {} hours, we have {} agents.".format(hours_to_run, len(world.residents))
    print("This time, we use total {} times by RAG and normal model, {} is RAG model, {} is basic model.".format(
        len(world.results['frequency']),
        frequency_data['rag'],
        frequency_data['basic']
    ))
    plt.bar(range(len(frequency_data)), values, tick_label=names)
    plt.show()
    
    print("This is points compare for daily action by generate text between RAG model and basic mdoel.")
    print(pd.DataFrame(world.results['points']).describe())
    a = np.array(world.results['points']["rag_model"])
    b = np.array(world.results['points']["basic_model"])
    plt.plot(a, label="RAG model")
    plt.plot(b, label="basic mdoel")
    plt.legend(loc='best')
    plt.show()
    
    
    print("This is points compare for daily plan by generate text between RAG model and basic mdoel.")
    print(pd.DataFrame(world.results['plan']).describe())
    a = np.array(world.results['plan']["rag_model"])
    b = np.array(world.results['plan']["basic_model"])
    plt.plot(a, label="RAG model")
    plt.plot(b, label="basic mdoel")
    plt.legend(loc='best')
    plt.show()
    
    if len(world.results['summary']['basic_model']) != 0 and len(world.results['summary']['rag_model']) != 0:
        print("This is points compare for daily summary by generate text between RAG model and basic mdoel.")
        print(pd.DataFrame(world.results['summary']).describe())
        a = np.array(world.results['summary']["rag_model"])
        b = np.array(world.results['summary']["basic_model"])
        plt.plot(a, label="RAG model")
        plt.plot(b, label="basic mdoel")
        plt.legend(loc='best')
        plt.show()
        

def check_continue_simulation(continue_simulation=False):
    """
    Determine whether you need to use the new environment or use the old environment
    """
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
    """
    Check the number of people in a location and generate new action 
    patterns based on the number of people
    """
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
        
        ### check if it's new day 
        if world.cur_time == 8:
            world.reset_date()
            agent = list(world.residents.keys())
            element = input("Do yu need Special Event on that day? y/n \t")      
            while element == 'y':
                name_special = input("Which will agent will have? {}\t".format(", ".join(agent)))
                if name_special not in agent:
                    name_special = input("Please enter a name from {}\t".format(", ".join(agent)))
                else:
                    agent.remove(name_special)
                
                special_event = input("Please enter event and time of excute event: \t")
                world.residents[name_special].special_event = str(special_event)
                if len(agent) == 0:
                    break
                element = input("Do yu need Special Event on that day? y/n \t")   
                world.residents[name_special].special_event = special_event 
            for resident in world.residents:
                world.residents[resident].plan()
            print(pd.DataFrame(world.plan))
        
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
    
    plot_data(world, hours_to_run)
    return world



if __name__ == '__main__':
    run_simulation(int(sys.argv[1]))