# functions.py
import ROOT
import pandas as pd

######################
#PROCESSING FUNCTIONS#
######################

#PREPROCESS THE HIST TO A DATAFRAME
def processHistML(tf,file,f_path,f_path_list, binNums,binNumsY, occupancies):  
    #main loop
    for key in tf.GetListOfKeys():    
        input = key.ReadObj()

        #determine if the location in the file we are at is a directory
        if issubclass(type(input),ROOT.TDirectoryFile):
           
            #record the path of the directory we are looking in
            try:
                f_path = input.GetPath() 
            except:
                print("cant GetPath")

            #split the path by '/' so we can determine where we are in the folder structure        
            try:
                split_path = f_path.split("/")
            except:
                print('cant split_path')            
            
            
            #recursively go deeper into the file structure depending on the length of split_path
#             if len(split_path) == 3:
            if 'run' in split_path[-1]:
                #we are 2 directories deep, go deeper
                f_path,f_path_list, binNums,binNumsY, occupancies = processHistML(input,file,f_path, f_path_list, binNums,binNumsY, occupancies)  
            elif len(split_path) > 3 and any(folder in split_path for folder in ('CaloMonitoring', 'Jets','MissingEt','Tau','egamma')):                
                #we are greater than 3 directories deep and these directories include the specified folders above, goo deeper
                f_path, f_path_list, binNums,binNumsY, occupancies = processHistML(input,file,f_path, f_path_list, binNums,binNumsY, occupancies)     
            else:
                pass
            
            #record the file_path that will result now that we are done with the current folder level
            #i.e. the folder path that results from going up a level in the directory
            f_path = f_path.split('/')
            f_path = '/'.join(f_path[:-1])
                
        elif issubclass(type(input), ROOT.TProfile):
            
            #record te path of the directory we are looking in with the name of the hist file as part of the path
            try:
                f_path_tp = f_path + '/' + input.GetName()                
            except:
                print("cant GetPath3")
            
            #get the part of f_path that follows the ':'
            f_path_tp = f_path_tp.split(':')
            f_path_tp = f_path_tp[1][1:]
            
            
            hist_file = file.Get(f_path_tp)
            binsX = hist_file.GetNbinsX()                                    
            
            #setup the 3 arrays for creating the dataframe
            for binX in range(binsX+1):
                f_path_list.append(f_path_tp)
                binNum = hist_file.GetBin(binX)
                binNums.append(binX)
                binNumsY.append(None)
                occupancies.append(hist_file.GetBinContent(binNum))                        
            
        elif issubclass(type(input),ROOT.TH2):

            #record the path of the directory we are looking in with the name of the hist file as part of the path
            try:
                f_path_th2 = f_path + '/' + input.GetName()                
            except:
                print("cant GetPath3")
            
            #get the part of f_path that follows the ':'
            f_path_th2 = f_path_th2.split(':')
            f_path_th2 = f_path_th2[1][1:]
            
            
            hist_file = file.Get(f_path_th2)
            binsX = hist_file.GetNbinsX()                        
            binsY = hist_file.GetNbinsY()
            
            #setup the 3 arrays for creating the dataframe
            for binX in range(binsX+1):
                for binY in range(binsY+1):
                    f_path_list.append(f_path_th2)
                    binNumXY = hist_file.GetBin(binX,binY)
                    binNums.append(binX)
                    binNumsY.append(binY)
                    occupancies.append(hist_file.GetBinContent(binNumXY))            
                
        elif issubclass(type(input),ROOT.TH1):
            
            #record the path of the directory we are looking in with the name of the hist file as part of the path
            try:
                f_path_th1 = f_path + '/' + input.GetName()                
            except:
                print("cant GetPath2")

            #get the part of f_path that follows the ':'
            f_path_th1 = f_path_th1.split(':')
            f_path_th1 = f_path_th1[1][1:]
            
            
            hist_file = file.Get(f_path_th1)
            binsX = hist_file.GetNbinsX()            
            
            #setup the 3 arrays for creating the dataframe
            for binX in range(binsX+1):                
                f_path_list.append(f_path_th1)
                binNum = hist_file.GetBin(binX,0)                
                binNums.append(binNum)
                binNumsY.append(None)                
                occupancies.append(hist_file.GetBinContent(binNum))
    
    return f_path, f_path_list, binNums,binNumsY, occupancies


#CONVERT HIST TO DATAFRAME
def hist_to_df(path):
    file = ROOT.TFile.Open(path)

    f_path,f_path_list, binNums,binNumsY, occupancies = processHistML(file,file,'',[],[],[],[])
    
    return pd.DataFrame({'paths':f_path_list,'x':binNums,'y':binNumsY,'occ':occupancies})


#ADD ANOTHER HIST TO DATAFRAME
def select_add_hist(df,choice):
    
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

#UNSUPERVISED LEARNING
def train_ae(df):
    
    Z = df[['x','occ']]

    #set parameters
    outliers_fraction = 0.05 #outliers_fraction = 0.003

    #train the ML algorithm
    clf = AutoEncoder(hidden_neurons =[3,2,1,2,3], contamination = outliers_fraction, epochs=500)
    clf.fit(Z)
    predictions = clf.labels_  # binary labels (0: inliers, 1: outliers)
    scores = clf.decision_scores_  # raw outlier scores
    #########################
    try:
        df = df.drop('outlier',1)
    except:
        print("")

    #########################
    df['outlier'] = predictions
    #########################
    color = np.where(df['outlier'] == 1, 'red', 'black')
    #########################
    return clf, predictions, scores,color


# def process_ae_TH1(df_train,choice):
    """
    df is a dataframe
    choice is a number from 1 to len(df['paths'].values)
    """
    
    #select the histogram of choice
    #df_train = df[df['paths']==df['paths'].unique()[choice]]
    #what histogram are we working on?
    print(f"Histogram in training:{df_train['paths'].values[0]}")
    
    #train and prepare the auto encoder
    c,p,s,color = ae(df_train)
    
    #get a standard plot of the histograms distribution value
    df_train.plot.scatter('x','occ')
    
    #produce a plot of the auto encoders outlier values labelled in red
    fig = plt.figure(figsize=(10,10))
    plt.scatter(df_train['x'], df_train['occ'], c=color, s=60)
    plt.xlabel('eta')
    plt.ylabel('occupancy')
    plt.show()
    
    
def display_hists_in_dataset(df):
    
    """
    
    Displays histograms in a dataframe that contains multiple subsets based on a path feature.
    
    EXAMPLE USE:
    Use the database of dataframes called express_hists_totrain.csv ; This is constructed from the function read_process_hist_paths_file(express_db_df,txt_file_path)
    
    display_hists_in_dataset(express_hists_totrain)

    """
    
    for path in df['paths'].unique():
        tmp = df[df['paths']==path]
        ax = sns.heatmap(tmp.pivot(index='y',columns='x',values='occ'))
        ax.invert_yaxis()
        plt.title( f" { path.split('/')[0] } , { path.split('/')[-1] } [Occupancies]" )
        plt.xlabel(r'$\eta$')
        plt.ylabel(r'$\phi$')
        plt.show()
    del tmp
