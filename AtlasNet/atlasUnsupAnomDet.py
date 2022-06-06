import numpy as np
import pandas as pd
import keras
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Conv2D
from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

pd.options.mode.chained_assignment = None # default='warn'

def anomaly_scores(y_true, y_pred):
    """
    Similar to keras's system, we calculate the loss between the true values and predicted values of the model. As far as I am aware, keras does not give us access to these
    individually calculated losses, therefore we use this function to calculate the elementwise loss and convert/compute the probability that the loss between those two elements
    is an outlier. Currently, we directly convert the elementwise loss to a value between 0 and 1 and use it as the outlier probability.

    This function is used within other functions, not standalone.
    """
    
    
    # Mean Squared Loss
    calc = (np.array(y_true)-np.array(y_pred))**2/np.size(y_true)
    print(calc)
    loss = np.sum( ((np.array(y_true) - np.array(y_pred))**2)/np.size(y_true) , axis=1)
    print(loss)
    

    # return anomaly_scores
    return loss #loss_scaled

def build_clAE():
    """

    Construct the Autoencoder model that will transform the data for final anomaly prediction.

    pMtrain_a2 and pMtest_a2 are the names of the training and testing set that were loaded from the x_train_df2.csv and x_test_df2.csv that have been constructed from
    the .ipynb files found at https://github.com/CaryRandazzo/ATLAScollab/tree/main/ATLAS_DQ%26ML_Tools/data_prep.

    The final notebook that constructs these split datasets is can be found at the following link as part of step7:
    https://github.com/CaryRandazzo/ATLAScollab/blob/main/ATLAS_DQ%26ML_Tools/data_prep/Step6FullHistsSplit-2-23-22.ipynb

    Example Use:
        pMtrain_a2: A dataframe used for training the model
         =
        pMtest_a2: A dataframe used for testing the model

    """

    # The names for the split datasets have been preserved so they can be followed from the ATLAScollab/datafiles .ipynb files that detail how to construct this split dataset
    try:
        pMtrain_a2 = pd.read_csv('x_train_df2.csv', dtype={'x':'int8','y':'int8','ftag_id':'int8','occ':'float32','hist_type':'int8','hist_id':'int16','quality':'int8','occ_0to1':'float32','occ_zscore':'float32','occ_robust':'float32'})
        pMtest_a2 = pd.read_csv('x_test_df2.csv', dtype={'x':'int8','y':'int8','ftag_id':'int8','occ':'float32','hist_type':'int8','hist_id':'int16','quality':'int8','occ_0to1':'float32','occ_zscore':'float32','occ_robust':'float32'})
    except:
        print('ERROR LOADING DATASET! NAVIGATE TO: https://github.com/CaryRandazzo/ATLAScollab/tree/main/ATLAS_DQ%26ML_Tools/data_prep and construct x_train_df2.csv and x_test_df2.csv to construct the datasets and reload this function')

    # Get a handle for the sequential model constructor
    clAE = Sequential()

    # This is the configuration that was present during the writing of the masters degree, even though several were tested.
    # Model architecture
    clAE.add(Dense(1, activation='linear',input_dim=1))
    clAE.add(keras.layers.LeakyReLU())
    clAE.add(Dense(3, activation='linear'))
    clAE.add(keras.layers.LeakyReLU())
    clAE.add(Dense(2, activation='linear'))
    clAE.add(keras.layers.LeakyReLU())
    clAE.add(Dense(3, activation='linear'))
    clAE.add(keras.layers.LeakyReLU())
    clAE.add(Dense(1, activation='linear'))

    # Initialize the optimizer and loss parameters
    optimizer = 'adam'
    loss = 'mean_squared_error'

    # Compile the model and prepare the early stopping parameter
    clAE.compile(optimizer=optimizer, loss=loss)
    es = keras.callbacks.EarlyStopping(monitor='loss', mode='min', verbose=1, patience=32)

    # Initialize model fitting parameters
    epochs = 3
    batch_size = 2048
    features = ['occ_0to1']

    # Capture the training data while training the algorithm
    log = clAE.fit(pMtrain_a2[features], pMtrain_a2[features], 
            epochs = epochs,
            batch_size = batch_size,
            shuffle = True,
            validation_data = (pMtest_a2[features],pMtest_a2[features]),
            verbose = 1, 
            callbacks=[es]
            )

    # Save the model for later use
    clAE.save('13231leaky_a2set')

    # Return the model
    return clAE


