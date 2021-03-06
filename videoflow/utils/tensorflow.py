from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import tensorflow as tf

class TensorflowModel:
    def __init__(self, pb_file_path, input_tensors_names, output_tensors_names, device_id = "cpu:0"):
        '''
        - Arguments:
            - pb_file_path (str): path to pb file
            - input_tensors_names (list(str)): list of names of input tensors
            - output_tensors_names (list(str)): list of names of output tensors
            - device_id (str): name of device where model should be allocated. Model allocation \
                in that device is not guaranteed. If the device cannot be found, it will \
                default to cpu.
        '''
        self._pb_file_path = pb_file_path
        self._device_id = device_id
        self._output_tensors_names = output_tensors_names
        self._input_tensors_names = input_tensors_names
        self._session = None
        self._model_graph = None
        self._output_tensors = None
        self._input_tensors = None
        self._load_model()
    
    def _load_model(self):
        '''
        Loads model from file and creates the model session to make it ready
        for inference.
        '''
        with tf.device(self._device_id):
            self._model_graph = tf.Graph()
            with self._model_graph.as_default():
                graph_def = tf.GraphDef()
                with tf.gfile.GFile(self._pb_file_path, 'rb') as fid:
                    serialized_graph = fid.read()
                    graph_def.ParseFromString(serialized_graph)
                    tf.import_graph_def(graph_def, name = '')
        
        self._session = tf.Session(graph = self._model_graph)
        self._output_tensors = [self._model_graph.get_tensor_by_name(name) for name in self._output_tensors_names]
        self._input_tensors = [self._model_graph.get_tensor_by_name(name) for name in self._input_tensors_names]

    def _close_session(self):
        '''
        Closes the tensorflow session that was opened when the model was loaded.
        '''
        self._session.close()
    
    def run_on_input(self, *inp_l):
        '''
        - Arguments:
            - inp_l: a list of inputs to be passed to the model. \
                Must be given in the same order that the list of `input_tensors_names` was given to the constructor.

        - Returns:
            - output_l: a list of outputs of the same length and in the same order as the `output_tensors_names` \
                was provided to the constructor.
        '''
        if self._session is None:
            self._load_model()
        feed_dict = dict(zip(self._input_tensors, inp_l))
        output_l = self._session.run(
            self._output_tensors,
            feed_dict = feed_dict
        )
        return output_l
