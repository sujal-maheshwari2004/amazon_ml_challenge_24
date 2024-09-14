import os
import re
import urllib.request
import cv2
from PIL import Image
from tqdm import tqdm
import multiprocessing
from pathlib import Path
from functools import partial
import constants
import pandas as pd
import time  # Fix: Import the time module
from time import time as timer

# Utility function to handle common unit errors
def common_mistake(unit):
    if unit in constants.allowed_units:
        return unit
    if unit.replace('ter', 'tre') in constants.allowed_units:
        return unit.replace('ter', 'tre')
    if unit.replace('feet', 'foot') in constants.allowed_units:
        return unit.replace('feet', 'foot')
    return unit

# Create a placeholder image in case of download failures
def create_placeholder_image(image_save_path):
    try:
        placeholder_image = Image.new('RGB', (100, 100), color='black')
        placeholder_image.save(image_save_path)
    except Exception as e:
        print(f"Failed to create placeholder image: {e}")

# Download the image from URL and save it to the folder
def download_image(image_link, index, entity_name, save_folder, retries=3, delay=3):
    if not isinstance(image_link, str):
        return

    # Generate the filename using index and entity_name
    filename = f"{index}_{entity_name}.jpg"
    image_save_path = os.path.join(save_folder, filename)

    if os.path.exists(image_save_path):
        return  # Skip download if already exists

    for _ in range(retries):
        try:
            urllib.request.urlretrieve(image_link, image_save_path)
            return
        except:
            time.sleep(delay)
    
    # If download fails, create a placeholder image
    create_placeholder_image(image_save_path)

# Function to download an image with an indexed filename
def download_image_with_index(image_data, save_folder, retries=3, delay=3):
    image_link, index, entity_name = image_data
    download_image(image_link, index, entity_name, save_folder, retries, delay)

# Download all images, with multiprocessing for efficiency
def download_images(df, download_folder, allow_multiprocessing=True):
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    # Create a list of tuples containing (image_link, index, entity_name)
    image_data = list(zip(df['image_link'], df.index, df['entity_name']))

    if allow_multiprocessing:
        download_image_partial = partial(download_image_with_index, save_folder=download_folder)

        # Limit the number of processes to avoid Windows handle limits
        with multiprocessing.Pool(60) as pool:
            list(tqdm(pool.imap(download_image_partial, image_data), total=len(image_data)))
            pool.close()
            pool.join()
    else:
        for image_data_item in tqdm(image_data, total=len(image_data)):
            download_image_with_index(image_data_item, download_folder)

# Label images based on index, entity type, and group ID
def label_images(df, download_folder):
    labeled_data = []
    for _, row in df.iterrows():
        filename = f"{row['index']}_{row['entity_name']}.jpg"
        image_path = os.path.join(download_folder, filename)
        if os.path.exists(image_path):
            labeled_data.append({
                'index': row['index'],
                'image_path': image_path,
                'entity_name': row['entity_name'],
                'group_id': row['group_id']
            })
    return labeled_data

# Combined process: download and label images for both train and test datasets
def process_images(data_csv, download_folder):
    df = pd.read_csv(data_csv)
    
    # Step 1: Download images
    download_images(df, download_folder)

    # Step 2: Label images
    labeled_data = label_images(df, download_folder)

    # Convert the labeled data into a DataFrame for easy manipulation
    labeled_df = pd.DataFrame(labeled_data)
    
    return labeled_df

# Process both train and test datasets, storing labeled data in CSV files
def process_train_and_test(train_csv, test_csv, base_folder):
    train_download_folder = os.path.join(base_folder, 'train_images')
    test_download_folder = os.path.join(base_folder, 'test_images')

    # Process Train Dataset
    print("Processing Train Dataset...")
    train_labeled_df = process_images(train_csv, train_download_folder)
    train_labeled_df.to_csv(os.path.join(base_folder, 'train_labeled.csv'), index=False)
    
    # Process Test Dataset
    print("Processing Test Dataset...")
    test_labeled_df = process_images(test_csv, test_download_folder)
    test_labeled_df.to_csv(os.path.join(base_folder, 'test_labeled.csv'), index=False)

    print("Finished processing both datasets.")
    
# Example usage
if __name__ == "__main__":
    base_folder = 'processed_data'  
    train_csv = 'train.csv'  
    test_csv = 'test.csv'    

    # Process both train and test datasets
    process_train_and_test(train_csv, test_csv, base_folder)