def build_preds_df(hist, features, clAE):
    """

    Example Use:
        hist: hist we are interested in determining outliers for OR hist_to_calibrate in the case we are using it to get calibration data prior to anomaly detection
        features: This is the features that will be used over the clAE model when predicting the results.
         = ['x','y','occ_0to1']
        clAE: the AutoEncoder model that was trained with the input data from the user

    """


    #############################################
    # PART I: AE anomaly_scores and Predictions #
    #############################################
    
    # Set which occupancy feature to use for this test, may need modification for multiple features
#     occ_feature = features[2]
    occ_feature = 'occ_0to1'

    # Extract info from histogram
    hist = hist[features]

    # Gather the anomaly scores and prediction dataframe from model.predict
    preds = clAE.predict(hist[occ_feature])
    asc = anomaly_scores(hist[occ_feature],preds.reshape(-1,1)) # It is important to only run this scoring function over the target values!
    preds_df = pd.DataFrame({'x':hist['x'],'y':hist['y'],occ_feature:preds.reshape(1,-1)[0], 'asc':asc})
   
    return preds_df


def build_preds_df_modified(anomalous_hist):
    """
    IMPORTANT:
        Not yet constructed.

    This function will be used for building the modified version of the preds_df for use in calculate_anoms_DB()
    
    """



    return


def gen_mmnorm(df,feature_to_norm,normed_feature_name):
    """
    Likely does not need to be tested. Very simple function and has been used as is in V12.ipynb.

    Calculate and return normed_feature_name as the minmax of the input feature feature_to_norm from dataframe df. This scales the inputs to values between
    0 and 1.

    This function is used within the eval_cm_...() function when calculating the clusters. Thus the input is specific to sections of that function.
    Thus,
    df: A histogram that contains the feature we want to norm (in eval_...())
    feature_to_norm: name implies what it is (from eval_...())
    normed_feature_name: name implies what it is (to be used in eval_...())
    
    """

    # If the max equals the min, do nothing
    if df[feature_to_norm].max()==df[feature_to_norm].min():
        pass
    else: 
        # Otherwise, scale bewteen 0 and 1
        df[normed_feature_name] = (df[feature_to_norm]-df[feature_to_norm].min())/(df[feature_to_norm].max()-df[feature_to_norm].min())

    return df


def eval_cm_get_roc_inputs_noplots(hist_to_calibrate, preds_df, eps, minpts):
    """
    IMPORTANT:
        This function has been tested on hist_to_calibrate with preds_df associated with model generated from the V12.ipynb notebook. Use in this script is untested.
        Needs to be tested and potentially debugged.

    This is the business end of the clustering part of the anomaly detection system. It calculates the clusters for global, strip, and zonewise outliers, then
    calculates classification information relevant for roc inputs.

    Example Use:
        hist_to_calibrate = will either be the anomalous_hist when the end user wants their final output(see the calculate_anoms_etc() functions) OR
         will be the histogram of a specific type that we want to calibrate the algorithm over. (Calibration hist should be of the same type as the anomalous_hist the 
         user will later use).
        preds_df = is generated from build_preds_df(), see that function for more on this.
        eps = constant that the algorithm will use to predict results
        minpts = constant that the algorithm will use to predict results
    
    """


    #######################
    # Part II: Clustering #
    #######################
    
    # If the max and min vals of anomaly_scores are not equal, scale them between 0 and 1
    if preds_df['asc'].max()==preds_df['asc'].min():
        pass
    else:
        preds_df['asc_0to1'] = (preds_df['asc']-preds_df['asc'].min())/(preds_df['asc'].max()-preds_df['asc'].min())

#     print('scaling complete.')

    dbscan = DBSCAN(eps=eps, min_samples=minpts).fit(preds_df[['occ_0to1','asc_0to1']])
    occlabels = dbscan.labels_

    # Plot clusters by color
    labels_set = list(set(occlabels))


    for unique_val in labels_set:
        if unique_val == -1:
            mask = [idx for idx,val in enumerate(occlabels) if val==unique_val]
            globalOLs = ([(int(val/65),val%65) for val in mask])
        else:
            globalOLs = []
        
