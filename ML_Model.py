"""
Initialization of the Machine Learning model;
author = hobin;
email = '627227669@qq.com';
"""
import json

import cv2
import numpy as np
import requests
import tensorflow as tf
import time
from PyQt5.QtCore import QThread, pyqtSignal
import traceback, sys
import logging
from datetime import datetime

from object_detection import visualization_utils_hobin as vis_util_hobin
from object_detection.utils import label_map_util

class Detection_Test(object):
    def __init__(self):
        PATH_TO_CKPT = 'D:\\01PythonFile\\Brindley\\object_detection\\output_inference_graph.pb\\frozen_inference_graph.pb'
        PATH_TO_LABELS = 'D:\\01PythonFile\\Brindley\\object_detection\\output_inference_graph.pb\\pascal_label_map.pbtxt'
        NUM_CLASSES = 25
        cap = cv2.VideoCapture(1)
        cap.set(3, 800)
        cap.set(4, 640)
        ## graph
        detection_graph = tf.Graph()
        with detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

        ## labels
        label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
        categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES,
                                                                    use_display_name=True)
        category_index = label_map_util.create_category_index(categories)

        # -----------------------------------------------------------------------------------------------------------
        with detection_graph.as_default():
            # deploy_config = model_deploy.DeploymentConfig(num_clones=2,clone_on_cpu=False)
            with tf.Session(graph=detection_graph) as sess:
                image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
                detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
                detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
                detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
                num_detections = detection_graph.get_tensor_by_name('num_detections:0')
                # ----------------------------------------------------------------------------------------------------
                while True:
                    ret, image = cap.read()
                    # image = image[500:1000,500:1000]
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                    image_np_expanded = np.expand_dims(image, axis=0)

                    (boxes, scores, classes, num) = sess.run(
                        [detection_boxes, detection_scores, detection_classes, num_detections],
                        feed_dict={image_tensor: image_np_expanded})

                    img, result = vis_util_hobin.visualize_boxes_and_labels_on_image_array(
                        image,
                        np.squeeze(boxes),
                        np.squeeze(classes).astype(np.int32),
                        np.squeeze(scores),
                        category_index,
                        use_normalized_coordinates=True,
                        line_thickness=3)

                    print(result)
                    cv2.imshow('a', cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                    if cv2.waitKey(10) & 0xFF == ord('q'):
                        break


class Detection1(QThread):
    """
    It is used for detect products.
    """
    detected = pyqtSignal(object)

    def __init__(self, camera_object, parent=None):
        super(Detection1, self).__init__(parent)
        self.parent = parent
        self.capture = camera_object
        PATH_TO_CKPT = 'D:\\01PythonFile\\Brindley\\object_detection\\output_inference_graph.pb\\frozen_inference_graph.pb'
        PATH_TO_LABELS = 'D:\\01PythonFile\\Brindley\\object_detection\\output_inference_graph.pb\\pascal_label_map.pbtxt'
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


class Detection1_2(QThread):
    """
    It is used for detect products.
    Compared with the Detection1 class, the difference is emitting the image after the successful detection.
    """
    detected = pyqtSignal(object)
    upload_img = pyqtSignal(object, object)

    def __init__(self, camera_object, logger_name='hobin',parent=None):
        super(Detection1_2, self).__init__(parent)
        self.parent = parent
        self.capture = camera_object
        PATH_TO_CKPT = 'D:\\01PythonFile\\Brindley\\object_detection\\output_inference_graph.pb\\frozen_inference_graph.pb'
        PATH_TO_LABELS = 'D:\\01PythonFile\\Brindley\\object_detection\\output_inference_graph.pb\\pascal_label_map.pbtxt'
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
        image2 = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        image_np_expanded = np.expand_dims(image2, axis=0)

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
        detect_time = datetime.now()
        self.upload_img.emit(image, detect_time)
        self.detected.emit(result)


class Detection1_2_1(QThread):
    """
    It is used for detect products.
    Compared with the Detection1_2 class, the logging module is introduced to this module at first time.
    Compared with the Detection1 class, the difference is emitting the image after the successful detection.
    Compared with the Detection1 class, the __del__ function is removed.
    """
    detected = pyqtSignal(object)
    upload_img = pyqtSignal(object, object)

    def __init__(self, camera_object, logger_name='hobin', *,
                 path_to_ckpt = 'D:\\01PythonFile\\Brindley\\object_detection\\output_inference_graph.pb\\frozen_inference_graph.pb',
                 path_to_labels = 'D:\\01PythonFile\\Brindley\\object_detection\\output_inference_graph.pb\\pascal_label_map.pbtxt',
                 num_classes=25, parent=None, **kwargs):
        super(Detection1_2_1, self).__init__(parent)
        # the first way to configuring the parameters, almost all parameters get their value from those named keyword arguments.
        PATH_TO_CKPT = path_to_ckpt
        PATH_TO_LABELS = path_to_labels
        NUM_CLASSES = int(num_classes)

        # the second way to configure the parameters, almost all parameters get their value from the keyword argument 'kwargs'.
        # PATH_TO_CKPT = kwargs['PATH_TO_CKPT']
        # PATH_TO_LABELS = kwargs['PATH_TO_LABELS']
        # NUM_CLASSES = int(kwargs['NUM_CLASSES'])

        # some variables
        self.parent = parent
        self.capture = camera_object
        self.mylogger1_2_1 = logging.getLogger(logger_name)
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

        # print('The initialization of ML model successes')
        self.mylogger1_2_1.info('The initialization of ML model successes')


    def run(self):
        """
        :return: a list of detected products;
        """
        # print('ML Model begins')
        self.mylogger1_2_1.info('ML Model begins')
        time.sleep(0.2)  # to ensure the image is stable;

        ret, image = self.capture.read()
        image2 = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        image_np_expanded = np.expand_dims(image2, axis=0)

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
        # print("ML Model (end): %s" % result)
        self.mylogger1_2_1.info("ML Model (end): %s" % result)
        detect_time = datetime.now()
        self.upload_img.emit(image, detect_time)
        self.detected.emit(result)
        

class Detection1_2_2(QThread):
    """
    It is used for detect products.
    The Detection1_2_2 class firstly compares the length of current result and then compare the current result and the last result.
    Compared with the Detection1_2 class, the logging module is introduced to this module at first time.
    Compared with the Detection1 class, the difference is emitting the image after the successful detection.
    Compared with the Detection1 class, the __del__ function is removed.
    Compared with the Detection1_2_1 class, the Detection1_2_2 class will require the current detected result must not be empty.
    """
    detected = pyqtSignal(object)
    detect_same = pyqtSignal()
    detect_empty_same = pyqtSignal()  # the current result and the last result is empty
    detect_empty_diff = pyqtSignal()  # the current result is empty but the last result is not empty
    upload_img = pyqtSignal(object, object)

    def __init__(self, camera_object, logger_name='hobin', *,
                 path_to_ckpt = 'D:\\01PythonFile\\Brindley\\object_detection\\output_inference_graph.pb\\frozen_inference_graph.pb',
                 path_to_labels='D:\\01PythonFile\\Brindley\\object_detection\\output_inference_graph.pb\\pascal_label_map.pbtxt',
                 num_classes=25, parent=None, **kwargs):
        super(Detection1_2_2, self).__init__(parent)
        # the first way to configuring the parameters, almost all parameters get their value from those named keyword arguments.
        PATH_TO_CKPT = path_to_ckpt
        PATH_TO_LABELS = path_to_labels
        NUM_CLASSES = int(num_classes)

        # the second way to configure the parameters, almost all parameters get their value from the keyword argument 'kwargs'.
        # PATH_TO_CKPT = kwargs['PATH_TO_CKPT']
        # PATH_TO_LABELS = kwargs['PATH_TO_LABELS']
        # NUM_CLASSES = int(kwargs['NUM_CLASSES'])

        # some variables
        self.parent = parent
        self.capture = camera_object
        self.mylogger1_2_2 = logging.getLogger(logger_name)
        self.last_result = []  # assuming the last result is empty at the beginning. It will be used in the operation '=='.
        self.current_result = None
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

        # print('The initialization of ML model successes')
        self.mylogger1_2_2.info('The initialization of ML model successes')


    def run(self):
        """
        :return: a list of detected products;
        """
        # print('ML Model begins')
        self.mylogger1_2_2.info('ML Model begins')
        time.sleep(0.2)  # to ensure the image is stable;

        ret, image = self.capture.read()
        image2 = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        image_np_expanded = np.expand_dims(image2, axis=0)

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

        if len(result) == 0:
            if len(self.last_result) == 0:
                # self.mylogger1_2_2.debug('ML Model: the current result and the last result are empty.')
                self.detect_empty_same.emit()
            else:
                # the current detected result is empty and the last result is not empty.
                self.last_result = []  # refreshing the last result.
                # self.mylogger1_2_2.debug('ML Model: the current result is empty and the last result is not.')
                self.detect_empty_diff.emit()
        else:
            self.current_result = sorted([int(item) for item in result])  # if using list.sort(), it does not return a new list.
            if self.last_result == self.current_result:
                # self.mylogger1_2_2.debug('ML Model: the current result is not empty and both are same.')
                self.detect_same.emit()
            else:
                # using self.last_result = self.current_result[:] to ensure there is a new list for self.last_result.
                self.last_result = self.current_result
                detect_time = datetime.now()
                # self.mylogger1_2_2.debug('ML Model: the current result is not empty and both are different.')
                self.upload_img.emit(image, detect_time)
                self.detected.emit(result)

        # print("ML Model (end): %s" % result)
        self.mylogger1_2_2.info("ML Model (end): %s" % result)


class Detection1_2_3(QThread):
    """
    It is used for detect products.
    Compared with the Detection1_2 class, the logging module is introduced to this module at first time.
    Compared with the Detection1 class, the difference is emitting the image after the successful detection.
    Compared with the Detection1 class, the __del__ function is removed.
    Compared with the Detection1_2_1 class, the Detection1_2_2 class will require the current detected result must not be empty.
    Compared with the Detection1_2_2, the Detection1_2_3 class compares the current result and last result directly since the Model will easily detects nothing.
    """
    detected = pyqtSignal(object)
    detect_same = pyqtSignal()
    detect_empty_same = pyqtSignal()  # the current result and the last result is empty
    detect_empty_diff = pyqtSignal()  # the current result is empty but the last result is not empty
    upload_img = pyqtSignal(object, object)

    def __init__(self, camera_object, logger_name='hobin', *,
                 path_to_ckpt = 'D:\\01PythonFile\\Brindley\\object_detection\\output_inference_graph.pb\\frozen_inference_graph.pb',
                 path_to_labels='D:\\01PythonFile\\Brindley\\object_detection\\output_inference_graph.pb\\pascal_label_map.pbtxt',
                 num_classes=25, parent=None, **kwargs):
        super(Detection1_2_3, self).__init__(parent)
        # the first way to configuring the parameters, almost all parameters get their value from those named keyword arguments.
        PATH_TO_CKPT = path_to_ckpt
        PATH_TO_LABELS = path_to_labels
        NUM_CLASSES = int(num_classes)

        # the second way to configure the parameters, almost all parameters get their value from the keyword argument 'kwargs'.
        # PATH_TO_CKPT = kwargs['PATH_TO_CKPT']
        # PATH_TO_LABELS = kwargs['PATH_TO_LABELS']
        # NUM_CLASSES = int(kwargs['NUM_CLASSES'])

        # some variables
        self.parent = parent
        self.capture = camera_object
        self.mylogger1_2_3 = logging.getLogger(logger_name)
        self.last_result = []  # assuming the last result is empty at the beginning. It will be used in the operation '=='.
        self.current_result = None
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

        # print('The initialization of ML model successes')
        self.mylogger1_2_3.info('The initialization of ML model successes')


    def run(self):
        """
        :return: a list of detected products;
        """
        # print('ML Model begins')
        self.mylogger1_2_3.info('ML Model begins')
        time.sleep(0.2)  # to ensure the image is stable;

        ret, image = self.capture.read()
        image2 = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        image_np_expanded = np.expand_dims(image2, axis=0)

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

        self.current_result = sorted(
            [int(item) for item in result])  # if using list.sort(), it does not return a new list.
        if self.last_result == self.current_result:
            # self.mylogger1_2_3.debug('ML Model: the current result is not empty and both are same.')
            self.detect_same.emit()
        else:
            # using self.last_result = self.current_result[:] to ensure there is a new list for self.last_result.
            self.last_result = self.current_result
            detect_time = datetime.now()
            # self.mylogger1_2_3.debug('ML Model: the current result is not empty and both are different.')
            self.upload_img.emit(image, detect_time)
            self.detected.emit(result)

        # print("ML Model (end): %s" % result)
        self.mylogger1_2_3.info("ML Model (end): %s" % result)


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
                    time.sleep(0.2)
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
    Compared with the Detection2_1 class, the main difference is the way to refresh the camera frame (using QML object);
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


class Detection2_3(QThread):
    """
    It is used for detect the thumbs-up gesture.
    Compared with the Detection2_1 class, the main difference is the logical part. It only checks the new order flag.
    Another change is the refresh of the frame since the main layout changes (using mainlyaout_ZHY file).
    """
    detected = pyqtSignal()

    def __init__(self, parent):
        super(Detection2_3, self).__init__(parent)
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
        self.frame = self.parent.main_widget.rightlayout.firstlayout.camera_img.thread1.frame
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
                if self.parent.new_order_flag:
                    print('ML Model for hand detection (end): new order at first time')
                    time.sleep(2)
                    continue
                first_result = self.detecting_ThumbsUp()
                if 'GOOD' in first_result:
                    print('ML Model for hand detection: successes to detect thumbs-up at first time.')
                    time.sleep(0.5)
                    if self.parent.new_order_flag:
                        print('ML Model for hand detection (end): new order at second time')
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


class Detection2_3_1(QThread):
    """
    It is used for detect the thumbs-up gesture.
    Compared with the Detection2 class, one main difference is the while loop in its run();
    Compared with the Detection2_1 class, the main difference is the logical part. It only checks the new order flag.
    Another change is the refresh of the frame since the main layout changes (using mainlyaout_ZHY file).
    Compared with the Detection2_3 class, the difference is emitting the image after the successful detection for upload;
    Compared with the Detection2_3 class, the logging module is introduced to the Detection2_3_1 class;
    Compared with the Detection2_3 class, the __del__ function is removed;
    Compared with the Detection2_3 class, the order number is stored after the successful gesture detection to ensure that the order number is correct;
    """
    detected = pyqtSignal()
    upload_image = pyqtSignal(object, object)

    def __init__(self, parent, logger_name='hobin', *,
                 path_to_ckpt = 'D:\\01PythonFile\\tensorflow\\models-master\\research\\object_detection\\hand_rfcn_resnet101out\\output_inference_graph.pb\\frozen_inference_graph.pb',
                 path_to_labels = 'D:\\01PythonFile\\tensorflow\\models-master\\research\\object_detection\\data\\hand_label_map.pbtxt',
                 num_classes = 3,  **kwargs):
        super(Detection2_3_1, self).__init__(parent)
        # the first way to configuring the parameters, almost all parameters get their value from those named keyword arguments.
        PATH_TO_CKPT = path_to_ckpt
        PATH_TO_LABELS = path_to_labels
        NUM_CLASSES = int(num_classes)

        # the second way to configure the parameters, almost all parameters get their value from the keyword argument 'kwargs'.
        # PATH_TO_CKPT = kwargs['PATH_TO_CKPT']
        # PATH_TO_LABELS = kwargs['PATH_TO_LABELS']
        # NUM_CLASSES = int(kwargs['NUM_CLASSES'])

        # some variables
        self.parent = parent
        self.frame = None
        self.status = True
        self.order_number = 'invalid'
        self.mylogger2_3_1 = logging.getLogger(logger_name)
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

        # print('The initialization of ML model for hand detection successes')
        self.mylogger2_3_1.info('The initialization of ML model for hand detection successes')


    def detecting_ThumbsUp(self):
        """
        It processes the frame of the camera and returns the result of the detection;
        the possible results are: 'GOOD', 'OTHER', 'OK'
        """
        self.frame = self.parent.main_widget.rightlayout.firstlayout.camera_img.thread1.frame
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
                # print('ML Model for hand detection begins')
                self.mylogger2_3_1.info('ML Model for hand detection begins')
                if self.parent.new_order_flag:
                    # print('ML Model for hand detection (end): new order at first time')
                    self.mylogger2_3_1.info('ML Model for hand detection (end): new order at first time')
                    time.sleep(1)
                    continue
                first_result = self.detecting_ThumbsUp()
                if 'GOOD' in first_result:
                    # print('ML Model for hand detection: successes to detect thumbs-up at first time.')
                    self.mylogger2_3_1.info('ML Model for hand detection: successes to detect thumbs-up at first time.')
                    time.sleep(0.2)
                    if self.parent.new_order_flag:
                        # print('ML Model for hand detection (end): new order at second time')
                        self.mylogger2_3_1.info('ML Model for hand detection (end): new order at second time')
                        time.sleep(1)
                        continue
                    second_result = self.detecting_ThumbsUp()
                    if 'GOOD' in second_result:
                        # print('ML Model for hand detection (end): successes to detect thumbs-up at second time.')
                        self.order_number = self.parent.thread6.dict02['data']['order_no']
                        self.mylogger2_3_1.info('ML Model for hand detection (end): successes to detect thumbs-up at second time.')
                        self.status = False
                        detect_time = datetime.now()
                        self.upload_image.emit(self.frame, detect_time)
                        self.detected.emit()
                    else:
                        # print('ML Model for hand detection (end): cannot detect thumbs-up at second time.')
                        self.mylogger2_3_1.info('ML Model for hand detection (end): cannot detect thumbs-up at second time.')
                        time.sleep(1)
                        continue
                else:
                    # print('ML Model for hand detection (end): cannot detect thumbs-up at first time.')
                    self.mylogger2_3_1.info('ML Model for hand detection (end): cannot detect thumbs-up at first time.')
                    time.sleep(1)
                    continue
            # print('ML Model for hand detection ends')
            self.mylogger2_3_1.info('ML Model for hand detection ends')
        except BaseException as e:
            self.mylogger2_3_1.error(e)
            self.mylogger2_3_1.error('***------------------------Be careful! Error occurs in ml item thread!------------------------***')


class Detection2_3_1_klas(Detection2_3_1):
    """The camera frame is refreshed by the qml widget"""
    def __init__(self, parent, **kwargs):
        super(Detection2_3_1_klas, self).__init__(parent=parent, **kwargs)

    def detecting_ThumbsUp(self):
        ret, self.frame = self.parent.main_window.getCamera().read()
        # self.frame = self.parent.main_window.getCamrea()._frame
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


class Detection2_3_2(QThread):
    """
    It is used for detect the thumbs-up gesture.
    Compared with the Detection2 class, one main difference is the while loop in its run();
    Compared with the Detection2_1 class, the main difference is the logical part. It only checks the new order flag.
    Another change is the refresh of the frame since the main layout changes (using mainlyaout_ZHY file).
    Compared with the Detection2_3_1 class, it emits the frame and the position information about the gesture after successful detection;
    """
    detected = pyqtSignal()
    detected_gesture_info = pyqtSignal(object, object) # frame, gesture location information
    upload_image = pyqtSignal(object, object)

    def __init__(self, parent, logger_name='hobin', *,
                 path_to_ckpt = 'D:\\01PythonFile\\tensorflow\\models-master\\research\\object_detection\\hand_rfcn_resnet101out\\output_inference_graph.pb\\frozen_inference_graph.pb',
                 path_to_labels = 'D:\\01PythonFile\\tensorflow\\models-master\\research\\object_detection\\data\\hand_label_map.pbtxt',
                 num_classes = 3,  **kwargs):
        super(Detection2_3_2, self).__init__(parent)
        # the first way to configuring the parameters, almost all parameters get their value from those named keyword arguments.
        PATH_TO_CKPT = path_to_ckpt
        PATH_TO_LABELS = path_to_labels
        NUM_CLASSES = int(num_classes)

        # the second way to configure the parameters, almost all parameters get their value from the keyword argument 'kwargs'.
        # PATH_TO_CKPT = kwargs['PATH_TO_CKPT']
        # PATH_TO_LABELS = kwargs['PATH_TO_LABELS']
        # NUM_CLASSES = int(kwargs['NUM_CLASSES'])

        # some variables
        self.parent = parent
        self.frame = None
        self.status = True
        self.order_number = 'invalid'
        self.mylogger2_3_2 = logging.getLogger(logger_name)
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

        # print('The initialization of ML model for hand detection successes')
        self.mylogger2_3_2.info('The initialization of ML model for hand detection successes')

    def detecting_ThumbsUp(self):
        """
        It processes the frame of the camera and returns the result of the detection;
        the possible results are: 'GOOD', 'OTHER', 'OK'
        """
        self.frame = self.parent.main_widget.rightlayout.firstlayout.camera_img.thread1.frame
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


    def detecting_ThumbsUp_withLocation(self):
        """
        It processes the frame of the camera and returns the result of the detection;
        the possible results are: 'GOOD', 'OTHER', 'OK'
        the element of the 'result_location' list is a tuple consisting of (xmin, ymin, xmax, ymax)
        """
        self.frame = self.parent.main_widget.rightlayout.firstlayout.camera_img.thread1.frame
        image = cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR)
        image_np_expanded = np.expand_dims(image, axis=0)

        (boxes, scores, classes, num) = self.sess.run(
            [self.detection_boxes, self.detection_scores, self.detection_classes, self.num_detections],
            feed_dict={self.image_tensor: image_np_expanded})

        img, result, result_location = vis_util_hobin.visualize_boxes_and_labels_on_image_array_klas(
            image,
            np.squeeze(boxes),
            np.squeeze(classes).astype(np.int32),
            np.squeeze(scores),
            self.category_index,
            use_normalized_coordinates=True,
            line_thickness=3)
        return result, result_location


    def run(self):
        """
        :return: a list of hand gesture;
        """
        try:
            self.status = True
            while self.status:
                # print('ML Model for hand detection begins')
                self.mylogger2_3_2.info('ML Model for hand detection begins')
                if self.parent.new_order_flag:
                    # print('ML Model for hand detection (end): new order at first time')
                    self.mylogger2_3_2.info('ML Model for hand detection (end): new order at first time')
                    time.sleep(1)
                    continue
                first_result = self.detecting_ThumbsUp()
                if 'GOOD' in first_result:
                    # print('ML Model for hand detection: successes to detect thumbs-up at first time.')
                    self.mylogger2_3_2.info('ML Model for hand detection: successes to detect thumbs-up at first time.')
                    time.sleep(0.2)
                    if self.parent.new_order_flag:
                        # print('ML Model for hand detection (end): new order at second time')
                        self.mylogger2_3_2.info('ML Model for hand detection (end): new order at second time')
                        time.sleep(1)
                        continue
                    second_result, second_result_location = self.detecting_ThumbsUp_withLocation()
                    if 'GOOD' in second_result:
                        for index, detected_result in enumerate(second_result):
                            if detected_result == 'GOOD':
                                self.order_number = self.parent.thread6.dict02['data']['order_no']
                                self.mylogger2_3_2.info('ML Model for hand detection (end): successes to detect thumbs-up at second time.')
                                self.status = False
                                detect_time = datetime.now()
                                self.detected_gesture_info.emit(self.frame, second_result_location[index])
                                self.upload_image.emit(self.frame, detect_time)
                                break  # break for the 'second_result' for loop.
                    else:
                        self.mylogger2_3_2.info('ML Model for hand detection (end): cannot detect thumbs-up at second time.')
                        time.sleep(1)
                        continue
                else:
                    # print('ML Model for hand detection (end): cannot detect thumbs-up at first time.')
                    self.mylogger2_3_2.info('ML Model for hand detection (end): cannot detect thumbs-up at first time.')
                    time.sleep(1)
                    continue
            # print('ML Model for hand detection ends')
            self.mylogger2_3_2.info('ML Model for hand detection ends')
        except BaseException as e:
            self.mylogger2_3_2.error('***------------------------Be careful! Error occurs in ml item thread!------------------------***', exc_info=True)


