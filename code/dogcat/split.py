from tensorflow import keras
from keras.applications import inception_v3
from keras.applications import resnet50
from keras.applications import mobilenet_v2
from keras.preprocessing.image import ImageDataGenerator
import h5py
import re

def write_gap(MODEL, image_size, preprocessing_input):
    width = image_size[0]
    height = image_size[1]
    input_tensor = keras.Input((height, width, 3))
    x = input_tensor
    base_model = MODEL(input_tensor=x, weights='imagenet', include_top=False, pooling='avg')
    model = keras.Model(inputs=base_model.input, outputs=base_model.output)

    gen = ImageDataGenerator(preprocessing_function=preprocessing_input)
    train_generator = gen.flow_from_directory("img_train", image_size, shuffle=False, classes=['cat', 'dog'], class_mode='sparse',
                                              batch_size=10)
    test_generator = gen.flow_from_directory("img_test", image_size, shuffle=False,
                                             batch_size=10, class_mode=None)
    filenames = test_generator.filenames
    index = [int(re.split('[/.]', name)[1]) for name in filenames]
    model.compile(
        loss='binary_crossentropy',
        optimizer='adam',
        metrics=['acc']
    )

    train = model.predict_generator(train_generator, verbose=1)
    test = model.predict_generator(test_generator, verbose=1)

    with h5py.File("gap_%s.h5"%MODEL.__name__) as h:
        h.create_dataset("train", data=train)
        h.create_dataset("test", data=test)
        h.create_dataset("label", data=train_generator.classes)
        h.create_dataset("index", data=index)

write_gap(inception_v3.InceptionV3, (299, 299), inception_v3.preprocess_input)

# write_gap(resnet50.ResNet50, (224, 224), resnet50.preprocess_input)

# write_gap(mobilenet_v2.MobileNetV2, (224, 224), mobilenet_v2.preprocess_input)
