import os
import numpy as np
from sqlalchemy import create_engine
import pandas as pd # specifically as pd
import numpy as np # specifically as np
from IPython.display import clear_output
# CERN's ROOT package
import ROOT

def processHistML(tf,file,f_path,f_path_list, binNums,binNumsY, occupancies):  
    
    """
    
    Preprocesses ROOT runfile histogram to data
    
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
                f_path,f_path_list, binNums,binNumsY, occupancies = processHistML(input,file,f_path, f_path_list, binNums,binNumsY, occupancies)  
            elif len(split_path) > 3 and any(folder in split_path for folder in ('CaloMonitoring', 'Jets','MissingEt','Tau','egamma')):                
                # We are greater than 3 directories deep and these directories include the specified folders above, goo deeper
                f_path, f_path_list, binNums,binNumsY, occupancies = processHistML(input,file,f_path, f_path_list, binNums,binNumsY, occupancies)     
            else:
                pass
            
            # Record the file_path that will result now that we are done with the current folder level
            #  i.e. the folder path that results from going up a level in the directory
            f_path = f_path.split('/')
            f_path = '/'.join(f_path[:-1])
                
        elif issubclass(type(input), ROOT.TProfile):
            
            # Record te path of the directory we are looking in with the name of the hist file as part of the path
            try:
                f_path_tp = f_path + '/' + input.GetName()                
            except:
                print("cant GetPath3")
            
            # Get the part of f_path that follows the ':'
            f_path_tp = f_path_tp.split(':')
            f_path_tp = f_path_tp[1][1:]
            
            
            hist_file = file.Get(f_path_tp)
            binsX = hist_file.GetNbinsX()                                    
            
            # Setup the 3 arrays for creating the dataframe
            for binX in range(binsX+1):
                f_path_list.append(f_path_tp)
                binNum = hist_file.GetBin(binX)
                binNums.append(binX)
                binNumsY.append(None)
                occupancies.append(hist_file.GetBinContent(binNum))                        
            
        elif issubclass(type(input),ROOT.TH2):

            # Record the path of the directory we are looking in with the name of the hist file as part of the path
            try:
                f_path_th2 = f_path + '/' + input.GetName()                
            except:
                print("cant GetPath3")
            
            # Get the part of f_path that follows the ':'
            f_path_th2 = f_path_th2.split(':')
            f_path_th2 = f_path_th2[1][1:]
            
            
            hist_file = file.Get(f_path_th2)
            binsX = hist_file.GetNbinsX()                        
            binsY = hist_file.GetNbinsY()
            
            # Setup the 3 arrays for creating the dataframe
            for binX in range(binsX+1):
                for binY in range(binsY+1):
                    f_path_list.append(f_path_th2)
                    binNumXY = hist_file.GetBin(binX,binY)
                    binNums.append(binX)
                    binNumsY.append(binY)
                    occupancies.append(hist_file.GetBinContent(binNumXY))            
                
        elif issubclass(type(input),ROOT.TH1):
            
            # Record the path of the directory we are looking in with the name of the hist file as part of the path
            try:
                f_path_th1 = f_path + '/' + input.GetName()                
            except:
                print("cant GetPath2")

            # Get the part of f_path that follows the ':'
            f_path_th1 = f_path_th1.split(':')
            f_path_th1 = f_path_th1[1][1:]
            
            
            hist_file = file.Get(f_path_th1)
            binsX = hist_file.GetNbinsX()            
            
            # Setup the 3 arrays for creating the dataframe
            for binX in range(binsX+1):                
                f_path_list.append(f_path_th1)
                binNum = hist_file.GetBin(binX,0)                
                binNums.append(binNum)
                binNumsY.append(None)                
                occupancies.append(hist_file.GetBinContent(binNum))
    
    return f_path, f_path_list, binNums,binNumsY, occupancies


def hist_to_df(path):
    
    """
    
    Converts ROOT histogram data from ProcessHistML() to a pandas dataframe.
    
    """
    
    file = ROOT.TFile.Open(path)

    f_path,f_path_list, binNums,binNumsY, occupancies = processHistML(file,file,'',[],[],[],[])
    
    return pd.DataFrame({'paths':f_path_list,'x':binNums,'y':binNumsY,'occ':occupancies})


def select_add_hist(df,choice):
    
    """
    
    Tries to add another histogram to the df_train dataframe. If df_train does not exist, then it initializes the df_train dataframe with the histogram of choice.
    
    """
    
    try:
        df_train = pd.concat([df_train,df[df['paths']==df['paths'].unique()[choice]]])
        df_train.shape
    except:
        df_train = df[df['paths']==df['paths'].unique()[choice]]
        df_train.shape
    
    return df_train

def drop_table_from_sqlalchemy(db_name, table_name_str):
    
    """
    from sqlalchemy import engine
    from pandas.io import sql
    
    """
    
    engine = create_engine(f'sqlite:///{db_name}', echo=False)
    
    sql.execute('DROP TABLE IF EXISTS %s'%table_name_str, engine)
    sql.execute('VACUUM', engine)
    
    print(engine.table_names())
    del engine


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

def run_til_works(batch,database_and_path,run_source_path,hists_of_interest_txts_path,database_csv_backup_path):
    try:
        build_sql_database(database_and_path, prep_dict_of_dfs_and_tables(f'{run_source_path}{batch}/'), hists_of_interest_txts_path, database_csv_backup_path)
    except:
        run_til_works(batch,database_and_path,run_source_path,hists_of_interest_txts_path,database_csv_backup_path)


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


#################### UNUSED? #################### 
#################### UNUSED? #################### 
#################### UNUSED? #################### 
#################### UNUSED? #################### 
#################### UNUSED? #################### 
#################### UNUSED? #################### 


def progress_bar(id_,array_):
    # Progress Bar
    clear_output(wait=True)
    print(f"Processing file {id_+1} of {len(array_)} files... {round(100*(id_+1)/len(array_),2)}% Complete")
    return


def status_update_msg(msg):
    clear_output(wait=True)
    print(msg)
    return


# # See replica_download_script.py for all run request function needs
# # def what_replicas_to_request(input_filename, stream):
# # def proc_what_replicas_to_request(input_filename,stream)        

def prep_dict_of_dfs_and_tables(replica_folders_path):
    
    """
    IMPORTANT: 
        The 'replica_folders_path' variable MUST end with a / in its string
        
    EXAMPLE: 
        replica_folders_path = '../defectless_runs/'
    
    EXAMPLE USE:
        replica_folders_path = '../defectless_runs/'
    """
    
    # Initialize the dictionary of tables that will contain the dataframes
    dict_of_tables = {}
    
    
    for unique_table in set([f"{i.split('.')[0]}${i.split('.')[5]}${i.split('.')[2].split('_')[0].replace('hysics','Main')}" for i in os.listdir(replica_folders_path) if 'HIST' in i and 'sys' not in i]):
        dict_of_tables[unique_table] = []

    
    status_update_msg('Looking for files inside of folders...')
    for idF,file in enumerate([i for i in os.listdir(replica_folders_path) if 'HIST' in i and 'sys' not in i]):

        progress_bar(idF,[i for i in os.listdir(replica_folders_path) if 'HIST' in i and 'sys' not in i])
        
        # Splitting the folder/file name into an array, if that array has equal than 6, then this directory contains folders and we need to loop through each folder in this directory
        if len(file.split('.')) == 6:

            # Loop through data replica file inside each folder
            for file2 in os.listdir(replica_folders_path+file):

                dict_of_tables[f"{file2.split('.')[0]}${file2.split('.')[5]}${file2.split('.')[2].split('_')[0].replace('hysics','Main')}"].append(
#                     f" processing file2 ----  {file2.split('.')[0]}-{file2.split('.')[5]}-{file2.split('.')[2]} , replica_folders_path:{replica_folders_path+file}/{file2}"
                    hist_to_df(replica_folders_path+file+'/'+file2)
                )

        # If instead, the length of the folder/file name split array is less than 6, this must be a file. So we process it directly
        else:

            dict_of_tables[f"{file.split('.')[0]}${file.split('.')[5]}${file.split('.')[2].split('_')[0].replace('hysics','Main')}"].append(
#                 f" processing file ----  {file2.split('.')[0]}-{file2.split('.')[5]}-{file2.split('.')[2]} , replica_folders_path:{replica_folders_path+file}"
                hist_to_df(replica_folders_path+file)
            )
            
    return dict_of_tables
            

# # def build_hists_paths_arr(paths_txt_file):
    
# #     """
    