class Detection2_3_2_klas(Detection2_3_2):
    """The camera frame is refreshed by the qml widget"""
    def __init__(self, parent, **kwargs):
        super(Detection2_3_2_klas, self).__init__(parent=parent, **kwargs)

    def detecting_ThumbsUp(self):
        """
        It processes the frame of the camera and returns the result of the detection;
        the possible results are: 'GOOD', 'OTHER', 'OK'
        """
        ret, self.frame = self.parent.main_window.getCamera().read()
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

    def detecting_ThumbsUp_withLocation(self):
        """
        It processes the frame of the camera and returns the result of the detection;
        the possible results are: 'GOOD', 'OTHER', 'OK'
        the element of the 'result_location' list is a tuple consisting of (xmin, ymin, xmax, ymax)
        """
        ret, self.frame = self.parent.main_window.getCamera().read()
        image = cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR)
        image_np_expanded = np.expand_dims(image, axis=0)

        (boxes, scores, classes, num) = self.sess.run(
            [self.detection_boxes, self.detection_scores, self.detection_classes, self.num_detections],
            feed_dict={self.image_tensor: image_np_expanded})

        img, result, result_location = vis_util_hobin.visualize_boxes_and_labels_on_image_array_klas(
            image,
            np.squeeze(boxes),
            np.squeeze(classes).astype(np.int32),
            np.squeeze(scores),
            self.category_index,
            use_normalized_coordinates=True,
            line_thickness=3)
        return result, result_location


