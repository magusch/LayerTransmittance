import os
import requests

import numpy as np

material_folder = 'app/static/data'
raw_material_folder = 'app/static/raw_materials'

def available_materials():
    materials = ['empty']
    for file in os.listdir(material_folder):
        if file.endswith('.csv'):
            material_name = file.split('.csv')[0]
            materials.append(material_name)

    return materials

def download_file(url, material=''):
    filename = os.path.join(raw_material_folder, material + '_' + os.path.basename(url))

    # Download the file
    with open(filename, 'wb') as f:
        response = requests.get(url)
        f.write(response.content)

def prepare_material_file():
    for file in os.listdir(raw_material_folder):
        if file.endswith('.csv'):
            transform_csv(raw_material_folder+'/'+file)
        # elif file.endswith('.txt'):
        #     transform_txt


def transform_csv(file):
    data = ''
    with open(file,'r') as f:
        data = f.read()
    data_blocks = data.strip().split("\n\n")

    # Create DataFrames for 'n' and 'k'
    sections = data.strip().split('\n\n')

    parsed_data = []
    for section in sections:
        lines = section.split('\n')[1:]  # Skip the header line
        array_data = np.array([line.strip().split(',') for line in lines], dtype=float)
        parsed_data.append(array_data)

    # Interpolate data for common wavelengths

    if len(parsed_data)==2:
        n_data, k_data = parsed_data
    else:
        # If data doesn't have k_data
        n_data = parsed_data[0]
        wv_start, wv_end = n_data[0][0], n_data[-1][0]

        k_data = np.array([[wv_start, 0.0], [wv_end, 0.0], ], dtype=float)

    wl_common = np.linspace(max(n_data[:, 0].min(), k_data[:, 0].min()),
                            min(n_data[:, 0].max(), k_data[:, 0].max()),
                            100)

    n_interpolated = np.interp(wl_common, n_data[:, 0], n_data[:, 1])
    k_interpolated = np.interp(wl_common, k_data[:, 0], k_data[:, 1])

    # Combine the interpolated data into one table
    combined_data = np.column_stack((wl_common * 1000, n_interpolated, k_interpolated))

    # Save to CSV
    save_path = f"{material_folder}/{file.split('/')[-1].split('.')[0]}_ri.csv"
    np.savetxt(save_path, combined_data, delimiter=';', header='wv;n;k', comments='')
    os.remove(file)


def divide_url_ri(url):

    ri_query_pairs = url.split('?')[-1].split('&')
    ri_url_dict = {}

    # Iterate through the key-value pairs
    for pair in ri_query_pairs:
        key, value = pair.split('=')
        ri_url_dict[key] = value

    return ri_url_dict