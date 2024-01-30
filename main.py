from person import *
from world import *

def run_simulation():
    world = World() # world and agent will be initialized
    for resident in world.residents:
        world.residents[resident].plan() # start first daily plan for the person 

    # test what tom will do 
    tom = world.residents['Tom']
    tom.action()

    

    

    

if __name__ == '__main__':
    run_simulation()

#     while True:
#         count = input("Enter iteration to run: ")
#         while count > 0:
#             run_simulation()
#             count -= 1

