#!/usr/bin/env python
# coding: utf-8

# Note: This script should process the main dataset after the normalization script runs over it. This is roughly the final step before converting the datasets into numpy arrays (or using them as dataframes as is if keras takes dataframes as input) for modelling.

# 1. Imports


from utilities import *


# 2. Load the main dataset

df = pd.read_csv('normed_nonanoms.csv', dtype={'x':'int8','y':'int8','ftag_id':'int8','occ':'float32','hist_type':'int8','hist_id':'int16','quality':'int8','occ_0to1':'float32','occ_zscore':'float32','occ_robust':'float32'})
df


# 3. Define the processing function 


def full_hist_split(main_dfs,train_set_pct):
    """
    On about 27million datapoints, took only 6-7mins
    
    Example Use:
        x_train,x_test = full_hist_split(main_dfs,.67)
    """
    
    try:
        del x_train_df
        del x_test_df
    except:
        pass

    for idf,ftid in enumerate(main_dfs['ftag_id'].unique()):

        # Progress
        progress_bar(idf,main_dfs['ftag_id'].unique())

        # Initialize randomized hist index lists
        rand_train_list = []
        rand_test_list = []

        print('setting up mask1 datapoints...')
        mask1 = main_dfs['ftag_id'] == ftid
        tmp = main_dfs.loc[mask1,:]

        # Gen rand_train_list for train_set
        print('generating rand_list...')
        while len(rand_train_list) < round(train_set_pct*len(tmp['hist_id'].unique())):
            rand_num = random.randint(0,len(tmp['hist_id'].unique())-1)
            if rand_num in rand_train_list:
                continue
            rand_train_list.append(rand_num)

        # Gen rand_test_list for train_set
        while len(rand_test_list) < round((1-train_set_pct)*len(tmp['hist_id'].unique())):
            rand_num = random.randint(0,len(tmp['hist_id'].unique())-1)
            if rand_num in rand_train_list or rand_num in rand_test_list:
                continue
            rand_test_list.append(rand_num)

        # Build the training set
        
        print('setting up mask2 datapoints...')
        mask2 = tmp['hist_id'].isin(rand_train_list)
        tmp2 = tmp.loc[mask2,:]
        
        print('updating dataframe...')
        try:
            x_train_df = pd.concat([x_train_df,tmp2])
        except:
            x_train_df = tmp2

        # Build the test set
        
        print('setting up mask2 datapoints...')
        mask2 = tmp['hist_id'].isin(rand_test_list)
        tmp2 = tmp.loc[mask2,:]
        
        print('updating dataframe...')
        try:
            x_test_df = pd.concat([x_test_df,tmp2])
        except:
            x_test_df = tmp2
            
    return x_train_df, x_test_df


# 4. split the hists with the function and set parameters

x_train_noanom_df,x_test_noanom_df = full_hist_split(df,.67)


# 5. View and verify the result

x_train_noanom_df['quality'].value_counts()



x_test_noanom_df['quality'].value_counts()



tmp = x_train_noanom_df[x_train_noanom_df['quality']==1]
tmp = tmp[tmp['ftag_id']==7]
tmp = tmp[tmp['hist_id']==2]
tmp



# How many histograms do we have that are invalid (all occ values are 0)
cnt=0
for ftag in x_train_noanom_df['ftag_id'].unique():
    tmp = x_train_noanom_df[x_train_noanom_df['ftag_id']==ftag]
    for histid in x_train_noanom_df[x_train_noanom_df['ftag_id']==ftag]['hist_id'].unique():
        tmp2 = tmp[tmp['hist_id']==histid]
        if len(tmp2['occ'].value_counts().values)==1:
            cnt+=1
#             print(ftag,histid)
#             input_heatmap(x_train_noanom_df,ftag,histid)
#             plt.show()
cnt



# How many histograms do we have that are invalid (all occ values are 0) for the test set
cnt=0
for ftag in x_test_noanom_df['ftag_id'].unique():
    tmp = x_test_noanom_df[x_test_noanom_df['ftag_id']==ftag]
    for histid in x_test_noanom_df[x_test_noanom_df['ftag_id']==ftag]['hist_id'].unique():
        tmp2 = tmp[tmp['hist_id']==histid]
        if len(tmp2['occ'].value_counts().values)==1:
            cnt+=1
#             print(ftag,histid)
#             input_heatmap(x_train_noanom_df,ftag,histid)
#             plt.show()
cnt



# How many histograms total do we have in this dataset
cnt=0
for ftag in df['ftag_id'].unique():
    tmp = df[df['ftag_id']==ftag]
    for histid in tmp[tmp['ftag_id']==ftag]['hist_id'].unique():
        tmp2 = tmp[tmp['hist_id']==histid]
        cnt+=1
cnt



def input_heatmap(df,ftag_id,hist_id):
    tmp = df[df['ftag_id']==ftag_id]
    tmp = tmp[tmp['hist_id']==hist_id]
    sns.heatmap( tmp.pivot_table(index='y',columns='x',values='occ') )



# This is the monitoring histogram in its unaltered form (non noisy, no generated anomalous data)
input_heatmap(x_test_noanom_df,0,1)


# 6. Save results

x_train_noanom_df.to_csv('x_train_noanom_df.csv',index=False)
x_test_noanom_df.to_csv('x_test_noanom_df.csv',index=False)
