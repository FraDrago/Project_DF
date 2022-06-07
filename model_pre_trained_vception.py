# -*- coding: utf-8 -*-
"""Model_pre-trained-Xception.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1_CFGbhDM7HSgL0Jr90rf25-kP5CuQXF5
"""

import tensorflow as tf
from tensorflow import keras
import matplotlib.pyplot as plt
import numpy as np
from sklearn.utils import shuffle

from tensorflow.keras.applications.inception_v3 import InceptionV3
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import Model
from tensorflow.keras import layers
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.preprocessing.image import ImageDataGenerator

import os
import cv2

train_path="C:/Users/Franc/OneDrive/Desktop/PROGETTO/Dataset/PeopleFace"

##I extract images from the folders and create the dataset train_x
x_train=[]

for folder in sorted(os.listdir(train_path)):

    sub_path=train_path+"/"+folder
    print(sub_path)

    for img in os.listdir(sub_path):

        image_path=sub_path+"/"+img

        img_arr=cv2.imread(image_path)

        img_arr=cv2.resize(img_arr,(256,256))

        x_train.append(img_arr)

train_x=np.array(x_train)

from keras.preprocessing.image import ImageDataGenerator

train_datagen = ImageDataGenerator(rescale = 1./255)
training_set = train_datagen.flow_from_directory(train_path,
                                                 target_size = (224, 224),
                                                 batch_size = 32,
                                                 class_mode = 'sparse')

train_y=training_set.classes

label_ids= training_set.class_indices


def plot_images(images, labels, predictions=None, class_names=None):
    assert len(images) == len(labels) == 9
    
    # Create figure with 3x3 sub-plots.
    fig, axes = plt.subplots(3, 3, figsize=(20, 20))
    fig.subplots_adjust(hspace=0.3, wspace=0.3)
    
    for i, ax in enumerate(axes.flat):
        
        # Plot image.
        ax.imshow(images[i].squeeze(), cmap='gray')
        
        # Show true and predicted classes.
        if predictions is None:
            xlabel = "True: {0}".format(class_names[int(labels[i])])
        else:
            xlabel = "True: {0}, Pred: {1}".format(class_names[int(labels[i])],
            class_names[int(predictions[i].argmax())])

        ax.set_xlabel(xlabel)
        
        # Remove ticks from the plot.
        ax.set_xticks([])
        ax.set_yticks([])
    
    # Ensure the plot is shown correctly with multiple plots
    # in a single Notebook cell.
    plt.show()

class_names = {value:key for key, value in label_ids.items()}
"""
plot_images(  #plot image in BGR format
    train_x[[1, 300, 600, 900, 1200, 1500, 1800, 2100, 2400]],
    train_y[[1, 300, 600, 900, 1200, 1500, 1800, 2100, 2400]],
    predictions=None,
    class_names=class_names
)
"""

#shuffle sets using the shuffle function from sklearn (provided above)
train_x, train_y = shuffle(train_x, train_y, random_state=1)
#create test set
from sklearn.model_selection import train_test_split
train_x, test_x, train_y, test_y = train_test_split(train_x, train_y, test_size=0.33, random_state=1)

train_labels = train_y
train_images = train_x

test_labels = test_y
test_images = test_x


# Normalization
train_images = train_images / 255.0
test_images = test_images/255.0
################# code here ###################

#Onehot Encoding the labels.
from tensorflow.keras.utils import to_categorical
train_labels=to_categorical(train_labels)
test_labels=to_categorical(test_labels)


# Number of samples and image dimension (images are squared)
num_samples = train_x.shape[0]
img_shape = train_x.shape[1]

print(num_samples)
print(img_shape)

np.random.seed(1000)

num_classes = 13

#######CREATION OF THE MODEL#################
# create the base pre-trained model
base_model = tf.keras.applications.InceptionV3(include_top=False, weights="imagenet", input_shape=(256, 256, 3))


# get the layer with output shape None 14 14
lastlayer = base_model.get_layer('mixed7')
old_output = lastlayer.output

# Flatten the output layer for remove all of the dimensions except for one.
x = layers.Flatten()(old_output)
# let's add a fully-connected layer
x = Dense(1024, activation='relu')(x)
# and a logistic layer -- let's say we have 200 classes
predictions = Dense(num_classes, activation='softmax')(x)

# this is the model we will train
model = Model(inputs=base_model.input, outputs=predictions)

model.summary()
#######END CREATION OF THE MODEL#################

# first: train only the top layers (which were randomly initialized)
# i.e. freeze all convolutional InceptionV3 layers
for layer in base_model.layers:
    layer.trainable = False

# compile the model (should be done *after* setting layers to non-trainable)
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

#balance class weights for imbalanced classes
#https://stackoverflow.com/questions/42586475/is-it-possible-to-automatically-infer-the-class-weight-from-flow-from-directory
from collections import Counter
newLabels = Counter()
for label in train_labels:
    for idx, key in enumerate(label):
         newLabels[idx]+=key
print("counter", newLabels)                             
max_val = float(max(newLabels.values()))  
class_weights = {class_id : max_val/num_images for class_id, num_images in newLabels.items()} 
print("class weights:", class_weights)


# train the model on the new data for a few epochs
history = model.fit(train_images, train_labels, 
                    batch_size = 32, epochs=10, validation_split = 0.2, class_weight=class_weights)


train_images, test_images, train_labels, test_labels
print("shape train_images: ", train_images.shape)
print("shape test_images: ", test_images.shape)
print("shape train_labels: ", train_labels.shape)
print("shape test_labels: ", test_labels.shape)
test_loss, test_acc = model.evaluate(test_images, test_labels)

print('Test accuracy:', test_acc)

print('Test loss:', test_loss)

print("test_images type: ", type(test_images))
print("test_labels type: ", type(test_labels))
print("test_images shape: ", test_images.shape)
print("test_labels shape: ", test_labels.shape)

from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
predictions = model.predict(test_x)
print("AAAAAAAAAAAAA")

cm = confusion_matrix(y_true=test_y, y_pred=np.argmax(predictions,axis=1))
print("BBBBBBBBB")

print(cm)
print("CCCCCCCCC")

plot_images(test_x[:9], test_y[:9], model.predict(test_x[:9]), class_names)




tf.keras.models.save_model(model, 'D:/Project_DF/Vception_Classifier_retrain.h5')
