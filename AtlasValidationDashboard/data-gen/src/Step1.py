#!/usr/bin/env python
# coding: utf-8

# # Specifically for unsupervised data (physics_Main stream)

# ##### Locate the data

# 1. Navigate to https://atlasdqm.cern.ch/webdisplay/tier0
# 2. Do a search for a range of approximately 30000-50000 run numbers such as 33025-365219 as in the following: https://atlasdqm.cern.ch/webdisplay/tier0?highrun=365219&nruns=1000&lowrun=330025
# 3. Highlight all the runs text data from the first run number of interet to the last run number of interest (note, the metainformation such as the run year, data18 vs data17 is stored in the html data and would require you looking at the html data of this web page, rather we are grabbing the direct text and assuming that we are using data18/data17/or it doesnt matter by inspection)
# 4. With that text data grabbed and stored in a text file, run the following code:

from utilities import *


def raw_requests(energy,run_list_file,stream):
    """
    
    This function generates the request lines to download run files from rucio on lxplus from a text file called run_list_file. The run_list_file is a copy and paste version of a tier0
    dqmdisplay search of exactly the portion starting with the first run number line down to the last run number line. (see run320000-358300.txt for reference)
    
    Example Use:
        energy = 'data18_13TeV'
        run_list_file = "../../datafiles/run320000-358300.txt"
        stream = 'express_express'
        
        raw_requests('data18_13TeV',"../../datafiles/run320000-358300.txt",'express_express')
    
    """
    
    with open(run_list_file) as f:
    
        # Initialize the run file count to keep track of how many runs we are going to pull
        cnt = 0
        
        # Initialize the run_list for later verification and determination if the run files have or have not already been requested
        run_list = []

        for id_,line in enumerate(f.readlines()):
            
            # Replace artifacts from the document
            line = line.replace('\t',' ')
            
            # Initialize a placeholder array for the current data line each iteration
            data_line = []
            
            # If this line in the file contains the stream of interest
            if stream not in line:     
                
                 # express is not in the line, but it may contain the relevant run number
                try:
                        # Get and process the run  if this is a run number
                        data_line.append('00'+str(int(line.split(' ')[0])))
                        
                        # Store the number for lines that still use this
                        tmp = data_line[0]
                        
                except:
                    # This line has no run number and its assumed to have the same run number as before, tmp
                    data_line.append(tmp)
                    

            else: # Stream is in the line

                try:
                        # Get and process the run #
                        data_line.append('00'+str(int(line.split(' ')[0])))
                        
                        # Store the number for lines that still use this #
                        
                        tmp = data_line[0]
                        
                except:
                    # This line has no run number and its assumed to have the same run number as before, tmp
                    data_line.append(tmp)

                for item in line.split(' '):

                    # Get the ftag
                    if 'f' in item or 'x' in item and len(item)==9:
                        data_line.append(item)
                        
                    # Remove the processing info
                    if 'BLK' in item or 'ES1' in item:
                        continue

                # Update the file number
                cnt+=1

#                 print(f'{energy}:{energy}.{data_line[0]}.{stream}.merge.HIST.{data_line[1]}')
                
                run_list.append(data_line)
            

        print('total number of potential requests:', cnt)
        return run_list


# 5. use raw_requests() to generate runs_to_get from the  raw_requests(energy/run year info, text file we found previously, and the stream such as express_express) similar to the following:

runs_to_get = raw_requests('data18_13TeV',"run330025-365219.txt",'physics_Main')


# 6. Now, what we want to know is - Which runs do we already have in batch folders from the above generated run list? To get this, we run the following code:
# (this will generate a dictionary of runs/ftags that already exist in batch form if you already have runs and a database from those runs, we use this information to determine what runs we already have and compare to the runs we want to get in that text file)


# Init the list
list_ = []

# Loop through the batches and get reach entry
for batch in os.listdir('data18_13TeV--pMain'):
    for item in [run for run in os.listdir(f'data18_13TeV--pMain/{batch}')]:
        # Store each entry in list_
        list_.append(item)

# Init the dictionary
dict_ = {}

# Run through each entry in list_ that fits the right criteria, do this loop to initialize the keys in dict_
for item in [item for item in list_ if 'sys' not in item if 'physics_Main' in item]:
    key = item.split('.')[1][2:]
    dict_[key] = [] 

# Run through each entry in list_ that fits the right criteria, do this a second time so initializing the key in dict_ will not wipe out all the ftags in each list with each iteration
# Hence instead of dict_[key] = [only one thing present], its dict_[key] = [multiple, things, present]
for item in [item for item in list_ if 'sys' not in item if 'physics_Main' in item]:
    key = item.split('.')[1][2:]
    
    # Fix unusual entrys
    if item.split('.')[-1] != '1':
        dict_[key].append(item.split('.')[-1])
    else:
        dict_[key].append(item.split('.')[-3])
        
display(dict_)


# 7. Now, we remove the identified readout files that already exist from the run_list to generate the net requests:
# (this will generate the run requests that you can copy, and paste at https://rucio-ui.cern.ch/r2d2/request)


# Initialize the number of requests to get
cnt = 0        

set_of_20=0

# Loop through the runs that might need to be requested
# NOTE: one or more of these files may or may not be a .0001_1 file.
for ii,run_to_get in enumerate(runs_to_get):        

    # If that run number is a key in dict_ (if we already have that run number)
    if run_to_get[0][2:] in dict_.keys() and dict_[run_to_get[0][2:]] != []:
    
        for i,ftag in enumerate(dict_[run_to_get[0][2:]]):
            
            # Check to see if the potential ftag to get already exists in the batch list (if we already have the ftag of the run number we have)
            if run_to_get[1] in dict_[run_to_get[0][2:]]:
            
                # And skip it if it does
                pass
        
            else:
                # Runs less than 348197 are data17, so we skip these
                if int(run_to_get[0][2:]) < 348197:
                    continue

                # Skip all runs that don't acquire a valid ftag, these usually are listed as Unknown
                if len(run_to_get)<2:
                    continue
                    
                # Otherwise, add a value to the number of requests we need to make
                cnt+=1

                # Download these in batches of 50 at a time so that rucio will actually process the request
                if (cnt%20)==0:
                    set_of_20+=1
