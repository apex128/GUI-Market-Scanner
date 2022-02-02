import subprocess
import sys


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


packages = ['numpy', 'pandas', 'pandas_ta', 'tqdm',
            'yfinance', 'plotly', 'numerize', 'tk', 'kaleido']

for package in packages:
    install(package)
