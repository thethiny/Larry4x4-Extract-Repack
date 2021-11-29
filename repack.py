from sys import argv
import os
import struct

if len(argv) < 2:
    print(f"Usage: {argv[0]} <file(s)>")
    exit(1)

main_folders = argv[1:]

for main_folder in main_folders:

    file_meta = []
    folder_meta = []
    all_folders = {"": 0}

    for root, folders, files in os.walk(main_folder):
        inner_root = root.split('\\', 1)
        if len(inner_root) > 1:
            inner_root = inner_root[1]
        else:
            inner_root = ""
        # all_folders[inner_root] = len(all_folders)
        for folder in folders:
            folder_info = {}
            folder_info["name"] = folder
            folder_info["parent"] = all_folders[inner_root]
            folder_info["parent_name"] = inner_root
            folder_info["path"] = os.path.join(inner_root, folder)
            all_folders[folder_info["path"]] = len(all_folders)
            folder_meta.append(folder_info)
        for file in files:
            file_info = {}
            file_info["name"] = file
            file_info["parent"] = all_folders[inner_root]
            file_info["parent_name"] = inner_root
            file_info["path"] = os.path.join(inner_root, file)
            file_info["size"] = os.path.getsize(os.path.join(root, file))
            file_meta.append(file_info)

    print(len(all_folders), len(folder_meta), len(file_meta))

    os.makedirs("repacked", exist_ok=True)


    total_size = 0
    total_size += 8
    total_size += len(folder_meta) * 0x21 * 4
    total_size += len(file_meta) * (0x26) * 4
    print("Total Header Size", hex(total_size))
    with open(os.path.join("repacked", main_folder + ".dat"), "wb") as f:
        f.write(struct.pack("<i", len(folder_meta)))
        f.write(struct.pack("<i", len(file_meta)))
        for folder in folder_meta:
            f.write(struct.pack("<i", folder["parent"]))
            f.write(folder["name"].encode("utf-8"))
            for i in range(32*4 - len(folder["name"])):
                f.write(b"\x00")
        for file in file_meta:
            f.write(struct.pack("<i", file["parent"]))
            f.write(file["name"].encode("utf-8"))
            for i in range(32*4 - len(file["name"])):
                f.write(b"\x00")
            f.write(struct.pack("<i", total_size))
            f.write(struct.pack("<i", file["size"]))
            for i in range(12):
                f.write(b"\x00")
            total_size += file["size"]

        for file in file_meta:
            print(file["path"])
            with open(os.path.join(main_folder, file["path"]), "rb") as f2:
                f.write(f2.read())