#!/usr/bin/env python3

import sys
import os

base_dir = '/home/users/user/general_python_projects'  # Directory path above /Macro-Maker/
input_dir = os.path.join(base_dir, 'input')
actions_dir = os.path.join(input_dir, 'actions')

sys.path.append(input_dir)
sys.path.append(actions_dir)

from Main import load_from_pkl, run_all

pickle_file_path = os.path.join(os.path.dirname(__file__), 'pkl_name.pkl')

load_from_pkl(pickle_file_path)
run_all()
