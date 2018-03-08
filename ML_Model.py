"""
Initialization of the Machine Learning model;
author = hobin
"""
import json

import cv2
import numpy as np
import requests
import tensorflow as tf
import time
from PyQt5.QtCore import QThread, pyqtSignal
import traceback, sys

from datetime import datetime

from object_detection import visualization_utils_hobin as vis_util_hobin
from object_detection.utils import label_map_util

class Detection1(QThread):
    """
    It is used for detect products.
    """
    detected = pyqtSignal(object)

    def __init__(self, camera_object, parent=None):
        super(Detection1, self).__init__(parent)
        self.parent = parent
        self.capture = camera_object
        PATH_TO_CKPT = 'D:\\01PythonFile\\Project1\\object_detection\\output_inference_graph.pb\\frozen_inference_graph.pb'
        PATH_TO_LABELS = 'D:\\01PythonFile\\Project1\\object_detection\\output_inference_graph.pb\\pascal_label_map.pbtxt'
        NUM_CLASSES = 25
        # graph
        detection_graph = tf.Graph()
        with detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

        # labels
        label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
        categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
        self.category_index = label_map_util.create_category_index(categories)

        # -----------------------------------------------------------------------------------------------------------
        with detection_graph.as_default():
            gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.6)
            self.sess = tf.Session(graph=detection_graph, config=tf.ConfigProto(gpu_options=gpu_options))
            self.image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
            self.detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
            self.detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
            self.detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
            self.num_detections = detection_graph.get_tensor_by_name('num_detections:0')

        print('The initialization of ML model successes')


    def __del__(self):
        """The __del__ method requires the interpreter alive, but it seems no effect"""
        self.sess.close()
        del self.sess


    def run(self):
        """
        :return: a list of detected products;
        """
        print('ML Model begins')
        time.sleep(0.2)  # to ensure the image is stable;

        ret, image = self.capture.read()
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        image_np_expanded = np.expand_dims(image, axis=0)

        (boxes, scores, classes, num) = self.sess.run(
            [self.detection_boxes, self.detection_scores, self.detection_classes, self.num_detections],
            feed_dict={self.image_tensor: image_np_expanded})

        img, result = vis_util_hobin.visualize_boxes_and_labels_on_image_array(
            image,
            np.squeeze(boxes),
            np.squeeze(classes).astype(np.int32),
            np.squeeze(scores),
            self.category_index,
            use_normalized_coordinates=True,
            line_thickness=3)
        print("ML Model (end): %s" % result)
        self.detected.emit(result)


class Detection1_1(QThread):
    """
    It communicates with one server to detect the products;
    """
    detected = pyqtSignal(object)

    def __init__(self, camera_object, parent=None):
        super(Detection1_1, self).__init__(parent)
        self.parent = parent
        self.capture = camera_object
        self.url = 'http://192.168.20.78:5000/detect_goods'
        self.files = {'cam60_0': None}
        self.dict01 = {'utm_medium': 'cmBox',
                       'utm_source': 'pc',
                       'store_id': '2',
                       'table':'1',
                       'client_time': None}
        self.dict02 = {}  # the dictionary object of the first HTTP result


    def run(self):
        """
        :return: a list of detected products;
        """
        try:
            print('ML thread begins')
            time.sleep(0.2)  # to ensure the image is stable;
            ret, image = self.capture.read()
            ret, buffer = cv2.imencode('.jpg', image)
            self.files['cam60_0'] = buffer.tostring()
            self.dict01['client_time'] = str(int(datetime.now().timestamp()))
            resp01 = requests.post(self.url, files=self.files, data=self.dict01, timeout=3)
            if resp01.status_code == 200:
                self.dict02 = json.loads(resp01.text)
                # print(self.dict02)
                print(self.dict02['camera_list'][0]['item_list'])
                result = []
                for item in self.dict02['camera_list'][0]['item_list']:
                    result.append(item['class_id'])
                print("ML thread (end): %s" % result)
                self.detected.emit(result)
            else:
                print('ML thread (end): network problem.')

        except BaseException as e:
            print('Error is:\n',e)
            print('***------------------------Be careful! Error occurs in ML thread!------------------------***')


