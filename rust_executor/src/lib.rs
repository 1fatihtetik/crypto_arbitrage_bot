use pyo3::prelude::*;
use pyo3::types::PyDict;

/// A high-performance executor struct for bypassing Python GIL during critical trade paths.
#[pyclass]
pub struct FastExecutor {
    api_key_encrypted: String,
    exchange: String,
}

#[pymethods]
impl FastExecutor {
    #[new]
    fn new(api_key_encrypted: String, exchange: String) -> Self {
        FastExecutor {
            api_key_encrypted,
            exchange,
        }
    }

    /// Simulates a fast network dispatch to the exchange.
    fn execute_trade(&self, py: Python, trade_details: &PyDict) -> PyResult<String> {
        // In a real tournament bot, this would use e.g. reqwest to fire async HTTP/WS calls directly.
        let side: Option<&str> = trade_details.get_item("side")?.and_then(|t| t.extract().ok());
        let amount: Option<f64> = trade_details.get_item("amount")?.and_then(|t| t.extract().ok());
        let price: Option<f64> = trade_details.get_item("price")?.and_then(|t| t.extract().ok());

        let result = format!(
            "Executed {} of {} at {} on {} via Rust!",
            side.unwrap_or("UNKNOWN"),
            amount.unwrap_or(0.0),
            price.unwrap_or(0.0),
            self.exchange
        );
        Ok(result)
    }
}

/// The initialization function for the Python module.
#[pymodule]
fn rust_executor(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<FastExecutor>()?;
    Ok(())
}
