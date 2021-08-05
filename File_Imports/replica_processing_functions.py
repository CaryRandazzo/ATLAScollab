from functions import * 
from IPython.display import clear_output
import os

# Get a handle for the record_path
# Example: record_path = '../Scripts&Records/'
record_path = input("Where are the replias stored? record_path=")


def progress_bar(id_,array_):
    # Progress Bar
    clear_output(wait=True)
    print(f"Processing file {id_+1} of {len(array_)} files... {round(100*(id_+1)/len(array_),2)}% Complete")
    return


def status_update_msg(msg):
    clear_output(wait=True)
    print(msg)
    return


def prepeach_expresspmain_df(replica_folders_path):

    """
    Prepare the list of express_dfs and pMain dfs
    """

    # Initialize lists of dataframes, one per stream type
    df_express_list, df_pMain_list = [],[]

    # Initialize path of data replica folders
    # EXAMPLE: path = '../'
    path = replica_folders_path

    # Loop through data replica folders
    for idF,file in enumerate(os.listdir(path)):

        # Progress Bar
        clear_output(wait=True)
        print(f"Processing file {idF+1} of {len(os.listdir(path))} files... {round(100*(idF+1)/len(os.listdir(path)),2)}% Complete")

        # Skip irrelevant folders
        if file == "Scripts&Records":
            continue

        # Loop through data replica files inside folder
        for file2 in os.listdir(path+file):

            # Process data to dataframe and append to list of dataframes, some are express stream some are pMain stream, 2 separate df_lists will reduce memory vs adding columns
            if 'express_express' in file2:
                df_express_list.append(hist_to_df(path+file+'/'+file2))
            else:
                df_pMain_list.append(hist_to_df(path+file+'/'+file2))
    return df_express_list,df_pMain_list
    


def construct_dfs_by_runstream(df_express_list,df_pMain_list):

    # Loop through the pMain dataframe list 
    for idN,df in enumerate(df_express_list):

        #Construct the run string from the list of express dataframes
        run_string = df['paths'].values[0].split('/')[0]

        # Send the processed pMain df.csv to the appropriate folder with the appropriate name
        # MODIFY OUTPUT LOCATION AS NEEDED
        df.to_csv('../unprocessed_dfs_express/express_data_files_'+run_string+'.csv')

    # Loop through the pMain dataframe list
    for idN,df in enumerate(df_pMain_list):

        #Construct the run string from the list of pMain dataframes
        run_string = df['paths'].values[0].split('/')[0]

        # Send the processed pMain df.csv to the appropriate folder with the appropriate name
        # MODIFY OUTPUT LOCATION AS NEEDED
        df.to_csv('../unprocessed_dfs_pMain/pMain_data_files_'+run_string+'.csv')

    # Free up the memory
    del df_express_list
    del df_pMain_list
    del run_string
    
    
    
