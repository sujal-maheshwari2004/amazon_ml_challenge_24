import os
import csv
import requests
from PIL import Image, ImageFilter
import numpy as np
import cv2
from tqdm import tqdm
from io import BytesIO

# Define directories
train_input_csv = 'dataset/train.csv'  
test_input_csv = 'dataset/test.csv'
train_output_dir = 'output/train/images'
test_output_dir = 'output/test/images'
batch_size = 10000
target_size = (256, 256) 

# Ensure output directories exist
for output_dir in [train_output_dir, test_output_dir]:
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

# Function to convert the image to grayscale
def convert_to_grayscale(img):
    return img.convert('L')

# Function to denoise the image
def denoise_image(img):
    img = img.filter(ImageFilter.MedianFilter())
    return img

# Function to apply adaptive thresholding (for OCR purposes)
def enhance_contrast(img):
    img_cv = np.array(img)
    img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2GRAY)
    img_cv = cv2.adaptiveThreshold(img_cv, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    return Image.fromarray(img_cv)

# Function to resize and pad the image
def resize_and_pad(img, size):
    img = convert_to_grayscale(img)  # Convert to grayscale
    img = denoise_image(img)         # Denoise the image

    # Resize while maintaining aspect ratio
    img_ratio = img.width / img.height
    target_ratio = size[0] / size[1]

    if img_ratio > target_ratio:
        new_width = size[0]
        new_height = round(size[0] / img_ratio)
    else:
        new_width = round(size[1] * img_ratio)
        new_height = size[1]

    img = img.resize((new_width, new_height), Image.ANTIALIAS)

    # Pad to 256x256 pixels
    new_img = Image.new('L', size, color=255)  # White background
    paste_position = ((size[0] - new_width) // 2, (size[1] - new_height) // 2)
    new_img.paste(img, paste_position)

    return new_img

# Function to download image from URL
def download_image(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        return Image.open(BytesIO(response.content))
    else:
        raise Exception(f"Failed to download image from {image_url}")

# Function to process a batch of images
def process_batch(image_links, output_dir, batch_index):
    batch_output_dir = os.path.join(output_dir, f'batch_{batch_index}')
    if not os.path.exists(batch_output_dir):
        os.makedirs(batch_output_dir)

    for i, (index, image_link) in tqdm(enumerate(image_links), total=len(image_links), desc=f'Processing batch {batch_index}'):
        try:
            img = download_image(image_link)
            img_resized = resize_and_pad(img, target_size)

            # Save the processed image
            img_name = f"{index}.jpg"
            img_resized.save(os.path.join(batch_output_dir, img_name))

        except Exception as e:
            print(f"Error processing image {image_link}: {e}")

# Function to process images from a CSV file
def process_images_in_batches(csv_file, output_dir, batch_size):
    with open(csv_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        image_links = [(row['index'], row['image_link']) for row in reader]

    num_batches = len(image_links) // batch_size + 1
    for batch_index in range(num_batches):
        start_index = batch_index * batch_size
        end_index = min(start_index + batch_size, len(image_links))
        current_batch_links = image_links[start_index:end_index]

        if current_batch_links:
            process_batch(current_batch_links, output_dir, batch_index)

if __name__ == '__main__':
    # Process both train and test images
    print("Processing training images...")
    process_images_in_batches(train_input_csv, train_output_dir, batch_size)

    print("Processing test images...")
    process_images_in_batches(test_input_csv, test_output_dir, batch_size)