class Detection2(QThread):
    """
    It is used for detect the thumbs-up gesture.
    """
    detected = pyqtSignal(object)

    def __init__(self, parent=None):
        super(Detection2, self).__init__(parent)
        self.parent = parent
        self.frame = None
        PATH_TO_CKPT = 'D:\\01PythonFile\\tensorflow\\models-master\\research\\object_detection\\hand_rfcn_resnet101out\\output_inference_graph.pb\\frozen_inference_graph.pb'
        PATH_TO_LABELS = 'D:\\01PythonFile\\tensorflow\\models-master\\research\\object_detection\\data\\hand_label_map.pbtxt'
        NUM_CLASSES = 3
        # graph
        detection_graph = tf.Graph()
        with detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

        # labels
        label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
        categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
        self.category_index = label_map_util.create_category_index(categories)

        # -----------------------------------------------------------------------------------------------------------
        with detection_graph.as_default():
            gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.3)
            self.sess = tf.Session(graph=detection_graph, config=tf.ConfigProto(gpu_options=gpu_options))
            self.image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
            self.detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
            self.detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
            self.detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
            self.num_detections = detection_graph.get_tensor_by_name('num_detections:0')

        print('The initialization of ML model for hand detection successes')


    def __del__(self):
        """The __del__ method requires the interpreter alive, but it seems no effect"""
        self.sess.close()
        del self.sess


    def run(self):
        """
        :return: a list of hand gesture;
        """
        try:
            print('ML Model for hand detection begins')
            time.sleep(0.2)  # to ensure the image is stable;

            self.frame = self.parent.main_widget.mainlayout.rightlayout.secondlayout.thread1.frame
            image = cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR)
            image_np_expanded = np.expand_dims(image, axis=0)

            (boxes, scores, classes, num) = self.sess.run(
                [self.detection_boxes, self.detection_scores, self.detection_classes, self.num_detections],
                feed_dict={self.image_tensor: image_np_expanded})

            img, result = vis_util_hobin.visualize_boxes_and_labels_on_image_array(
                image,
                np.squeeze(boxes),
                np.squeeze(classes).astype(np.int32),
                np.squeeze(scores),
                self.category_index,
                use_normalized_coordinates=True,
                line_thickness=3)
            print("ML Model for hand detection (end): %s" % result)
            self.detected.emit(result)
        except BaseException:
            print(''.join(traceback.format_exception(*sys.exc_info())))


class Detection2_1(QThread):
    """
    It is used for detect the thumbs-up gesture.
    Compared with the Detection2 class, one main difference is the while loop in its run();
    """
    detected = pyqtSignal()

    def __init__(self, parent):
        super(Detection2_1, self).__init__(parent)
        self.parent = parent
        self.frame = None
        self.status = True
        PATH_TO_CKPT = 'D:\\01PythonFile\\tensorflow\\models-master\\research\\object_detection\\hand_rfcn_resnet101out\\output_inference_graph.pb\\frozen_inference_graph.pb'
        PATH_TO_LABELS = 'D:\\01PythonFile\\tensorflow\\models-master\\research\\object_detection\\data\\hand_label_map.pbtxt'
        NUM_CLASSES = 3
        # graph
        detection_graph = tf.Graph()
        with detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

        # labels
        label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
        categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
        self.category_index = label_map_util.create_category_index(categories)

        # -----------------------------------------------------------------------------------------------------------
        with detection_graph.as_default():
            gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.3)
            self.sess = tf.Session(graph=detection_graph, config=tf.ConfigProto(gpu_options=gpu_options))
            self.image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
            self.detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
            self.detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
            self.detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
            self.num_detections = detection_graph.get_tensor_by_name('num_detections:0')

        print('The initialization of ML model for hand detection successes')


    def __del__(self):
        """The __del__ method requires the interpreter alive, but it seems no effect"""
        self.sess.close()
        del self.sess


    def detecting_ThumbsUp(self):
        """
        It processes the frame of the camera and returns the result of the detection;
        the possible results are: 'GOOD', 'OTHER', 'OK'
        """
        self.frame = self.parent.main_widget.mainlayout.rightlayout.secondlayout.thread1.frame
        image = cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR)
        image_np_expanded = np.expand_dims(image, axis=0)

        (boxes, scores, classes, num) = self.sess.run(
            [self.detection_boxes, self.detection_scores, self.detection_classes, self.num_detections],
            feed_dict={self.image_tensor: image_np_expanded})

        img, result = vis_util_hobin.visualize_boxes_and_labels_on_image_array(
            image,
            np.squeeze(boxes),
            np.squeeze(classes).astype(np.int32),
            np.squeeze(scores),
            self.category_index,
            use_normalized_coordinates=True,
            line_thickness=3)
        return result


    def run(self):
        """
        :return: a list of hand gesture;
        """
        try:
            self.status = True
            while self.status:
                print('ML Model for hand detection begins')
                if self.parent.new_order_flag or self.parent.new_user_flag:
                    print('ML Model for hand detection (end): new order or new user at first time')
                    time.sleep(1)
                    continue
                first_result = self.detecting_ThumbsUp()
                if 'GOOD' in first_result:
                    print('ML Model for hand detection: successes to detect thumbs-up at first time.')
                    time.sleep(0.5)
                    if self.parent.new_order_flag or self.parent.new_user_flag:
                        print('ML Model for hand detection (end): new order or new user at second time')
                        time.sleep(1)
                        continue
                    second_result = self.detecting_ThumbsUp()
                    if 'GOOD' in second_result:
                        print('ML Model for hand detection (end): successes to detect thumbs-up at second time.')
                        self.status = False
                        self.detected.emit()
                    else:
                        print('ML Model for hand detection (end): cannot detect thumbs-up at second time.')
                        time.sleep(1)
                        continue
                else:
                    print('ML Model for hand detection (end): cannot detect thumbs-up at first time.')
                    time.sleep(1)
                    continue
            print('ML Model for hand detection ends')
        except BaseException:
            print(''.join(traceback.format_exception(*sys.exc_info())))


