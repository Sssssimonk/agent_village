import pickle
import os

def save_simulation_state(world, filename="simulation_state.pkl"):
    with open(filename, 'wb') as f:
        pickle.dump(world, f)

def load_simulation_state(filename="simulation_state.pkl"):
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)
    return None
    
def delete_saved_state(filename="simulation_state.pkl"):
    if os.path.exists(filename):
        os.remove(filename)