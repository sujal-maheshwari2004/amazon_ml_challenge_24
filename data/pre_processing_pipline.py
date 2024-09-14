import os
import re
import urllib.request  # Fix: Import urllib.request directly
import cv2
from PIL import Image
from tqdm import tqdm
import multiprocessing
from pathlib import Path
from functools import partial
import pandas as pd
import time  # Fix: Import the time module
from time import time as timer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Utility function to handle common unit errors
def common_mistake(unit, allowed_units):
    if unit in allowed_units:
        return unit
    if unit.replace('ter', 'tre') in allowed_units:
        return unit.replace('ter', 'tre')
    if unit.replace('feet', 'foot') in allowed_units:
        return unit.replace('feet', 'foot')
    return unit

# Create a placeholder image in case of download failures
def create_placeholder_image(image_save_path):
    try:
        placeholder_image = Image.new('RGB', (100, 100), color='black')
        placeholder_image.save(image_save_path)
        logging.info(f"Created placeholder image: {image_save_path}")
    except Exception as e:
        logging.error(f"Failed to create placeholder image: {e}")

# Download the image from URL and save it to the folder
def download_image(image_link, index, entity_name, save_folder, retries=3, delay=3):
    if not isinstance(image_link, str):
        return

    # Generate the filename using index and entity_name
    filename = f"{index}_{entity_name}.jpg"
    image_save_path = os.path.join(save_folder, filename)

    if os.path.exists(image_save_path):
        logging.info(f"Image already exists, skipping: {image_save_path}")
        return  # Skip download if already exists

    for _ in range(retries):
        try:
            urllib.request.urlretrieve(image_link, image_save_path)
            logging.info(f"Downloaded image: {image_save_path}")
            return
        except Exception as e:
            logging.error(f"Error downloading {image_link}: {e}")
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

        num_cores = multiprocessing.cpu_count()  # Dynamic CPU core allocation
        logging.info(f"Using {min(num_cores, 60)} processes for downloading images.")
        
        with multiprocessing.Pool(min(num_cores, 60)) as pool:
            list(tqdm(pool.imap(download_image_partial, image_data), total=len(image_data)))
            pool.close()
            pool.join()
    else:
        for image_data_item in tqdm(image_data, total=len(image_data)):
            download_image_with_index(image_data_item, download_folder)

# Preprocess a single image (grayscale, resize, noise removal)
def preprocess_image(image_path, output_folder, base_width=500):
    try:
        # Grayscale Conversion
        img = Image.open(image_path).convert('L')

        # Resizing
        w_percent = (base_width / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_percent)))
        img = img.resize((base_width, h_size), Image.LANCZOS)

        # Noise Removal
        img_cv = cv2.imread(image_path, 0)  # Read image in grayscale (OpenCV)
        img_cv = cv2.GaussianBlur(img_cv, (5, 5), 0)
        _, img_cv = cv2.threshold(img_cv, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Save the preprocessed image
        preprocessed_path = os.path.join(output_folder, os.path.basename(image_path))
        cv2.imwrite(preprocessed_path, img_cv)
        logging.info(f"Preprocessed and saved image: {preprocessed_path}")
        return preprocessed_path
    except Exception as e:
        logging.error(f"Error preprocessing image {image_path}: {e}")
        return None

# Preprocess all downloaded images
def preprocess_all_images(image_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    image_files = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.endswith('.jpg')]
    preprocessed_paths = []
    for image_path in tqdm(image_files, total=len(image_files)):
        preprocessed_image = preprocess_image(image_path, output_folder)
        if preprocessed_image:
            preprocessed_paths.append(preprocessed_image)
    return preprocessed_paths

# Label images based on index, entity type, and group ID
def label_images(df, preprocessed_folder):
    labeled_data = []
    for _, row in df.iterrows():
        filename = f"{row['index']}_{row['entity_name']}.jpg"
        preprocessed_path = os.path.join(preprocessed_folder, filename)
        if os.path.exists(preprocessed_path):
            labeled_data.append({
                'index': row['index'],
                'preprocessed_image_path': preprocessed_path,
                'entity_name': row['entity_name'],
                'group_id': row['group_id']
            })
    return labeled_data

# Combined process: download, preprocess, and label images for both train and test datasets
def process_images(data_csv, download_folder, preprocessed_folder):
    df = pd.read_csv(data_csv)

    # Ensure required columns exist in the dataframe
    required_columns = ['image_link', 'entity_name', 'group_id']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Step 1: Download images
    download_images(df, download_folder)

    # Step 2: Preprocess images
    preprocess_all_images(download_folder, preprocessed_folder)

    # Step 3: Label images
    labeled_data = label_images(df, preprocessed_folder)

    # Convert the labeled data into a DataFrame for easy manipulation
    labeled_df = pd.DataFrame(labeled_data)
    
    return labeled_df

# Process both train and test datasets, storing preprocessed images in respective folders
def process_train_and_test(train_csv, test_csv, base_folder):
    train_download_folder = os.path.join(base_folder, 'train_images')
    train_preprocessed_folder = os.path.join(base_folder, 'train_preprocessed')

    test_download_folder = os.path.join(base_folder, 'test_images')
    test_preprocessed_folder = os.path.join(base_folder, 'test_preprocessed')

    # Process Train Dataset
    logging.info("Processing Train Dataset...")
    train_labeled_df = process_images(train_csv, train_download_folder, train_preprocessed_folder)
    train_labeled_df.to_csv(os.path.join(base_folder, 'train_labeled.csv'), index=False)
    
    # Process Test Dataset
    logging.info("Processing Test Dataset...")
    test_labeled_df = process_images(test_csv, test_download_folder, test_preprocessed_folder)
    test_labeled_df.to_csv(os.path.join(base_folder, 'test_labeled.csv'), index=False)

    logging.info("Finished processing both datasets.")
    
# Example usage
if __name__ == "__main__":
    base_folder = 'processed_data'  # Root folder for all processed data
    train_csv = 'train.csv'  # Update with the correct path to your train.csv
    test_csv = 'test.csv'    # Update with the correct path to your test.csv

    # Process both train and test datasets
    process_train_and_test(train_csv, test_csv, base_folder)
