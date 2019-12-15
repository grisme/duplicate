import os
import sys
import hashlib
from PIL import Image


# Global hash tables
images_hash_table = {}
videos_hash_table = {}


# Builds and returns perceptive hash of the image with image_path
def image_hash_perceptive(image_path):

    bitmask_width = 8
    bitmask_height = 8

    image = Image.open(image_path)
    image = image.resize((bitmask_width, bitmask_height), Image.HAMMING).convert("LA")

    # Calculating middle color value
    middle_color = 0
    for y in range(0, bitmask_height - 1):
        for x in range(0, bitmask_width - 1):
            pixel = image.getpixel((x, y))
            middle_color += pixel[0]
    middle_color = middle_color / (bitmask_width * bitmask_height)

    # Building bit mask array
    bit_mask = ""
    for y in range(0, bitmask_height - 1):
        for x in range(0, bitmask_width - 1):
            pixel = image.getpixel((x, y))
            if pixel[0] >= middle_color:
                bit_mask += "1"
            else:
                bit_mask += "0"

    return hashlib.md5(bit_mask.encode()).hexdigest()


# Process image path
def process_image_path(image_path):
    extend_hash = image_hash_perceptive(image_path)
    if extend_hash in images_hash_table.keys():
        images_hash_table[extend_hash].append(image_path)
    else:
        images_hash_table[extend_hash] = [image_path]


# Process video path
def process_video_path(video_path):
    print("Processing video: " + video_path)


# Enumerates target path
def enumerate_path(path):
    for root, dirs, files in os.walk(path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if file_name.endswith(".jpg") or file_name.endswith(".jpeg") or file_name.endswith(".png"):
                process_image_path(file_path)
            elif file_name.endswith(".mov") or file_name.endswith(".avi") or file_name.endswith(".mkv"):
                process_video_path(file_path)


# Cleans up all founded duplicates from images hash table
def process_image_duplicates():
    images_dup_count = 0
    images_removed_size = 0
    for key in images_hash_table.keys():
        paths = images_hash_table[key]
        if len(paths) > 1:
            images_dup_count += 1
            for path_index in range(1, len(paths)):
                path = paths[path_index]
                images_removed_size += os.path.getsize(path)
                os.remove(path)
    print("Found " + str(images_dup_count) + " duplicated image(s)")
    print("Removed " + "{0:.2f}".format(images_removed_size / 1024 / 1024) + " MB of images")


def print_usage():
    print("Usage: python Duplicate.py /path/to/check")
    exit(0)


def main(argv):
    if len(argv) < 2 or not os.path.isdir(argv[1]):
        print_usage()
    path = argv[1]
    enumerate_path(path)
    process_image_duplicates()


main(sys.argv)