#                     print(set_of_20,'\n')
                
                # And print out which run/ftag combo we need to request that do not exist
                print(f'data18_13TeV.00{run_to_get[0][2:]}.physics_Main.merge.HIST.{run_to_get[1]}')
                
    else: # Otherwise, the run doesn't exist
        
        # So add the run, but not the ftag because we havnt downloaded it
        
        dict_[run_to_get[0][2:]] = []
        
        # Runs less than 348197 are data17, so we skip these
        if int(run_to_get[0][2:]) < 348197:
            continue
            
        # Skip all runs that don't acquire a valid ftag, these usually are listed as Unknown
        if len(run_to_get)<2:
            continue
            
        # Also, increase the number of requests we need to make
        cnt+=1
            
        # Download these in batches of 50 at a time so that rucio will actually process the request
        if (cnt%20)==0:
            set_of_20+=1
#             print(set_of_20,'\n')
        
        # And print out which run/ftag combo we need to request that do not exist
        print(f'data18_13TeV.00{run_to_get[0][2:]}.physics_Main.merge.HIST.{run_to_get[1]}')
        
            
# Get a readout of the number of requests we must make
cnt


# 384 of the 397 requests were valid in this format on rucio, presumably because it does not take the format given above for ftags with /<number> at the end

# 8. If you have not done so already, take the above request lines, copy them, and request them from https://rucio-ui.cern.ch/r2d2/request (This step and previous step for viewing dqm web display requires ATLAS collaboration credentials as well as a valid, installed grid certificate specific to the browser it was installed on, and perhaps one other requirement to do these steps)
# 
# 9. We now generate the code as before, but with 'rucio download' in front of it so we can procedurally download it from lxplus


# Initialize the number of requests to get
cnt = 0        

# Loop through the runs that might need to be requested
# NOTE: one or more of these files may or may not be a .0001_1 file.
for ii,run_to_get in enumerate(runs_to_get):        

    # If that run number is a key in dict_ (if we already have that run number)
    if run_to_get[0][2:] in dict_.keys() and dict_[run_to_get[0][2:]] != []:
    
        for i,ftag in enumerate(dict_[run_to_get[0][2:]]):
            
            # Check to see if the potential ftag to get already exists in the batch list (if we already have the ftag of the run number we have)
            if run_to_get[1] in dict_[run_to_get[0][2:]]:
            
                # And skip it if it does
                pass
        
            else:
                # Runs less than 348197 are data17, so we skip these
                if int(run_to_get[0][2:]) < 348197:
                    continue
                    
                # Skip all runs that don't acquire a valid ftag, these usually are listed as Unknown
                if len(run_to_get)<2:
                    continue    
                    
                # Otherwise, add a value to the number of requests we need to make
                cnt+=1

                    
                # And print out which run/ftag combo we need to request that do not exist
                print(f'rucio download data18_13TeV.00{run_to_get[0][2:]}.physics_Main.merge.HIST.{run_to_get[1]}')
                
    else: # Otherwise, the run doesn't exist
        
        # So add the run, but not the ftag because we havnt downloaded it
        
        dict_[run_to_get[0][2:]] = []
        
        # Runs less than 348197 are data17, so we skip these
        if int(run_to_get[0][2:]) < 348197:
            continue
            
        # Skip all runs that don't acquire a valid ftag, these usually are listed as Unknown
        if len(run_to_get)<2:
            continue
            
        # Also, increase teh number of requests we need to make
        cnt+=1
            
        # Download these in batches of 50 at a time so that rucio will actually process the request
        if (cnt%50)==0:
            pass
#             print('') # break line to indicate batch
        
        # And print out which run/ftag combo we need to request that do not exist
        print(f'rucio download data18_13TeV.00{run_to_get[0][2:]}.physics_Main.merge.HIST.{run_to_get[1]}')
        
            
# Get a readout of the number of requests we must make
cnt


# 10. open a terminal in your linux based pc, if you have windows I recommend removing it asap.
# 
# 11. type the command: ssh yourcernusername@lxplus.cern.ch
# 
# 12. input your password
# 
# 13. navigate to your eos/home-c/yourusername/SWAN_projects/datafiles/ location by doing the command: cd ../ until you get above the afs directory, then doing cd eos/home-c/yourusername/SWAN_projects/datafiles ( DO NOT DOWNLOAD THE FILES DIRECTLY INTO THE DIRECTORY THAT ALSO CONTAINS THE BATCHES, if their is an error, then it will put empty folders there and make this program think you already have the files when it creates the dict_ dictionary), move to a higher level directory and download them there, after process them into batches with the other code as directed later.
# 
# 14. now run the command: setupATLAS
# 
# 15. now run the command: lsetup rucio
# 
# 16. now run the command: voms-proxy-init -voms atlas ,as instructed by the terminal ; type in your GRID password
# 
# 17. At this directory, copy and paste the 'rucio download' commands that were generated above, this will download all those files into your cernbox storage location. These files can be accessed, processed, and more at swan.cern.ch (assuming the requests went through on rucio from the previous step, be sure before running the download commands that the rucio requests show an 'OK' status so we know they can be accessed.
# 
# 18. With the runs now downloaded and accessible, we need to organize them into batches. Start by verifying the number of runs in the run file as they download (the -1 is because the first folder generated is empty)


# How many runs were downloaded, minus the empty folder at the beginning
len(os.listdir('run_files'))-1


