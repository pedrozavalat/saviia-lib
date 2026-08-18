import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
source_dir = os.path.join(project_root, "src")
sys.path.insert(0, source_dir)
