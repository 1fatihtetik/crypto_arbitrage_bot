import os
import logging
import onnxruntime as ort

logger = logging.getLogger("ModelRegistry")

class ModelRegistry:
    _instance = None

    def __new__(cls, weights_dir="ml/weights/"):
        if cls._instance is None:
            cls._instance = super(ModelRegistry, cls).__new__(cls)
            cls._instance._initialize(weights_dir)
        return cls._instance

    def _initialize(self, weights_dir: str):
        self.weights_dir = weights_dir
        self.sessions = {}
        
        # We intentionally bind onnxruntime with specific providers to keep <2ms inference limits
        self.providers = ['CPUExecutionProvider']
        
        if os.path.exists(weights_dir):
            for model_file in os.listdir(weights_dir):
                if model_file.endswith(".onnx"):
                    model_name = model_file.replace(".onnx", "")
                    path = os.path.join(weights_dir, model_file)
                    try:
                        self.sessions[model_name] = ort.InferenceSession(path, providers=self.providers)
                        logger.info(f"Loaded ONNX model: {model_name}")
                    except Exception as e:
                        logger.error(f"Failed to load ONNX model {model_name}: {e}")
        else:
            logger.warning(f"Weights directory {weights_dir} does not exist yet. Models not loaded.")

    def predict(self, model_name: str, input_data):
        """
        Fast Hot-path prediction. Input_data should be a valid numpy array matching the specific model signature.
        """
        session = self.sessions.get(model_name)
        if not session:
            # Fallback if model missing to avoid bot crash
            return None
        
        try:
            input_name = session.get_inputs()[0].name
            # The sub-2ms constraint relies on avoiding Python object mutation here.
            # Directly feed numpy float32.
            res = session.run(None, {input_name: input_data})
            return res[0]
        except Exception as e:
            logger.error(f"Inference error on {model_name}: {e}")
            return None
