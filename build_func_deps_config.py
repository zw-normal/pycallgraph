import os

# Roots path of the python source code
roots = [
    '/home/weizheng/xplan/src',
    '/home/weizheng/xplan/lib'
]

# Output folder
output_folder = './output'

# Function name to inspect
func_to_check = 'check_filename_and_content'

# Function names to exclude
funcs_to_exclude = set()

# Upstream cutoff (who is calling the func), 0 to turn off
upstream_cutoffs = 4

# Downstream cutoff (who the func is calling), 0 to turn off
downstream_cutoff = 0

# Create output folder of not exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
