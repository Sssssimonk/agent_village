## Data Access
The data in our project is about the world settings, including the area in the town and the town's residents, their description and personality.
The data is stored in [world_settings.json](https://github.com/Sssssimonk/agent_village/blob/main/world_settings.json).

## Set Up
### Launch the Server
After login to DSMLP, run the following commands:
```bash
launch-scipy-ml.sh -W DSC180A_FA23_A00 -c 8 -m 64 -g 2 -p low
```

### Software Dependencies
The librabries and packages is in [requirements.txt](https://github.com/Sssssimonk/agent_village/blob/main/requirements.txt). To install these dependencies, run the following command in your terminal:

```bash
pip install -r requirements.txt
```

This command should be executed in the environment where you intend to run the project. It will automatically install all the libraries and packages specified in the requirements.txt file,
which is essential to reproduce our project.

## Parameters
1. `hours_to_run` (optional): The number of hours you want the simulation to run. Default is 16

## Reproducing Results
To run the simulation, you simply need to run the `main.py`. This file will call the functions we defined in other files, so it is the primary entry point for our project and executes the necessary code to generate the results.

### Add openai api key to the `llm.py`
In order to run the code, an openai api key is needed.
Add your api key to `llm.py`  `rate_plan` function where a comment says # add your api key here.

### Running `main.py`
Follow these steps to run `main.py`:
1. **Open Terminal or Command Line:**
   - Navigate to the directory `agent_village`.
2. **Execute the Script:**
   - To run the script with default parameters, execute:
   ```bash
   python main.py
   ```
   - To customize the parameters, follow the format below:
   ```bash
   python main.py [hours_to_run]
   ```
   Replace `[hours_to_run]` with the desired number of hours for the simulation based on your preference. 


   **Example**
   - To run the simulation for 3 hours:
   ```bash
   python main.py 3
   ```
