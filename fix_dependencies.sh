#!/bin/bash

echo "Fixing dependency conflicts..."

# Fix critical conflicts
pip install --upgrade opentelemetry-api>=1.27.0
pip install --upgrade protobuf~=5.29.3
pip install --upgrade packaging>=24.0

# Downgrade urllib3 to satisfy botocore and elasticsearch
pip install 'urllib3<2.0,>=1.25.4'

# Install missing packages for conda-repo-cli and spyder
pip install requests_mock
pip install 'pyqt5<5.16'
pip install 'pyqtwebengine<5.16'

# Reinstall requirements.txt with resolved dependencies
pip install -r requirements.txt --upgrade

echo "Dependencies fixed. Running pip check..."
pip check