# #     Extracts the path-lines from paths_txt_file and sends them to arr_. The list arr_ is used against the paths available in each processed run.csv to determine which 
# #     histograms to extract from that run. This function should be used prior to running the build_sql_database() function. 
    
# #     EXAMPLE USE:
# #         paths_txt_file = 'backups/express_good_hists2_various-508_processed1.txt'
        
# #     """
    
# #     with open(paths_txt_file,'r') as f:
        
# #         arr_, ftags, energys, streams = [], [], [], []
        
# #         for idL,line in enumerate(f.readlines()):

# #             # Skip lines that are spaces
# #             if line == ' ':
# #                 continue
            
# #             # Lines that do not have ClusterMon are either meta_info lines or R/Y target lines
# #             if 'ClusterMon' not in line:
                
# #                 # Skip R/Y target lines
# #                 if 'R' in line or 'Y' in line:
# #                     continue
                
# #                 # Process the meta_info line
# #                 line = line.replace('\n','')
                
# #                 # Skip empty lines
# #                 if line.split(' ')[0] == '':
# #                     continue
                
# #                 # Process the ftags from line
# #                 ftag = line.split(' ')[0]
                
# #                 # Process the energy info from line
# #                 energy = line.split(' ')[1]
                    
# #             if 'ClusterMon' in line:
# #                 ftags.append(ftag)
                
# #                 energys.append(energy)
                
# #                 if 'express' in paths_txt_file:
# #                     streams.append('express')
# #                 elif 'pMain' in paths_txt_file:
# #                     streams.append('pMain')
# #                 arr_.append(line.replace('\n',''))
            
# #     return arr_, energys, ftags, streams


# # Verification of runs downloaded vs runs needed from histograms of interest in the following few verification functions. These are to be done before constructing 
# # the sql database in order to prevent errors during its creation.


# def verify_hoi_from_file(replica_hoi_path):
    
#     """
    
#     Generates the hoi_list for verifying histograms of interests from file.
    
#     Currently, all histograms are assumed to be of the 'express stream' type. Thus, stream='express' in this function.
    
#     EXAMPLE USE:
#         verify_hoi_from_file('backups/red_hists_of_interest/150redhists_express_processed1.txt')
    
#     """
    
#     # Initialize ftag, energy, and run lists
#     fs,es,rs = [],[],[]
    
#     # Open the Replica histogram of interest path/file
#     with open(replica_hoi_path) as f:
        
#         # Loop through the lines in the file
#         for line in f.readlines():
            
#             # Remove the return command from the line. All lines have this at the end even blank ones.
#             line = line.replace('\n','')
            
#             # Get a handle for what stream it is
#             stream = 'express'
            
#             # If this line in the file is a space, skip it
#             if line == ' ':
#                 continue
            
#             # If the line is blank, skip it. This occurs as a result of a line that has a return being converted to ''.
#             if line == '':
#                 continue
                
#             # ClusterMon is in the lines that contain the path info for the histogram of interest, lines without are either meta_info lines, blank lines, space lines, or R/Y target lines
#             if 'ClusterMon' not in line:
                
#                 # Some lines with ClusterMon contain 'R', for the lines without ClusterMon, if R is in the line, skip it. Otherwise it must be a meta_info line
                
#                 # Skip R/Y target lines
#                 if 'R' in line or 'Y' in line:
#                     continue
                    
#                 # Process meta_info lines
#                 line = line.split(' ')
                
#                 # Get a handle for the ftag part of the line
#                 ftag = line[0]
                
#                 # Get a handle for the energy part of the line
#                 energy = line[1]
                
#             # if line contains 'path info'
#             elif 'ClusterMon' in line:
#                 # Line up and append the information for this specific histogram's path, its energy, and its ftag information for later use
#                 fs.append(ftag)
#                 es.append(energy)
#                 rs.append(line.split('/')[0].split('_')[1])

                
#     # Initialize array that will contain properly formatted "ftag energy run" information
#     hoi_list = []
    
    
#     # Append the values as they line up by id all to hoi_list
#     for idE,entry in enumerate(rs):
#         hoi_list.append(f"{fs[idE]} {es[idE]} {rs[idE]}")

        
#     return hoi_list

            
# def verify_run_directory_list(run_directory_path):
    
#     """
    
#     Generates the properly formatted run directory list by "ftag energy run" information.
    
#     All histograms are assumed to be of the stream type stream='express' in this function. Will identify express stream files on its own but no other streams are
#     currently recognized.
    
#     EXAMPLE USE:
#         verify_run_directory_list('../defective_runs/')
    
#     """
    
#     # Initialize the ftag, energy, run lists
#     fs,es,rs = [],[],[]
    
#     # Initialize the run directory list
#     run_directory_list = []
    
    
#     # Loop through the run_directory_path and find each run(entry) with its "ftag energy run" info contained in its name
#     for entry in os.listdir(run_directory_path):
        
#         # Skip entries that have .sys in their name
#         if 'sys' in entry:
#             continue
        
#         # Set the stream as express if it exists in the name of the entry
#         if 'express' in entry:
#             stream = 'express'
            
#         # Prepare the entry for meta info processing
#         entry = entry.split('.')
        
#         # Get the ftag of the entry
#         ftag = entry[5]
        
#         # Get the energy of the entry
#         energy = entry[0]
        
#         # Get the run information of the entry
#         run = entry[1]
        
#         # If the run has a leading '0' in its name, it is of format '00xxxxxx' and those leading values should be removed
#         if run[0] and run[1] == '0':
            
#             # Get the modified run information of the entry based on the condition
#             run = run[2:]
            
#         # Add the information for the single entry to the run_directory_list, in the appropriate format
#         run_directory_list.append(f"{ftag} {energy} {run}")
        
        
#     return run_directory_list
    
    
# def verify_hois_in_run_directory(hoi_list,runs_in_directory):
    
#     """
    
#     Handles the verification that the runs that contain the histograms of interest exist in the run directory. Uses the results of
#     verify_hoi_from_file() and verify_run_directory_list() to run this verification process.
    
    
#     EXAMPLE USE:
#         verify_hois_in_run_directory(verify_hoi_from_file('backups/red_hists_of_interest/150redhists_express_processed1.txt'),verify_run_directory_list('../defective_runs/'))
    
#     """
    
#     # Initialize a count for how many histograms of interest are not present in the run directory
#     cnt=0
    
    
#     # Loop through the histograms of interest list and get a handle for each 'unique' entry
#     for unique_entry in set(hoi_list):
        
#         # If the histogram of interest from ho_list not present in run directory
#         if unique_entry not in runs_in_directory:
            
#             # Update how many hoi are not present in the count cnt
#             cnt+=1
            
#             # And notify the user that unique entry 'unique_entry' is not present in the run directory
#             print(unique_entry, 'not in directory')  
            
#     # Otherwise, the count will be zero and all histograms of interest are in the run directory
#     if cnt == 0:
#         print('All histograms_of_interest in run_directory')

    
# def verify_run_directory_filesizes(run_directory_path):
    
#     """
    
#     Another important verification step as part of building the database is verifying the filesizes of the runs in the directory in the case they did not download
#     properly. This function assists in that process.
    
#     Only identifies stream information for 'express' streams.
    
#     EXAMPLE USE:
#         verify_run_directory_filesizes('../defective_runs/')
    
#     """
    
#     # Initialize the ftag, energy, and run lists
#     fs,es,rs = [],[],[]
    
#     # Initialize the run directory list
#     run_directory_list = []
    
#     # Initialize the file size list
#     file_size_list = []
    
#     # Loop through the runs in the run directory path
#     for entry in os.listdir(run_directory_path):     
        
