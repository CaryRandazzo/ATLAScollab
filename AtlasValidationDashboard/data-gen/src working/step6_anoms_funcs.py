from replica_processor import *
import random

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