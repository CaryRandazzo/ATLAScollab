#!/usr/bin/env python
# coding: utf-8

# Prior to running this script, generate anomalies in the dataset IF this dataset will be the "noisy" dataset. Otherwise this script should be run after the original dataset is cleaned (in our case duplicates were removed). Also, there is a separate notebook that uses this same script for the non noisy dataset. This script is specifically for normalizing the noisy dataset.

# 1. Imports

# In[1]:


from replica_processor import *


# 2. Load data to construct normalization features

# In[2]:


df = pd.read_csv('anomalous_dfs2.csv', dtype={'x':'int8','y':'int8','ftag_id':'int8','occ':'float32','hist_type':'int8','hist_id':'int16'})
df


# 3. Initialize normalization features in dataframe

# In[3]:


df['occ_0to1'] = [0]*df.shape[0]
df['occ_zscore'] = [0]*df.shape[0]
df['occ_robust'] = [0]*df.shape[0]


# 4. Turn off unnecessary warning option

# In[4]:


pd.options.mode.chained_assignment = None  # default='warn'


# 5. Normalize occupancy by histogram
# - minmax
# - zscore
# - robust

# In[5]:


# Slow process because the pointwise calculation of minmax goes through a for loop

# In the event of rerunning this script, if output_df is already in memory it will cause issues, remove it
try:
    del output_df
except:
    pass

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
        print(hid)\
        
        # Set the subset of tmp whose hist_id is hid to tmp2
        mask2 = tmp['hist_id'] == hid
        tmp2 = tmp.loc[mask2,:]

        # Calculate the normalization features and store them in their respective columns
        # MinMax scaling, not using standard deviation
        if tmp2['occ'].max() == tmp2['occ'].min():
            tmp2['occ_0to1'] = tmp2['occ']
            tmp2['occ_0to1'] = ( tmp2['occ']-tmp2['occ'].min() )/( tmp2['occ'].max()-tmp2['occ'].min() )
            
        # Zscore normalization
        tmp2['occ_zscore'] = ( tmp['occ']-tmp['occ'].mean() ) / tmp['occ'].std()
        
        # Robust nor\alization
        q75,q25 = np.percentile(tmp2['occ'],[75,25])
        iqr = q75-q25
        tmp2['occ_robust'] = ( tmp2['occ']-tmp2['occ'].median() )/iqr

        # Record the subset of datapoints whose normalized occupancies have been calculated into the main dataframe 
        df.loc[tmp2.index,:] = tmp2


# 6. Some Exploratory Analysis test to make sure it worked:

# In[6]:


# Looks good so far
df


# In[7]:


# Get a histogram subset to view some specifics
test = df[df['ftag_id']==0]
test = test[test['hist_id']==0]
sns.heatmap( test.pivot_table(index='y',columns='x',values='occ') )
test.head()


# In[8]:


test.describe()


# In[14]:


test = test[test['x']==48]
test


# In[15]:


plt.hist(test['occ'],bins=100);


# In[16]:


plt.hist(test['occ_zscore'], bins=100);


# In[17]:


plt.hist(test['occ_robust'], bins=100);


# In[18]:


plt.hist(test['occ_0to1'], bins=100);


# In[19]:


# What kind of values does the zscore feature have
test['occ_zscore'].value_counts()


# In[20]:


# What kind of values does the robust feature have?
test['occ_robust'].value_counts()


# In[21]:


# What kind of values does the 0to1 feature have?
test['occ_0to1'].value_counts()


# In[22]:


# A deeper look at the values in 0to1 since the vast majority are 0's
test[test['occ_0to1']!=0]


# 7. Save the updated dataframe now containing both anomalous data and data normalized on occupancy on a histogram per histogram basis
# - For EDA, consider looking at the distributions of occupancies of different histograms and different norm features

# In[24]:


df.info()


# In[26]:


df['occ_0to1'] = df['occ_0to1'].astype('float32')
df['occ_zscore'] = df['occ_zscore'].astype('float32')
df['occ_robust'] = df['occ_robust'].astype('float32')
df['quality'] = df['quality'].astype('int8')
df.info()


# In[9]:


# Save the results
df.to_csv('normed_anoms2.csv',index=False)


# In[ ]:


# To load, use the following
df = pd.read_csv('normed_anoms2.csv', dtype={'x':'int8','y':'int8','ftag_id':'int8','occ':'float32','hist_type':'int8','hist_id':'int16','quality':'int8','occ_0to1':'float32','occ_zscore':'float32','occ_robust':'float32'})
df


# This anomaly dataset can now be moved to the splitting script