#         # Skip the entries with .sys in their name
#         if 'sys' in entry:
#             continue
            
#         # Look for and tag this run's stream as 'express' if express exists in this entry's name
#         if 'express' in entry:
#             stream = 'express'
            
#         # Handle the processing of the entry as a separate variable 'entryy'
#         entryy = entry.split('.')
        
#         # Get the ftag for the entry
#         ftag = entryy[5]
        
#         # Get the energy for the entry
#         energy = entryy[0]
        
#         # Get the run for the entry
#         run = entryy[1]
        
#         # If the run has a leading '0' in its name, it is of format '00xxxxxx' and those leading values should be removed
#         if run[0] and run[1] == '0':
            
#             # Get the modified run information of the entry based on the condition
#             run = run[2:]
            
#         # Append the formatted ftag energy and run information to the run_directory list
#         run_directory_list.append(f"{ftag} {energy} {run}")
        
#         # Get and append the file size information for the run whose information was appended to run_directory_list
#         file_size_list.append(round(os.path.getsize(f"{run_directory_path}/{entry}")/1000000,1))
        
#     # Run information and file size information is available for viewing via the returned pandas dataframe
#     return pd.DataFrame({'run_info(ftag energy run)':run_directory_list, 'file_size(MB)':file_size_list}).sort_values(by=['file_size(MB)'])


# def verify_unique_hoi_ftag_tables_in_dots(dots,hoi_file_path):
    
#     """
    
#     Verifies which unique hoi ftag tables are in dictionary of dfs and tables. Prints out which exist, which do not exist, and if all exist.
    
#     Each unique_entry here is a unique run number, but IT IS NOT A UNIQUE FTAG. The tables are constructed by UNIQUE FTAGS not UNIQUE RUNS(unique_entry).
    
#     EXAMPLE USE:
#         dots = prep_dict_of_dfs_and_tables(f'../defective_runs/')
#         hoi_file_path = 'backups/red_hists_of_interest/150redhists_express_processed1.txt'
        
#     """
    
#     # Keep track of how many unique_entries(these are unique runs with associated ftags(tables) do not exist as tables in dots(dots.keys()))
#     cnt = 0
    
#     # Loop through unique_entries(unique runs with associated ftags(tables), the loop goes through an array of entries that are formatted to match dots.keys() format)
#     for unique_entry in [f"{unique_entry.split(' ')[1]}${unique_entry.split(' ')[0]}$express" for unique_entry in set( verify_hoi_from_file(hoi_file_path) )]:
        
#         # If the ftag(table) part of the unique_entry does not exist as a table in dots.keys()
#         if unique_entry not in dots.keys():
            
#             # Update the number of ftags(tables) that do not exist in dots.keys()
#             cnt+=1
            
#             # Display the ftag(table) that does not exist in dots.keys()
#             print(f"{unique_entry} not in dots")
         
#         # Otherwise, the ftag(table) part of unique_entry exists in dots.keys() and for this unique_entry, we want to see that it exists, so we display it
#         else:
#             print(unique_entry,'-- exists')
#     # If all ftag(table) parts of unique_entries exist as tables in dots.keys(), say so at the end of the function
#     if cnt == 0:
#         print("All unique_entries exist as a table in dots")

    
# # def build_sql_database(db_name, dict_of_dfs_and_tables, paths_txt_file_directory,backup_output_dir):
    
# #     """
    
# #     If recreating the database, delete the .db file. dont simply rerun this function.
    
# #     NOTE ON MEMORY CONSTRAINTS:
# #         As part of this function, it uses dict_of_dfs_and_tables() to construct a needed parameter. This parameter constructs a large dictionary of potentially many dataframes of runs - 
# #         So many in fact, that it may crash the system as it is holding all these runs/dataframes in memory while it is building the database out. 
# #         A simple way of dealing with this is to organize the runs in a series of folders, called batches, each of which will be targeted with replica_folders_path parameter inside of 
# #         the dict_of_dfs_and_tables() function so that it will convert only a set number of dataframes/runs at a time, store those into the database, then move on to the next batch 
# #         (assuming we run build_sql_database in a loop over all such batch directories)
        
# #     EXAMPLE USE and USING ABOVE INFO:
# #         db_name == 'runs2.db'
# #         paths_txt_file_directory = 'backups/' # Must have '/' at end of path
# #         backup_output_dir = 'backups/'  # Must have '/' at end of path
# #         dict_of_dfs_and_tables = prep_dict_of_dfs_and_tables(f'../defectless_runs/{dir_}/'), 'backups/')
# #         * the path '../defectless_runs/' should contain a series of folders that are the batches containing the subset of folders/files to process with build_sql_database

# #         # Loop over the batches, here called dir_
# #         for dir_ in os.listdir('../defectless_runs/'):

# #             # Construct the database for each batch with proper input parameters
# #             build_sql_database('runs2.db', prep_dict_of_dfs_and_tables(f'../defectless_runs/{dir_}/'), 'backups/')
# #             print(dir_,' Complete.')
            
            
# #        # Example from construction of defectless histogram database
# #        build_sql_database('runs_redhists.db', dots, 'backups/red_hists_of_interest/','backups/database_backup_files/red_without_qual_values/')
        
# #     """
    
# #     # Construct the engine used to create and manipulate the sql database
# #     engine = create_engine(f'sqlite:///{str(db_name)}', echo=False)

    
# #     status_update_msg('Constructing dict_of_arrs...')
# #     # Construct dict_of_arrs
# #     dict_of_arrs = {}
# #     for idF,paths_txt_file in enumerate([i for i in os.listdir(paths_txt_file_directory) if 'sys' not in i and '.csv' not in i and 'processed' in i]):
# #         dict_of_arrs[f'arrs_{idF}'] = build_hists_paths_arr(f'{paths_txt_file_directory}{paths_txt_file}')
       
# #     status_update_msg('Looping through dict_of_dfs_and_tables...')
# #     for idT,table in enumerate(dict_of_dfs_and_tables.keys()):
    
# #         print('Processing table',table)
    
# #         # Gather the meta info that contains the energy, ftag, and stream information for this table
# #         meta_info = table.split('$')

        
# #         # Loop through the dataframes we previously processed that are contained inside this particular table
# #         for iddF,df in enumerate(dict_of_dfs_and_tables[table]):

            
# #             # Loop through the arrays stored inside dict_of_arrs (each array corresponds to a single processed file containing hists_of_interest and meta_info)
# #             for key in dict_of_arrs.keys():

# #                 # Initialize the paths_in_df (the paths for the hists_of_interest that we will identify)
# #                 paths_in_df = []

                
# #                 # For this hist_of_interest path in dict_of_arrs current array key, 
# #                 for idP, path in enumerate(dict_of_arrs[key][0]):

# #                     # If the meta_info for the table matches up with the meta_info for this path, this path goes in paths_in_df
# #                     if meta_info[0] == dict_of_arrs[key][1][idP] and meta_info[1] == dict_of_arrs[key][2][idP] and meta_info[2] == dict_of_arrs[key][3][idP]:
# #                         paths_in_df.append(path)

# #                 # For this array called key in dict_of_arrs.keys(), skip this array of paths_in_df if paths_in_df empty
# #                 # If no meta_info matches were made on this dataframe as a hist_of_interest, the paths_in_df list will be empty, then we can move onto the next dataframe immediately
# #                 if not paths_in_df:
# #                     continue

                    
# #                 for idP2,path2 in enumerate(paths_in_df):            

# #                     # If hists_of_interest already exists, concatenate the subset dataframe in df that is df[df['paths']==paths_in_df[i]]
# #                     try:
# #                         hists_of_interest = pd.concat([hists_of_interest,df[df['paths']==paths_in_df[idP2]]])

# #                     # If hists_of_interest does not exist, set it to this subset dataframe df[df['paths']==paths_in_df[i]]
# #                     except:
# #                         hists_of_interest = df[df['paths']==paths_in_df[idP2]]

