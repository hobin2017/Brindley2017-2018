"""
Initialization of the Machine Learning model;
author = hobin
"""
import cv2
import numpy as np
import tensorflow as tf
import time
from PyQt5.QtCore import QThread, pyqtSignal
import traceback, sys
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
                    time.sleep(2)
                    continue
                first_result = self.detecting_ThumbsUp()
                if 'GOOD' in first_result:
                    print('ML Model for hand detection: successes to detect thumbs-up at first time.')
                    time.sleep(0.5)
                    if self.parent.new_order_flag or self.parent.new_user_flag:
                        print('ML Model for hand detection (end): new order or new user at second time')
                        time.sleep(2)
                        continue
                    second_result = self.detecting_ThumbsUp()
                    if 'GOOD' in second_result:
                        print('ML Model for hand detection (end): successes to detect thumbs-up at second time.')
                        self.status = False
                        self.detected.emit()
                    else:
                        print('ML Model for hand detection (end): cannot detect thumbs-up at second time.')
                        time.sleep(2)
                        continue
                else:
                    print('ML Model for hand detection (end): cannot detect thumbs-up at first time.')
                    time.sleep(2)
                    continue
            print('ML Model for hand detection ends')
        except BaseException:
            print(''.join(traceback.format_exception(*sys.exc_info())))

