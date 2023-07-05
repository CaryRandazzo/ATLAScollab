#!/usr/bin/env python
# coding: utf-8

# While it would be faster to generate handle the non anomalous 'occ' data and 'occ_generated_anomalies' columns in the same dataset, some extra code would have to be added in this script, as well as in the normalization script to generate unique normalization columns (occ_0to1_anomalous,occ_zscore_anomalous,etc).

# 1. Imports

# In[1]:


from replica_processor import *
import random

# Turn off chained assignment message
pd.options.mode.chained_assignment = None  # default='warn'


# 2. Load main dataframe

# In[2]:


df = dfs = pd.read_csv('main_dfs.csv', dtype={'x':'int8','y':'int8','ftag_id':'int8','occ':'float32','hist_type':'int8','hist_id':'int16'})
df


# 3. Define functions for script
# - coldspots can be added to the anomaly generation here

# In[3]:


def gen_rand_hotspot(hist):
    
    # Randomly select an eta coordinate from the histogram
    rand_x_coord = random.randint(0,99) 
    
    # Randomly select a phi coordinate from the histogram
    rand_y_coord = random.randint(0,65)
    
    # Get a handle for the intervals of the strip from which the eta coordinate comes from
    strip_vals = hist[hist['x']==rand_x_coord]['occ']
    
    # Use that list of values from the strip to calculate 3 times the standard deviation
    three_times_strip_stdev = 3*strip_vals.std()
    
    # Use that same list of values to calculate 4 times the standard deviation
    four_times_strip_stdev = 4*strip_vals.std()
    
    # Generate a random hotspot that is between 3 and 4 standard deviations above the occupancy value that is
    # initially at the eta,phi coordinate
    try:
        rand_hotval_occ = random.randint(round(three_times_strip_stdev),round(four_times_strip_stdev))
    except:
        # Sometimes, the standard deviation comes out as an erroneous float NaN which throws an error, this
        # catches that issue
        rand_hotval_occ = 1
    
    # Return the (eta,phi,hotspot_value) as (rand_x_coord, rand_y_coord, rand_hotval_occ)
    return (rand_x_coord, rand_y_coord, rand_hotval_occ)

def gen_rand_hotstrip(hist):
   
    
    rand_start_x_coord = random.randint(0,99)
    
    rand_stop_x_coord = random.randint(0,99)
    while rand_start_x_coord == rand_stop_x_coord:
        rand_stop_x_coord = random.randint(0,99)
    
    rand_y_coord = random.randint(0,65)
    
    # If the ending coordinate is larger than the starting coordinate
    if rand_start_x_coord < rand_stop_x_coord:
        # And the difference between the two coordinates is greater than 10
        if (rand_stop_x_coord-rand_start_x_coord) > 10:
            # Cap the length of the layer to 10
            rand_x_arr = np.arange(rand_start_x_coord,rand_start_x_coord+(10-1))
        else:
            # Otherwise, let the length of the layer be defined by the stop coordinate
            rand_x_arr = np.arange(rand_start_x_coord,rand_stop_x_coord)
    else: # If the start coordinate is larger
        # And if the difference between the two coordinates is greater than 10
        if (rand_start_x_coord-rand_stop_x_coord) > 10:
            # Cap the length of the layer to 10
            rand_x_arr = np.arange(rand_stop_x_coord,rand_stop_x_coord+(10-1))    
        else:
            # Otherwise, let the length of the layer be defined by the start coordinate
            rand_x_arr = np.arange(rand_stop_x_coord,rand_start_x_coord)
    
    # Get a handle for the intervals of the strip from which the eta coordinate comes from
    strip_vals = hist[hist['x']==rand_start_x_coord]['occ'].values
    
    # Use that list of values from the strip to calculate 3 times the standard deviation
    three_times_strip_stdev = 3*strip_vals.std()
    
    # Use that same list of values to calculate 4 times the standard deviation
    four_times_strip_stdev = 4*strip_vals.std()
    
    # Generate a random hotspot that is between 3 and 4 standard deviations above the occupancy value that is
    # initially at the eta,phi coordinate
    try:
        rand_hotval_occ = random.randint(round(three_times_strip_stdev),round(four_times_strip_stdev))
    except:
        # Sometimes, the standard deviation comes out as an erroneous float NaN which throws an error, this
        # catches that issue
#         print(strip_vals.std())
        rand_hotval_occ = 1
    
    # Return the (eta,phi,hotspot_value) as (rand_x_coord, rand_y_coord, rand_hotval_occ)
    return (rand_x_arr, rand_y_coord, rand_hotval_occ)  


