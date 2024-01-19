#!/usr/bin/python

FILE_PATH = "/Users/simo/MultiCamCalib/example_data/image_paths.txt"

with open(FILE_PATH, 'r') as file:
    lines = file.readlines()

with open(FILE_PATH, 'w') as file:
    for line in lines:
        line = line.replace('{YOUR_ROOT}', '/Users/simo/MultiCamCalib')
        line = line.replace('\\', '/')
        file.write(line)