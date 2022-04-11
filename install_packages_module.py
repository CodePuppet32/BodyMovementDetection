import urllib3
import os
import shutil

try:
    import cv2
    import tensorflow
    import PIL
    import keras
except ModuleNotFoundError:
    required_modules = ['opencv-python==4.5.5.64', 'tensorflow==2.8.0', 'pillow==9.1.0', 'keras==2.8.0']
    for required_module in required_modules:
        os.system('pip install {}'.format(required_module))

resnet_model_path = 'models\\resnet50_coco_best_v2.1.0.h5'
os.mkdir('models')
if not os.path.exists(resnet_model_path):
    url = 'https://github.com/fizyr/keras-retinanet/releases/download/0.5.1/resnet50_coco_best_v2.1.0.h5'
    model_name = 'resnet50_coco_best_v2.1.0.h5'
    c = urllib3.PoolManager()

    with c.request('GET', url, preload_content=False) as resp, open(resnet_model_path, 'wb') as out_file:
        shutil.copyfileobj(resp, out_file)