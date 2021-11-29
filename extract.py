import struct
import os
from sys import argv 

if len(argv) < 2:
    print(f"Usage: {argv[0]} <file(s)>")
    exit(1)

files = argv[1:]

def read_int(f):
    return struct.unpack("<i", f.read(4))[0]

def get_parent_package(i, packages):
    if i:
        return packages[i - 1]
    return ""

def get_file_names(f):
    name = f.read(32*4).decode("utf-8")
    return [n for n in name.split("\x00") if n]

def read_struct(f, folders):
    parent_package = read_int(f)
    names = get_file_names(f)
    null_terminated_name = names[0]
    parent_package_name = get_parent_package(parent_package, folders)
    return parent_package_name, null_terminated_name, names[1:]

def read_content(f, location, size):
    f.seek(location)
    return f.read(size)

def write_file_data(name, content):
    os.makedirs(os.path.dirname(name), exist_ok=True)
    with open(name, "wb") as f:
        f.write(content)

def extract_file(file):
    open_file = file
    if not os.path.exists(file):
        open_file = file + ".dat"
    with open(open_file, "rb") as f:
        folders = []
        data_meta = []
        folders_count = read_int(f)
        data_count = read_int(f)

        for i in range(folders_count):
            parent_package_name, null_terminated_name, names = read_struct(f, folders)
            folders.append(os.path.join(parent_package_name, null_terminated_name))
            print(f"{i+1}/{folders_count} {folders[i]}")

        for i in range(data_count):
            parent_package_name, null_terminated_name, names = read_struct(f, folders)
            data_location = read_int(f)
            data_size = read_int(f)
            f.seek(12, 1)
            data_meta.append((os.path.join(parent_package_name, null_terminated_name), data_location, data_size))
            print(f"{i+1}/{data_count} {data_meta[i]}")
        
        for i in range(data_count):
            print(f"{i+1}/{data_count} {data_meta[i]}")
            read_data = read_content(f, data_meta[i][1], data_meta[i][2])
            write_file = os.path.join(file, data_meta[i][0])
            write_file_data(write_file, read_data)

for file in files:
    extract_file(file)