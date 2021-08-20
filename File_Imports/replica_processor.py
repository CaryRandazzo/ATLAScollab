from default_imports import *
from functions import *
from sqlalchemy import create_engine


def progress_bar(id_,array_):
    # Progress Bar
    clear_output(wait=True)
    print(f"Processing file {id_+1} of {len(array_)} files... {round(100*(id_+1)/len(array_),2)}% Complete")
    return

def status_update_msg(msg):
    clear_output(wait=True)
    print(msg)
    return
  

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
            

def build_hists_paths_arr(paths_txt_file):
    
    """
    
    Extracts the path-lines from paths_txt_file and sends them to arr_. The list arr_ is used against the paths available in each processed run.csv to determine which 
    histograms to extract from that run. This function should be used prior to running the build_sql_database() function. 
    
    EXAMPLE USE:
        paths_txt_file = 'backups/express_good_hists2_various-508_processed1.txt'
        
    """
    
    with open(paths_txt_file,'r') as f:
        
        arr_, ftags, energys, streams = [], [], [], []
        
        for idL,line in enumerate(f.readlines()):
            if 'ClusterMon' not in line:
                
                line = line.replace('\n','')
                
                ftag = line.split(' ')[0]
                
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
        
    """
    
    # Construct the engine used to create and manipulate the sql database
    engine = create_engine(f'sqlite:///{str(db_name)}', echo=False)

    
    # Construct dict_of_arrs
    dict_of_arrs = {}
    for idF,paths_txt_file in enumerate([i for i in os.listdir(paths_txt_file_directory) if 'sys' not in i and '.csv' not in i and 'processed' in i]):
        dict_of_arrs[f'arrs_{idF}'] = build_hists_paths_arr(f'{paths_txt_file_directory}{paths_txt_file}')
       
    
    for idT,table in enumerate(dict_of_dfs_and_tables.keys()):
    
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
            # Construct the backup file for this table as .csv
            hists_of_interest.to_csv(f'{backup_output_dir}{db_name.replace(".","_")}${table}$backup.csv')
            
            # Send the concatenated dataframes of interest, for this particular table, to the sql database
            hists_of_interest.to_sql(table, engine, if_exists='append')
            
            # How far along in the process of preparing the hists_of_interests for this table for this batch of runs? - Also, notify that the table succesfully made it to the database
            print(f"Table #{idT+1} of {len(dict_of_dfs_and_tables.keys())}, {table}, Table exists and has been saved to database.")
            
            # Clear the hists_of_interests variable for the next table - we do not want the hists_of_interest from two different tables mixing
            del hists_of_interest
        except:
            # How far along in the process of preparing the hists_of_interests for this table for this batch of runs? - Also, notify that the table did not succesfully go to database
            print(f"Table #{idT+1} of {len(dict_of_dfs_and_tables.keys())}, {table}, Table Empty.")

            
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
    
    
    engine = create_engine(f'sqlite:///{db_name}', echo=False)
    
    
    try:
        df = pd.read_sql(query,engine)
    except:
        print('ERROR: false query? or engine error?')
    
    # Free up system resources
    try:
        del engine
    except:
        pass
    
    return df    
  
  
def create_db_backup_csvs(db_name,output_dir):
    
    """
    The build_sql_database() function should now build these backups itself, if that works then update and remove this function. This has been tested to work if
    the database itself has not been corrupted.
    
    EXAMPLE USE:
        db_name = 'runs2.db'
        output_dir = 'backups/'  #must have '/' at the end of the path
    """
    
    engine = create_engine(f'sqlite:///{db_name}', echo=False)
    
    for table in engine.table_names():
        try:
            get_dataframe_from_sql(db_name,f'SELECT * FROM {table}').to_csv(f'{output_dir}{db_name.replace(".","_")}${table}$backup.csv')
        except:
            print(f'TABLE({table}) CORRUPTED - RECREATE!')
            
            
def test_database_for_corruption(db_name):
    
    """
    EXAMPLE USE:
        db_name = 'runs2.db'
    """
    
    engine = create_engine(f'sqlite:///{db_name}', echo=False)
    
    for table in engine.table_names():
        try:
            print(f"TABLE:{table} \n")
            display(engine.execute(f'SELECT * FROM {table} LIMIT 5').fetchall())
        except:
            print(f'TABLE({table}) CORRUPTED - RECREATE!')