# #         try:
# #             # If the database is not located in the current directory, it will have a pathname instead of db name
# #             # Detect this and define tmp as the temporary actual db_name so the csv can properly be constructed
# #             if len(db_name.split('/'))>1:
# #                 tmp = db_name.split('/')[-1]
# #             # Construct the backup file for this table as .csv
# #             hists_of_interest.to_csv(f'{backup_output_dir}{tmp.replace(".","_")}${table}$backup.csv')
# #         except Exception as e:
# #             print(f'error creating csv(hists_of_interest) for table({table})\n {e}')

# #         try:
# #             # Send the concatenated dataframes of interest, for this particular table, to the sql database
# #             hists_of_interest.to_sql(table, engine, if_exists='append')
# #         except Exception as e:
# #             print(f'error sending hists_of_interest to sql database for table({table}) - Table Empty.\n {e}')

# #         # How far along in the process of preparing the hists_of_interests for this table for this batch of runs? - Also, notify that the table succesfully made it to the database
# #         print(f"Table #{idT+1} of {len(dict_of_dfs_and_tables.keys())}, {table}, Table exists and has been saved to database.")
        
# #         try:
# #             # Clear the hists_of_interests variable for the next table - we do not want the hists_of_interest from two different tables mixing
# #             del hists_of_interest
# #         except Exception as e:
# #             print(f'error deleteing hists_of_interest for table({table}) - Table Empty.\n {e}')


# #############################################################
# # ADDING INITIAL QUALITY=0 VALUES TO HISTOGRAMS OF INTEREST #
# #############################################################


# def init_hists_quality_feature(db_df,db_name,table_name):

#     """
    
#     Initializes the quality feature column to the dataframe 'db_df' in the database 'db_name' whose values are all quality=0.
    
#     EXAMPLE USE:
#         db_df  = get_dataframe_from_sql('runs.db','SELECT paths,x,y,occ FROM data_hi_express')
#         db_name = 'runs.db'
#         table_name = 'data_hi_express'
        
        
#     HOW TO INITIALIZE ALL DFS/TABLES IN DATABASE:
#         for idT,table in enumerate(engine.table_names()):
#             status_update_msg(f'Initializing quality values for table #{idT+1} of {len(engine.table_names())}...')
#             init_hists_quality_feature( get_dataframe_from_sql('runs_redhists.db',f'SELECT paths,x,y,occ FROM {table}'),'runs_redhists.db', table )
#         status_update_msg('---Complete---')
        
#     """
    
#     # Initialize all good quality hist 'quality' values to 0. (0 as good, 1 as bad 'quality').

#     # Create the quality column and set it to all zeros(good quality)
#     db_df['quality'] = [int(0)]*len(db_df['x'].values)

#     # Save the newly edited database
#     engine = create_engine(f'sqlite:///{db_name}', echo=False)
#     db_df.to_sql(table_name,engine, if_exists='replace', index=False)

    


# ##################################################
# # ADDING DEFECT VALUES TO HISTOGRAMS OF INTEREST #
# ##################################################


# def scale_cnvrt_dic(hists_df,index_of_hist_of_interest,x_or_y_axis_as_0or1):
    
#     """
    
#     Converts the x or y coordinates(scaled coordinates) from a histogram of interest to the bin coordinates(unscaled coordinates) and returns all these information as
#     the dictionary 'dict_convert'
    
#     IMPORTANT NOTE!: MAKE SURE THAT THE X/Y axes in the dataframe are columns 1 and 2 respectively. For example an extra column 'index' in the dataframe will return a path and shoot an
#     error that says it cannot convert int to string or something. So drop that extra column from the dataframe.
    
#     EXAMPLE USE:
#         Using the pMain set of 20 histograms compiled in a previous iteration of the code development, 
#         to convert the 0th histogram's x(as 0) axis...do the following:
#         scale_cnvrt_dic(pMain_hist20,0,0)
    
#     """
    
#     # Setting up to convert the scale from the bin numbers (0-98, example only) to the dqm's histogram's scale values (-4.9 to 4.9, example only)
    
#     # Get a handle for the histogram of interest within hists_df
#     tmp = hists_df[hists_df['paths']==hists_df['paths'].unique()[index_of_hist_of_interest]]
    
#     # Get a handle for the array of indexes whose range is based off the max size of the x or y coordinate in the histogram of interest
#     tmp_i = np.array([(idx) for idx,i in enumerate(range(int(tmp[tmp.columns[x_or_y_axis_as_0or1+1]].values.max()+1)))])
    
#     # Get a handle for the array of scaled values that are scaled by tmp_i's minimum and maximum values
#     tmp_int = np.interp(tmp_i,(tmp_i.min(),tmp_i.max()),(-tmp[tmp.columns[x_or_y_axis_as_0or1+1]].values.max()/20,tmp[tmp.columns[x_or_y_axis_as_0or1+1]].values.max()/20))
    
#     # Round this result
#     tmp_int = tmp_int.round(2)
    
#     # Prepare the conversion dictionary for this histogram ['bin_coordinate':dqm_scale_value]
#     dict_convert = {}
    
    
#     # Loop through the range of values for x or y that is in tmp_i
#     for idx,val in enumerate(tmp_i):
        
#         # Loop through the scaled values in tmp_int in its entirely for each unscaled  value in tmp_i
#         for idxx,vall in enumerate(tmp_int):
            
#             # If the id of the unscaled value and the scaled value match up
#             if idx==idxx:
                
#                 # And if it is an X coordinate
#                 if x_or_y_axis_as_0or1 == 0:
                    
#                     # Add the scaled coordinate value as the item whose key is the unscaled coordinate in the format of 'x_(unscaled coordinate)'
#                     dict_convert['x_'+str(val)] = vall
#                 # Or if it is a Y coordinate
#                 else:
                    
#                     # Add the scaled coordinate value as the item whose key is the unscaled coordinate in the fomrat of 'y_(unscaled coordinate)'
#                     dict_convert['y_'+str(val)] = vall

#     return dict_convert


# def tenths_ceil(num_str):
    
#     """
    
#     As part of the scale conversion process, a histogram of interest has scaled coordinate values that include 3 decimal places such as '1.123'. To convert to bin
#     coordinates(unscaled coordinates) these are rounded up in a fashion that is similar to a ceiling function targeting the tenths place of the scaled values. This
#     function processes this rounding mechanism and returns the would be unscaled coordinate value as a floating point number.
    
#     """
    
#     # Get num_str as string
#     num_str = str(num_str)
    
#     # Get num_str_fixed as num_str with the '-' removed if it exists
#     num_str_fixed = num_str.replace('-','')
    
#     # Create the tuples of ints and decimals
#     int_tups = [('1e'+str(idx),char) for idx,char in enumerate(num_str_fixed.split(".")[0][::-1])]
#     dec_tups = [('1e'+str(-1*idx-1),char) for idx,char in enumerate(num_str_fixed.split(".")[1])]
    
    
#     # Loop through decimal tuples
#     for id_,tup in enumerate(dec_tups):
        
        
#         # Loop through each individual tuple's decimal value as it loops through tuples in decimals
#         for dec in tup[1]:
            
#             # if its the first decimal, skip it
#             if id_ == 0:
#                 continue
                
#             # if any other decimals are greater than 0
#             if int(dec) > 0:
                
#                 # num_str is negative, return the negative value truncated to the tenths
#                 if '-' in num_str:  
#                     return -1 * ( float( ''.join( [tup[1] for tup in int_tups[::-1]] ) ) + float( '0.'+str ( int(dec_tups[0][1]) ) ) )
                
                
#                 # its positive, return the postive value's ceiling to the tenths
#                 else:
#                     # the tenths place is 9, the hundredths are greater than 0, add 1 to the integer part and zero the rest
#                     if int(dec_tups[0][1]) == 9 and  int(dec_tups[1][1]) > 0:
#                         # We have a float that is greater than 0, a 9 in the tenths place, and a hundredths place greater than 0, round the integer part of the number up
#                         return( [float(tup[1]) for tup in int_tups][0]+1 )

