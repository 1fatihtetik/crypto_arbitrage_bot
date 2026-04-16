import pytest
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from backtesting.walk_forward import WalkForwardOptimizer

def test_walk_forward_scikit_learn_mock():
    # 1. Generate Synthetic Data
    # 50 rows of dummy data, features: f1, f2, target: y
    np.random.seed(42)
    df = pd.DataFrame({
        'f1': np.random.rand(50),
        'f2': np.random.rand(50),
        'y': np.random.rand(50)
    })

    # 2. Define train_func using Scikit-Learn
    def train_rf(train_data: pd.DataFrame):
        X = train_data[['f1', 'f2']]
        y = train_data['y']
        model = RandomForestRegressor(n_estimators=5, random_state=42)
        model.fit(X, y)
        return model

    # 3. Define test_func utilizing the Scikit-Learn model
    def test_rf(model: RandomForestRegressor, test_data: pd.DataFrame) -> dict:
        X = test_data[['f1', 'f2']]
        y_true = test_data['y']
        y_pred = model.predict(X)
        
        # Calculate a mock metric, e.g., Mean Absolute Error
        mae = np.mean(np.abs(y_true - y_pred))
        return {'mae': mae}

    # 4. Instantiate WalkForwardOptimizer
    # Train constraint: 20 rows, Test constraint: 10 rows
    # Expected windows with size 50:
    # W1: Train[0:20], Test[20:30]
    # W2: Train[10:30], Test[30:40]
    # W3: Train[20:40], Test[40:50] 
    optimizer = WalkForwardOptimizer(data=df, train_window_size=20, test_window_size=10)
    
    # 5. Run Walk-Forward Optimization
    results = optimizer.run_optimization(train_func=train_rf, test_func=test_rf)

    # 6. Verify Results
    assert len(results) == 3
    
    assert results[0]['window'] == 1
    assert results[0]['train_start_idx'] == 0
    assert results[0]['test_start_idx'] == 20
    assert 'mae' in results[0]
    
    assert results[1]['window'] == 2
    assert results[1]['train_start_idx'] == 10
    assert results[1]['test_start_idx'] == 30
    
    assert results[2]['window'] == 3
    assert results[2]['train_start_idx'] == 20
    assert results[2]['test_start_idx'] == 40