def create_dbs_from_expresspmain(data_path):

    """
    data_path: Get a handle for the location of the express csv files
    """
    
    status_update_msg("Initializing Processing for express...")


    # Get a handle for the location of the express csv files
    # EXAMPLE: data_path = '../unprocessed_dfs_express/'
    #data_path = input("What is the location of the express csv files that were processed? data_path=")


    # Determine if express_db_df exists, initialize or append to the database accordingly
    if 'express_db_df.csv' in os.listdir(record_path):
        express_db_df = pd.read_csv(record_path +'express_db_df.csv',,index_col=[0])
    else:
        express_db_df = pd.DataFrame()


    # Loop through the files in the data_path, process them, and append them    
    for idF,express_file in enumerate(os.listdir(data_path)):

        # Progress Bar
        progress_bar(idF,os.listdir(data_path))

        # Processing dataframe and compiling dataframe_database
        df = pd.read_csv(data_path+express_file,index_col=[0])
        express_db_df = pd.concat([express_db_df,df])


    # Free up memeory from this file
    del express_file


    # Reduce df.memory_usage() by converting paths column to category datatype - these 14 datasets nearly max out the entire 8gb of ram
    status_update_msg("Converting express path column to category datatype...")
    express_db_df['paths'] = express_db_df['paths'].astype('category')


    # Save database as csv (56,064,638 datapoints took 7m15s for this part of the code alone..thats 6.36GB file size according to the directory viewer)
    status_update_msg("Saving express_db_df datafarme to csv(this could take several minutes+)...")
    express_db_df.to_csv('express_db_df.csv')
    del df
    del express_db_df


    # Notify that Express Database Processing is Complete
    status_update_msg("Express Database Processing Complete.")


    status_update_msg("Initializing Processing for pMain...")


    # Get a handle for the location of the pMAin csv files
    data_path = '../unprocessed_dfs_pMain/'


    # Determine if pMain_db_df exists, initialize or append to the database accordingly
    if 'pMain_db_df.csv' in os.listdir(record_path):
        pMain_db_df = pd.read_csv(record_path+'pMain_db_df.csv',index_col=[0])
    else:
        pMain_db_df = pd.DataFrame()


    # Loop through the files in the data_path, process them, and append them    
    for idF,pMain_file in enumerate(os.listdir(data_path)):

        # Progress Bar
        progress_bar(idF,os.listdir(data_path))

        # Processing dataframe and compiling dataframe_database
        df = pd.read_csv(data_path+pMain_file,index_col=[0])
        pMain_db_df = pd.concat([pMain_db_df,df])


    # Free up memeory from this file
    del pMain_file

    # Reduce df.memory_usage() by converting paths column to category datatype - these 14 datasets nearly max out the entire 8gb of ram
    status_update_msg("Converting pMain path column to category datatype...")
    pMain_db_df['paths'] = pMain_db_df['paths'].astype('category')


    # Save database as csv (56,064,638 datapoints took 7m15s for this part of the code alone..thats 6.36GB file size according to the directory viewer)
    status_update_msg("Saving pMain_db_df dataframe to csv(this could take several minutes+)...")
    pMain_db_df.to_csv('pMain_db_df.csv')
    del df
    del pMain_db_df


    # Notify that pMain DatabASEProcessing is Complete
    status_update_msg("pMain Database Processing Complete.")


    # Notify that Processing is Complete
    status_update_msg("Processing Complete.")    
    

def process_dbs_to_hist20s():

    """
    
    """


    # express PROCESSING STEP

    # Read the express database into memory
    status_update_msg('Reading express database...')
    express_db_df = pd.read_csv(record_path+'express_db_df.csv',index_col=[0])


    # Get a subset of the express database as express_hist20
    status_update_msg('Getting the subset of express database...')
    express_hist20 = express_db_df[express_db_df['paths'].str.contains('CaloCalTopoClustersNoTrigSel/2d_Rates/m_clus_etaphi_Et_thresh1')]


    # Free up memory from the express database
    del express_db_df


    # Save the express_hist20.csv
    status_update_msg('Saving express_hist20.csv...')
    express_hist20.to_csv(record_path+'express_hist20.csv')


    # pMain PROCESSING STEP


    # Read the pMain database into memory
    status_update_msg('Reading pMain database...')
    pMain_db_df = pd.read_csv(record_path+'pMain_db_df.csv',index_col=[0])


    # Get a subset of the pMain database as pMain_hist20
    status_update_msg('Getting the subset of pMain database...')
    pMain_hist20 = pMain_db_df[pMain_db_df['paths'].str.contains('CaloCalTopoClustersNoTrigSel/2d_Rates/m_clus_etaphi_Et_thresh1')]


    # Free up memory from the pMain database
    del pMain_db_df


    # Save the oMain_hist20.csv
    status_update_msg('Saving pMain_hist20.csv...')
    pMain_hist20.to_csv(record_path+'pMain_hist20.csv')


    # Notify that Processing is Complete
    status_update_msg('Processing Complete.')

    

def load_express_and_pmain_hist20():

    express_hist20 = pd.read_csv(record_path+'express_hist20.csv',index_col=[0])
    pMain_hist20 = pd.read_csv(record_path+'pMain_hist20.csv',index_col=[0])

 return express_hist20,pMain_hist20
 
 
 
def init_hist20s_forqualityvals():

    """
    This function assumes the hist_targets_txt_files folder containing the hist targets text files exist and are accessable.
    """
    
    # Get a handle for express_hist20 and drop the index column
    express_hist20 = pd.read_csv(record_path+'express_hist20.csv',index_col=[0])
    
    # IMPORTANT: Do this line only if the previous line reads the df and the df shows a column[0] that shouldnt be there
    # express_hist20 = express_hist20.drop(columns=express_hist20.columns[0])

    # Get a handle for pMain_hist20 and drop the index column
    pMain_hist20 = pd.read_csv(record_path+'pMain_hist20.csv',index_col=[0])
    
    # IMPORTANT!: Do this line only if the previous line reads the df and the df shows a column[0] that shouldnt be there
    # pMain_hist20 = pMain_hist20.drop(columns=pMain_hist20.columns[0])


    # ALL quality values should get initialized to 0, because processing will occur with the functions:

    # Create the quality column express_hist20 dataset and set it to all zeros(bad quality)
    express_hist20['quality'], pMain_hist20['quality'] = [int(0)]*len(express_hist20['x'].values),[int(0)]*len(pMain_hist20['x'].values)


    # Save the databases
    express_hist20.to_csv(record_path+'express_hist20.csv')
    pMain_hist20.to_csv(record_path+'pMain_hist20.csv')
    



