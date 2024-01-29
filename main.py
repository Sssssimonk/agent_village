from person import *
from world import *

def run_simulation():
    world = World()
    

if __name__ == '__main__':
    world = World()
    
    
    print(generate_prompt("daily_plan", world.residents["Tom"], world))
#     while True:
#         count = input("Enter iteration to run: ")
#         while count > 0:
#             run_simulation()
#             count -= 1

