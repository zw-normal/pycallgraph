import os

# Roots path of the python source code
source_roots = (
    '/Users/weizheng/Programming/Python/coveragepy/ci',
    '/Users/weizheng/Programming/Python/coveragepy/coverage',
    '/Users/weizheng/Programming/Python/coveragepy/lab',
    '/Users/weizheng/Programming/Python/coveragepy/perf',
)

# Exclude folders
exclude_folders = (
    'xtest', 'test',
)

# Allow guessing ambiguity call
enable_ambiguity_call_guessing = True

# Output folder
output_folder = './output'

# Create output folder of not exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