def scale_cnvrt_dic(hists_df,index_of_hist_of_interest,x_or_y_axis_as_0or1):
    """
    # So, for example, using the pMain set of 20 histograms we have compiled, to convert the 0th histogram's x(as 0) axis...do the following 
    scale_cnvrt_dic(pMain_hist20,0,0)
    """
    
    # Setting up to convert the scale from the bin numbers (0-98, example only) to the dqm's histogram's scale values (-4.9 to 4.9, example only)
    tmp = hists_df[hists_df['paths']==hists_df['paths'].unique()[index_of_hist_of_interest]]
    tmp_i = np.array([(idx) for idx,i in enumerate(range(int(tmp[tmp.columns[x_or_y_axis_as_0or1+1]].values.max()+1)))])
    tmp_int = np.interp(tmp_i,(tmp_i.min(),tmp_i.max()),(-tmp[tmp.columns[x_or_y_axis_as_0or1+1]].values.max()/20,tmp[tmp.columns[x_or_y_axis_as_0or1+1]].values.max()/20))
    tmp_int = tmp_int.round(2)
    
    # Prepare the conversion dictionary for this histogram ['bin_coordinate':dqm_scale_value]
    dict_convertX = {}
    for idx,val in enumerate(tmp_i):
        for idxx,vall in enumerate(tmp_int):
            if idx==idxx:
                if x_or_y_axis_as_0or1 == 0:
                    dict_convertX['x_'+str(val)] = vall
                else:
                    dict_convertX['y_'+str(val)] = vall

    return dict_convertX

#Example
#print('Example scale_cnvrt_dic to convert hitcoords from cern coordinates to bin coordinates (-1.8,1-.8)->(31,50)')
#print(scale_cnvrt_dic(pMain_hist20,0,0))

#print(f"Example hitstring: 'Y0-(eta,phi)[OSRatio]=(-1.850,1.723)[7.59e+01]:6829.0'")

def tenths_ceil(num_str):
    """
    Currently, this gives the correct value when transforming (eta,phi)_cern coordinates to (eta,phi)_bin(the dataframe version of histograms) coordinates.
    
    This may not work in all cases, double check to make sure???
    """
    
    
    # Get num_str as string
    num_str = str(num_str)
    
    # Get num_str_fixed as num_str with the '-' removed if it exists
    num_str_fixed = num_str.replace('-','')
    
    # Create the tuples of ints and decimals
    int_tups = [('10e'+str(idx),char) for idx,char in enumerate(num_str_fixed.split(".")[0][::-1])]
    dec_tups = [('10e'+str(-1*idx-1),char) for idx,char in enumerate(num_str_fixed.split(".")[1])]
    
    # Loop through decimal tuples
    for id_,tup in enumerate(dec_tups):
        
        # Loop through each individual tuple's decimal value as it loops through tuples in decimals
        for dec in tup[1]:
            
            # if its the first decimal, skip it
            if id_ == 0:
                continue
                
            # if any other decimals are greater than 0
            if int(dec) > 0:
                
                # and if the given num_str input is negative, return the negative value truncated to the tenths
                if '-' in num_str:  
                    return -1 * ( float( ''.join( [tup[1] for tup in int_tups[::-1]] ) ) + float( '0.'+str ( int(dec_tups[0][1]) ) ) )
                
                # else if its not negative, return the postive value's ceiling to the tenths
                else:
                    return  float( ''.join( [tup[1] for tup in int_tups[::-1]] ) ) + float( '0.'+str ( int(dec_tups[0][1])+1 ) )
                
    # if none of the previous loops return a value, the num_str was not rounded up, so return the same negative value
    if '-' in num_str:
        return -1* ( float(''.join([tup[1] for tup in int_tups[::-1]]))+float('0.'+dec_tups[0][1]) )
    
    # else if none of the previous loops return a value, the num_str was not rounded up, so return the same positive value
    else:        
        return float(''.join([tup[1] for tup in int_tups[::-1]]))+float('0.'+dec_tups[0][1])

