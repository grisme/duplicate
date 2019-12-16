import os
import sys
import hashlib
from PIL import Image


# Global hash tables
images_hash_table = {}
videos_hash_table = {}
should_remove_duplicates = False


# Calculates perceptive hash for image and returns as md5 hex digest
def image_hash_perceptive(image):
    bit_mask_width = 8
    bit_mask_height = 8

    image = image.resize((bit_mask_width, bit_mask_height), Image.HAMMING).convert("LA")

    # Calculating middle color value
    middle_color = 0
    for y in range(0, bit_mask_height - 1):
        for x in range(0, bit_mask_width - 1):
            pixel = image.getpixel((x, y))
            middle_color += pixel[0]
    middle_color = middle_color / (bit_mask_width * bit_mask_height)

    # Building bit mask array
    bit_mask = ""
    for y in range(0, bit_mask_height - 1):
        for x in range(0, bit_mask_width - 1):
            pixel = image.getpixel((x, y))
            if pixel[0] >= middle_color:
                bit_mask += "1"
            else:
                bit_mask += "0"

    return hashlib.md5(bit_mask.encode()).hexdigest()


# Calculates hash set for image, separated by blocks
# For perceptive comparsion with another images
# def image_hash_set_perceptive(image_path):
#     hash_set = set()
#
#     # Image each hashing block width and height
#     block_w = 64
#     block_h = 64
#
#     image = Image.open(image_path)
#     image_width, image_height = image.size()
#
#     # Image is too small - simply hash returning
#     if image_width < block_w or image_height < block_h:
#         hash_set.add(image_hash_perceptive(image))
#         return hash_set
#
#     # Image width and height padding to block size
#     image_width = image_width - image_width % block_w
#     image_height = image_height - image_height % block_h
#
#     # Blocks count calculation
#     blocks_width_count = image_width / block_w
#     blocks_height_count = image_height / block_h
#
#     for block_y in range(0, blocks_height_count - 1):
#         for block_x in range(0, blocks_width_count - 1):
#             left = block_x * block_w
#             up = block_y * block_h
#             right = left + block_w
#             down = up + block_h
#             block_image = image.crop((left, up, right, down))
#             image_hash = image_hash_perceptive(block_image)
#             hash_set.add(image_hash)
#
#     return hash_set


def unique_image_path(image_path):
    image = Image.open(image_path)
    return image_hash_perceptive(image)


# Process image path
def process_image_path(image_path):
    image_hash = unique_image_path(image_path)
    if image_hash in images_hash_table.keys():
        images_hash_table[image_hash].append(image_path)
    else:
        images_hash_table[image_hash] = [image_path]


# Process video path
def process_video_path(video_path):
    video_path = video_path


# Enumerates target path
def enumerate_path(path):
    for root, dirs, files in os.walk(path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if os.path.islink(file_path):
                continue
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
            print("Found dup with original path: " + paths[0])
            for path_index in range(1, len(paths)):
                path = paths[path_index]
                images_removed_size += os.path.getsize(path)
                print(" ---> dup: " + path)
                if should_remove_duplicates:
                    os.remove(path)

    print("")
    print("-----------------------------")
    print("Summary:")
    print("Found " + str(images_dup_count) + " duplicated image(s)")
    print("Removed " + "{0:.2f}".format(images_removed_size / 1024 / 1024) + " MB of images")


def print_usage():
    print("Usage: python Duplicate.py /path/to/check [--remove]")
    exit(0)


def main(argv):
    if len(argv) < 2 or not os.path.isdir(argv[1]):
        print_usage()
    if len(argv) > 2:
        global should_remove_duplicates
        should_remove_duplicates = argv[2] == "--remove"
    path = argv[1]
    enumerate_path(path)
    process_image_duplicates()


main(sys.argv)


