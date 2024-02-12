import os

# Define your directory path here
dir_path = '/Users/simo/surgical-tracking/bundle_adjustment/custom_data/images'
output_path = '/Users/simo/surgical-tracking/bundle_adjustment/custom_data/image_paths.txt'

# Open the paths.txt file in write mode
with open(output_path, 'w') as f:
    # Walk through each file in the directory, including subdirectories
    for root, dirs, files in os.walk(dir_path):
        # Ignore hidden directories and sort
        dirs[:] = sorted(d for d in dirs if not d.startswith('.'))
        for filename in sorted(files):
            # Ignore hidden files
            if not filename.startswith('.'):
                # Write the full path of each file to paths.txt
                # print(filename[0] + "<<>>" + os.path.join(root, filename) + '\n')
                f.write(filename[0] + "<<>>" + os.path.join(root, filename) + '\n')