#print(f'Example tenths_ceil(-1.850,1.723): ({tenths_ceil(-1.850)},{tenths_ceil(1.723)})')
    
    
def transform_hitstring(line):
    """
    Takes a line in as the format received from the txt_file which was copy/pasted from cern's dqm display on a specific histogram, then extracts the (x_hitcoord,y_hitcoord)
    """
    #line = "Y0-(eta,phi)[OSRatio]=(-1.850,1.723)[7.59e+01]:	6829.0"
    
    color_identifier_string=line[0]
    
    hit_number = line.replace(line[0],'').split('-',1)[0]
    
    occ_val = int(line.split(':')[1].replace('\t','').split('.')[0])
    
    # Begin the process of extracting the x_hitcoord and y_hitcoord from line
    line = line.replace(color_identifier_string+hit_number+'-'+'(eta,phi)[OSRatio]=','')
    line = line.split(')')[0]
    line = line.replace("(",'')
    line = line.split(',')
    x_hitcoord, y_hitcoord = tenths_ceil( float( line[0] ) ), tenths_ceil( float ( line[1] ) )
    
    return ( x_hitcoord, y_hitcoord, color_identifier_string, hit_number, occ_val )

# Example string, works as expected
#print(f'Example of transform_hitstring: {transform_hitstring("Y0-(eta,phi)[OSRatio]=(-1.850,1.723)[7.59e+01]:	6829.0")}')

def extract_val_list(txt_file_path):
    """
        
    txt_file_path requires the pathname with the filename and file extension included.
    Example: "dir1/dir2/dir3/filename.txt"
    NOTE: Our current txt_file_path working directory is: "../hist_targets_txt_files/" such that the text file would look like "../hist_targets_txt_files/filename.txt"
    
    txt_file Structure:
    It is a .txt file structured from a paste function after copying from the dqm starting from the line that reads "NRedBins:", then "NYellowBins:", then the lines of most interest.
    From there, the lines of interest proceed line by line in a format such as the following ...
    C#-(eta,phi)[OSRatio]=(x_coord,y_coord)[7.59e+01]: occ_val 
    where
    C = color character identifier (Y for yellow bin, R for red bin)
    # = the number of the R/Y bin (if there are NYellowBins=44 then this number will be a number from 0-44)
    x_coord = the eta or x coordinate location of the point of interest (red or yellow hit)
    y_coord = the phi or y coordinate location of the point of interest (red or yellow hit)
    occ_Val = the occupancy value that was recorded at the location (x_coord,y_coord) 
    
    val_list Structure:
    It is a list of tuples whose tuples are each (x_hitcoord,y_hitcoord) such that ...
    val_list = [ (xhc_0,yhc_0), (xhc_1,yhc_1), ..., (xhc_n,yhc_n) ]
    """
    
    
    # Initialize the val_list
    val_list = []
    
    
    # Convert the txt_file_path with '-'s in it to txt_file_path with '/'s in it instead
    txt_file_path = txt_file_path.replace('-','/')
    
    # Get a handle for the hist_path based on the txt_file_path ???
    hist_path = txt_file_path.replace('.txt','')
    
    # Open the text file
    # directory_path = '../hist_targets_txt_files/'
    with open('../hist_targets_txt_files/'+'run_348251-CaloMonitoring-ClusterMon-CaloCalTopoClustersNoTrigSel-2d_Rates-m_clus_etaphi_Et_thresh1.txt',"r") as f:       
        # Extract the path_name(first line of the txt_file) - the first line is the path_name
        path_name = f.readline()
        
        # Read the text file line by line and
        for line in f.readlines():
            
            # Skip these two lines
            if 'NRedBins' in line:
                continue
            if 'NYellowBins' in line:
                continue
            
            # Get a handle for the transform of the hitstring in each line of txt_file_path to the tuple of values of interest
            transformed_line = transform_hitstring(line)
            
            # (x_hitcoord, y_hitcoord, color_identifier_string, hit_number, occ_val, hist_path)
            val_list.append( ( transformed_line[0], transformed_line[1], transformed_line[2], transformed_line[3], transformed_line[4], hist_path ) )
    
    # return the val_list in the format as described above
    return val_list

