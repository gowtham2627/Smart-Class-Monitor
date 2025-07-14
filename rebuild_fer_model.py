import tensorflow as tf
from tensorflow.keras.models import model_from_json

# Step 1: Load architecture from fer.json
with open("fer.json", "r") as json_file:
    model_json = json_file.read()

model = model_from_json(model_json)

# Step 2: Load weights from fer.h5
model.load_weights("fer.h5")

# Step 3: Save as new Keras SavedModel format (recommended)
model.save("fer_model_saved")  # This creates a folder you can use with OpenVINO directly

print("[✓] Model rebuilt and saved as 'fer_model_saved/'")
