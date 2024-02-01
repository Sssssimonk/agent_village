import pickle
import os
import glob
import re

def generate_simulation_filename():
    existing_files = glob.glob("simulation_*.pkl")
    max_number = 0
    for file in existing_files:
        # Extracting the number from filenames like 'simulation_1.pkl'
        number = int(file.replace("simulation_", "").replace(".pkl", ""))
        if number > max_number:
            max_number = number

    new_number = max_number + 1
    return f"simulation_{new_number}.pkl"

def select_simulation_file():
    existing_files = glob.glob("simulation_*.pkl")
    if not existing_files:
        print("No saved simulation found.")
        return None
    
    existing_files.sort(key=lambda x: int(re.search(r"simulation_(\d+)\.pkl", x).group(1)))
    
    while True:
        for i, file in enumerate(existing_files, 1):
            print(f"{i}. {file}")
        choice = input("Select a simulation to load (number), or type 'exit' to start a new simulation: ")
        
        if choice.lower() == 'exit':
            return None
        
        try:
            choice = int(choice) - 1
            if 0 <= choice < len(existing_files):
                return existing_files[choice]
            else:
                print("Invalid Selection: number out of range.\n")
        except ValueError:
            print("Invalid input: please enter a numerical value.\n")


def save_simulation_state(world, filename):
    with open(filename, 'wb') as file:
        pickle.dump(world, file)

def load_simulation_state(filename):
    if os.path.exists(filename):
        with open(filename, 'rb') as file:
            return pickle.load(file)
    return None
    
def delete_saved_state(filename):
    if os.path.exists(filename):
        os.remove(filename)