# $*.$ In the event that there is an interruption of the download commands in the terminal such as an internet outage, save the list of requests (without rucio download in front of them) from above and save them to a text file. Then, run this next line of code to loop through the lines in the text file you just saved, then compare it to the entries as they appear in the directory where the runs are located (in this case, "run_files"). This will generate a new list of terminal commands that, having relogged into the lxplus system as before, will allow you to download the files that have not yet been downloaded but were listed in the above requests. (In our example, we successfully downloaded 320 of the expected 384 run_files that rucio listed rules for. Running this command resumed downloading the missing files)

# 19. If necessary, verify there are no duplicate run files that have been downloaded


items = []
for item in os.listdir('run_files'):
    if item in items:
        print(item,'duplicate')
    else:
        items.append(item)
print('done')


# 20. If necessary, use this code to generate the code to download the remaining run files after a download issue such as loss of internet


cnt = 0
with open('requestsTxt/runlist.txt') as f:
    for line in f.readlines():
        line = line.replace('\n','')
        if line in os.listdir('run_files'):
            pass
        else:
            cnt+=1
            print('rucio download',line)
print(cnt)


# The 13 remaining above complete the list of 397 original requests we had. Only 384 of the requests went through in rucio and as can be seen below, we have all 384 requests we expected. We can move on.

# 21. Final verification - make sure the number of runs you have downloaded is the number you expect (the number requested from rucio online)


# How many runs were downloaded, minus the empty folder at the beginning
len(os.listdir('run_files'))


# 22. Generate batch folders and move batches of runs to those folders


def runs_to_batches(source_path,batches_we_currently_have_in_folder):
    """
    WARNING:
        Take care - this makes and moves files. Running it after it has already been prepared is not recommended.
    
    DESCRIPTION:
        Moves the runs from the source_path to a series of batch folders --batch folders each contain 20 runs per batch. 
        The reason for this is because processing these all at once requires holding too much data in memory before 
        sending to the database.
    
    NOTE:
        The source_path parameter MUST contain a / at the end.
        
        Also, after running this, if you get an error saying mv did not work. Check the directory you set as the source path and determine the number of batches it generated then rerun
        this function with the same parameters except batches_we_currently_have_in_folder now equals however many batches it generated with the first run.
    
    EXAMPLE USE:
        source_path = 'data18express/data18_13TeV/'
    """
    
    # Get an array of each run that is located in the source directory
    runs = [run for run in os.listdir(source_path) if '.sys' not in run if 'data' in run]
    runs
    
    # Initialize the directory_count so we know what to number the batches, always start with 1 so the batch folder will be 1ahead of batches_we_currently_have_in_folder
    directory_count = 1
    
    # Loop through the runs
    for id_,run in enumerate(runs):
        
        # everytime id_ is a multiple of 20 (20,40,60,etc.)
        if (id_+1)%20==0:
            # This is the next directory, so update the count
            directory_count +=1
            
            # make a directory at the path source_path/batch(that multiple +4) --example: at id_=19, id_+1 ==20, so directory_count = 1, and we make directory source_path/batch(1+3)
            os.system(f'mkdir {source_path}batch{str(directory_count+batches_we_currently_have_in_folder)}')
            
        # Send every 20 runs between the multiples of id_ that are 20 -- runs 0-19 go to batch4 in this case because we already had 3 batches
        from_ =  f'{source_path}{run}'
        
        
        try: # Try to create the to_ location
            to_ = f'{source_path}batch{str(directory_count+batches_we_currently_have_in_folder)}/{run}'
        except: # If that doesn't work, make the directory for the to_ location then set the to_ location
            os.system(f'mkdir {source_path}batch{str(directory_count+batches_we_currently_have_in_folder)}')
            to_ = f'{source_path}batch{str(directory_count+batches_we_currently_have_in_folder)}/{run}'
        os.system(f"mv {from_} {to_}")



runs_to_batches("run_files/",0)


# 23. If not all files moved into bactches properly in the first run of runs_to_batches, count the number of batch folders in the run_files directory and update the runs_to_batches parameter as follows:


runs_to_batches("run_files/",19)


# 24. Verify there are 20 runs in each batch folder in the directory, if you had to run runs_to_batches a second time, the connecting batch folder will have a few runs more than 20. If this is excessive, move the extra runs to a final batch manually


total=0
for batch in os.listdir('run_files/'):
    print(batch)
    cnt=0
    for run in os.listdir(f"run_files/{batch}"):
        cnt+=1
        total+=1
    print(cnt)
total

# One of the batches has 39 because when we had to re run the function we didn't set the parameter correctly to generate batch 11 as the final 19 runs, this should be fixed with the
# newest update of the function.


# 25. generate hists_of_interest_txt file that include all 18 histograms for each run/ftag combination with the formatting required of the hist_of_interest_txt files for the datbase. (If TH1 is mentioned anywhere in here, it was a mistake --all are TH2s)


