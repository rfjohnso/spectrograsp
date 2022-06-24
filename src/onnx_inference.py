import numpy as np

from PySide6 import QtCore
from data_model import DataModel

from onnx_model_dialog import ONNXModelDialog

class ONNXInference(QtCore.QObject):

    def __init__(self, model: DataModel, parent=None):
        self.model = model

        self.onnx_config = ONNXModelDialog(parent)

    def configure_onnx_inference(self):
        self.onnx_config.exec()
        return self.onnx_config.result()

    def start_onnx_inference(self):

        inference_session = self.onnx_config.sess

        # Only single input models supported
        inference_input = inference_session.get_inputs()[0]
        inference_output = inference_session.get_outputs()[self.onnx_config.output_index]

        inference_input_size = np.prod(inference_input.shape[1:])

        for annotation in self.model.annotations:
            annotation_data = self.model.read_time(annotation.start, annotation.start + annotation.length)

            num_input_annotation = annotation_data.shape[0]//inference_input_size

            annotation_data = annotation_data[:num_input_annotation*inference_input_size]

            if np.iscomplexobj(annotation_data):
                annotation_data_iq = annotation_data.view("(2,)float32")
                # Transform complex IQ data
                pass
            else:
                # annotation data in samples format
                pass

            annotation_data_iq_reshaped = np.reshape(annotation_data_iq, tuple([-1] + inference_input.shape[1:]))

            inference_result = inference_session.run(
                [inference_output.name],
                {inference_input.name: annotation_data_iq_reshaped}
            )[0]

            label_idx = np.argmax(np.mean(inference_result, axis=0))
            annotation.label = self.onnx_config.labels_model.labels[label_idx]
            annotation.annotation_changed.emit(annotation)
