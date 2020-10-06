import os

# Roots path of the python source code
roots = [
    '/Users/weizheng/Programming/Python/coveragepy',
]

# Output folder
output_folder = './output'

# Create output folder of not exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