# TH2s not TH1s
def genth1s(run_str,ftag_str,energy):
#     print(ftag_str,energy)
    th1list = ['/CaloMonitoring/ClusterMon/CaloCalTopoClustersNoTrigSel/2d_Rates/m_clus_etaphi_Et_thresh0',
               '/CaloMonitoring/ClusterMon/CaloCalTopoClustersNoTrigSel/2d_Rates/m_clus_etaphi_Et_thresh1',
               '/CaloMonitoring/ClusterMon/CaloCalTopoClustersNoTrigSel/2d_Rates/m_clus_etaphi_Et_thresh2',
               '/CaloMonitoring/ClusterMon/CaloCalTopoClustersNoTrigSel/2d_Rates/m_clus_etaphi_Et_thresh3',
               '/CaloMonitoring/ClusterMon/CaloCalTopoClustersNoTrigSel/General/etaphi_ncellinclus',
              '/CaloMonitoring/ClusterMon/CaloCalTopoClustersNoTrigSel/TransEnergy/etaphi_thresh_avgEt_0',
              '/CaloMonitoring/ClusterMon/CaloCalTopoClustersNoTrigSel/TransEnergy/etaphi_thresh_avgEt_1',
              '/CaloMonitoring/ClusterMon/CaloCalTopoClustersNoTrigSel/TransEnergy/etaphi_thresh_avgEt_2',
              '/CaloMonitoring/ClusterMon/CaloCalTopoClustersNoTrigSel/TransEnergy/etaphi_thresh_avgEt_3',
              '/CaloMonitoring/ClusterMon/LArClusterEMNoTrigSel/2d_Rates/m_clus_etaphi_Et_thresh0',
              '/CaloMonitoring/ClusterMon/LArClusterEMNoTrigSel/2d_Rates/m_clus_etaphi_Et_thresh1',
              '/CaloMonitoring/ClusterMon/LArClusterEMNoTrigSel/2d_Rates/m_clus_etaphi_Et_thresh2',
              '/CaloMonitoring/ClusterMon/LArClusterEMNoTrigSel/2d_Rates/m_clus_etaphi_Et_thresh3',
              '/CaloMonitoring/ClusterMon/LArClusterEMNoTrigSel/General/etaphi_ncellinclus',
              '/CaloMonitoring/ClusterMon/LArClusterEMNoTrigSel/TransEnergy/etaphi_thresh_avgEt_0',
              '/CaloMonitoring/ClusterMon/LArClusterEMNoTrigSel/TransEnergy/etaphi_thresh_avgEt_1',
              '/CaloMonitoring/ClusterMon/LArClusterEMNoTrigSel/TransEnergy/etaphi_thresh_avgEt_2',
              '/CaloMonitoring/ClusterMon/LArClusterEMNoTrigSel/TransEnergy/etaphi_thresh_avgEt_3']
    th1list.insert(0,[ftag_str,energy])
    return [f'run_{run_str}{th1}' if id_>0 else (ftag_str,energy) for id_,th1 in enumerate(th1list)]

def gen_hist_of_interest_txt(batch_folder,energy):
    # Count the number of histograms we have generated
    cnt=0
    
    for batch in os.listdir(batch_folder):
        for run in os.listdir(f"{batch_folder}{batch}"):
            cnt+=18
            runsp = run.split('.')
            list_ = genth1s(runsp[1][2:],runsp[-1],energy)
            print(list_[0][0],list_[0][1])
            [print(item) for item in list_[1:]]
            print('')
    
    
    print(f"(Stats:{cnt} histograms are given in this file.)")



gen_hist_of_interest_txt("run_files/","data18_13TeV")


# 26. copy and paste it into a text file and store it in the hist_of_interest_txts folder(it must be stored in its own hist_of_interest_txts directory) for when we build the database.
# 
# <b>IMPORTANT: The Stream name MUST BE IN THE hists_of_interest FILENAME! (use either express for express_express stream or pMain for physics_Main stream) ALSO "processed" MUST BE IN THE NAME</b>
# 
# Ex: hists_of_interest_pMain_processed.txt

# Now that all the essential bits are generated, lets add these histograms to the database. The fragility and size of the database could take a while and lead to errors. If it keeps failing write a try, except loop that keeps trying to create the database until no errors are found. (see run_til_works function later)

# 27. Verify that the newly added data is formatted properly and will function properly in the database


# This function has been updated from the Github version
def build_hists_paths_arr(paths_txt_file):
    
    """
    
    Extracts the path-lines from paths_txt_file and sends them to arr_. The list arr_ is used against the paths available in each processed run.csv to determine which 
    histograms to extract from that run. This function should be used prior to running the build_sql_database() function. 
    
    IMPORTANT: The Stream name MUST BE IN THE hists_of_interest FILENAME! (use either express for express_express stream or pMain for physics_Main stream) IT ALSO MUST HAVE 'processed'
    in the name. Example: hists_of_interest_pMain_processed.txt
    
    EXAMPLE USE:
        paths_txt_file = 'backups/express_good_hists2_various-508_processed1.txt'
        
    """
    
    with open(paths_txt_file,'r') as f:
        
        arr_, ftags, energys, streams = [], [], [], []
        
        for idL,line in enumerate(f.readlines()):

            # Skip lines that are spaces
            if line == ' ':
                continue
            
            # Lines that do not have ClusterMon are either meta_info lines or R/Y target lines
            if 'ClusterMon' not in line:
                
                # Skip R/Y target lines
                if 'R' in line or 'Y' in line:
                    continue
                
                # Process the meta_info line
                line = line.replace('\n','')
                
                # Skip empty lines
                if line.split(' ')[0] == '':
                    continue
                
                # Process the ftags from line
                ftag = line.split(' ')[0]
                
                # Process the energy info from line
                energy = line.split(' ')[1]
                    
            if 'ClusterMon' in line:
                ftags.append(ftag)
                
                energys.append(energy)
                
                if 'express' in paths_txt_file:
                    streams.append('express')
                elif 'pMain' in paths_txt_file:
                    streams.append('pMain')
                arr_.append(line.replace('\n',''))
            
    return arr_, energys, ftags, streams



def verify_hists_of_interest_txts_formats(hists_of_interest_txts_path):
    """
    Verifies that the hists_of_interest_txts are formatted properly.
    
    WARNING: if the metadata line in the hist_of_interest txt file contains "tag space" and not "tag space energy" it will still accept it as a valid format! This could improperly
    create the dict_of_arrs metadata information for the energy and thus improperly label a table in the database. Make sure the txt files are properly formatted!
    
    Proper txt file format:
        "tag space energy" -->Example: "f993_h225 data18_13TeV"
    
    EXAMPLE USE:
        hists_of_interest_txts_path = 'hists_of_interest_txts'
    """
    
    # Initialize dict_of_arrs that contains the metadata of the hists of interest for constructing the database
    dict_of_arrs = {}
    
    # Initialize the exceptions counter
    exceptions = 0
    
    # Loop through the hists of interest txt files
    for idF,file in enumerate(file for file in os.listdir(hists_of_interest_txts_path) if '.sys' not in file):
        # Try to construct the key and hist_of_interest array for each file
        print(file)
        try:
            dict_of_arrs[f'arrs_{idF}'] = build_hists_paths_arr(f'{hists_of_interest_txts_path}/{file}')
        
        # If an error results, reformatting of the noted file is required
        except Exception as e:
            print(f'file {idF} requires reformatting. (metadata lines should be in the format of: tag space energy --> example: "f993_h225 data18_13TeV"\nError: {e}')
            exceptions+=1
    
    if exceptions == 0:
        print('All texts are likely formatted correctly. - further issues will require spot checking of dict_of_arrs')
    else:
        pass
    
    return dict_of_arrs