#     print('globalOLs complete.')

    stripOLs,zoneOLs = [],[]

    for ids,strip in enumerate(preds_df['x'].unique()):
        tmpp = preds_df[preds_df['x']==strip]

        if tmpp['occ_0to1'].max()==tmpp['occ_0to1'].min():
            continue # Should this be pass or continue? it moves to the next strip?
    #                 pass
        else:
            tmpp['occ_stripnorm'] = (tmpp['occ_0to1']-tmpp['occ_0to1'].min())/(tmpp['occ_0to1'].max()-tmpp['occ_0to1'].min())

        if tmpp['asc'].max()==tmpp['asc'].min():
            continue # Should this be pass or continue? it moves to the next strip?
    #                 pass
        else:
            tmpp['asc_stripnorm'] = (tmpp['asc']-tmpp['asc'].min())/(tmpp['asc'].max()-tmpp['asc'].min())

        dbscan = DBSCAN(eps=eps, min_samples=minpts).fit(tmpp[['occ_stripnorm','asc_stripnorm']])
        occlabels = dbscan.labels_

        # Plot clusters by color
        labels_set = list(set(occlabels))

        for unique_val in labels_set:
            # Getting the -1 values only
            if unique_val == -1:
                mask = [idx for idx,val in enumerate(occlabels) if val==unique_val]

                for val in mask:
                    stripOLs.append((strip,val))

        if strip==0: # Case 1, 0th strip is left border, zone strip is one to the right of strip at strip+1
            mask = (preds_df['x']==(strip+1)) | (preds_df['x']==strip)
            zone_strips = preds_df.loc[mask,:]
        elif strip==98: # Case 2, 64th strip is right border, zone strip is one to the left of strip at strip-1
            mask = (preds_df['x']==(strip-1)) | (preds_df['x']==strip)
            zone_strips = preds_df.loc[mask,:]
        else: # Case 3, ith strip is between two zone strips
            mask = (preds_df['x']==(strip+1)) | (preds_df['x']==strip) | (preds_df['x']==(strip-1))
            zone_strips = preds_df.loc[mask,:]

        zone_strips = gen_mmnorm(zone_strips,'occ_0to1','occ_stripnorm')
        zone_strips = gen_mmnorm(zone_strips,'asc','asc_stripnorm')

        dbscan = DBSCAN(eps=eps, min_samples=minpts).fit(zone_strips[['occ_stripnorm','asc_stripnorm']])
        occlabels = dbscan.labels_

        # Label clusters from dbscan
        labels_set = list(set(occlabels))          

        for unique_val in labels_set:
            if strip>0:
                # Getting the -1 values only
    #             if unique_val == -1:
                mask = [idx for idx,val in enumerate(occlabels) if val==-1]
                try:
                    for val in mask:
                        zoneOLs.append((strip-1+int(val/65),val%65))
                except:
                    pass # mask does not exist for classes other than -1

            elif strip==0:
                # Getting the -1 values only
    #             if unique_val == -1:
                mask = [idx for idx,val in enumerate(occlabels) if val==-1]
                try:
                    for val in mask:
                        zoneOLs.append((int(val/65),val%65))
                except:
                    pass # Mask does not exist for classes other than -1

#     print('stripOLs+zoneOLs complete.')
    
    
    ########################################
    # Classification Report and ROC Inputs #
    ########################################
    
    preds_df = preds_df.reset_index(drop=True)
    preds_df['quality_y'] = hist_to_calibrate['quality'].reset_index(drop=True)

    hist_to_calibrate = hist_to_calibrate.reset_index(drop=True)

    preds_df.loc[:,'quality_y'] = 0
    
    mask = hist_to_calibrate[hist_to_calibrate['quality']==1].index
    preds_df.loc[mask,'quality_y'] = 1

    preds_df.loc[:,'quality_preds'] = 0

    # add global OLs to preds list
# THIS NEEDS AN UPDATE ---- # = 1 ?
    try:
        mask = [val[0] for val in globalOLs]
        if len(mask)>0:
            preds_df.loc[mask,'quality_preds'] # = 1
    except:
        pass # no globalOLs

    # add strip OLs to preds list
    mask = [(val[0]*65+val[1]) for val in stripOLs]
    preds_df.loc[mask,'quality_preds'] = 1

    # add zone OLs to preds list
    mask = [(val[0]*65+val[1]) for val in zoneOLs]
    preds_df.loc[mask,'quality_preds'] = 1

    cm = confusion_matrix(preds_df['quality_y'],preds_df['quality_preds'])
#     ConfusionMatrixDisplay(cm,['inliers','outliers']).plot()
#     plt.show()
#     print(cm)
    
    try:
        tpr = cm[0,0]/(cm[0,0]+cm[0,1])
        fpr = cm[1,0]/(cm[1,0]+cm[1,1])
    except:
        tpr = cm[0,0]
        fpr = 0
    
#     print('config:',eps,minpts,tpr,fpr)
    
    return tpr, fpr, eps, minpts, globalOLs, stripOLs, zoneOLs