#                     # tenths place is not 9 or hundredths place is 0 or both, return the rounded down version of the number
#                     return (float( ''.join( [tup[1] for tup in int_tups[::-1]] ) ) + float( '0.'+str ( int(dec_tups[0][1])+1 ) ))
                
                
#     # if none of the previous loops return a value, the num_str was not rounded up, so return the same negative value
#     if '-' in num_str:
#         return -1* ( float(''.join([tup[1] for tup in int_tups[::-1]]))+float('0.'+dec_tups[0][1]) )
    
#     # else if none of the previous loops return a value, the num_str was not rounded up, so return the same positive value
#     else:        
#         return float(''.join([tup[1] for tup in int_tups[::-1]]))+float('0.'+dec_tups[0][1]) 
    
    
# def transform_hitstring(line):
    
#     """
    
#     Takes a line in as the format received from the txt_file which was copy/pasted from cern's dqm display on a specific histogram, then extracts the (x_hitcoord,y_hitcoord)
    
#     EXAMPLE HITSTRING FROM TEXT FILE:
#         line = "Y0-(eta,phi)[OSRatio]=(-1.850,1.723)[7.59e+01]:	6829.0"
    
#     """
    
#     # Get a handle for the color identifier string within the line ('R' or 'Y')
#     color_identifier_string=line[0]
    
    
#     # Get a handle for the hit number, the id of the defect as it was reported by the dqm algorithm (0 to NredBins/NyellowBins)
#     hit_number = line.replace(line[0],'').split('-',1)[0]
    
#     # Get a handle for the occupancy value from the hit string. It was discovered that the value reported in the histstring is rounded in some fashion
#     #  by the dqm algorithm as BinsDiffFromStripMedian runs over the histogram. ( occ of 140374 would be rounded up to 140400; 140424 would be rounded to 140400;
#     #  etc).
#     # Do not make this an int, there are float values of occupany present in histograms!
#     occ_val = line.split(':')[1].replace('\t','').split('.')[0]
    
#     # Extract the x_hitcoord and y_hitcoord from line
#     line = line.replace(color_identifier_string+hit_number+'-'+'(eta,phi)[OSRatio]=','')
#     line = line.split(')')[0]
#     line = line.replace("(",'')
#     line = line.split(',')
#     # The final value for x_hitcoord and y_hitcoord are rounded according to the method descibed by the function 'tenths_ceil()'
#     x_hitcoord, y_hitcoord = tenths_ceil( float( line[0] ) ), tenths_ceil( float ( line[1] ) )
    
#     # Return a tuple of information from the hit string as seen below
#     return ( x_hitcoord, y_hitcoord, color_identifier_string, hit_number, occ_val )


# def extract_val_list(txt_file_path):
    
#     """
        
#     Extracts the defects from a .txt file containing such defects whose format matches the hit string format of a dqm algorithm.
#     (line = "Y0-(eta,phi)[OSRatio]=(-1.850,1.723)[7.59e+01]:	6829.0"). Collectively, all such processed lines' information is output to a list of tuples called
#     'val_list'
        
#     txt_file_path requires the pathname with the filename and file extension included.
#     Example: "dir1/dir2/dir3/filename.txt"
#     NOTE: Our current txt_file_path working directory is: "../hist_targets_txt_files/" such that the text file would look like "../hist_targets_txt_files/filename.txt"
    
#     txt_file Structure:
#     It is a .txt file structured from a paste function after copying from the dqm starting from the line that reads "NRedBins:", then "NYellowBins:", then the lines of most interest.
#     From there, the lines of interest proceed line by line in a format such as the following ...
#     C#-(eta,phi)[OSRatio]=(x_coord,y_coord)[7.59e+01]: occ_val 
#     where
#     C = color character identifier (Y for yellow bin, R for red bin)
#     # = the number of the R/Y bin (if there are NYellowBins=44 then this number will be a number from 0-44)
#     x_coord = the eta or x coordinate location of the point of interest (red or yellow hit)
#     y_coord = the phi or y coordinate location of the point of interest (red or yellow hit)
#     occ_Val = the occupancy value that was recorded at the location (x_coord,y_coord) 
    
#     val_list Structure:
#     It is a list of tuples whose tuples are each (0-x_hitcoord, 1-y_hitcoord, 2-color_identifier_string, 3-hit_number, 4-occ_val, 5-hist_path, 6-meta_info)
#     val_list = [ (t00,t01,t02,t03,t04,t05,t06), (t10,t11,t12,t13,t14,t15,t16), ..., (tn1,tn2,tn3,tn4,tn5,tn6) ]
    
#     """
    
    
#     # Initialize the val_list
#     val_list = []
    
#     # Open the text file
#     # directory_path = '../hist_targets_txt_files/'
#     with open(txt_file_path,"r") as f:       
        
        
#         # Read the text file line by line and
#         for line in f.readlines():
            
#             # Skip these two lines
#             if 'NRedBins' in line:
#                 continue
#             if 'NYellowBins' in line:
#                 continue
#             if 'ClusterMon' in line:
#                 hist_path = line.replace('\n','')
#                 continue
#             if 'R' not in line and 'Y' not in line:
#                 meta_info = line.replace('\n','').split(' ')
#                 continue
            
#             # Get a handle for the transform of the hitstring in each line of txt_file_path to the tuple of values of interest
#             transformed_line = transform_hitstring(line)
            
#             # (0-x_hitcoord, 1-y_hitcoord, 2-color_identifier_string, 3-hit_number, 4-occ_val, 5-hist_path, 6-meta_info
#             val_list.append( ( transformed_line[0], transformed_line[1], transformed_line[2], transformed_line[3], transformed_line[4], hist_path, meta_info ) )
    
#     # return the val_list in the format as described above
#     return val_list
    

# def prep_quality_feature(list_of_hists_df, hist_index, val_list):
        
#     """
    
#     Adds the quality values for the histogram of interest identified as 'hist_index' which is in the dataframe lists_of_hists_df whose defective quality values are
#     identified by val_list.
    
#     val_list_xy must be structured as follows - it is a list of tuples whose tuples are each (x_hitcoord,y_hitcoord) such that 
#     val_list_xy = [ (xhc_0,yhc_0), (xhc_1,yhc_1), ..., (xhc_n,yhc_n) ]
    
#     EXAMPLE USE:
    
#         list_of_hists_df = dfs  # from a loop inside add_specific_qualityvals_to_hists()
#         hist_index = hist_index # also from a loop inside add_specific_qualityvals_to_hists()
    
#     """            
    
    
#     # Convert our val_list tuple of 5 values to a tuple of 2 coordinate values (x,y)
#     val_list_xy = [(tup[0],tup[1]) for tup in val_list]
    
#     # If the histogram of interest is in the list of paths that are associated with specific red/yellow hit coordinates (hit_n = (x,y,color,occ,hist_path))
#     if list_of_hists_df['paths'].unique()[hist_index] in [tup[5] for tup in val_list]:
        
#         # Get a handle for the histogram we are constructing the quality feature for
#         tmp = list_of_hists_df[list_of_hists_df['paths']==list_of_hists_df['paths'].unique()[hist_index]]
    
#     else:
#         print (f"Error: the unique histogram chosen as hist_index cannot be found for any of the hist_paths in val_list \n{list_of_hists_df['paths'].unique()[hist_index]} not in val_list")
#         # set tmp as an empty dataframe by looking for a subset that does not exist
#         tmp = list_of_hists_df[list_of_hists_df['quality']==9]
    
#     # Get the coordinate conversion dictionary
#     cnvrt_dic_x, cnvrt_dic_y = scale_cnvrt_dic(list_of_hists_df, hist_index, 0), scale_cnvrt_dic(list_of_hists_df, hist_index, 1)
    
    
#     # Loop through the quality values, if the coordinates match the location of the hit, modify their quality value
#     for idx,val in enumerate(tmp['quality'].values):
        
        
#         # If the tuple (x,y) from histogram tmp is in the list of (x,y) tuples from the hit value list (val_list_xy)
#         if ( cnvrt_dic_x['x_'+str(int(tmp.iloc[idx, 1]))], cnvrt_dic_y['y_'+str(int(tmp.iloc[idx,2]))] ) in val_list_xy:
    
