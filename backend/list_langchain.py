
import langchain
import os

path = os.path.dirname(langchain.__file__)
print(f"Path: {path}")
try:
    print(f"Contents: {os.listdir(path)}")
except Exception as e:
    print(f"Error listing: {e}")
