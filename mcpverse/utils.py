import csv
import os
import re

import pandas as pd


def get_all_files(directory):
    file_list = []
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            # 拼接完整的文件路径
            file_list.append(os.path.join(dirpath, filename))
    return file_list


def sanitize_text(text):
    if text is None:
        return ""
    # filter IllegalCharacter
    return re.sub(r'[\x00-\x1F\x7F-\x9F]', '', str(text))


def write_data(path, data):
    # print("=> save to ", path)
    dir_name, file_name = os.path.split(path)
    _, suffix = os.path.splitext(file_name)

    tempfile = os.path.join(
        dir_name, file_name.split('.')[0] + '_temp.' + suffix
    )

    try:
        if path.endswith('.xlsx'):
            data.to_excel(tempfile, index=False)
        elif path.endswith('.csv'):
            data.to_csv(tempfile, index=False)
        else:
            raise ValueError('path must be xlsx or csv')
        # 替换原文件
        os.replace(tempfile, path)

    except Exception as e:
        # if os.path.exists(tempfile):
        #     os.remove(tempfile)
        print("Error saving data to file: ", path)
        raise e


def read_data(dataset_path):
    if dataset_path.endswith('.xlsx'):
        df = pd.read_excel(dataset_path)
    elif dataset_path.endswith('.csv'):
        df = pd.read_csv(dataset_path)
    else:
        raise ValueError('dataset_path must be xlsx or csv')

    return df

