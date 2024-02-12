#!/usr/bin/python

FILE_PATH = "/Users/simo/surgical-tracking/bundle_adjustment/example_data/image_paths_original.txt"

with open(FILE_PATH, 'r') as file:
    lines = file.readlines()

with open(FILE_PATH, 'w') as file:
    for line in lines:
        line = line.replace('{YOUR_ROOT}', '/Users/simo/surgical-tracking/bundle_adjustment')
        line = line.replace('\\', '/')
        file.write(line)