dict_of_arrs = verify_hists_of_interest_txts_formats('hists_of_interest')



# total=0
# for key in dict_of_arrs.keys():
#     i=0
#     print('---',key,'---')
#     for val in dict_of_arrs[key][0]:
# #         if 'm_clus_etaphi_Et_thresh0' in val:
#         i+=1
#         print(val)
#     total+=i
#     print(i,'\n')
# print('\ntotal:',total)


# In this case, there were no further issues. Moving on.

# 28. Quickly analyze the new amount of data available accd to hists_of_interest_txts folder


# all m_clus_etaphi_Et_thresh0 in CaloCalTopoClusters hists
hists=0
for key in dict_of_arrs.keys():
    for hist in dict_of_arrs[key][0]:
        if 'm_clus_etaphi_Et_thresh0' in hist and 'Topo' in hist:
            hists+=1
print('#hists of m_clus_etaphi_Et_thresh0 in hists_of_interest_txt files:',hists)

# all hists minus m_clus CaloTopo hists
mclustopo_hists = hists
hists = 0
for key in dict_of_arrs.keys():
    hists+= len(dict_of_arrs[key][0])
print('#all_other_hists in hists_of_interest_txt files:',hists-mclustopo_hists)

hists = 0
for key in dict_of_arrs.keys():
    hists+= len(dict_of_arrs[key][0])
print('#all_hists in hists_of_interest_txt files:',hists)


# 29. Generate a report of how many of each histogram we have
# <br>
# There are 18 types of histograms (2 sets of mclus0-3, 2 sets of nclus, and 2 sets of avgEt0-3)


# Initialize
arr_ = []

# Loop through each hist_of_interest_txt file stored in dict_off_arrs as a key
for key in dict_of_arrs.keys():
    # Loop through each histogram stored at [key][0] in dict_of_arrs
    for hist in dict_of_arrs[key][0]:
        # Append that histogram, minus the run part of the path to the arr_ array
        arr_.append('/'.join(hist.split('/')[1:]))

# Convert this into a dataframe called tmp
tmp = pd.DataFrame({'hists_of_interest': arr_})

# Initialize
dfs = []

# Loop through the unique histograms in tmp
for unique_histogram in tmp['hists_of_interest'].unique():
    # Append eac hunique histogram to its own dataframe in the array of dataframes dfs
    dfs.append(tmp[tmp['hists_of_interest']==unique_histogram])
    
# Initialize
histogram = []
vals = []

# Loop through each df in dfs
for df in dfs:
    # Append each path of a histogram at df.values[0][0] to histogram
    histogram.append(df.values[0][0])
    
    # Append the length of that unique_histogram stored in its own dataframe df to vals to get the number of that histogram available
    vals.append(len(df[df.columns[0]]))
    
# Create a dataframe of unique histograms as histogram and the number of those unique histograms as vals
df_count = pd.DataFrame({'histogram':histogram,'num_hists':vals})

df_count


# We have an even 384 histograms per histogram type. Nothing unexpected here.

# ##### 30. Add the new data to the database

# 31. Create the new_unprocessed folder in the hists_of_interest_txts directory if it does not already exist. This is where our new_unprocessed hists_of_interest_txts will go, when we are done adding these to the database, we will move them up a directory level to live with the already processed txt files. Don't forget to make sure the word 'processed' is in the name of each properly formatted hists_of_interest_txt file in the new_unprocessed directory.
# 
# 32. Create the database backup csv folder in the BackupOfDatabases-byCsv directory. Call the backup folder '<database_name>_db' so we know what database this backup directory contains.
# 
# 33. Set the path and parameter values for build_sql_database() in the below variables all with a / at the end except for database_and_path
# 
# (I recommend using the 16gb ram setting if in the cloud such as swan.cern.ch or using a device with at least 16gb of ram)

# 34. Run the following to build the database. 
# 
# The following function allows recursive rebuilding of each batch for the database in the build_sql_database batchwise loop until that batch takes to the database. This system seems to be fragile, especially when large amounts of data are present, thus we often must repeatedly re-run it. This technique sort of brute forces that.


# Updated not in github
def build_sql_database(db_name, dict_of_dfs_and_tables, paths_txt_file_directory,backup_output_dir):
    
    """
    
    If recreating the database, delete the .db file. dont simply rerun this function.
    
    NOTE ON MEMORY CONSTRAINTS:
        As part of this function, it uses dict_of_dfs_and_tables() to construct a needed parameter. This parameter constructs a large dictionary of potentially many dataframes of runs - 
        So many in fact, that it may crash the system as it is holding all these runs/dataframes in memory while it is building the database out. 
        A simple way of dealing with this is to organize the runs in a series of folders, called batches, each of which will be targeted with replica_folders_path parameter inside of 
        the dict_of_dfs_and_tables() function so that it will convert only a set number of dataframes/runs at a time, store those into the database, then move on to the next batch 
        (assuming we run build_sql_database in a loop over all such batch directories)
        
    EXAMPLE USE and USING ABOVE INFO:
        db_name == 'runs2.db'
        paths_txt_file_directory = 'backups/' # Must have '/' at end of path
        backup_output_dir = 'backups/'  # Must have '/' at end of path
        dict_of_dfs_and_tables = prep_dict_of_dfs_and_tables(f'../defectless_runs/{dir_}/'), 'backups/')
        * the path '../defectless_runs/' should contain a series of folders that are the batches containing the subset of folders/files to process with build_sql_database

        # Loop over the batches, here called dir_
        for dir_ in os.listdir('../defectless_runs/'):

            # Construct the database for each batch with proper input parameters
            build_sql_database('runs2.db', prep_dict_of_dfs_and_tables(f'../defectless_runs/{dir_}/'), 'backups/')
            print(dir_,' Complete.')
            
            
       # Example from construction of defectless histogram database
       build_sql_database('runs_redhists.db', dots, 'backups/red_hists_of_interest/','backups/database_backup_files/red_without_qual_values/')
        
    """
    
    # Construct the engine used to create and manipulate the sql database
    engine = create_engine(f'sqlite:///{str(db_name)}', echo=False)

    