class Detection2_4(QThread):
    """
    It is used for detect the thumbs-up gesture.
    Compared with the Detection2 class, one main difference is the while loop in its run();
    Compared with the Detection2_1 class, the difference is emitting the image after the successful detection.
    """
    detected = pyqtSignal()
    upload_image = pyqtSignal(object, object)

    def __init__(self, parent, logger_name='hobin'):
        super(Detection2_4, self).__init__(parent)
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
                    time.sleep(0.2)
                    if self.parent.new_order_flag or self.parent.new_user_flag:
                        print('ML Model for hand detection (end): new order or new user at second time')
                        time.sleep(1)
                        continue
                    second_result = self.detecting_ThumbsUp()
                    if 'GOOD' in second_result:
                        print('ML Model for hand detection (end): successes to detect thumbs-up at second time.')
                        self.status = False
                        detect_time = datetime.now()
                        self.upload_image.emit(self.frame, detect_time)
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


class Detection2_4_1(QThread):
    """
    It is used for detect the thumbs-up gesture.
    Compared with the Detection2 class, one main difference is the while loop in its run();
    Compared with the Detection2_1 class, the difference is emitting the image after the successful detection.
    Compared with the Detection2_4 class, the logging module is introduced to this module at first time.
    Compared with the Detection2_4 class, the __del__ function is removed.
    """
    detected = pyqtSignal()
    upload_image = pyqtSignal(object, object)

    def __init__(self, parent, logger_name='hobin', *,
                 path_to_ckpt = 'D:\\01PythonFile\\tensorflow\\models-master\\research\\object_detection\\hand_rfcn_resnet101out\\output_inference_graph.pb\\frozen_inference_graph.pb',
                 path_to_labels = 'D:\\01PythonFile\\tensorflow\\models-master\\research\\object_detection\\data\\hand_label_map.pbtxt',
                 num_classes = 3,  **kwargs):
        super(Detection2_4_1, self).__init__(parent)
        # the first way to configuring the parameters, almost all parameters get their value from those named keyword arguments.
        PATH_TO_CKPT = path_to_ckpt
        PATH_TO_LABELS = path_to_labels
        NUM_CLASSES = int(num_classes)

        # the second way to configure the parameters, almost all parameters get their value from the keyword argument 'kwargs'.
        # PATH_TO_CKPT = kwargs['PATH_TO_CKPT']
        # PATH_TO_LABELS = kwargs['PATH_TO_LABELS']
        # NUM_CLASSES = int(kwargs['NUM_CLASSES'])

        # some variables
        self.parent = parent
        self.frame = None
        self.status = True
        self.mylogger2_4_1 = logging.getLogger(logger_name)
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

        # print('The initialization of ML model for hand detection successes')
        self.mylogger2_4_1.info('The initialization of ML model for hand detection successes')


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
                # print('ML Model for hand detection begins')
                self.mylogger2_4_1.info('ML Model for hand detection begins')
                if self.parent.new_order_flag or self.parent.new_user_flag:
                    # print('ML Model for hand detection (end): new order or new user at first time')
                    self.mylogger2_4_1.info('ML Model for hand detection (end): new order or new user at first time')
                    time.sleep(1)
                    continue
                first_result = self.detecting_ThumbsUp()
                if 'GOOD' in first_result:
                    # print('ML Model for hand detection: successes to detect thumbs-up at first time.')
                    self.mylogger2_4_1.info('ML Model for hand detection: successes to detect thumbs-up at first time.')
                    time.sleep(0.2)
                    if self.parent.new_order_flag or self.parent.new_user_flag:
                        # print('ML Model for hand detection (end): new order or new user at second time')
                        self.mylogger2_4_1.info('ML Model for hand detection (end): new order or new user at second time')
                        time.sleep(1)
                        continue
                    second_result = self.detecting_ThumbsUp()
                    if 'GOOD' in second_result:
                        # print('ML Model for hand detection (end): successes to detect thumbs-up at second time.')
                        self.mylogger2_4_1.info('ML Model for hand detection (end): successes to detect thumbs-up at second time.')
                        self.status = False
                        detect_time = datetime.now()
                        self.upload_image.emit(self.frame, detect_time)
                        self.detected.emit()
                    else:
                        # print('ML Model for hand detection (end): cannot detect thumbs-up at second time.')
                        self.mylogger2_4_1.info('ML Model for hand detection (end): cannot detect thumbs-up at second time.')
                        time.sleep(1)
                        continue
                else:
                    # print('ML Model for hand detection (end): cannot detect thumbs-up at first time.')
                    self.mylogger2_4_1.info('ML Model for hand detection (end): cannot detect thumbs-up at first time.')
                    time.sleep(1)
                    continue
            # print('ML Model for hand detection ends')
            self.mylogger2_4_1.info('ML Model for hand detection ends')
        except BaseException as e:
            # print(''.join(traceback.format_exception(*sys.exc_info())))
            self.mylogger2_4_1.error(e)
            self.mylogger2_4_1.error(
                '***------------------------Be careful! Error occurs in ml item thread!------------------------***')


if __name__ == '__main__':
    # initial test fot the frozen TensorFlow model
    # model1 = Detection_Test() # There is a while loop in the __init__ function!

    # test for the cooperation between QThread and frozen TensorFlow model
    cap = cv2.VideoCapture(1)
    a = Detection1_2_2(camera_object=cap)
    while True:
        a.start()
        time.sleep(2)


