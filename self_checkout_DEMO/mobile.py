from keras.applications.mobilenet import MobileNet
model = MobileNet(weights="imagenet")

from keras.preprocessing.image import load_img, img_to_array
import numpy as np
from keras.applications.mobilenet import preprocess_input, decode_predictions

img = load_img("elephant.jpg", target_size=(224,224))
img_array = img_to_array(img)
img_array1 = np.expand_dims(img_array,axis=0)
img_array1 = preprocess_input(img_array1)
pred = model.predict(img_array1)
results = decode_predictions(pred,top=5)[0]
for result in results:
         print(result)

         ('n01871265', 'tusker', 0.8331707)
         ('n02504458', 'African_elephant', 0.13779889)
         ('n02504013', 'Indian_elephant', 0.02774448)
         ('n02437312', 'Arabian_camel', 0.00064588425)
         ('n02113799', 'Standard_poodle', 0.00016444316)