#             # Set the quality class for this hit (0/1 for green/red, 0/1/2 for green/yellow/red ...for now we just use 0/1)
#             tmp.iloc[idx, 4] = 1 
            
    
#     # Return the list_of_hists_df whose 'quality' values have been updated
#     return tmp


# def add_specific_qualityvals_to_hists(db_name, quality_val_txtfile):

#     """
    
#     Adds the defective quality values to the range of histograms of interest inside the database 'db_name' using the functino prep_quality_feature(). This is the
#     main function to do this process over an entire database.
    
#     EXAMPLE USE:
#        db_name = 'runs_redhists.db' 
       
       
#     HOW TO VERIFY THE QUALITY VALUES WERE PROPERLY ADDED:
#         engine = create_engine(f'sqlite:///runs_redhists.db', echo=False)
#         cnt=0
#         for idT,table in enumerate(engine.table_names()):
#             df = get_dataframe_from_sql('runs_redhists.db',f'SELECT * FROM {table}')
#             print(table)
#             display(df[df['quality']!=0])
#             cnt += df[df['quality']!=0].shape[0]
#         display(cnt)
        
#     """
    
#     engine = create_engine(f'sqlite:///{db_name}', echo=False)

    
#     # Extract and get a handle for unprocessed_val_list from txt_file_path
#     unprocessed_val_list = extract_val_list(quality_val_txtfile)

    
#     for idT,table in enumerate(engine.table_names()):
        
#         # Detailed progress bar information
#         print(f'processing table #{idT+1} of {len(engine.table_names())}...')
        
#         # Get a handle for the meta info from the table
#         meta_info = table.split('$')
        
#         # Get a handle for dataframes that are the tables in the runs_redhists database and drop the index column
#         dfs = get_dataframe_from_sql(db_name, f'SELECT * FROM {table}')# pd.read_csv(record_path+'express_hist20.csv',index_col=[0])
        
#         # Convert float columns to integers - needed to do this for the big database as well...
#         dfs['y'] = [int(a) for a in dfs['y'].values]
        
#         # Extract and get a handle for val_list from txt_file_path
#         unprocessed_val_list = extract_val_list(quality_val_txtfile)
        
#         # Get a handle for the unique paths before the process mixes up the order
#         paths = dfs['paths'].unique()
        
        
#         # Loop through the unique hist values in the dataframe to update each histogram of interest's quality feature
#         for hist_index,path in enumerate(paths):
            
#             # More detailed progress bar information
#             print(f"hist_index #{hist_index+1} of {len(dfs['paths'].unique())} processing...")

#             # Initialize the processed_val_list
#             val_list = []
        
#             # loop through the vals in unprocessed_val_list
#             for idV,val in enumerate(unprocessed_val_list):
            
#                 # If the table matches the current table and the path is in the current tuple val
#                 if f"{val[6][1]}${val[6][0]}$express" == table and path in val[5]:
                    
#                     # This target value is in this table and dataframe and its information should be stored in val_list                    
#                     val_list.append(val)            
            
#             # Get a subset that does not include unique()[hist_index]
#             tmp = dfs[dfs['paths']!=path]

#             # Prepare the modified quality values
#             tmp2 = prep_quality_feature(dfs, hist_index, val_list)

#             # Concatenate the processed histogram with the rest of the histograms
#             dfs = pd.concat([tmp2,tmp])
    
    
#         # Clean this variable AFTER the loop finishes
#         del unprocessed_val_list

#         print(f'saving backups to csvs and tables to database for table {table}')

#         # Save the dataframe (table in database) as a table_backup.csv
#         dfs.to_csv(f'{meta_info[0]}${meta_info[1]}${meta_info[2]}$backups.csv')

#         # Save the dataframe(table in database) as a replacement table with the newly created quality feature for this table
#         dfs.to_sql(table, engine, if_exists='replace', index=False)

        
# ###########################
# # POST DATABASE FUNCTIONS #
# ###########################


def get_dataframe_from_sql(db_name,query):
    
    """
    
    Simplified way to extract dataframe from sqlite3 database.
    
    CURRENT TABLES:
        'data_hi_express',
        'data18_13TeV_express_good',
        'data18_13TeV_pMain_good'
    
    EXAMPLE USE:
        NOTE: columns = * will get an 'Index' column as well. SELECT paths,x,y,occ to get the columns of interest
        
        db_name = 'runs.db'
        query = 'SELECT * FROM data_hi_express WHERE paths="run_366268/CaloMonitoring/ClusterMon/CaloCalTopoClustersNoTrigSel/2d_Rates/m_clus_etaphi_Et_thresh3"'
        
        OR 
        tmp_path = engine.execute('SELECT DISTINCT paths FROM data_hi_express').fetchall()[0]
        query = f'SELECT * FROM data_hi_express WHERE paths="{tmp_path[0]}"'
        
        OR simply
        query = 'SELECT paths,x,y,occ FROM data_hi_express'
        
        When the other features are added to the table (such as 'quality') include those in the query as well.
    
    """
    
    # Get a handle for the sqlalchemy engine that allows commands to be executed over the database 'db_name'
    engine = create_engine(f'sqlite:///{db_name}', echo=False)
    
    # Try to get a dataframe who is based on a sql 'query' from the database identified in 'engine'
    try:
        df = pd.read_sql(query,engine)
    except Exception as e:
        print(e)
    
    # Try to free up system resources
    try:
        del engine
    except Exception as e:
        print(e)
    
    # Try to remove the index column if it exists in the df
    try:
        if 'index' in df.columns:
            df = df.drop(columns='index')
    except Exception as e:
        print(e)
    
    return df    
  

# def create_db_backup_csvs(db_name,output_dir):
    
#     """
#     EXAMPLE USE:
#         db_name = 'runs2.db'
#         output_dir = 'backups/'  #must have '/' at the end of the path
#     """
    
#     # Get database handle
#     engine = create_engine(f'sqlite:///{db_name}', echo=False)
    
#     # Loop through tables in database
#     for idT,table in enumerate(engine.table_names()):
        
#         # Notication of loop status
#         status_update_msg(f'saving table #{idT+1} of {len(engine.table_names())} to .csv')
        
#         # Try to get the data from the table as a dataframe
#         try:
#             get_dataframe_from_sql(db_name,f'SELECT * FROM {table}').to_csv(f'{output_dir}{db_name.replace(".","_")}${table}$backup.csv')
            
#         # If it doesnt work, print an exception
#         except Exception as e:
#             print(e)
            
#     # Notify that the verification is complete
#     print('Complete.')
            
            
# def test_database_for_corruption(db_name):
    
#     """
#     EXAMPLE USE:
#         db_name = 'runs2.db'
#     """
    
#     engine = create_engine(f'sqlite:///{db_name}', echo=False)
    
#     for table in engine.table_names():
#         try:
#             print(f"TABLE:{table} \n")
#             display(engine.execute(f'SELECT * FROM {table} LIMIT 5').fetchall())
#         except:
#             print(f'TABLE({table}) CORRUPTED - RECREATE!')


# def rebuild_db_from_backup_csvs(db_name,db_table_backup_csvs_path):
    
#     """
    
#     Use this function in case you need to rebuild a corrupt database from backup files. To rebuild, first delete the runs database that is corrupst as it will not allow opening to replace)
#     If instead, you are overwritting a noncorrupt database with a backup from the .csv files, deleting the database is not necessary.
    
#     EXAMPLE USE:
#        # For the defective histograms
#        rebuild_db_from_backup_csvs('runs_redhists.db','backups/database_backup_files/red_without_qual_values/')
       
#     """
    
#     # Construct the sql engine for db_name
#     engine = create_engine(f'sqlite:///{db_name}', echo=False)
    
    
#     # Loop through backup csvs in the backup csv directory
#     for backup_csv in [i for i in os.listdir(db_table_backup_csvs_path) if 'backup.csv' in i]:
    
#         # Progress notification on which backup_csv we are currently working on
#         status_update_msg(f'rebuilding {backup_csv}')
    
#         # Get the meta_info for this backup_csv
#         meta_info = backup_csv.split('$')
        
