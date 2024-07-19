import sys
import subprocess

# Print the Python version
print("Python version:", sys.version)

# Print the pip version
pip_version = subprocess.run(["pip", "--version"], capture_output=True, text=True)
print("Pip version:", pip_version.stdout)

