#!/usr/bin/env python
# coding: utf-8

# ### Version2.2: 
# Automatically generates the output and histogramAssessment sections to a single script as the Athena DQdisplay config script for a chosen main_folder - with given ROOT file(run_forconfig) 
# Author: Cary Randazzo
# Date: 10-27-21


# In[1]:


# IMPORTS
import ROOT
import pandas as pd
import os


# In[54]:


# FUNCTIONS
def map_paths(tf,file,f_path,f_path_list,folder_to_gen):  
    """
    Preprocesses ROOT runfile, outputs path information of all histograms in directory of interest(folder_to_gen).
    """
    
    # Main loop
    for key in tf.GetListOfKeys():    
        input = key.ReadObj()
        
        # Determine if the location in the file we are at is a directory
        if issubclass(type(input),ROOT.TDirectoryFile):   
        
            # Record the path of the directory we are looking in
            try:
                f_path = input.GetPath() 
            except:
                print("cant GetPath")

            # Split the path by '/' so we can determine where we are in the folder structure        
            try:
                split_path = f_path.split("/")
            except:
                print('cant split_path')            
            
            # Recursively go deeper into the file structure depending on the length of split_path
#             if len(split_path) == 3:
    
            if 'run' in split_path[-1]:
                # We are 2 directories deep, go deeper
                f_path,f_path_list = map_paths(input,file,f_path, f_path_list,folder_to_gen)  
            elif len(split_path) > 2 and folder_to_gen in split_path[-1]:                
                # We are greater than 2 directories deep and these directories include folder_to_gen
                f_path, f_path_list = map_paths(input,file,f_path, f_path_list,folder_to_gen)     
            elif len(split_path) > 2 and any(folder in split_path for folder in [folder_to_gen]):                
                # We are greater than 2 directories deep and these directories include any folders in folder_to_gen
                f_path, f_path_list = map_paths(input,file,f_path, f_path_list,folder_to_gen)         
            
            else:
                pass
            
            # Record the file_path that will result now that we are done with the current folder level
            #  i.e. the folder path that results from going up a level in the directory
            f_path = f_path.split('/')
            f_path = '/'.join(f_path[:-1])
            
                
        elif issubclass(type(input),ROOT.TH1):
            
            # Record the path of the directory we are looking in with the name of the hist file as part of the path
            try:
                f_path_th1 = f_path + '/' + input.GetName()                
            except:
                print("cant GetPath2")

            # Get the part of f_path that follows the ':'
            f_path_th1 = f_path_th1.split(':')
            f_path_th1 = f_path_th1[1][1:]
            
            # Adds the TH1 path to the list of paths
            f_path_list.append(f_path_th1)
    
    return f_path, f_path_list


def map_directory_paths_final(f_path_list):
    """
    Maps the histogram paths in f_path_list from map_paths() to a multi level dictionary.
    """
    
    architecture_map = ['/'.join(path.split('/')[1:]) for path in f_path_list]
    dict_ = {}

    for a in architecture_map:
        tmp = dict_
        for x in a.split('/'):            
            tmp = tmp.setdefault(x,{})        
    
    return dict_


def doit_output(dict_,path_list,key,f,alg_out,start_set):
    """
    Writes the Output section of the config script.
    """
    
    
    # Initialize a tab worth of whitespace
    tab = '    '
    
    # Set the output as False for this level of the recursion loop
    output_set = False
    
    # Loop through the keys in the current level of the dictionary
    for key in dict_.keys():

        # If the directory at dict_[key] is not an empty dictionary
        if dict_[key] != {}:
            # Then this is not a histogram and we need to recursively go deeper in the file structure
            
#             print('goin down from:',path_list)

            # Store the key for the pathing and recursion
            path_list.append(key)