def calibrate_histogram(hist_to_calibrate, clAE, eps, minpts_range):
    """

    IMPORTANT:
        Ready for testing and debugging. Unteseted.

    Given a constant value of eps and a range of minpts, generate a single ROC curve(each input of a single eps+minpts parameter = 1 point on the curve) 
    with a single AUC curve. This will generate multiple datapoints in an roc_df dataframe for that 1 value of eps and range of minpts all with the same AUC value.
    
    For a single histogram of a single type, this function should be run several times for a range of eps values to generate a range of AUC values to determine the best
    parameters later in the get_best_params_from_calibrated_df() function.

    Example Use:
        hist_to_calibrate: As name suggests.
        eps: A constant to calculate 1 AUC value and 1 ROC curve (of several parameter combinations). This value will come from a for loop over a range of eps such as 
         the following -> for eps in eps_range
        minpts_range: A range of minpts parameters. For a single run of this function an example looks as the following...
         = np.arange(0,60,1) 
        
        The  minpts range could be larger to more thoroughly fill out the single generated ROC curve, but changing eps will 
        typically generate a different ROC curve entirely.

    """

    # Check to see if roc_auc in current working directory. If it is not, create it for storing calibrated histograms
    # try:
        # calibrated_auc_df = pd.read_csv('calibrated_auc_df.csv')
    # except:
        # calibrated_auc_df = pd.DataFrame({
            # 'auc':[], 
            # 'eps':[], 
            # 'minpts':[], 
            # 'ftag_id':[],
            # 'hist_id':[]
            # }).to_csv('calibrated_auc_df.csv',index=False)

    preds_df = build_preds_df(hist_to_calibrate, ['x','y','occ_0to1'], 5, clAE)

    # Initialize the input array
    inputs = []

    # Loop through the minpts parameters
    for id3, j in enumerate(minpts_range):
        a = eval_cm_get_roc_inputs_noplots(hist_to_calibrate, preds_df, eps, minpts_range)
        inputs.append(a)

    # Get a handle for the roc/auc dataframe
    roc_df = pd.DataFrame({
        'tpr':[val[0] for val in inputs],
        'fpr':[val[1] for val in inputs],
        'eps':[val[2] for val in inputs],
        'mask_thresh':[val[3] for val in inputs],
        'auc': []
        })

    # Sort and prep the roc_df dataframe
    roc_df = roc_df.sort_values(by=['fpr']).reset_index(drop=True)
    roc_df.index += 1
    roc_df.loc[0,:] = 0
    roc_df = roc_df.sort_values(by=['fpr']).reset_index(drop=True)

    # Store this calibration entry in the auc column for all these values
    roc_df['auc'] = metrics.auc(roc_df['fpr'],roc_df['tpr'])
    
    # Save it
    roc_df.to_csv('roc_df.csv',index=False)


def get_best_params_from_calibrated_df(fpr_thresh, tpr_thresh):
    """

    IMPORTANT:
        Ready for testing and debugging. Unteseted.
        There needs to be added a case where no datapoints are generated for the required threshold settings. (for example the results may not generate a perfect 0.0 fpr,1.0 tpr model)

    This function takes in user requirements of false_positive_rate_threshold and true_positive_rate_threshold toleration levels and returns the best eps and minpts 
    parameter combination within those requirements. 
    This function produces better results when roc_df.csv exists and has plenty of calibration data that has been previously calculated from calibrate_histograms()

    Example Use:
        fpr_thresh = 0.2
        tpr_thresh = 0.8

    """
    
    # Load the roc_df where the best parameters are ready to be mined out
    roc_df = pd.read_csv('roc_df.csv')

    # Get a handle for the subset of data(tmp) that contains only the highest value of auc
    tmp = roc_df[roc_df['auc'] == roc_df['auc'].max()]

    # Select the best parameters in that dataframe based on the threshold settings and return the dataframe whose subset only contains those conditions (tmp)
    tmp = tmp[tmp['fpr']<fpr_thresh]
    tmp = tmp[tmp['tpr']<tpr_thresh]

    # tmp should contain the datapoints that fit the threshold requirements
    # Select the maximum of these points to get the value within these requirents that have the highest possible tpr with the highest allowable fpr
    eps = tmp['eps'].max()
    minpts = tmp['minpts'].max()

    return eps, minpts