#         # Construct the dataframe from the backup csv
#         df = pd.read_csv(db_table_backup_csvs_path+backup_csv,index_col=[0])
        
#         # Send that csv to the sql database whose table name is based on the meta info
#         df.to_sql(f"{meta_info[1]}${meta_info[2]}${meta_info[3]}", engine, if_exists='replace')
    
    
# #########################################################
# # CONSTRUCTING AND FORMATTING TENSORS FOR ML OPERATIONS #
# #########################################################

# def load_hists_dataset_matrices(db_name):
    
#     """
    
#     Assuming express hists as .csvs and pMain hists as .csvs have been constructed from the .py script,  this function will
#     load and construct the training and target matrices for the CNN (supervised dataset using quality feature).
    
#     IMPORTANT NOTE: We don't actually need to keep track of the runs that we train the model with because its just going to be used for future predictions over histograms whose run
#     numbers we WILL know. Therefore, it is not necessary to keep track of this.
    
#     tensor_list is 5d.    
#     Let the example tensor_list be of shape (18,2,24,65,99)
#     1st dimension is the number of tables. (based on the number of unique 'ftag energy stream' combinations)
#     2nd dimension is the number of datasets. There are only two. (feature_set(0) or target_set(1))
#     3rd dimension is the number of histograms.
#     4th dimension is the number of y coordinates.
#     5th dimension is the number of x coordinates.
#     Therefore, calling tensor_list[0][0][0] will return a matrix that is the feature set for the 1st histogram in the first table of the database. Its shape will be of size (65,99)
    
#     """
    
#     engine = create_engine(f'sqlite:///{db_name}', echo=False)
    
#     # Initialize list of tensors from tables
#     tensor_list = []
    
#     # Load the datasets
#     for idT, table in enumerate(engine.table_names()):
        
#         progress_bar(idT,engine.table_names())
        
#         # Get a handle for the dataframes 'dfs' from table 'table' in database 'db_name' 
#         dfs = get_dataframe_from_sql(db_name,f'SELECT * FROM {table}')
    
#         # Initialize the feature_set that will contain our feature variable matrices
#         feature_set = []

#         # Initialize the target_set that will contain our target variable matrices
#         target_set = []

        
#         # Loop through the unique histograms in the dataframe of histograms 'dfs'
#         for idH,hist in enumerate(dfs['paths'].unique()):
            
#             # Get a handle for each unique histogram we pass in the loop
#             df_tmp = dfs[dfs['paths']==hist]
            
#             # Append the feature set in the format appropriate for the tensor as a numpy tensor
#             feature_set.append(df_tmp.pivot_table(index='y',columns='x',values='occ').to_numpy())
            
#             # Do the same as above, but for the target set
#             target_set.append(df_tmp.pivot_table(index='y',columns='x',values='quality').to_numpy())
            
#         # Add each such feature_set,target_set combination to a list of tensors, each entry into this list containing the dataset,histogram,xcoordinate,ycoordinate information for
#         # the table 'table' in this interation of the loop
#         tensor_list.append( np.stack([np.array(feature_set),np.array(target_set)]) )
    
#     return tensor_list


# def split_hists(dataset,train_size):
    
#     """
    
#     Takes the dataset that we constructed from the previous assumptions, reads it in as a (2(features,targets),histograms,eta,phi)  shaped tensor,
#     randomizes the histograms in the dataset so they arent organized by any sort of run number, then splits them into their respective training and testing sets.
    
#     EXAMPLE USE:
#         train_set,test_set = split_hists(tensor_list[0],0.7)
        
#     TO GENERATE 'train_sets' and 'test_sets' FROM split_hists(), USE THE FOLLOWING:
    
#         NOTE: tensor_list is generated from load_hists_dataset_matrices(). Note also, that tensor_list will have to exist as a variable in the system at the time
#         of running this code in this comment block below.
    
#         # Initialize train_sets and test_sets
#         train_sets,test_sets = [],[]
        
#         # Initialize the table/tensor id
#         idT = 0
        
#         # Loop over the tensor/table in tensor_list
#         for tensor in tensor_list:
        
#             # get the train_set,test_set associated with this table/tensor
#             train_set,test_set = split_hists(tensor_list[idT],0.7)
            
#             # Append train_sets with train_set
#             train_sets.append(train_set)
            
#             # Append test_sets with test_set
#             test_sets.append(test_set)
            
#             # Update the iterator
#             idT += 1
        
#     display(train_set.shape)
#     # 1st dimension is number of datasets in this training set. (feature_values are the 0th part of this dimension, target_values are the 1st value of this dimension)
#     # 2nd dimension is number of histograms in this training set.
#     # 3rd dimension is their y coordinates.
#     # 4th dimension is their x coordinates.
    
#     test_set.shape
#     # 1st dimension is number of datasets in this test set. (feature_values are the 0th part of this dimension, target_values are the 1st value of this dimension)
#     # 2nd dimension is number of histograms in this training set.
#     # 3rd dimension is their y coordinates.
#     # 4th dimension is their x coordinates.
    
#     TO VERIFY THAT FUNCTION WORKS AS SHOULD:
#     # Make sure everything looks as it should
#     # display(train_set.shape)
#     # display(test_set.shape)
#     # print(round(100*train_set[0].shape[0]/round(load_hist20_dataset_matrices()[0].shape[0])),'%\n')
#     # print(round(100*test_set[0].shape[0]/round(load_hist20_dataset_matrices()[1].shape[0])),'%')
    
#     """
    
#     # Initialize the list that will store the random indexes
#     ri_list = []

#     # Loop through the number of matrices
#     for i in range(dataset[0].shape[0]):

#         # Get a random index
#         ri = np.random.randint(dataset[0].shape[0])

#         # While that integer is in the random integer list, keep looking for a random integer that isnt in there
#         while ri in ri_list:
#             ri = np.random.randint(dataset[0].shape[0])

#         # Then append that random integer to the list
#         ri_list.append(ri) 

#     # Construct the training and testing matrix index list
#     train_set_index = ri_list[0:round(train_size*dataset[0].shape[0])]
#     test_set_index = ri_list[round(train_size*dataset[0].shape[0]):dataset[0].shape[0]]
    
#     # Construct the set of matrixes from the matrix index lists
#     train_set = np.stack([np.array([matrix for matrix in dataset[0][train_set_index]]),np.array([matrix for matrix in dataset[1][train_set_index]])])
#     test_set = np.stack([np.array([matrix for matrix in dataset[0][test_set_index]]),np.array([matrix for matrix in dataset[1][test_set_index]])])

#     return train_set, test_set


# def format_traintest_as_numpy_for_ML(train_sets,test_sets):
    
#     """
    
#     Takes as input the train_sets and test_sets generated from the previous function. Outputs the final formatted version of the numpy tensors for ML with Keras.
    
#     See the previous notes on split_hists() on how to generate train_sets, test_sets.

#     """
    
#     # TRAIN SET PROCESSING
    
#     # Initialize table id idTable - looping through tensors doesnt allow you to immediate have access to the ids unless enumerate gives you access to everything in the tensor and ids
#     # So we initialize it outisde of the loop. Probably cleaner this way anyway.
#     idTable = 0

#     # Initialize these as the first table's features and first table's targets
#     final_features_dataset = train_sets[0][0]
#     final_targets_dataset = train_sets[0][1]


#     # Loop through train sets
#     for table_tensor in train_sets:

        
#         # Loop through the numerical size values in table_tensor.shape
#         for shape in table_tensor.shape:
            
#             # If there is any shape with a size of 0
#             if shape == 0:
                
#                 # Set the skip_table bool to True so that we skip this table
#                 print('shape is 0 in table',idTable, 'skipping table')
#                 skip_table = True
        
#         # If the bool skip_table is True
#         if skip_table == True:
            
#             # Skip the table, update the iterator, and continue the loop
#             print('skipping table')
#             skip_table = False
#             idTable += 1
#             continue
        
#         # Progress bar by table in train sets
#         print('\ntrain_sets, table_tensor id:', idTable,'-',table_tensor.shape)

#         # Show how idTable==0 was handled
#         if idTable == 0:            
            