#             print('I went down to:',path_list)

            # If we have not yet written the starting lines of code to the script, do so now
            if start_set == False:
                f.write('#############\n# Output\n#############\n\n')
                f.write(f'output top_level{" {"}\n')
                f.write(f'{tab}output {path_list[-1]}{" {"}\n')
                f.write(f'{tab*2}algorithm = {alg_out}\n\n')

                start_set = True
            # This is not the start of the file, therefore start_set is True and it it some directory further in the file structure
            else:
                # Write the code for opening the directory at path_list[-1]
                f.write(f'{tab*(len(path_list))}output {path_list[-1]}{" {"}\n')

            # Recursively go deeper into the file structure, storing data on the key, path_list, and if the starting output has been set
            key, path_list,start_set = doit_output(dict_[key],path_list,key,f,alg_out,start_set)

#             print('goin up from:',path_list)

            # If the path list only contains an empty list
            if path_list == []:
                pass
            # Otherwise, close the directory that is stored in path_list
            else:
                # Write the code for the closing part of this directory to the file
                f.write(f'{tab*(len(path_list))}{"}"} # {path_list[-1]}\n\n')

            # Go up a level after coming out of the recursion
            path_list = path_list[:-1]

#             print('I went up to:',path_list)


        # If the current level of the dictionary at dict_[key] only contains an empty dictionary,
        elif dict_[key] == {}:
            #this key is a histogram
            pass
            
    return key, path_list, start_set


def doit(dict_,path_list,key,f,alg_in,hist_algorithm,display, reference, start_set):
    """
    Writes the Histogram Assessment part of the config script.
    """
    
    # Initialize a tab worth of whitespace
    tab = '    '
    
    # Set the output as False for this level of the recursion loop
    output_set = False
    
    # Loop through the keys in the current level of the dictionary
    for key in dict_.keys():

        # If the directory at dict_[key] is not an empty dictionary
        if dict_[key] != {}:
            # Then this is not a histogram and we need to recursively go deeper in the file structure
            
#             print('goin down from:',path_list)

            # Store the key for the pathing and recursion
            path_list.append(key)
    
#             print('I went down to:',path_list)

            
            # If we have not yet written the starting lines of code to the script, do so now
            if start_set == False:
                f.write('######################\n# Histogram Assessment\n######################\n\n')
                f.write(f'dir {path_list[-1]}{" {"}\n')
                f.write(f'{tab}algorithm = {alg_in}\n')
                f.write(f'{tab}reference = {reference}\n\n')
                start_set = True
            # This is not the start of the file, therefore start_set is True and it it some directory further in the file structure
            else:
                # Write the code for opening the directory at path_list[-1]
                f.write(f'{tab*(len(path_list)-1)}dir {path_list[-1]}{" {"}\n')

            # Recursively go deeper into the file structure, storing data on the key, path_list, and if the starting output has been set
            key, path_list,start_set = doit(dict_[key],path_list,key,f,alg_in,hist_algorithm,display, reference, start_set)

#             print('goin up from:',path_list)

            # If the path list only contains an empty list
            if path_list == []:
                pass
            # Otherwise, close the directory that is stored in path_list
            else:
                # Write the code for the closing part of this directory to the file
                f.write(f'{tab*(len(path_list)-1)}{"}"} # {path_list[-1]}\n\n\n')

            # Go up a level after coming out of the recursion
            path_list = path_list[:-1]

#             print('I went up to:',path_list)

        # If the current level of the dictionary at dict_[key] only contains an empty dictionary,
        elif dict_[key] == {}:
            #this key is a histogram
#             print(path_list,'Im a histogram, write to file!)

            # If the output code has not been set for this lowest level directory
            if output_set == False:
            
                # Write the code for the output, then output_set is True
                f.write(f'{tab*(len(path_list))}output = {"/".join(path_list)}\n\n')
                output_set = True

            # Write the code for each histogram to the output file
            f.write(f'{tab*(len(path_list))}hist {key}{" {"}\n')
            f.write(f'{tab*(len(path_list)+1)}algorithm = {hist_algorithm}\n')
            f.write(f'{tab*(len(path_list)+1)}display = {display}\n')
            f.write(f'{tab*(len(path_list))}{"}"}\n')
            
    return key, path_list, start_set

