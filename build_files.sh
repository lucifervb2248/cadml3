set -e

# Download and install pip for Python 3.12
wget https://bootstrap.pypa.io/get-pip.py
python3.12 get-pip.py

# Activate the virtual environment (Windows)
source venv/Scripts/activate

python3.12 -m pip3.12 install --disable-pip-version-check --target . --upgrade -r /vercel/path0/requirements.txt
python3.12 manage.py collectstatic
