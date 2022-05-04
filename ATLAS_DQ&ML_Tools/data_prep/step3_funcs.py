from replica_processor import *
import random
import matplotlib.pyplot as plt
import seaborn as sns

# Turn off chained assignment message
pd.options.mode.chained_assignment = None  # default='warn'


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