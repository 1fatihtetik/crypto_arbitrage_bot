import os
from setuptools import setup
from setuptools_rust import Binding, RustExtension

setup(
    name="rust_executor",
    version="0.1.0",
    rust_extensions=[RustExtension("rust_executor.rust_executor", "rust_executor/Cargo.toml", binding=Binding.PyO3)],
    packages=["rust_executor"],
    zip_safe=False,
)
