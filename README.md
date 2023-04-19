# group7-project
CMSE 202 - Modeling an Ecosystem Project

Group Names: Gary Service, Kanishk Pal, Nitin Polavarapu, Ronald Gomillion, and Sage Foster

Basic Project Description: This repository is an agent based model for an ecosystem of grass, an herbivore, and a carnivore. Since the animals in this model are objects, they are able to interact with eachother and the environment.The herbivore and carnivores are able to reproduce and mutate, which should cause some natural selection to occur. 

GOAL - The goal is to accurate model and ecosystem with stable predator-prey dynamics. After achieving the base goal we can add complexity as we wish. We will be using an agent based model simulation with packages like numpy, pandas, mathplotlib, and pygame. We will also use various data structures like lists, dictionaries, etc.

File descriptions:

- base-herbivore.png:
    This file is the image used for the herbivore in the model
    
- base-carnivore.png:
    This file is the image used for the carnivore in the model
    
- tests:
    This is a directory filled with pngs of graphs, and mutliple csv files. These are from tests run while finalizing the model
    
- Data analysis.ipynb:
    This is a jupyter notebook used to generate graphs from csv files 
    
- carnivore.py:
    This is a python file that defines the carnivore class and its methods
    
- herbivore.py:
    This is a python file that defines the herbivore class and its methods
    
- environemnt.py:
    This is a python file that defines functions used in setting up, and iterating through the agent based model
    
- main.py:
    This python file imports from the other files in the repository, and then runs the model. When run, it plays the animation of the model in a pygame window, and then outputs a csv file containing the genes of all agents that lived in the model.



