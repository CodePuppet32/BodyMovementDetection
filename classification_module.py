import time

import tensorflow as tf
import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
from copy import deepcopy

from PIL import ImageTk, Image

file_path = os.path.realpath(__file__)
file_path = os.path.dirname(file_path)
models_path = os.path.join(file_path, 'models')
model_weight_path = os.path.join(models_path, "fer.h5")
execution_path = os.path.join(file_path, "DetectedImage/")
model = tf.keras.models.load_model(model_weight_path)
expression_code_dict = {code: expression for code, expression in
                        enumerate(["angry","disgust","fear","happy","neutral","sad","surprise"])}

expression_code_genre_dict = {code: expression for code, expression in
                        enumerate(["anger","anger","dark","party","love","motivation","electronic"])}
faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


def save_detection(image):
    frame = deepcopy(image)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray, 1.1, 4)
    for x, y, w, h in faces:
        roi_gray = gray[y:y + h, x:x + w]
        roi_color = image[y:y + h, x:x + w]
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
        faces = faceCascade.detectMultiScale(roi_gray)
        if len(faces) == 0:
            print("Face not detected")
        else:
            for (ex, ey, ew, eh) in faces:
                face_roi = roi_color[ey: ey + eh, ex:ex + ew]

    if len(faces):
        final_image = cv2.resize(face_roi, (224, 224))
        final_image = np.expand_dims(final_image, axis=0)
        final_image = final_image / 255.0

        font = cv2.FONT_HERSHEY_PLAIN

        Predictions = model.predict(final_image)
        prediction_code = np.argmax(Predictions)
        status = expression_code_dict[prediction_code]
        print(status)

        x1, y1, w1, h1 = 0, 0, 175, 75
        # Draw black background rectangle
        cv2.rectangle(frame, (x1, x1), (x1 + w1, y1 + h1), (0, 0,), -1)
        # Add text
        cv2.putText(frame, status, (x1 + int(w1 / 10), y1 + int(h1 / 2)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, status, (100, 150), font, 3, (0, 0, 255), 2, cv2.LINE_4)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255))
        return expression_code_genre_dict[prediction_code], frame


    return None, None