#!/bin/bash
rm -rf dist/ build/ *.egg-info
python3 -m build
twine upload dist/* --verbose