# This example is very large and very long, turn on for debugging
# print(f'Example extract_val_list using txt_file_path="run_348251-CaloMonitoring-ClusterMon-CaloCalTopoClustersNoTrigSel-2d_Rates-m_clus_etaphi_Et_thresh1.txt:')
# display(extract_val_list("run_348251-CaloMonitoring-ClusterMon-CaloCalTopoClustersNoTrigSel-2d_Rates-m_clus_etaphi_Et_thresh1.txt"))
    
    

def prep_quality_feature(list_of_hists_df, hist_index, txt_file_path):
        
    """
    val_list_xy must be structured as follows - it is a list of tuples whose tuples are each (x_hitcoord,y_hitcoord) such that 
    val_list_xy = [ (xhc_0,yhc_0), (xhc_1,yhc_1), ..., (xhc_n,yhc_n) ]
    
    EXAMPLE USE:
    tmp = pMain_hist20[pMain_hist20['paths']==pMain_hist20['paths'].unique()[0]]
    tmp['quality'] = [int(0)]*len(tmp['x'].values)
    # display(tmp)
    tmp = (prep_quality_feature(tmp, 0, "run_348251-CaloMonitoring-ClusterMon-CaloCalTopoClustersNoTrigSel-2d_Rates-m_clus_etaphi_Et_thresh1.txt"))
    # display(tmp)
    tmp[tmp['quality']!=0]
    # tmp[tmp['paths'] == tmp['paths'].unique()[0]]
    """
    
    
    # Convert the txt_file_path with '-'s in it to txt_file_path with '/'s in it instead
    txt_file_path = txt_file_path.replace('-','/')
    
    # Extract and get a handle for val_list from txt_file_path
    val_list = extract_val_list(txt_file_path)
    
    # Convert our val_list tuple of 5 values to a tuple of 2 coordinate values (x,y)
    val_list_xy = [(tup[0],tup[1]) for tup in val_list]
    
    # If the histogram of interest is in the list of paths that are associated with specific red/yellow hit coordinates (hit_n = (x,y,color,occ,hist_path))
    
    
    if list_of_hists_df['paths'].unique()[hist_index] in [tup[5] for tup in val_list]:
        
        # Get a handle for the histogram we are constructing the quality feature for
        tmp = list_of_hists_df[list_of_hists_df['paths']==list_of_hists_df['paths'].unique()[hist_index]]
    else:
        return "Error: the unique histogram chosen as hist_index cannot be found for any of the hist_paths in val_list"
    
    # Get the coordinate conversion dictionary
    cnvrt_dic_x, cnvrt_dic_y = scale_cnvrt_dic(pMain_hist20,hist_index,0), scale_cnvrt_dic(pMain_hist20,hist_index,1)
    
    # Loop through the quality values, if the coordinates match the location of the hit, modify their quality value
    for idx,val in enumerate(tmp['quality'].values):
        
        # If the tuple (x,y) from histogram tmp is in the list of (x,y) tuples from the hit value list (val_list_xy)
        if (cnvrt_dic_x['x_'+str(int(tmp.iloc[idx,1]))],cnvrt_dic_y['y_'+str(int(tmp.iloc[idx,2]))]) in val_list_xy:
            # Set the quality class for this hit (0/1 for green/red, 0/1/2 for green/yellow/red ...for now we just use 0/1)
            tmp.iloc[idx,4] = 1 
    
    # Return the list_of_hists_df whose 'quality' values have been updated
    return tmp

# Example prep_quality_feature
#print(f'Example prep_quality_feature for pMain_hist20 dataframe, hist_index=0, txt_file_path = ... :')
#display(prep_quality_feature(pMain_hist20, 0, "run_348251-CaloMonitoring-ClusterMon-CaloCalTopoClustersNoTrigSel-2d_Rates-m_clus_etaphi_Et_thresh1.txt"))




