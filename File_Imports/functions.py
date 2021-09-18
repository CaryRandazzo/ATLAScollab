# functions.py


###########
# IMPORTS #
###########


from default_imports import *


######################
#PROCESSING FUNCTIONS#
######################



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


############################
#MACHINE LEARNING FUNCTIONS#
############################


# UNSUPERVISED LEARNING

def train_ae(df):
    
    """
    
    Auto Encoder Neural Network via pyod to be trained with the histogram dataframe generated from hist_to_df().
    
    """
    
    Z = df[['x','occ']]

    # Set parameters
    outliers_fraction = 0.05 #outliers_fraction = 0.003

    # Train the ML algorithm
    clf = AutoEncoder(hidden_neurons =[3,2,1,2,3], contamination = outliers_fraction, epochs=500)
    clf.fit(Z)
    predictions = clf.labels_  # binary labels (0: inliers, 1: outliers)
    scores = clf.decision_scores_  # raw outlier scores
    
    # Remove the previously identified outlier column from this dataframe if it was constructed previously using this function.
    try:
        df = df.drop('outlier',1)
    except:
        pass

    # Construct the outlier column based on the predictions determined by the AutoEncoder
    df['outlier'] = predictions
    
    # Construct the color array based on the outlier values in the outlier column of the dataframe
    color = np.where(df['outlier'] == 1, 'red', 'black')
    
    # Return the model, predictions, outlier scores, and outlier colors
    return clf, predictions, scores,color


def process_ae_TH1(df_train,choice):
    
    """
    
    df is a dataframe.
    choice is a number from 1 to len(df['paths'].values).
    
    """
    
    # Select the histogram of interest as choice
    df_train = df[df['paths']==df['paths'].unique()[choice]]
    
    # Display what histogram we are training
    print(f"Histogram in training:{df_train['paths'].values[choice]}")
    
    # Generate the information of interest form the ae() function
    c,p,s,color = ae(df_train)
    
    # Get a standard plot of the histograms distribution value
    plt.figure(figsize=(10,10)
    df_train.plot.scatter('x','occ')
    
    # Produce a plot of the auto encoders outlier values labelled in red
    fig = plt.figure(figsize=(10,10))
    plt.scatter(df_train['x'], df_train['occ'], c=color, s=60)
    plt.xlabel('eta')
    plt.ylabel('occupancy')
    plt.show()

    
###########################
# VISUALIZATION FUNCTIONS #
###########################

    
def display_hists_in_dataset(df):
    
    """
    
    Displays histograms in a dataframe that contains multiple subsets based on a path feature.

    EXAMPLE USE:
        Use the database of dataframes called express_hists_totrain.csv ; This is constructed from the function read_process_hist_paths_file(express_db_df,txt_file_path)
    
        display_hists_in_dataset(express_hists_totrain)
    
    """
    
    # Loop through the paths available in the database of histograms
    for idP,path in enumerate(df['paths'].unique()):
        
        # get a handle for the histogram at this iteration
        tmp = df[df['paths']==path]
        
        # Prepare the heatmap and piivot table for the plot
        ax = sns.heatmap(tmp.pivot(index='y',columns='x',values='occ'))
        
        # Invert the yaxis on the plot so it is ascending upward
        ax.invert_yaxis()
        
        # Set the information on the histogram for title and labels
        plt.title( f"#{idP} { path.split('/')[0] } , { path.split('/')[-1] } [Occupancies]" )
        plt.xlabel(r'$\eta$')
        plt.ylabel(r'$\phi$')
        
        # Show the histogram that has been constructed at this iteration
        plt.show()
        
    # Cleanup variables after processing this function
    del tmp
    del ax
    del idP
    del path
    
    
###################
# OTHER FUNCTIONS #
###################

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