def calculate_anoms_AEDB(pMtrain_a2, pMtest_a2, anomalous_hist, hist_to_calibrate_sametype, features, clAE, eps_range, minpts_range, fpr_thresh, tpr_thresh):
    """

    IMPORTANT:
        Ready for testing and debugging. Unteseted.

    Example Use:
        anomalous_hist: The end user has a histogram they are interested in detecting anomalous data within. This is that histogram.
         = anomalous_hist (data_type is dataframe)
        features: the features the end user are interested training the dataset over (this will require making sure the occ_0to1 feature is built in the relevant histogram)
         = ['x', 'y', 'occ_0to1']
        clAE: the AE model that is outputted following training the autoencoder (usually a simple low level process)
         = clAE
        eps_range: a range of constant parameter (eps) used in combination with the minpts parameter to generate calibration results and find best eps parameter.
         = np.arange(1e-5, 1e-3, 1e-5)
        minpts_range: a range of constant parameter (minpts) used in combination with the eps parameter to generate calibration results and find best minpts parameter.
         = np.arange(0, 60, 1)
        fpr_thresh: tolerance level for false positive rate 
         = 0.2 for example
        tpr_thresh: tolerance level for true positive rate
         = 0.8 for example
    """

    # Try to load the clAE model if it exists
    try:
        clAE = keras.models.load_model("13231leaky_a2set")
    except:
        # If the model doesn't exist, build it
        clAE = build_clAE(pMtrain_a2, pMtest_a2)

    # Calculate the predictions from the clAE model for the anomalous_hist
    preds_df = build_preds_df(anomalous_hist, features, clAE)

    # Calibrate a histogram of the same type as anomalous_hist
    for eps in eps_range:
        calibrate_histogram(hist_to_calibrate_sametype, clAE, eps, minpts_range) # Populates data in roc_df.csv

    # Calculates the best eps and minpts parameters from the previously populated data in roc_df.csv
    eps, minpts = get_best_params_from_calibrated_df(fpr_thresh, tpr_thresh)

    # Determines the anomalous datapoints in the hist of interest anomalous_hist given the preds_df from the AE model and the best parameters from previous functions
    _, _, _, _, globalOLs, stripOLs, zoneOLs = eval_cm_get_roc_inputs_noplots(anomalous_hist, preds_df, eps, minpts)

    return


def calculate_anoms_DB(anomalous_hist, eps, minpts):
    """

    IMPORTANT:
        This function is not ready for use. Modification is required.
    
    Description:
    In the case the user does not have prior data to train the Autoencoder and also no labels to calibrate the clustering algorithm, we use a logic based method to
    generate the best possible dataless model for anomaly detection. This method does not use the Autoencoder - only the clustering part of the algorithm.

    Example Use:
        eps: The best eps parameter that comes from the get_best_params_from_calibrated_df() function.
        minpts: The best minpts parameter that comes from the get_best_params_from_calibrated_df() function.

    """

    # build_preds_df needs to be modified to not require clAE(the AE model), but have the properly formatted dataframe for input into eval_cm_get_roc_inputs_noplots()
    preds_df = build_preds_df_modified(anomalous_hist)

    # eval_cm_get_roc_inputs_noplots will have to be modified to not use AE specific information such as anomaly score or generate anything related to ROC/AUC due to no labels
    _, _, _, _, globalOLs, stripOLs, zoneOLs = eval_cm_get_roc_inputs_noplots(anomalous_hist, preds_df, eps, minpts)

    return


if __name__ == "__main__":
    """

    This call assumes that pMtrain_a2 and pMtest_a2 are available datasets from the dataset construction guide on the github. (x_train_df2.csv, x_test_df2.csv)

    """

    pMtrain_a2 = pd.read_csv('x_train_df2.csv')
    pMtest_a2 = pd.read_csv('x_test_df2.csv')

    #input from the user, for now we will use whatever
    anomalous_hist = pMtrain_a2[pMtrain_a2['ftag_id']==0][pMtrain_a2[pMtrain_a2['ftag_id']==0]['hist_id']==0]

    # The hist_to_calibrate_sametype will have known/labelled anomalous datapoints...so the algorithm should pick out the same as the labels,
    # This setting merel calibrates that hist_type
    hist_to_calibrate_sametype = anomalous_hist

    features = ['x','y','occ_0to1']

    clAE = build_clAE()

    eps_range = np.arange(1e-5,1e-4,1e-5)
    minpts_range = np.arange(0,60,1)

    # Could cause error if these requirements are not met
    fpr_thresh = 0.2
    tpr_thresh = 0.8

    calculate_anoms_AEDB(pMtrain_a2, pMtest_a2, anomalous_hist, hist_to_calibrate_sametype, features, clAE, eps_range, minpts_range, fpr_thresh, tpr_thresh)