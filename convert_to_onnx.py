import tensorflow as tf
import tf2onnx

model = tf.keras.models.load_model("fer.h5")
spec = (tf.TensorSpec((None, 48, 48, 1), tf.float32, name="input"),)

onnx_model, _ = tf2onnx.convert.from_keras(model, input_signature=spec, opset=13, output_path="fer.onnx")
print("[✓] Model converted to fer.onnx")