#     status_update_msg('Constructing dict_of_arrs...')
    # Construct dict_of_arrs
    dict_of_arrs = {}
    for idF,paths_txt_file in enumerate([i for i in os.listdir(paths_txt_file_directory) if 'sys' not in i and '.csv' not in i and 'processed' in i]):
        dict_of_arrs[f'arrs_{idF}'] = build_hists_paths_arr(f'{paths_txt_file_directory}{paths_txt_file}')
       
#     status_update_msg('Looping through dict_of_dfs_and_tables...')
    
    for idT,table in enumerate(dict_of_dfs_and_tables.keys()):
        
        print('Processing table',table)
    
        # Gather the meta info that contains the energy, ftag, and stream information for this table
        meta_info = table.split('$')

        
        # Loop through the dataframes we previously processed that are contained inside this particular table
        for iddF,df in enumerate(dict_of_dfs_and_tables[table]):
            
            
            # Loop through the arrays stored inside dict_of_arrs (each array corresponds to a single processed file containing hists_of_interest and meta_info)
            for key in dict_of_arrs.keys():
                
                # Initialize the paths_in_df (the paths for the hists_of_interest that we will identify)
                paths_in_df = []
                
                # For this hist_of_interest path in dict_of_arrs current array key, 
                for idP, path in enumerate(dict_of_arrs[key][0]):

                    # If the meta_info for the table matches up with the meta_info for this path, this path goes in paths_in_df
                    if meta_info[0] == dict_of_arrs[key][1][idP] and meta_info[1] == dict_of_arrs[key][2][idP] and meta_info[2] == dict_of_arrs[key][3][idP]:
                        paths_in_df.append(path)

                # For this array called key in dict_of_arrs.keys(), skip this array of paths_in_df if paths_in_df empty
                # If no meta_info matches were made on this dataframe as a hist_of_interest, the paths_in_df list will be empty, then we can move onto the next dataframe immediately
                if not paths_in_df:
                    continue

                    
                for idP2,path2 in enumerate(paths_in_df):            

                    # If hists_of_interest already exists, concatenate the subset dataframe in df that is df[df['paths']==paths_in_df[i]]
                    try:
                        hists_of_interest = pd.concat([hists_of_interest,df[df['paths']==paths_in_df[idP2]]])

                    # If hists_of_interest does not exist, set it to this subset dataframe df[df['paths']==paths_in_df[i]]
                    except:
                        hists_of_interest = df[df['paths']==paths_in_df[idP2]]

        try:
            # If the database is not located in the current directory, it will have a pathname instead of db name
            # Detect this and define tmp as the temporary actual db_name so the csv can properly be constructed
            if len(db_name.split('/'))>1:
                tmp = db_name.split('/')[-1]
            else:
                tmp = db_name
                
            # Construct the backup file for this table as .csv
            hists_of_interest.to_csv(f'{backup_output_dir}{tmp.replace(".","_")}${table}$backup.csv')
            
        except Exception as e:
            print(f'error creating csv(hists_of_interest) for table({table})\n {e}')

        try:
            # Send the concatenated dataframes of interest, for this particular table, to the sql database
            hists_of_interest.to_sql(table, engine, if_exists='append')
        except Exception as e:
            print(f'error sending hists_of_interest to sql database for table({table}) - Table Empty. Check that all arrays in dict_of_arrs are non empty and have the correct information. Also check the hists_of_interest_stream.txt file for errors.\n {e}')

        # How far along in the process of preparing the hists_of_interests for this table for this batch of runs? - Also, notify that the table succesfully made it to the database
        print(f"Table #{idT+1} of {len(dict_of_dfs_and_tables.keys())}, {table}, Table processing complete.")
        
        try:
            # Clear the hists_of_interests variable for the next table - we do not want the hists_of_interest from two different tables mixing
            del hists_of_interest
        except Exception as e:
            print(f'error deleteing hists_of_interest for table({table}) - Table Empty.\n {e}')


# * Set the parameters for building the database here


database_and_path = 'all_pMain.db'
run_source_path = 'run_files/' # energy level is data18_13TeV only, stream is physics_Main
hists_of_interest_txts_path = 'hists_of_interest/'
database_csv_backup_path = 'backups/'


# * Now run the following 4 blocks of code on the first batch only and make sure there are no errors, the database file is built, etc.


# Get a list of all the batches for processing
batches = [batch for batch in os.listdir('run_files')]



batches



# Set which batch to attempt to add to database
batch = batches[19]
batch


# potential upsampling in these .csv backups
# f964_h323
# f1034_h335
# f969_h323


# Do this separately because it takes a while. If it works, then you don't have to reprocess it while troubleshooting
# dict_of_dfs_and_tables = prep_dict_of_dfs_and_tables(f'{run_source_path}{batch}/')


# * (Before rerunning any build_sql_database from scratch, make sure to delete the .db file (or if appending make a copy before trying to update in the case of error) and also delete the backup csvs in the backups folder listed in the above parameters. (This prevents duplicate entries into the database))