def gen_script_output(run_forconfig,main_folder,alg_out,start_set):
    """
    Prepares the output file for writing the output part of the config script. Also writes necessary end code to script.
    """
    
    # Initialize a variable that will hold a tab worth of spacing
    tab = '    '
    
    # Initialize the ROOT file
    file = ROOT.TFile.Open(run_forconfig)
    
    # Initialize the output_File
    output_file = f'{main_folder}_run_collisions.config'
    
    # Construct the output file
    with open(output_file,'a+') as f:

        # Generate the histogram part of the script
#         doit_output(map_directory_paths_final((map_directory_paths_init(file,file,'',[],main_folder)[1])), [], '',f,alg_out,start_set);
        doit_output(map_directory_paths_final((map_paths(file,file,'',[],main_folder)[1])), [], '',f,alg_out,start_set);
        
        # Write final closing directory
        f.write(f'{"}"} # output top_level\n\n')
        
        
        
def gen_script(run_forconfig,main_folder,alg_in,hist_algorithm,display,reference,start_set):
    """
    Prepares the output file for writing the histogram assessment part of the config script.
    """
    
    
    # Initialize a variable that will hold a tab worth of spacing
    tab = '    '
    
    # Initialize the ROOT file
    file = ROOT.TFile.Open(run_forconfig)
    
    # Initialize the output_File
    output_file = f'{main_folder}_run_collisions.config'
    
    # Construct the output file
    with open(output_file,'a') as f:

        # Generate the histogram part of the script
        doit(map_directory_paths_final(map_paths(file,file,'',[],main_folder)[1]), [], '',f,alg_in,hist_algorithm,display, reference, start_set);
        
        
def gen_full_script(run_forconfig, main_folder, alg_out, alg_in, alg_hist, display, reference, start_set = False  ):
    """
    Determines if the output file already exists, deletes it if it does, then constructs output and histogram assessment sections of the config script for the given main_folder
    and ties them together in a single config script.
    """

    if f"{main_folder}_run_collisions.config" in os.listdir():
        os.remove(f"{main_folder}_run_collisions.config")
    
    # Generate the script
    gen_script_output(run_forconfig, main_folder, alg_out, start_set)

    gen_script(run_forconfig, main_folder, alg_in, alg_hist, display, reference, start_set)


# ### Example Use

# ##### Generate the config script for MissingEt:

# In[44]:


# Input Parameters
run_forconfig = 'data18_13TeV.00349268.physics_Main.merge.HIST..26844909._000001.pool.root.1'
main_folder = 'MissingEt'

# Generate the script to current directory as f"{main_folder}_run_collisions.config"
gen_full_script(run_forconfig, main_folder, 'WorseCasesSummary', 'METGatherData', 'METChisq', 'StatBox', 'CentrallyManagedReferences')


# ##### Generate the config script for PFOs:

# In[38]:


# Input Parameters
run_forconfig = 'data18_13TeV.00349268.physics_Main.merge.HIST..26844909._000001.pool.root.1'
main_folder = 'PFOs'

# Generate the script to current directory as f"{main_folder}_run_collisions.config"
gen_full_script(run_forconfig, main_folder, 'WorseCasesSummary', 'METGatherData', 'METChisq', 'StatBox', 'CentrallyManagedReferences')


# ##### Generate the config script for CaloTopoClusers:

# In[55]:


# Input Parameters
run_forconfig = 'data18_13TeV.00349268.physics_Main.merge.HIST..26844909._000001.pool.root.1'
main_folder = 'CaloTopoClusters'

# Generate the script to current directory as f"{main_folder}_run_collisions.config"
gen_full_script(run_forconfig, main_folder, 'WorseCasesSummary', 'METGatherData', 'METChisq', 'StatBox', 'CentrallyManagedReferences')


# A View of an output script, set with the above parameters:

# In[56]:


with open(f"{main_folder}_run_collisions.config") as f:
    for line in f.readlines():
        print(line.replace('\n',''))