class Detection2_2(QThread):
    """
    It is used for detect the thumbs-up gesture.
    Compared with the Detection2 class, one main difference is the while loop in its run();
    """
    detected = pyqtSignal()

    def __init__(self, parent):
        super(Detection2_2, self).__init__(parent)
        self.parent = parent
        self.frame = None
        self.status = True
        PATH_TO_CKPT = 'D:\\01PythonFile\\tensorflow\\models-master\\research\\object_detection\\hand_rfcn_resnet101out\\output_inference_graph.pb\\frozen_inference_graph.pb'
        PATH_TO_LABELS = 'D:\\01PythonFile\\tensorflow\\models-master\\research\\object_detection\\data\\hand_label_map.pbtxt'
        NUM_CLASSES = 3
        # graph
        detection_graph = tf.Graph()
        with detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

        # labels
        label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
        categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
        self.category_index = label_map_util.create_category_index(categories)

        # -----------------------------------------------------------------------------------------------------------
        with detection_graph.as_default():
            gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.3)
            self.sess = tf.Session(graph=detection_graph, config=tf.ConfigProto(gpu_options=gpu_options))
            self.image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
            self.detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
            self.detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
            self.detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
            self.num_detections = detection_graph.get_tensor_by_name('num_detections:0')

        print('The initialization of ML model for hand detection successes')


    def __del__(self):
        """The __del__ method requires the interpreter alive, but it seems no effect"""
        self.sess.close()
        del self.sess


    def detecting_ThumbsUp(self):
        """
        It processes the frame of the camera and returns the result of the detection;
        the possible results are: 'GOOD', 'OTHER', 'OK'
        """
        _, self.frame = self.parent.user_interface.camera.read()
        image = cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR)
        image_np_expanded = np.expand_dims(image, axis=0)

        (boxes, scores, classes, num) = self.sess.run(
            [self.detection_boxes, self.detection_scores, self.detection_classes, self.num_detections],
            feed_dict={self.image_tensor: image_np_expanded})

        img, result = vis_util_hobin.visualize_boxes_and_labels_on_image_array(
            image,
            np.squeeze(boxes),
            np.squeeze(classes).astype(np.int32),
            np.squeeze(scores),
            self.category_index,
            use_normalized_coordinates=True,
            line_thickness=3)
        return result


    def run(self):
        """
        :return: a list of hand gesture;
        """
        try:
            self.status = True
            while self.status:
                print('ML Model for hand detection begins')
                if self.parent.new_order_flag or self.parent.new_user_flag:
                    print('ML Model for hand detection (end): new order or new user at first time')
                    time.sleep(1)
                    continue
                first_result = self.detecting_ThumbsUp()
                if 'GOOD' in first_result:
                    print('ML Model for hand detection: successes to detect thumbs-up at first time.')
                    time.sleep(0.5)
                    if self.parent.new_order_flag or self.parent.new_user_flag:
                        print('ML Model for hand detection (end): new order or new user at second time')
                        time.sleep(1)
                        continue
                    second_result = self.detecting_ThumbsUp()
                    if 'GOOD' in second_result:
                        print('ML Model for hand detection (end): successes to detect thumbs-up at second time.')
                        self.status = False
                        self.detected.emit()
                    else:
                        print('ML Model for hand detection (end): cannot detect thumbs-up at second time.')
                        time.sleep(1)
                        continue
                else:
                    print('ML Model for hand detection (end): cannot detect thumbs-up at first time.')
                    time.sleep(1)
                    continue
            print('ML Model for hand detection ends')
        except BaseException:
            print(''.join(traceback.format_exception(*sys.exc_info())))


if __name__ == '__main__':
    cap = cv2.VideoCapture(1)
    a = Detection1_1(camera_object=cap)
    while True:
        a.start()
        time.sleep(2)


