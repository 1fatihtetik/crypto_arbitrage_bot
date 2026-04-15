import os
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, IsolationForest
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

def create_and_save_onnx(model, dummy_X, name):
    # Fit with dummy data so the model has initialized weights
    dummy_y = np.random.rand(10) if not isinstance(model, (IsolationForest, KMeans)) else None
    if isinstance(model, IsolationForest):
        model.fit(dummy_X)
    elif isinstance(model, KMeans):
        model.fit(dummy_X)
    elif isinstance(model, RandomForestClassifier):
        model.fit(dummy_X, np.random.randint(0, 2, 10))
    elif isinstance(model, MLPRegressor):
        # Neural net for RL mock routing policy (Outputs 2 values e.g. [BuySize, SellSize or VenueAction])
        dummy_y = np.random.rand(10, 2)
        model.fit(dummy_X, dummy_y)
    else:
        model.fit(dummy_X, dummy_y)

    initial_type = [('float_input', FloatTensorType([None, dummy_X.shape[1]]))]
    onnx_model = convert_sklearn(model, initial_types=initial_type, target_opset={'': 15, 'ai.onnx.ml': 3})
    
    os.makedirs(os.path.dirname(name), exist_ok=True)
    with open(name, "wb") as f:
        f.write(onnx_model.SerializeToString())
    print(f"Generated synthetic: {name}")

def main():
    print("Generating Synthetic ONNX Models...")
    
    # 1. Slippage Predictor (Mocked XGBoost using RF Regressor)
    # Inputs: [book_depth, recent_volume, order_size]
    slippage_model = RandomForestRegressor(n_estimators=10, max_depth=3)
    create_and_save_onnx(slippage_model, np.random.rand(10, 3), "ml/weights/slippage.onnx")

    # 2. Probability of Convergence (Random Forest Classifier)
    # Inputs: [rsi_divergence, order_flow_imbalance]
    convergence_model = RandomForestClassifier(n_estimators=10, max_depth=3)
    create_and_save_onnx(convergence_model, np.random.rand(10, 2), "ml/weights/convergence.onnx")

    # 3. Toxicity / Snipe Detector (Anomaly Detection)
    # Inputs: [trade_velocity, spread_volatility, whale_count]
    toxicity_model = IsolationForest(n_estimators=20)
    create_and_save_onnx(toxicity_model, np.random.rand(10, 3), "ml/weights/toxicity.onnx")

    # 4. Dynamic Fee Estimator (Linear Regression)
    # Inputs: [network_congestion, mempool_size, blocks_empty]
    fee_model = LinearRegression()
    create_and_save_onnx(fee_model, np.random.rand(10, 3), "ml/weights/fee_estimator.onnx")

    # 5. Smart Order Routing (RL Neural Network Mock)
    # Inputs: [spread, volume, our_capital, exchange_latency]
    routing_model = MLPRegressor(hidden_layer_sizes=(16, 16), max_iter=10)
    create_and_save_onnx(routing_model, np.random.rand(10, 4), "ml/weights/routing_policy.onnx")

    # 6. Market Regime Detection (K-Means Clustering)
    # Inputs: [adx, atr, bb_bandwidth]
    regime_model = KMeans(n_clusters=3, n_init=1)
    create_and_save_onnx(regime_model, np.random.rand(10, 3), "ml/weights/regime.onnx")

if __name__ == "__main__":
    main()
