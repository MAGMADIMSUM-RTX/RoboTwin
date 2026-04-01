import h5py, pickle
import numpy as np
import os
import cv2
from collections.abc import Mapping, Sequence
import shutil
from .images_to_video import images_to_video


def images_encoding(imgs):
    encode_data = []
    padded_data = []
    max_len = 0
    for i in range(len(imgs)):
        success, encoded_image = cv2.imencode(".jpg", imgs[i])
        jpeg_data = encoded_image.tobytes()
        encode_data.append(jpeg_data)
        max_len = max(max_len, len(jpeg_data))
    # padding
    for i in range(len(imgs)):
        padded_data.append(encode_data[i].ljust(max_len, b"\0"))
    return encode_data, max_len


def parse_dict_structure(data):
    if isinstance(data, dict):
        parsed = {}
        for key, value in data.items():
            if isinstance(value, dict):
                parsed[key] = parse_dict_structure(value)
            elif isinstance(value, np.ndarray):
                parsed[key] = []
            else:
                parsed[key] = []
        return parsed
    else:
        return []


def append_data_to_structure(data_structure, data):
    for key in data_structure:
        if key in data:
            if isinstance(data_structure[key], list):
                # 如果是叶子节点，直接追加数据
                data_structure[key].append(data[key])
            elif isinstance(data_structure[key], dict):
                # 如果是嵌套字典，递归处理
                append_data_to_structure(data_structure[key], data[key])


def load_pkl_file(pkl_path):
    with open(pkl_path, "rb") as f:
        data = pickle.load(f)
    return data


def create_hdf5_from_dict(hdf5_group, data_dict):
    for key, value in data_dict.items():
        if isinstance(value, dict):
            subgroup = hdf5_group.create_group(key)
            create_hdf5_from_dict(subgroup, value)
        elif isinstance(value, list):
            value = np.array(value)
            if "rgb" in key:
                encode_data, max_len = images_encoding(value)
                hdf5_group.create_dataset(key, data=encode_data, dtype=f"S{max_len}")
            else:
                hdf5_group.create_dataset(key, data=value)
        else:
            return
            try:
                hdf5_group.create_dataset(key, data=str(value))
                print("Not np array")
            except Exception as e:
                print(f"Error storing value for key '{key}': {e}")


def pkl_files_to_hdf5_and_video(pkl_files, hdf5_path, video_path):
    data_list = parse_dict_structure(load_pkl_file(pkl_files[0]))
    for pkl_file_path in pkl_files:
        pkl_file = load_pkl_file(pkl_file_path)
        append_data_to_structure(data_list, pkl_file)

    # images_to_video(np.array(data_list["observation"]["head_camera"]["rgb"]), out_path=video_path)
    
    # 解析 video_path 获取基础目录和文件名
    # video_path 类似于 /path/to/save/video/episode0.mp4
    video_dir = os.path.dirname(video_path)
    video_filename = os.path.basename(video_path)

    # Save video for each camera in observation
    if "observation" in data_list:
        for cam_name, cam_data in data_list["observation"].items():
            if isinstance(cam_data, dict) and "rgb" in cam_data:
                # 为每个相机创建一个子文件夹
                cam_dir = os.path.join(video_dir, cam_name)
                os.makedirs(cam_dir, exist_ok=True)
                
                # 视频路径：/path/to/save/video/{cam_name}/episode0.mp4
                current_video_path = os.path.join(cam_dir, video_filename)
                
                print(f"Generating video for {cam_name} at {current_video_path}...")
                try:
                    images_to_video(np.array(cam_data["rgb"]), out_path=current_video_path)
                except Exception as e:
                    print(f"Failed to generate video for {cam_name}: {e}")

    # Save video for third_view if exists
    if "third_view_rgb" in data_list:
        # 为 third_view 创建子文件夹
        cam_dir = os.path.join(video_dir, "third_view")
        os.makedirs(cam_dir, exist_ok=True)
        
        current_video_path = os.path.join(cam_dir, video_filename)
        
        print(f"Generating video for third_view at {current_video_path}...")
        try:
            images_to_video(np.array(data_list["third_view_rgb"]), out_path=current_video_path)
        except Exception as e:
            print(f"Failed to generate video for third_view: {e}")

    with h5py.File(hdf5_path, "w") as f:
        create_hdf5_from_dict(f, data_list)


def process_folder_to_hdf5_video(folder_path, hdf5_path, video_path):
    pkl_files = []
    for fname in os.listdir(folder_path):
        if fname.endswith(".pkl") and fname[:-4].isdigit():
            pkl_files.append((int(fname[:-4]), os.path.join(folder_path, fname)))

    if not pkl_files:
        raise FileNotFoundError(f"No valid .pkl files found in {folder_path}")

    pkl_files.sort()
    pkl_files = [f[1] for f in pkl_files]

    expected = 0
    for f in pkl_files:
        num = int(os.path.basename(f)[:-4])
        if num != expected:
            raise ValueError(f"Missing file {expected}.pkl")
        expected += 1

    pkl_files_to_hdf5_and_video(pkl_files, hdf5_path, video_path)