"""
# Example Contents of txt_file_path, copy and pasted from a select run, pMain stream, a select ftag, and a select histogram:

-this_line_is_reserved_for_the_histogram_path_name- (as it would be called in hist['paths'] for this specific histogram)
NRedBins:	0.0
NYellowBins:	44.0
Y0-(eta,phi)[OSRatio]=(-1.850,1.723)[7.59e+01]:	6829.0
Y1-(eta,phi)[OSRatio]=(1.750,3.101)[6.36e+01]:	6491.0
Y10-(eta,phi)[OSRatio]=(4.650,2.412)[3.66e+01]:	2158.0
Y11-(eta,phi)[OSRatio]=(4.350,2.116)[4.24e+01]:	2100.0
Y12-(eta,phi)[OSRatio]=(4.350,-3.002)[4.13e+01]:	2068.0
Y13-(eta,phi)[OSRatio]=(4.650,2.510)[3.30e+01]:	2047.0
Y14-(eta,phi)[OSRatio]=(4.350,3.101)[4.00e+01]:	2029.0
Y15-(eta,phi)[OSRatio]=(4.350,3.002)[3.81e+01]:	1973.0
Y16-(eta,phi)[OSRatio]=(-4.350,2.116)[3.49e+01]:	1938.0
Y17-(eta,phi)[OSRatio]=(4.650,0.541)[2.81e+01]:	1890.0
Y18-(eta,phi)[OSRatio]=(4.350,-3.101)[3.36e+01]:	1842.0
Y19-(eta,phi)[OSRatio]=(4.550,-1.230)[4.05e+01]:	1833.0
Y2-(eta,phi)[OSRatio]=(4.250,-0.935)[3.18e+01]:	3093.0
Y20-(eta,phi)[OSRatio]=(-4.550,-1.230)[3.65e+01]:	1814.0
Y21-(eta,phi)[OSRatio]=(4.350,-2.116)[3.14e+01]:	1777.0
Y22-(eta,phi)[OSRatio]=(-4.550,1.920)[3.41e+01]:	1746.0
Y23-(eta,phi)[OSRatio]=(4.550,1.132)[3.64e+01]:	1724.0
Y24-(eta,phi)[OSRatio]=(4.550,-1.132)[3.62e+01]:	1718.0
Y25-(eta,phi)[OSRatio]=(4.550,2.018)[3.48e+01]:	1680.0
Y26-(eta,phi)[OSRatio]=(-4.350,-3.002)[2.53e+01]:	1653.0
Y27-(eta,phi)[OSRatio]=(-4.550,2.018)[2.63e+01]:	1528.0
Y28-(eta,phi)[OSRatio]=(4.450,-3.002)[3.06e+01]:	1417.0
Y29-(eta,phi)[OSRatio]=(4.450,2.018)[2.96e+01]:	1392.0
Y3-(eta,phi)[OSRatio]=(-4.250,-0.738)[3.01e+01]:	2965.0
Y30-(eta,phi)[OSRatio]=(-4.450,-3.002)[2.78e+01]:	1392.0
Y31-(eta,phi)[OSRatio]=(4.450,3.002)[2.86e+01]:	1366.0
Y32-(eta,phi)[OSRatio]=(-4.450,2.018)[2.66e+01]:	1360.0
Y33-(eta,phi)[OSRatio]=(-4.750,-2.510)[3.52e+01]:	1012.0
Y34-(eta,phi)[OSRatio]=(4.750,-0.837)[3.42e+01]:	942.0
Y35-(eta,phi)[OSRatio]=(4.750,-2.609)[3.28e+01]:	917.0
Y36-(eta,phi)[OSRatio]=(-4.750,-0.837)[2.84e+01]:	883.0
Y37-(eta,phi)[OSRatio]=(-4.750,-2.412)[2.74e+01]:	864.0
Y38-(eta,phi)[OSRatio]=(-4.750,0.640)[2.56e+01]:	832.0
Y39-(eta,phi)[OSRatio]=(4.750,-0.935)[2.74e+01]:	819.0
Y4-(eta,phi)[OSRatio]=(4.250,0.738)[2.79e+01]:	2930.0
Y40-(eta,phi)[OSRatio]=(4.750,-2.510)[2.60e+01]:	794.0
Y41-(eta,phi)[OSRatio]=(4.250,-0.541)[-2.54e+01]:	693.0
Y42-(eta,phi)[OSRatio]=(-4.250,0.541)[-2.62e+01]:	632.0
Y43-(eta,phi)[OSRatio]=(4.250,0.541)[-2.69e+01]:	631.0
Y5-(eta,phi)[OSRatio]=(4.150,-2.707)[3.37e+01]:	2897.0
Y6-(eta,phi)[OSRatio]=(4.250,-2.116)[2.60e+01]:	2851.0
Y7-(eta,phi)[OSRatio]=(4.150,0.738)[2.78e+01]:	2664.0
Y8-(eta,phi)[OSRatio]=(-4.150,0.837)[2.68e+01]:	2577.0
Y9-(eta,phi)[OSRatio]=(-4.150,0.738)[2.65e+01]:	2564.0
"""

