import os

# Define your directory path here
dir_path = '/Users/simo/surgical-tracking/bundle_adjustment/custom_data/cam_3'

for filename in os.listdir(dir_path):
    if filename.endswith('.png'):
        parts = filename.split('_')
        parts[1] = parts[1].zfill(8)  # pad with zeros to 4 digits
        new_filename = '_'.join(parts)
        os.rename(os.path.join(dir_path, filename), os.path.join(dir_path, new_filename))