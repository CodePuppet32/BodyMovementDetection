from imageai.Detection import ObjectDetection

model_weight_path = "models/resnet50_coco_best_v2.1.0.h5"
execution_path = "DetectedImage/"
detector = ObjectDetection()
detector.setModelTypeAsRetinaNet()
detector.setModelPath(model_weight_path)
detector.loadModel(detection_speed='flash')


def save_detection(minimum_probability, image, save_path):
    detector.detectObjectsFromImage(input_image=image,
                                    input_type='np_array',
                                    output_image_path=save_path,
                                    minimum_percentage_probability=minimum_probability)