def add_specific_qualityvals_to_hist20s(hist_index,quality_val_txtfile):

    # Get a handle for express_hist20 and drop the index column
    express_hist20 = pd.read_csv(record_path+'express_hist20.csv',index_col=[0])
    
    # IMPORTANT: Do this line only if the previous line reads the df and the df shows a column[0] that shouldnt be there
    # express_hist20 = express_hist20.drop(columns=express_hist20.columns[0])

    # Get a handle for pMain_hist20 and drop the index column
    pMain_hist20 = pd.read_csv(record_path+'pMain_hist20.csv',index_col=[0])
    
    # IMPORTANT!: Do this line only if the previous line reads the df and the df shows a column[0] that shouldnt be there
    # pMain_hist20 = pMain_hist20.drop(columns=pMain_hist20.columns[0])

    # Convert float columns to integers - needed to do this for the big database as well...
    express_hist20['y'] = [int(a) for a in express_hist20['y'].values]
    express_hist20['occ'] = [int(a) for a in express_hist20['occ'].values]

    # Convert float columns to integers - needed to do this for the big database as well...
    pMain_hist20['y'] = [int(a) for a in pMain_hist20['y'].values]
    pMain_hist20['occ'] = [int(a) for a in pMain_hist20['occ'].values]


    # Create the target value for the histogram(s) of interest based on hist index(unique histogram number from a list_of_hists such as pMain_hist20)

    # There has not been any target values extracted from the dqm display in txt_file format for the target values yet, so we comment this line out
    # express_hist20 = prep_quality_feature(express_hist20, 0, "run_348251-CaloMonitoring-ClusterMon-CaloCalTopoClustersNoTrigSel-2d_Rates-m_clus_etaphi_Et_thresh1.txt")

    # Only unique hist value = 0 is present in pMain_hist20, therefore, we only use hist_index 0 in the function
    # This is the single histogram worth of dataponts that need changing

    # Here, hist_index = 0 ...maybe put this in a function later

    # Get a subset that does not include unique()[hist_index] == 0
    tmp = pMain_hist20[pMain_hist20['paths']!=pMain_hist20['paths'].unique()[0]]
    # Prepare the modified quality values
    tmp2 = prep_quality_feature(pMain_hist20, hist_index, quality_val_txtfile)
    # then concatonate the pMain_hist20 with tmp_df
    pMain_hist20 = pd.concat([tmp,tmp2])

    # Now, we just need to do this same thing to add the red/yellow values for THIS m_clus_etaphi_Et_thresh1 hist for the 20 different histograms


    # Save the databases
    express_hist20.to_csv(record_path+'express_hist20.csv')
    pMain_hist20.to_csv(record_path+'pMain_hist20.csv')

    # Databases must be kept separate to properly construct matrices!
    # DO NOT DO THIS - express_pMain_hist20 = pd.concat([express_hist20,pMain_hist20])

    # Free up Memory
    del express_hist20
    del pMain_hist20



def load_hist20_dataset_matrices():
    """
    Assuming express_hist20.csv and pMain_hist20.csv have been constructed from ReplicasProcessingScript.py,  this function will
    load and construct the training and target matrices for the CNN.
    
    IMPORTANT NOTE: We don't actually need to keep track of the runs that we train the model with because its just going to be used for future predictions over histograms whose run
    numbers we WILL know. Therefore, it is not necessary to keep track of this.
    """
    
    # Load the datasets
    express_hist20 = pd.read_csv(record_path+'express_hist20.csv',index_col=[0])
    pMain_hist20 = pd.read_csv(record_path+'pMain_hist20.csv',index_col=[0])
    
    # Initialize the feature_set that will contain our feature variable matrices
    feature_set = []
    
        # Initialize the target_set that will contain our target variable matrices
    target_set = []
    
    # These are our taret_set feature Matrices for this hist20 dataset - specifically for the express stream
    for idH,hist in enumerate(express_hist20['paths'].unique()):
        df_tmp = express_hist20[express_hist20['paths']==hist]
        feature_set.append(df_tmp.pivot(index='y',columns='x',values='occ').to_numpy())
        target_set.append(df_tmp.pivot(index='y',columns='x',values='quality').to_numpy())
    
    # These are our target_set feature Matrices for this hist20 dataset - specifically for the pMain stream
    for idH,hist in enumerate(pMain_hist20['paths'].unique()):
        df_tmp = pMain_hist20[pMain_hist20['paths']==hist]
        feature_set.append(df_tmp.pivot(index='y',columns='x',values='occ').to_numpy())
        target_set.append(df_tmp.pivot(index='y',columns='x',values='quality').to_numpy())
    
    # returns dataset
    return np.stack([np.array(feature_set),np.array(target_set)])



