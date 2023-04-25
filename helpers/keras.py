from tensorflow import keras


def get_model_input_shape(model: keras.models.Model):
    _, levels, length, channels = model.get_config()['layers'][0]['config']['batch_input_shape']
    return levels, length


def get_model_output_shape(model: keras.models.Model):
    return model.output_shape[1]
