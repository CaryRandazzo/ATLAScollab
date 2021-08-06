#########
#IMPORTS#
#########

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.layers import Dense, Dropout, Input, InputLayer, Conv2D, UpSampling2D, DepthwiseConv2D
from tensorflow.keras.layers import Flatten, MaxPooling2D, Conv2DTranspose, AveragePooling2D
from tensorflow.keras.applications.vgg16 import VGG16
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.optimizers import Adam
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.image import img_to_array, load_img
from PIL import Image
from tensorflow.keras.utils import plot_model
from math import ceil
import random
import cv2
from skimage import io, color
from tensorflow.keras.optimizers import RMSprop


##############
##############

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


########################
#MODEL OPTIONS: 1-vgg16#
########################

# For model input ?
model6 = VGG16(weights='imagenet', include_top=False, input_shape=(65,99,3))

# Sequential model constructor initialization
model = Sequential()

# This is simply defining the input layer and its shape
model.add(InputLayer(input_shape=(X.shape[1], X.shape[2], 1)))

# A dense layer of 3 neurons, 1 unit for each input (each channel in this case..or each 64x96 matrix) ...need to use 3 because VGG16 requires 3 input channels..this is a main problem
model.add(layers.Dense(units=3))

# The inputs are coming from models or the VGG16 pretrained model, we do not want this
model.add(Model(inputs=model6.inputs, outputs=model6.layers[-10].output))

# Adds repeating rows/columns in the input to this layer. Rows/column repeats are determined by the size parameter
model.add(UpSampling2D(size=(2,2)))

# Adds repeating rows/columns in the input to this layer. Rows/column repeats are determined by the size parameter
model.add(UpSampling2D(size=(2,2)))

# Specifies 2d depthwise convolution of inputs whose kernel size is 32x32, strides is (2,2) for each movement of kernel/filter, the input gets passed through a tanh filter before 
# convolution (values come through as -1 to 1), and the padding as 'same'  results in padding with zeros evenly to the left/right or
# up/down of the input such that output has the same height/width dimension as the input. 
model.add(DepthwiseConv2D(32,(2,2), activation='tanh', padding='same'))

# Adds repeating rows/columns in the input to this layer. Rows/column repeats are determined by the size parameter
model.add(UpSampling2D(size=(2,2)))

# Specifies 2d depthwise convolution of inputs whose kernel size is 32x32, strides is (2,2) for each movement of kernel/filter, the input gets passed through a tanh filter before 
# convolution (values come through as -1 to 1), and the padding as 'same'  results in padding with zeros evenly to the left/right or
# up/down of the input such that output has the same height/width dimension as the input. 
# The convolution operates by - splitting the input to individual channels, convolve each input with the layer's kernel/filter(called depthwise kernel), and stack convolved outputs together
# along the channel's axis ..unlike regular 2d convolution, does not mix information across different outputs
model.add(DepthwiseConv2D(32,(2,2), activation='tanh', padding='same'))

# Passing information from the convolution that gets converted to 0 until it reaches some minimum value, then becomes that value (is this correct?)
model.add(layers.ReLU(0.3))

# Drops some neurons out to assist in overfitting (correct?)
model.add(layers.Dropout(0.4))

# Adds repeating rows/columns in the input to this layer. Rows/column repeats are determined by the size parameter
model.add(UpSampling2D(size=(2,2)))

# Adds repeating rows/columns in the input to this layer. Rows/column repeats are determined by the size parameter
model.add(UpSampling2D(size=(2,2)))

# Specifies 2d depthwise convolution of inputs whose kernel size is 32x32, strides is (2,2) for each movement of kernel/filter, the input gets passed through a tanh filter before 
# convolution (values come through as -1 to 1), and the padding as 'same'  results in padding with zeros evenly to the left/right or
# up/down of the input such that output has the same height/width dimension as the input. 
model.add(DepthwiseConv2D(2,(2,2), activation='tanh', padding='same'))

# Activation function that cutsoff values at 0.3?
model.add(layers.ReLU(0.3))

# Layer to prevent overfitting, drops some neurons
model.add(layers.Dropout(0.2))

# Adds repeating rows/columns in the input to this layer. Rows/column repeats are determined by the size parameter
model.add(UpSampling2D(size=(2,2)))

# Another value filter
model.add(layers.ReLU(0.3))

# Another overfitting balancer
model.add(layers.Dropout(0.2))

# ?
model.add(AveragePooling2D(pool_size = (2,2)))

# passes the previous input to 2 neurons in this new hidden layer (This is the output layer..the output is 2 neurons of information)
model.add(layers.Dense(units=2))

# Get a summary of the model
print(model.summary())

# This will need to be optimized...


# Construct optimizer for the model
def adam_optimizer():
    return Adam(lr = 0.001, beta_1=0.99, beta_2=0.999)
  
# Configure and compile the model
model.compile(loss='mape', optimizer = adam_optimizer(), metrics=['accuracy'])

# Fit the model
model.fit(x=X, y=Y,validation_data=(X2,Y2),batch_size=10, epochs=11)


###############################
#MODEL OPTIONS: 2-simple vgg16#
###############################

# Constructing a simple tensorflow/keras CNN:


# For model input ?
vgg_model = VGG16(weights=None, include_top=False, input_shape=(64,96,3))


weights_file='../../Machine Learning/Data/vgg16_weights_tf_dim_ordering_tf_kernels_notop.h5'


vgg_model.load_weights(weights_file)

for layer in vgg_model.layers:
     layer.trainable = False

#vgg_model.summary()

last_layer = vgg_model.get_layer('block5_pool')
last_output = last_layer.output


x = layers.Flatten()(last_output)
x = layers.Dense(1024, activation='relu')(x)
x = layers.Dropout(0.2)(x)                  
x = layers.Dense(1, activation='sigmoid')(x)           

vgg_model = Model(vgg_model.input, x) 

#vgg_model.summary()

# Configure and compile the model
model.compile(loss='binary_crossentropy', optimizer = RMSprop(lr=0.0001), metrics=['accuracy'])

# Fit the model
model.fit(x=X, y=Y,validation_data=(X2,Y2),batch_size=10, epochs=11)

################
#POST MODELLING# 
################

def make_predictions(X,X2):
  
  train_pred = model.predict(X)
  test_pred = model.predict(X2)
  
  return train_pred,test_pred

# This rescales the data in train_pred, whose minimum and maximum are (train_pred.min(),train_pred.max()) to a scale whose min and max are (0,255)
# check_train=np.interp(train_pred, (train_pred.min(), train_pred.max()), (0,255))
# check_test = np.interp(test_pred, (test_pred.min(),test_pred.max()),(0,255))

# Because we are not predicting colorization, this below few lines doesnt make much sense..except maybe l_channel

# l_channel = X2[20]*255
# a_channel=check_test[20,:,:,0]
# b_channel=check_test[20,:,:,1]

# transfer = cv2.merge([l_channel, a_channel, b_channel])
# transfer = cv2.cvtColor(transfer.astype('uint8'), cv2.COLOR_LAB2BGR)

###############################
#MODEL OPTIONS: 2-simple vgg16#
###############################



##################
#MODEL EVALUATION#
##################

def eval_with_test(model):
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
