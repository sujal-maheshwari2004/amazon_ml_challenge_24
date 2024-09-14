# Image Download, Labeling, and Batch Pre-processing Pipeline

This repository contains two key Python scripts:
1. **`download_label.py`**: Downloads images from URLs, saves them locally, and labels them with metadata.
2. **`batch_pre_processing.py`**: Pre-processes images in batches, ensuring consistent size and quality for OCR (Optical Character Recognition) purposes.

## Features

- **Image Downloading** (`download_label.py`):
  - Downloads images from URLs specified in CSV files and saves them with generated filenames.
  - Uses multiprocessing to speed up the download process.
  - Provides error handling with automatic retries and the generation of placeholder images in case of failures.
  - Labels downloaded images based on their metadata, associating file paths with entity names and IDs.

- **Batch Image Pre-processing** (`batch_pre_processing.py`):
  - Pre-processes images for OCR, including resizing, padding, and noise reduction.
  - Processes images in batches of 10,000, ensuring secure handling and tracking progress with `tqdm`.
  - Adds padding to images to normalize their dimensions to 128x128 pixels.
  - Handles both training and testing datasets.

## Folder Structure

```plaintext
├── train.csv                        # CSV file containing metadata for the training images
├── test.csv                         # CSV file containing metadata for the testing images
├── processed_data                   # Folder where processed data will be saved
│   ├── train_images                 # Downloaded and saved training images
│   ├── test_images                  # Downloaded and saved testing images
│   ├── train_preprocessed           # Preprocessed training images
│   ├── test_preprocessed            # Preprocessed testing images
│   ├── train_labeled.csv            # Labeled data for training set
│   ├── test_labeled.csv             # Labeled data for testing set
├── constants.py                     # Constants like allowed units for the entity
├── download_label.py                # Script to download and label images
├── batch_pre_processing.py          # Script to preprocess images in batches
├── README.md                        # Documentation file
```

## Requirements

- Python 3.7 or higher
- The following Python packages:
  - `Pillow`
  - `opencv-python`
  - `tqdm`
  - `pandas`
  - `multiprocessing`
  - `urllib`

Install the required packages with:

```bash
pip install -r requirements.txt
```

## Usage

### 1. Download and Label Images (`download_label.py`)

To download and label images, run the `download_label.py` script:

```bash
python download_label.py
```

This will:
- Download images from URLs specified in `train.csv` and `test.csv`.
- Save the images in `processed_data/train_images` and `processed_data/test_images`.
- Create labeled CSV files `train_labeled.csv` and `test_labeled.csv` containing the paths of the saved images along with their corresponding metadata.

### 2. Pre-process Images in Batches (`batch_pre_processing.py`)

To pre-process images for OCR, run the `batch_pre_processing.py` script:

```bash
python batch_pre_processing.py
```

This will:
- Normalize images in batches of 10,000, resizing them to 128x128 pixels.
- Add padding if necessary to ensure consistent image sizes.
- Pre-process both the training and testing datasets and save them in `processed_data/train_preprocessed` and `processed_data/test_preprocessed` directories, respectively.

### 3. Customization

You can customize the script settings to match your requirements. For example:
- `base_folder`: Set the base directory where all processed data will be saved.
- `train_csv`, `test_csv`: Paths to the CSV files containing metadata for training and testing images.
- Modify batch size or image dimensions in `batch_pre_processing.py` as per your OCR model's requirements.

## Error Handling

- **Image Downloading**: 
  - Images are retried up to 3 times if the download fails. If it still fails, a placeholder image is created.
  
- **Batch Pre-processing**:
  - The script processes images in batches to prevent memory overflow. Progress is tracked using `tqdm`.

## Output

After running both scripts, you will find the following output:
- **Downloaded Images**: Stored in `processed_data/train_images` and `processed_data/test_images`.
- **Preprocessed Images**: Saved in `processed_data/train_preprocessed` and `processed_data/test_preprocessed`.
- **Labeled CSV Files**: `train_labeled.csv` and `test_labeled.csv`, containing paths to the images and their metadata.

## Example Usage

1. Run the image downloading and labeling:
   ```bash
   python download_label.py
   ```

2. Run the batch pre-processing for OCR:
   ```bash
   python batch_pre_processing.py
   ```

After this, you will have a fully downloaded, labeled, and pre-processed dataset ready for OCR tasks.