# Attempt to add that batch to the database
dict_of_dfs_and_tables = prep_dict_of_dfs_and_tables(f'{run_source_path}{batch}/')
build_sql_database(database_and_path, dict_of_dfs_and_tables, hists_of_interest_txts_path, database_csv_backup_path)    
print('\n adding',batch,'complete.')


# * If the above build_sql_database function had no errors and processed correctly for that first batch, stop any other processes running in this notebook, delete the .db file in your directory the database is located, delete the .csv backup files in the backup file directory, and proceed to the next step where we will attempt to build the entire database. Can take a long time and varies on the number of batches you have to process. Since each database is contained in a file via SQLAlchemy, it is possible excessively large databases will behave poorly.
# 
# If any errors occur in the below, refer to the previous few blocks of code and work through the functions and variables used in build_sql_database to detemine the cause. Test again, then when you are confident there are no issues, build the whole thing below. (It is also possible to build the database batch by batch with the above if too much time feels like it is being wasted running the below block and repeatedly failing ...currently taking about 2hr45 minutes for 20 batches for my run)

# * Build the database here. If it fails, refer to the above to begin troubleshooting.


# Not in Github
def run_til_works(batch,database_and_path,run_source_path,hists_of_interest_txts_path,database_csv_backup_path):
    try:
        build_sql_database(database_and_path, prep_dict_of_dfs_and_tables(f'{run_source_path}{batch}/'), hists_of_interest_txts_path, database_csv_backup_path)
    except:
        run_til_works(batch,database_and_path,run_source_path,hists_of_interest_txts_path,database_csv_backup_path)



for id_,batch in enumerate(os.listdir(run_source_path)):
    run_til_works(batch,database_and_path,run_source_path,hists_of_interest_txts_path,database_csv_backup_path)    


# How many histograms are in the database to train with?(modify path information as necessary)
# 
# Expecting 6912


engine = create_engine(f'sqlite:///all_pMain.db', echo=False)



cnt=0
for id_,TABLE in enumerate(engine.table_names()):
    print(id_)
    
    df_new = get_dataframe_from_sql('all_pMain.db',f'SELECT * FROM {TABLE}')
    for val in [val for val in df_new['paths'].unique()]:
        cnt+=1

cnt


# DB Error Note: When reading the data from the database, if you get an error, consider rerunning it a few times as sometimes it could crash just by virtue of running or using it.

# 35. Following a succesful update of the database with the new unprocessed runs,
# - update the database name to all_pMain_v2.db
# - move the runs in the run_files folder into the a directory of the processed runs (keep them in their own folder separate still)
# - move the hists_of_interest_txt file from a new unprocessed directory to a directory of processed files

# NOTE: on swan.cern.ch, when a file size of say a database (all_pMain.db) reaches a large enough size (we are currently at about 3.83GB), if you try to duplicate the file it will crash your server/instance and you will have to reload the server. A potential workaround for this is downloading the file from the server, copying it directly, then reuploading it to ther server. For now, we will not make a copy of all_pMain_v2 and use it as is. Further issues with crashing due to file size can be handled on a local computer.
# 
# TLDR: large file handling can be done locally, for processing upload necessary files to swan and process them.

# 36. Get a handle for the dataset

# 37. Develop the function for load_hists_dataset_matrices specifically for the unsupervised dataset we will use
# - loads all data from sql to dataframe
# - creates the ftag_id feature


def load_hists_dataset_matrices_unsup(db_name):
    
    """
    
    Assuming express hists as .csvs and pMain hists as .csvs have been constructed from the .py script,  this function will
    load and construct the training and target matrices for the CNN.
    
    IMPORTANT NOTE: We don't actually need to keep track of the runs that we train the model with because its just going to be used for future predictions over histograms whose run
    numbers we WILL know. Therefore, it is not necessary to keep track of this.
    
    tensor_list is 5d.    
    Let the example tensor_list be of shape (18,2,24,65,99)
    1st dimension is the number of tables. (based on the number of unique 'ftag energy stream' combinations)
    2nd dimension is the number of datasets. There are only two. (feature_set(0) or target_set(1))
    3rd dimension is the number of histograms.
    4th dimension is the number of y coordinates.
    5th dimension is the number of x coordinates.
    Therefore, calling tensor_list[0][0][0] will return a matrix that is the feature set for the 1st histogram in the first table of the database. Its shape will be of size (65,99)
    
    """
    
    engine = create_engine(f'sqlite:///{db_name}', echo=False)
    
    # Initialize list of tensors from tables
#     tensor_list = []
#     ftags = []
    path_ids = ['...']
    
    # Load the datasets
    for idT, table in enumerate(engine.table_names()):
    
        progress_bar(idT,engine.table_names())
        
        # Get a handle for the dataframes 'dfs' from table 'table' in database 'db_name' 
        dfs_tmp = get_dataframe_from_sql(db_name,f'SELECT * FROM {table}')
        dfs_tmp['ftag_id'] = [idT]*len(dfs_tmp['paths'].values)
        
#         for path in dfs_tmp['paths']:
#             print('processing hist_type...')
#             this_path_id = ''.join(path.split('/')[1:])
#             for id_num,path_id in enumerate(path_ids):
#                 if this_path_id == path_id:
#                     dfs_tmp['hist_type'] = [id_num]*len(dfs_tmp['paths'].values)    
#             if path_id == path_ids

#         ftags.append([idT]*len(dfs_tmp['paths'].values))
        
        try: # Try to add dfs_tmp to dfs
            dfs = pd.concat([dfs,dfs_tmp])
            
        except Exception as e: # Otherwise, create dfs' first entry as dfs_tmp
            dfs = dfs_tmp
        

    # Convert the concatenated dataframes to a numpy tensor with only the selected features of interest and all n_samples