def gen_rand_hotlayer(hist):
    
    
    rand_start_x_coord = random.randint(0,99)
    
    
    rand_stop_x_coord = random.randint(0,99)
    while rand_start_x_coord == rand_stop_x_coord:
        rand_stop_x_coord = random.randint(0,99)
    
    
    rand_start_y_coord = random.randint(0,65)
    

    rand_stop_y_coord = random.randint(0,65)
    while rand_start_y_coord == rand_stop_y_coord:
        rand_stop_y_coord = random.randint(0,65)
    

    # If the ending coordinate is larger than the starting coordinate
    if rand_start_x_coord < rand_stop_x_coord:
        # And the difference between the two coordinates is greater than 10
        if (rand_stop_x_coord-rand_start_x_coord) > 10:
            # Cap the length of the layer to 10
            rand_x_arr = np.arange(rand_start_x_coord,rand_start_x_coord+(10-1))
        else:
            # Otherwise, let the length of the layer be defined by the stop coordinate
            rand_x_arr = np.arange(rand_start_x_coord,rand_stop_x_coord)
    else: # If the start coordinate is larger
        # And if the difference between the two coordinates is greater than 10
        if (rand_start_x_coord-rand_stop_x_coord) > 10:
            # Cap the length of the layer to 10
            rand_x_arr = np.arange(rand_stop_x_coord,rand_stop_x_coord+(10-1))    
        else:
            # Otherwise, let the length of the layer be defined by the start coordinate
            rand_x_arr = np.arange(rand_stop_x_coord,rand_start_x_coord)
    
    # Likewise for y, but capped at 3
    if rand_start_y_coord < rand_stop_y_coord:
        if (rand_stop_y_coord-rand_start_y_coord) > 3:
            rand_y_arr = np.arange(rand_start_y_coord,rand_start_y_coord+(3-1))
        else:
            rand_y_arr = np.arange(rand_start_y_coord,rand_stop_y_coord)
    else:
        if (rand_start_y_coord-rand_stop_y_coord) > 3:
            rand_y_arr = np.arange(rand_stop_y_coord,rand_stop_y_coord+(3-1))
        else:
            rand_y_arr = np.arange(rand_stop_y_coord,rand_start_y_coord)
    
    # Get a handle for the intervals of the strip from which the eta coordinate comes from
    strip_vals = hist[hist['x']==rand_start_x_coord]['occ'].values
    
    # Use that list of values from the strip to calculate 3 times the standard deviation
    three_times_strip_stdev = 3*strip_vals.std()
    
    # Use that same list of values to calculate 4 times the standard deviation
    four_times_strip_stdev = 4*strip_vals.std()
    
    # Generate a random hotspot that is between 3 and 4 standard deviations above the occupancy value that is
    # initially at the eta,phi coordinate
    try:
        rand_hotval_occ = random.randint(round(three_times_strip_stdev),round(four_times_strip_stdev))
    except:
#         print(strip_vals.std())
          rand_hotval_occ = 1
    
    # Return the (eta,phi,hotspot_value) as (rand_x_coord, rand_y_coord, rand_hotval_occ)
    return (rand_x_arr, rand_y_arr, rand_hotval_occ)



def gen_rand_coldspot():
    # same as hotspot but subtract the std instead of add?
    return

# For Debugging
def input_heatmap(df,ftag_id,hist_id):
    tmp = df[df['ftag_id']==ftag_id]
    tmp = tmp[tmp['hist_id']==hist_id]
    sns.heatmap( tmp.pivot_table(index='y',columns='x',values='occ') )
    plt.show()


# 4. Initialize quality values at 0

# In[5]:


df['quality']=0
df['quality'].value_counts()


# 5. Main section: Generate anomalies and update the main dataframe to include these anomalies

# In[6]:


for idf,ftid in enumerate(df['ftag_id'].unique()):
    
    progress_bar(idf,df['ftag_id'].unique())
    
    # Get the subset of the main dataframe whose ftag_id is ftid
    mask = df['ftag_id'] == ftid
    tmp = df.loc[mask,:]
    
    for hid in tmp['hist_id'].unique():
        
        # Get the subset of the ftag_id dataframe whose hist_id is hid
        mask = tmp['hist_id'] == hid
        tmp2 = tmp.loc[mask,:]

        # 0 = do not generate anomaly in this histogram, 1 = generate anomaly in this histogram 
        #(50% of histograms should contain anomalies)
        rand_5050 = random.randint(0,1)

        # If its 1, generate an anomaly in the histogram
        if rand_5050 == 1:
            
            # 1 = hotspot, 2 = hotstrip, 3 = hotlayer (33% of anomalies could be either)
            rand_1in3 = random.randint(1,3)
            
            if rand_1in3 == 1:
                
                # Generate the hotspot with the function
                hotspot = gen_rand_hotspot(tmp2)
                
                # Get a subset of datapoints for the hotspot based on generated coordinates
                tmpx = tmp2[tmp2['x']==hotspot[0]]
                tmpy = tmpx[tmpx['y']==hotspot[1]]
                
                # Get the indexes that will be used to update the hotspot in the histogram
                index_to_change = tmpy.index
                
                # Update the data point(s) in the histogram based on the hotspot that we generated
                # The std needs to be added to the original occupancy value to be higher than the avg occ
                tmp2.loc[index_to_change,'occ'] = tmp2.loc[index_to_change,'occ']+hotspot[2]
                
                # If the occupancy(ies) is/are 0...
                # The std of 0 is 0, so instead of changing an occ to an anomaly and it staying 0, we switch
                # the value of the 0 occupancy to the highest occ value in the histogram
                try:
                    if tmp2.loc[index_to_change,'occ'].values[0] == 0:

                        # Switch the value with the max occupancy on the histogram to ensure it is an anomaly
                        tmp2.loc[index_to_change,'occ'] = tmp2['occ'].max()
                        
                    # Update the label in the dataframe to show this(these) coordinates are now anomalies
                    tmp2.loc[index_to_change,'quality'] = 1
                    
                except:
                    # If index 0 for axis 0 is size 0, the coordinate likely does not exist, leave it as is
                    pass
                                
                # Debugging lines below
                
                # Get a readout of the coordinates of the hotspot and its associated occ value
