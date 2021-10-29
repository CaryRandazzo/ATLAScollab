###########
# IMPORTS #
###########

import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.layers import Dense, Dropout, Input, InputLayer, Conv2D, UpSampling2D, DepthwiseConv2D
from tensorflow.keras.layers import Flatten, MaxPooling2D, Conv2DTranspose, AveragePooling2D
from tensorflow.keras import layers
from tensorflow.keras.optimizers import Adam
import random
from tensorflow.keras.optimizers import RMSprop

###########################
# LOAD AND TRANSFORM DATA #
###########################

# Open the file that train_set is stored in as f
with open('train_set.npy', 'rb') as f:

    # Load and get a handle for train_set
    train_set = np.load(f)

# Open the file that train_set is stored in as f
with open('test_set.npy', 'rb') as f:
    
    # Load and get a handle for test_set
    test_set = np.load(f)
    
    
# Prepare the input values from the training set (used for model training)
X = train_set[0]
X = ((X.reshape(X.shape[0],X.shape[1],X.shape[2],1)))
# X = X[:,:64,:96,:]
X = X[:,:65,:99,:]
#X.shape


# Prepare the target values from the training set (used for model training)
Y = train_set[1]
Y = ((Y.reshape(Y.shape[0],Y.shape[1],Y.shape[2],1)))
# Y = Y[:,:64,:96,:]
Y = Y[:,:65,:99,:]
#Y.shape


# Prepare the input values from the test set (used for model evaluation)
X2 = test_set[0]
X2 = ((X2.reshape(X2.shape[0],X2.shape[1],X2.shape[2],1)))
# X2 = X2[:,:64,:96,:]
X2 = X2[:,:65,:99,:]
#X2.shape


# Prepare the target values from the test set (used for model evaluation)
Y2 = test_set[1]
Y2 = ((Y2.reshape(Y2.shape[0],Y2.shape[1],Y2.shape[2],1)))
# Y2 = Y2[:,:64,:96,:]
Y2 = Y2[:,:65,:99,:]
#Y2.shape


#########
# MODEL #
#########


def build_model():
    
    # Sequential model constructor initialization
    model = Sequential()

    # Get a summary of the model
    print(model.summary())

    # This will need to be optimized...
    
    return model


# Construct optimizer for the model
def adam_optimizer(lrate,b1,b2):
    return Adam(lr = lrate, beta_1 = b1, beta_2 = b2)
  

# Construct the loss function
lossfn = 'mape'

# Identify metrics of interest
metric_list = ['accuracy']

# Configure and compile the model
model.compile(loss = lossfn, optimizer = adam_optimizer(0.001, 0.99, 0.999), metrics = metric_list)


# Select batch size
num_batches = 10

# Select number of epochs
num_epochs = 11

# Fit the model
model.fit(x = X, y = Y, validation_data = (X2, Y2), batch_size = num_batches, epochs = num_epochs)


####################
# MODEL EVALUATION #
####################

def eval_with_randomtest(model):
  # Initialize the matrix
  Xtest = np.zeros((1,65,99))

  # Set random values inside the matrix
  Xtest[0] = np.random.rand(65,99)

  # Turn these random values into integers that range from 0 to 300,000
  Xtest[0] = (Xtest[0] * random.randint(0,300000)).round()

  # Reshape the matrix to the shape that is required to input into the model
  Xtest = ((Xtest.reshape(Xtest.shape[0],Xtest.shape[1],Xtest.shape[2],1)))
  Xtest = Xtest[:,:64,:96,:]

  # View the shape for final clarification
  display(Xtest.shape)

  # Make predicutions using the model over the histogram
  Xtest_pred = model.predict(Xtest)
  
  return Xtest_pred
