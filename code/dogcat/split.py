
#%%
from __future__ import print_function
from tensorflow import keras
import h5py

ImageDataGenerator = keras.preprocessing.image.ImageDataGenerator
GlobalAveragePooling2D = keras.layers.GlobalAveragePooling2D
Input = keras.Input
InceptionV3 = keras.applications.InceptionV3
ResNet50 = keras.applications.ResNet50
Xception = keras.applications.Xception
Model = keras.Model
resnet_input = keras.applications.resnet50.preprocess_input
inception_input = keras.applications.inception_v3.preprocess_input
xception_input = keras.applications.xception.preprocess_input

def write_gap(MODEL, image_size, preprocessing_input):
    width = image_size[0]
    height = image_size[1]
    input_tensor = Input((height, width, 3))
    x = input_tensor
    base_model = MODEL(input_tensor=x, weights='imagenet', include_top=False, pooling='avg')
    model = Model(inputs=base_model.input, outputs=base_model.output)
    
    gen = ImageDataGenerator(preprocessing_function=preprocessing_input)
    train_generator = gen.flow_from_directory("img_train", image_size, shuffle=False, classes=['cat', 'dog'], class_mode='sparse',
                                              batch_size=50)
    test_generator = gen.flow_from_directory("img_test", image_size, shuffle=False,
                                             batch_size=50, class_mode=None)
    model.compile(
        loss='binary_crossentropy',
        optimizer='adam',
        metrics=['acc']
    )
    print(test_generator.index_generator)
    # train = model.predict_generator(train_generator, verbose=1)
    # test_generator.reset()
    # test = model.predict_generator(test_generator, verbose=1)

    # with h5py.File("gap_%s.h5"%MODEL.__name__) as h:
    #     h.create_dataset("train", data=train)
    #     h.create_dataset("test", data=test)
    #     h.create_dataset("label", data=train_generator.classes)

# write_gap(InceptionV3, (299, 299), inception_input)
# #%%
# write_gap(Xception, (299, 299), xception_input)
#%%
write_gap(ResNet50, (224, 224), resnet_input)

