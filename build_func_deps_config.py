import os

# Roots path of the python source code
roots = [
    '/Users/weizheng/Programming/Python/coveragepy',
]

# Output folder
output_folder = '.'

# Function name to inspect
func_to_check = 'load_plugins'

# Upstream cutoff (who is calling the func), 0 to turn off
upstream_cutoffs = 3

# Downstream cutoff (who the func is calling), 0 to turn off
downstream_cutoff = 2