#                 print(hotspot[0],hotspot[1],tmp2.loc[index_to_change,'occ'].values[0])
                
                # Set the figure large enough so we can see the anomaly we generated
#                 plt.figure(figsize=(20,20))
                
                # View the heatmap of this histogram so we can see the anomaly we generated
#                 input_heatmap(tmp2,ftid,hid)

                # End Debugging lines
                
            # Previous comments apply similarly for generating hotstrips in the histogram
            elif rand_1in3 == 2:
                
                hotstrip = gen_rand_hotstrip(tmp2)

                maskx = tmp2['x'].isin(hotstrip[0])
                tmpx = tmp2.loc[maskx,:]

                masky = tmpx['y'] == hotstrip[1]
                tmpy = tmpx.loc[masky,:]

                indexes_to_change = tmpy.index

                tmp2.loc[indexes_to_change,'occ'] = tmp2.loc[indexes_to_change,'occ']+hotstrip[2]
                
                tmp2.loc[indexes_to_change,'quality'] = 1
                
                if all(tmp2.loc[indexes_to_change,'occ']) == 0:
                    tmp2.loc[indexes_to_change,'occ'] = tmp2['occ'].max()
                    
                # Debugging lines
                
#                     print('final:',hotstrip[0],hotstrip[1],tmp2['occ'].max())
#                 else:
#                     print('final:',hotstrip[0],hotstrip[1],tmp2.loc[indexes_to_change,'occ'])
                
#                 plt.figure(figsize=(20,20))               
#                 input_heatmap(tmp2,ftid,hid)

                # End Debugging lines
                
            # Previous comments apply similarly for generating hotstrips in the histogram
            elif rand_1in3 == 3:

                hotlayer = gen_rand_hotlayer(tmp2)

                maskx = tmp2['x'].isin(hotlayer[0])
                tmpx = tmp2.loc[maskx,:]

                masky = tmpx['y'].isin(hotlayer[1])
                tmpy = tmpx.loc[masky,:]

                indexes_to_change = tmpy.index

                tmp2.loc[indexes_to_change,'occ'] = tmp2.loc[indexes_to_change,'occ']+hotlayer[2]
                
                tmp2.loc[indexes_to_change,'quality'] = 1
                
                if all(tmp2.loc[indexes_to_change,'occ']) == 0:
                    tmp2.loc[indexes_to_change,'occ'] = tmp2['occ'].max()
                    
                # Debugging lines below
                
#                     print('final:',hotlayer[0],hotlayer[1],tmp2['occ'].max())
#                 else:
#                     print('final:',hotlayer[0],hotlayer[1],tmp2.loc[indexes_to_change,'occ'])
                
#                 plt.figure(figsize=(20,20))                
#                 input_heatmap(tmp2,ftid,hid)

                # End Debugging lines

            # Update the main dataframe with the anomalous values
            df.loc[tmp2.index,:] = tmp2


# 6. Verify anomalies were added

# In[7]:


df['quality'].value_counts()


# What percentage of datapoints are anomalous? Is this a problem and should we comment about it?

# In[8]:


total = df['quality'].value_counts().values[0]+df["quality"].value_counts().values[1]
print(f'Pct values non anomalous:{100*df["quality"].value_counts().values[0]/total}%')
print(f'Pct values anomalous:{100*df["quality"].value_counts().values[1]/total}%')


# 7. Save main df with anomalies added as anomalous_dfs.csv

# In[11]:


df.to_csv('anomalous_dfs.csv',index=False)


# We can now move to the normalization script for further processing of this anomalous set, and if not already done, processing of the non anomalous set