#     np_tensor = dfs.to_numpy()[:,1:4]
    
    return dfs # np_tensor



dfs = load_hists_dataset_matrices_unsup('all_pMain.db')



def recursive_function_runs(func,func_input):
    """
    A recursive function that will continuously retry the function its given with that function's input until it successfully completes that function's operation.
    
    Example use:
        np_tensor = recursive_function_runs(load_hists_dataset_matrices_unsup,'Databases/allhists_v2.db')
        
    """
    
    try:
        output = func(func_input)
    except Exception as e:
        print(e)
        recursive_function_runs(func,func_input)
        
    return output



dfs = recursive_function_runs(load_hists_dataset_matrices_unsup,'all_pMain.db')



dfs


# 38. The dataframe is not optimized for memory in its data types, fix this


dfs.info()



dfs['x'] = dfs['x'].astype('int8')
dfs['y'] = dfs['y'].astype('int8')
dfs['ftag_id'] = dfs['ftag_id'].astype('int8')
dfs['occ'] = dfs['occ'].astype('float32')



dfs.to_csv('dfs.csv',index=False)


# 39. Construct the hist_type feature


# Initialize the new feature
dfs['hist_type'] = [0]*len(dfs['paths'].values)
dfs['hist_type'] = dfs['hist_type'].astype('int8')



# Construct the list of unique histogram types
path_list = ['/'.join(i.split('/')[1:]) for i in dfs['paths'].unique() if 'run_363664' in i]



len(path_list)



[print(id_,i) for id_,i in enumerate(path_list)];



# Calculate and input the correct value to the hist_type feature
for ide,entry in enumerate(path_list):
    print(f'processing {ide}...')
    split = entry.split('/')
    tmp_mask = dfs['paths'].str.contains(split[2]) & dfs['paths'].str.contains(split[-1])
    dfs.loc[tmp_mask,'hist_type'] = ide
print('processing complete.')



# Doing this and a few other operations, we verify the above code processed the new feature correctly
dfs['hist_type'].unique()



dfs



dfs.to_csv('dfs.csv',index=False)


# Loading data with correct dtypes when reading csv in pandas is essential unless using another save/load mechanism


# LOAD DATA HERE, load the datatypes you want to minimize the memory load of the dataframe. IMPORTANT: Pandas auto converts up the bit size of each data column unless specified!
dfs = pd.read_csv('dfs.csv', dtype={'x':'int8','y':'int8','ftag_id':'int8','occ':'float32','hist_type':'int8'})
display(dfs.head())
display(dfs.info())


# 40. Implement a hist_id feature so I can plot the heatmap


dfs.head()



# Initialize hist_id feature column
dfs['hist_id'] = 0
dfs['hist_id'] = dfs['hist_id'].astype('int16')
dfs.info()



# Build the hist_id feature

# There are about 30million datapoints
# There are at least 87 loops that must be done in the ftag loop
# For each of the 87 loops, 1 loop for each unique histogram will be done for a grand total of 4165 histograms
# That brings us to a total of 87+4165 loops
# Within each of the 4165 loops, a mask is created, and datapoints are modified in the 29million datapoint dataframe
# Generally speaking...it could take a while depending on the number of histograms in any of the 87 ftags in the ftag loop (less histograms/ftag = shorter time to complete iteration)
# (Everything that could be modified by vector operations, that I can think of, has been used to modify the dataframe for this feature..the modification is simply too technical to
# correct with a single vector operation on the table)
for i in range( int((dfs['ftag_id'].max()+1)/2) ):
    if i!=1:
        continue
    # In this case, i goes to 90, but we stop half way to do it in 2 pieces (i=0 to i=44)
    print(f'processing {i}')
    print(f'getting ftag subset..')
    df_tmp = dfs[dfs['ftag_id']==i]
    print(f'getting unique paths..')
    path_index = [(a,path) for a,path in enumerate(df_tmp['paths'].unique())]
    print('loopin through paths and setting values..')
    for path in path_index:
        tmp_mask = (dfs['paths'] == path[1]) & (dfs['ftag_id'] == i)
        dfs.loc[tmp_mask,'hist_id'] = path[0]



# Second part to above code, split to prevent having to restart if it breaks post half way
for i in range( int((dfs['ftag_id'].max()+1)/2), dfs['ftag_id'].max()+1 ):       
    # In this case, i goes to 90, but we stop half way to do it in 2 pieces (i=45 to i=90)
    print(f'processing {i}')
    print(f'getting ftag subset..')
    df_tmp = dfs[dfs['ftag_id']==i]
    print(f'getting unique paths..')
    path_index = [(a,path) for a,path in enumerate(df_tmp['paths'].unique())]
    print('loopin through paths and setting values..')
    for path in path_index:
        tmp_mask = (dfs['paths'] == path[1]) & (dfs['ftag_id'] == i)
        dfs.loc[tmp_mask,'hist_id'] = path[0]



dfs.to_csv('dfs.csv',index=False)



dfs = pd.read_csv('dfs.csv', dtype={'x':'int8','y':'int8','ftag_id':'int8','occ':'float32','hist_type':'int8','hist_id':'int16'})



dfs



dfs.shape



# Are there duplicate datapoints? And how many histograms do we officially have in the dataset?
cnt=0
cnt_hist=0
for ftag in range(91):
    tmp = dfs[dfs['ftag_id']==ftag]
    for histid in tmp['hist_id'].unique():
        cnt_hist+=1
        tmp2 = tmp[tmp['hist_id']==histid]
        print(ftag,histid,tmp2.shape[0]/6435-1)
        cnt+= tmp2.shape[0]/6435-1
print('There are',cnt,'histograms worth of duplicate datapoints of histograms. (only the datapoints are duplicate, this doesnt create extra unique histograms)')
print('There are',cnt_hist,'unique histograms present in this dataset. (This will remain constant even after removing duplicate datapoints)')


# We may now move to the drop duplicates / cleaning script