#             # Show the features and targets for the initial table, skip this table because it was initialized as this, update the iterator, and continue
#             print(f'skipping table 0, features:{final_features_dataset.shape}, targets:{final_targets_dataset.shape}')
#             idTable += 1
#             continue

#         # Construct the final_features_dataset as all the histograms concatenated across all 18 tables 
#         final_features_dataset = np.concatenate([ final_features_dataset, train_sets[idTable][0] ])

#         # Construct the final_targets_dataset as all the histograms concatenated across all 18 tables 
#         final_targets_dataset = np.concatenate([ final_targets_dataset, train_sets[idTable][1] ])


#         # Update the iterator for what table we are on
#         idTable += 1
        
    
#     # TEST SET PROCESSING
    
#     # Initialize table id idTable
#     idTable = 0

#     # Initialize table id idTable - looping through tensors doesnt allow you to immediate have access to the ids unless enumerate gives you access to everything in the tensor and ids
#     # So we initialize it outisde of the loop. Probably cleaner this way anyway.
#     final_features_dataset_test = test_sets[0][0]
#     final_targets_dataset_test = test_sets[0][1]

#     # Loop through test_sets 
#     for table_tensor in test_sets:

        
#         # Loop through the numerical size values in table_tensor.shape
#         for shape in table_tensor.shape:
            
#             # If there is any shape with a size of 0
#             if shape == 0:
                
#                 # Set the skip_table bool to True so that we skip this table
#                 print('shape is 0 in table',idTable, 'skipping table')
#                 skip_table = True
                
#         # If the bool skip_table is True                
#         if skip_table == True:
            
#             # Skip the table, update the iterator, and continue the loop
#             print('skipping table')
#             skip_table = False
#             idTable += 1
#             continue
        
#         # progress bar by table in test_sets
#         print('\ntest_sets, table_tensor id:', idTable,'-',table_tensor.shape)

#         # Show how idTable==0 was handled
#         if idTable == 0:

#             # Show the features and targets for the initial table, skip this table because it was initialized as this, update the iterator, and continue
#             print(f'skipping table 0, features:{final_features_dataset_test.shape}, targets:{final_targets_dataset_test.shape}')
#             idTable +=1
#             continue

#         # Construct the final_features_dataset as all the histograms concatenated across all 18 tables 
#         final_features_dataset_test = np.concatenate([ final_features_dataset_test, test_sets[idTable][0] ])

#         # Construct the final_targets_dataset as all the histograms concatenated across all 18 tables 
#         final_targets_dataset_test = np.concatenate([ final_targets_dataset_test, test_sets[idTable][1] ])

#         # Visualize the dataset shapes as they get concatenated
#         print(final_features_dataset_test.shape)
#         print(final_targets_dataset_test.shape)

#         # Update the iterator for what table we are on
#         idTable += 1
        
    
#     # Reshape final_features_dataset so its in the format needed for our future ML stuff
#     final_features = final_features_dataset.reshape(1,final_features_dataset.shape[0],final_features_dataset.shape[1],final_features_dataset.shape[2])
    
#     # Reshape final_targets_dataset so its in the format needed for our future ML stuff
#     final_targets = final_targets_dataset.reshape(1,final_targets_dataset.shape[0],final_targets_dataset.shape[1],final_targets_dataset.shape[2])
    
#     # Construct the final_train_set by concatenating the features/targets from the previous two
#     final_train_set = np.concatenate( [final_features,final_targets] )
    
#     # Reshape final_features_dataset_test so its in the format needed for our future ML stuff
#     final_features2 = final_features_dataset_test.reshape(1,final_features_dataset_test.shape[0],final_features_dataset_test.shape[1],final_features_dataset_test.shape[2])
    
#     # Reshape final_targets_dataset_test so its in the format needed for our future ML stuff
#     final_targets2 = final_targets_dataset_test.reshape(1,final_targets_dataset_test.shape[0],final_targets_dataset_test.shape[1],final_targets_dataset_test.shape[2])
    
#     # Construct the final_test_set by concatenating the features/targets from the previous two
#     final_test_set = np.concatenate( [final_features2,final_targets2] )
    
#     return final_train_set, final_test_set


# def save_traintest_sets(train_set,test_set,train_save_file,test_save_file):

#     """
    
#     Saves the formatted train and test numpy tensors as .npy files.
    
#     EXAMPLE USE:
#         train_save_file = 'train_set.npy'
#         test_save_file = 'test_set.npy'
        
#     """
    
#     # Open a file to store the numpy matrix in
#     with open(train_save_file, 'wb') as f:

#         # Save the matrix
#         np.save(f, train_set)
#         print('train_set saved')

#     # Open a file to store the numpy matrix in
#     with open(test_save_file, 'wb') as f:

#         # Save the matrix
#         np.save(f, test_set)
#         print('test_set_saved')


# def load_saved_traintest_set(train_set_filename, test_set_filename):

#     """
    
#     Loads the saved train and test numpy tensors from the previously saved .npy files.
    
#     EXAMPLE USE:
#     train_set,test_set = load_saved_traintest_set('train_set.npy','test_set.npy')
    
#     """

#     # Open the file that train_set is stored in as f
#     with open(train_set_filename, 'rb') as f:

#         # Load and get a handle for train_set
#         train_set = np.load(f)

#     # Open the file that train_set is stored in as f
#     with open(test_set_filename, 'rb') as f:

#         # Load and get a handle for test_set
#         test_set = np.load(f)
        
#     return train_set,test_set

    
# ##########################
# # MAIN RUN OF THS SCRIPT #
# ##########################

# # DEFECTLESS HISTOGRAMS - needs confirmation, but this is a rough sketch of what it looks like
# # Constructing the sql database from the directory containing the batch folders of run files/folders

# # for dir_ in os.listdir('../defectless_runs/'):
# #     print(dir_,' Complete.')
# #     build_sql_database('runs2.db', prep_dict_of_dfs_and_tables(f'../defectless_runs/{dir_}/'), 'backups/green_hists_of_interest/','backups/database_backup_files/green_hists_of_interest)
    

# # # Construct all the quality values for the good histograms

# # # Start by creating the sqlalchemy engine to manipulate the database
# # engine = create_engine(f'sqlite:///runs2.db', echo=False)
# # # Then loop through the tables and do add the quality feature to the good hists
# # for idT,table in enumerate(engine.table_names()):
# #     init_goodhists_quality_feature(get_dataframe_from_sql('runs2.db',f'SELECT * FROM {table}'), 'runs2.db', table)
# #     print(f"{idT+1} of {len(engine.table_names())} Complete")
    
    
# # # Quick view of dataframes in sql database tables

# # for table in engine.table_names():
# #     display(table, get_dataframe_from_sql('runs2.db',f'SELECT * FROM {table}').head(1))
    
# # # With the newly constructed quality features for the good histograms, we create backups of this

# # create_db_backup_csvs('runs2.db','backups/qual_processed/')

                       
                       
# # # GETTING A FEW HISTOGRAM HEATMAPS/BINARY MASKS for VISUALIZATION
# # df = get_dataframe_from_sql('runs_redhists.db','SELECT * FROM data18_13TeV$f1001_h327$express')
# # for idU,unique_path in enumerate(df['paths'].unique()):
# #     if idU==2:
# #         break
        
# #     sns.heatmap( df[df['paths']==unique_path].pivot_table(index='y', columns='x', values='occ') )
# #     plt.gca().invert_yaxis()
# #     plt.title(f'OCCUPANCY: \ndata18_hi,f1027_h331,express \n{unique_path}')
# #     plt.xlabel(r'$\eta$')
# #     plt.ylabel(r'$\phi$')
# #     plt.show()
    
# #     sns.heatmap( df[df['paths']==unique_path].pivot_table(index='y', columns='x', values='quality') )
# #     plt.title(f'BINARY MASK: \ndata18_hi,f1027_h331,express \n{unique_path}')
# #     plt.xlabel(r'$\eta$')
# #     plt.ylabel(r'$\phi$')
# #     plt.gca().invert_yaxis()
# #     plt.show()