import os
import csv
from PIL import Image
import pytesseract
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm  # Importing tqdm for the progress bar

# Path to the directory containing images and the existing CSV file
image_directory = "C://Users//shaks//amazon_ml_challenge_24//data//processed_data//train_preprocessed"
csv_file_path = "C://Users//shaks//amazon_ml_challenge_24//data//train.csv"

def process_image(image_path):
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return os.path.basename(image_path), text
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return os.path.basename(image_path), ''

# Function to read existing CSV and create a dictionary for fast lookup
def read_existing_csv(csv_file_path):
    data = {}
    if os.path.exists(csv_file_path):
        with open(csv_file_path, mode='r', newline='', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)  # Skip header
            for row in reader:
                data[row[0]] = row[1]  # Assuming the first column is the filename
    return data

# Function to process images and append results to the existing CSV
def process_images_and_append_to_csv(image_directory, csv_file_path, num_threads=8):
    # Read existing data
    existing_data = read_existing_csv(csv_file_path)

    # Collect all image paths
    image_paths = [os.path.join(image_directory, img) for img in os.listdir(image_directory) if img.endswith(('.png', '.jpg', '.jpeg', '.tiff'))]

    # Open CSV file to append results
    with open(csv_file_path, mode='a', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        # Only write the header if the file is new
        if os.stat(csv_file_path).st_size == 0:
            writer.writerow(['Filename', 'Extracted Text'])

        # Process images in parallel with progress bar
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            # Wrap the executor with tqdm for progress tracking
            results = list(tqdm(executor.map(process_image, image_paths), total=len(image_paths), desc="Processing Images"))

            # Write results to CSV incrementally
            for filename, text in results:
                if filename not in existing_data:
                    writer.writerow([filename, text])
                    existing_data[filename] = text

    print(f"Completed OCR for {len(image_paths)} images. Results appended to {csv_file_path}")

# Run the function
process_images_and_append_to_csv(image_directory, csv_file_path)