def split_hist20(dataset,train_size):
    """
    Takes the dataset that we constructed from the previous assumptions, reads it in as a (2(features,targets),histograms,eta,phi)  shaped tensor,
    randomizes the histograms in the dataset so they arent organized by any sort of run number, then splits them into their respective training and testing sets.
    
    EXAMPLE USE:
    # train_set,test_set = split_hist20(load_hist20_dataset_matrices(),0.7)
    
    TO VERIFY THAT FUNCTION WORKS AS SHOULD:
    # Make sure everything looks as it should
    # display(train_set.shape)
    # display(test_set.shape)
    # print(round(100*train_set[0].shape[0]/round(load_hist20_dataset_matrices()[0].shape[0])),'%\n')
    # print(round(100*test_set[0].shape[0]/round(load_hist20_dataset_matrices()[1].shape[0])),'%')
    """
    
    # Initialize the list that will store the random indexes
    ri_list = []

    # Loop through the number of matrices
    for i in range(dataset[0].shape[0]):

        # Get a random index
        ri = np.random.randint(dataset[0].shape[0])

        # While that integer is in the random integer list, keep looking for a random integer that isnt in there
        while ri in ri_list:
            ri = np.random.randint(dataset[0].shape[0])

        # Then append that random integer to the list
        ri_list.append(ri) 

    # Construct the training and testing matrix index list
    train_set_index = ri_list[0:round(train_size*dataset[0].shape[0])]
    test_set_index = ri_list[round(train_size*dataset[0].shape[0]):dataset[0].shape[0]]
    
    # Construct the set of matrixes from the matrix index lists
    train_set = np.stack([np.array([matrix for matrix in dataset[0][train_set_index]]),np.array([matrix for matrix in dataset[1][train_set_index]])])
    test_set = np.stack([np.array([matrix for matrix in dataset[0][test_set_index]]),np.array([matrix for matrix in dataset[1][test_set_index]])])

    return train_set, test_set
    
    
def save_traintest_sets(train_set,test_set):

    # Open a file to store the numpy matrix in
    with open('train_set.npy', 'wb') as f:

        # Save the matrix
        np.save(f, train_set)

    # Open a file to store the numpy matrix in
    with open('test_set.npy', 'wb') as f:

        # Save the matrix
        np.save(f, test_set)


def load_saved_traintest_set(train_set_filename, test_set_filename):

    """
    EXAMPLE USE:
    train_set,test_set = load_saved_traintest_set('train_set.npy','test_set.npy')
    """

    # NOTE: to read the data back from the files...

    # Open the file that train_set is stored in as f
    with open('train_set.npy', 'rb') as f:

        # Load and get a handle for train_set
        train_set = np.load(f)

    # Open the file that train_set is stored in as f
    with open(test_set_filename, 'rb') as f:

        # Load and get a handle for test_set
        test_set = np.load(f)
        
    return train_set,test_set


def build_qualityvals_for_hist20s(hist_idx,txt_file_pth,hist20_as_db):
    """
    Builds the qualityvals from txt_file_pth whose hist_index is hist_idx, and the hist20 is hist20_as_db or just db
    
    Select the id value for the histogram that we are updating the target values
    hist_idx = 0

    Set the string value for the path to the text file for the histogram we are updating
    txt_file_pth = ""
    """

    # Set the database we are updating the target values to
    # db = express_hist20
    db = hist20_as_db


    # Get a subset that does not include unique()[hist_index] == 0
    tmp = db[db['paths']!=db['paths'].unique()[0]]
    
    # Prepare the modified quality values
    tmp2 = prep_quality_feature(db, hist_idx, txt_file_pth)
    
    # then concatonate the pMain_hist20 with tmp_df
    pMain_hist20 = pd.concat([tmp,tmp2])

    # Save the databases
    express_hist20.to_csv(record_path+'express_hist20.csv')
    pMain_hist20.to_csv(record_path+'pMain_hist20.csv')

    print("Complete.")