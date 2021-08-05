#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#############
###IMPORTS###
#############

import ROOT
# from IPython.display import clear_output
import pandas as pd

###############
###FUNCTIONS###
###############

def validate_uw_hists(tf,file,f_path,f_path_list, binNums,binNumsY, occupancies):  
    """
    
    EXAMPLE USE:
    
    # set the path of the histogram to convert to dataframe
    path = '../../../../../eos/atlas/atlascerngroupdisk/data-dqm/references/data18_13TeV.00358031.physics_Main.merge.HIST.f961_h322._0001.1'
    
    # set file as the opened root tfile
    file = ROOT.TFile.Open(path)
    
    # get the proper output variables from and call validate_uw_hists with the correct inputs
    f_path,f_path_list, binNums,binNumsY, occupancies = validate_uw_hists(file,file,'',[],[],[],[])
    
    # construct the dataframe from the previous outputs
    df = pd.DataFrame({'paths':f_path_list,'x':binNums,'y':binNumsY,'occ':occupancies})
    
    # display the dataframe
    display(df)
    
    """
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
#             print(split_path)
#             print(len(split_path)) # this number goes in the conditions below
            if len(split_path) <= 12:
                #we are 2 directories deep, go deeper
                f_path,f_path_list, binNums,binNumsY, occupancies = validate_uw_hists(input,file,f_path, f_path_list, binNums,binNumsY, occupancies)  
            elif len(split_path) > 12 and any(folder in split_path for folder in ('CaloMonitoring', 'Jets','MissingEt','Tau','egamma')):                
                #we are greater than 3 directories deep and these directories include the specified folders above, goo deeper
                f_path, f_path_list, binNums,binNumsY, occupancies = validate_uw_hists(input,file,f_path, f_path_list, binNums,binNumsY, occupancies)     
            else:
                pass
            
            #record the file_path that will result now that we are done with the current folder level
            #i.e. the folder path that results from going up a level in the directory
            f_path = f_path.split('/')
            f_path = '/'.join(f_path[:-1])
                
        elif issubclass(type(input), ROOT.TProfile):
            #record the path of the directory we are looking in with the name of the hist file as part of the path
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

