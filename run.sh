# Install virtualenv
sudo apt install virtualenv

# Create virtual env
virtualenv -p /usr/bin/python3 venv
source venv/bin/activate
pip install -r requirements.txt

# Run app
export FLASK_DEBUG=true
python index.py
