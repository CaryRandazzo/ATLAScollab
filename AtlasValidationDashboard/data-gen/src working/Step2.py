#!/usr/bin/env python
# coding: utf-8

# This is the script that should be run after constructing the main dataset to further clean the dataset of internal defects.

# In[1]:


from replica_processor import *


# ### Script to fix duplicate values

# In[2]:


dfs = pd.read_csv('dfs.csv', dtype={'x':'int8','y':'int8','ftag_id':'int8','occ':'float32','hist_type':'int8','hist_id':'int16'})


# Determine and store a list of ftag_ids that contain duplicate data points to clean

# In[4]:


# Initialize the list that will contain the reduced list of offended ftags that contain duplicate datapoints
tags_to_clean = []

# Loop through ftags in the dataset
for ftag in dfs['ftag_id'].unique():
    
    # Get a handle for that ftag subset
    tmp = dfs[dfs['ftag_id']==ftag]
    
    # Loop through the histogram's datapoints in that ftag
    for hist in tmp['hist_id'].unique():
        
        # Get a handle for that histogram's datapoints in that ftag
        tmp2 = tmp[tmp['hist_id']==hist]
        
        # Determine how many sets of extra datapoints there are per histogram (1.0 implies double the datapoints, 2 implies triple, etc.)
        val = tmp2.shape[0]/6435-1
        
        # If there are duplicate datapoints
        if val>0:
            # Display the information relevant to those duplicate datapoints such as the ftag they come from, histid they come from, # datapoints, and #sets of extra datapoints
            print(ftag,hist,tmp2.shape[0],tmp2.shape[0]/6435-1)
            
            # If this ftag has not been found to previously have duplicate data points, add that ftag to the list of ftags to clean for the next step
            if ftag not in tags_to_clean:
                tags_to_clean.append(ftag)

# Display the ftags that have been found to need duplicate data point removal
display(tags_to_clean);


# How many histograms are there in each ftag_id that contains duplicates - in case we are interested

# In[5]:


for ftag in dfs['ftag_id'].unique():
    tmp = dfs[dfs['ftag_id']==ftag]
    if ftag in tags_to_clean:
        print(ftag,tmp['hist_id'].max()+1)


# Drop the duplicate data points from the offending ftag_ids

# In[6]:


# Delete clean_dfs if it already exists
try:
    del clean_dfs
except:
    pass


# loop through ftags
for idf,ftag in enumerate(range(dfs['ftag_id'].max()+1)):
    
    # Display the ftag thats processing
    print('ftag:',ftag)
    
    # Skip ftags we aren't cleaning
    if ftag not in tags_to_clean:
        continue
        
    # Display the progress to completing this ftag to process
    progress_bar(idf,range(dfs['ftag_id'].max()+1))
    
    # Get a handle for the ftag we are cleaning
    tmp = dfs[dfs['ftag_id']==ftag]
    
    # Loop through hists
    for idh,hist_id in enumerate(range(tmp['hist_id'].max()+1)):
        
        # Display which histogram is processing
        print(idh,'of',len(range(tmp['hist_id'].max()+1)))
        
        # Get a handle for the histogram we are cleaning
        tmp2 = tmp[tmp['hist_id']==hist_id]
        
        # Loop through the x coords, this will give us access to the subset of ftag|hist|x vals where there are
        # 130 datapoints when there should be 65, drop duplicates effectively removes the problem in each subset
        for xcoord in range(99):
            # Get a handle for the strip to clean in the histogram
            tmp3 = tmp2[tmp2['x']==xcoord]
            
            # Drop the duplicates in that strip for each duplicate y value
            tmp3 = tmp3.drop_duplicates(subset='y')
            
            # Move the cleaned values to their own dataframe
            try: # If the dataframe exists, add the new values to it
                clean_dfs = pd.concat([clean_dfs,tmp3])
            except: # If not, initialize the dataframe with the first values
                clean_dfs = tmp3

# This process takes long enough where we want to dump the data to a csv file right after in case we cant be
# present to immediately save it
clean_dfs.to_csv('clean_dfs.csv', index=False)


# The clean_dfs dataframe only contains the histograms in the ftags listed in tags_to_clean. We now collect the hists from the non cleaned ftags and combine them together for the final cleaned dataset.

# In[10]:


for idf,ftag in enumerate(dfs['ftag_id'].unique()):
    
    progress_bar(idf,dfs['ftag_id'].unique())
    print('ftag:',ftag)
    
    if ftag in tags_to_clean:
        continue
        
    tmp = dfs[dfs['ftag_id']==ftag]
    
    try:
        non_cleaned_df = pd.concat([non_cleaned_df,tmp])
    except:
        non_cleaned_df = tmp


# combine the cleaned and not cleaned ftag datapoints together to create the duplicate cleaned dataset - main_dfs

# In[14]:


main_dfs = pd.concat([non_cleaned_df,clean_dfs])


# In[15]:


main_dfs.shape #should be near 44 million (#hists*65*99)


# In[16]:


main_dfs.to_csv('main_dfs.csv',index=False)


# In[17]:


main_dfs


# We can now move to the script that will generate the anomalies in the noisy dataset or go straight to the normalization script to generate the non noisy dataset.
