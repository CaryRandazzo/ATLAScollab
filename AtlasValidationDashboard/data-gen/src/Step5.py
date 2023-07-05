#!/usr/bin/env python
# coding: utf-8

# Prior to running this script (specifically for the non noisy / non anomalous dataset), clean the main dataset (in our case the duplicates were removed prior to running this script). Once that has been done, this script can be run to create the normalized non noisy dataset that will need to be split.


from utilities import *



df = pd.read_csv('main_dfs.csv', dtype={'x':'int8','y':'int8','ftag_id':'int8','occ':'float32','hist_type':'int8','hist_id':'int16'})
df



df['occ_0to1'] = [0]*df.shape[0]
df['occ_zscore'] = [0]*df.shape[0]
df['occ_robust'] = [0]*df.shape[0]
df



pd.options.mode.chained_assignment = None  # default='warn'



# Slow process because the pointwise calculation of minmax goes through a for loop

# Loop through ftags in df
for idf,ftid in enumerate(df['ftag_id'].unique()):
    
    # Progress update for current ftag processing..
    progress_bar(idf,df['ftag_id'].unique())
    
    # Set the subset of df whose ftag_id is ftid to tmp
    mask1 = df['ftag_id'] == ftid
    tmp = df.loc[mask1,:]
    
    # Loop through hists for the current ftag
    for hid in tmp['hist_id'].unique():
        
        # Progress update of histogram currently in process..
        print(hid)
        
        # Set the subset of tmp whose hist_id is hid to tmp2
        mask2 = tmp['hist_id'] == hid
        tmp2 = tmp.loc[mask2,:]

        # Calculate the normalization features and store them in their respective columns
        # MinMax scaling, not using standard deviation
        tmp2['occ_0to1'] = ( tmp2['occ']-tmp2['occ'].min() )/( tmp2['occ'].max()-tmp2['occ'].min() )
        
        # Zscore normalization
        tmp2['occ_zscore'] = ( tmp['occ']-tmp['occ'].mean() ) / tmp['occ'].std()
        
        # Robust normalization
        q75,q25 = np.percentile(tmp2['occ'],[75,25])
        iqr = q75-q25
        tmp2['occ_robust'] = ( tmp2['occ']-tmp2['occ'].median() )/iqr

        # Record the subset of datapoints whose normalized occupancies have been calculated into the main dataframe 
        df.loc[tmp2.index,:] = tmp2



# Looks good so far
df



# Get a histogram subset to view some specifics
test = df[df['ftag_id']==0]
test = test[test['hist_id']==0]
sns.heatmap( test.pivot_table(index='y',columns='x',values='occ') )
test.head()



# display(test.describe())
# display(sns.displot(test['occ']))
# display(sns.displot(test['occ_zscore']))
# display(sns.displot(test['occ_robust']))
# display(sns.displot(test['occ_0to1']))
# test = test[test['x']==48]
# display(test)
# display(plt.hist(test['occ'],bins=100))
# display(plt.hist(test['occ_zscore'], bins=100))
# display(plt.hist(test['occ_robust'], bins=100))
# display(plt.hist(test['occ_0to1'], bins=100))
# # What kind of values does the zscore feature have
# display(test['occ_zscore'].value_counts())
# # What kind of values does the robust feature have?
# display(test['occ_robust'].value_counts())
# # What kind of values does the 0to1 feature have?
# display(test['occ_0to1'].value_counts())



df['quality'] = 0
df



df['occ_0to1'] = df['occ_0to1'].astype('float32')
df['occ_zscore'] = df['occ_zscore'].astype('float32')
df['occ_robust'] = df['occ_robust'].astype('float32')
df['quality'] = df['quality'].astype('int8')
df.info()



# Save the results
df.to_csv('normed_nonanoms.csv',index=False)



# To load, use the following
df = pd.read_csv('normed_nonanoms.csv', dtype={'x':'int8','y':'int8','ftag_id':'int8','occ':'float32','hist_type':'int8','hist_id':'int16','quality':'int8','occ_0to1':'float32','occ_zscore':'float32','occ_robust':'float32'})
df


# Now, no further processing needed for these ,split them into x_train_nonnoisy_df and x_test_nonnoisy_df using non noisy split script
