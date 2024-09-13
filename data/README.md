#### `common_mistake(unit)`

**Purpose:**  
Handles common unit errors by checking if the unit is within allowed units or correcting common misspellings.

**Parameters:**  
- `unit` (str): The unit of measurement to be validated or corrected.

**Returns:**  
- (str): The corrected or validated unit if it matches an allowed unit or a corrected form of it. Returns the original unit if no match is found.

**Description:**  
This function ensures that the unit of measurement conforms to allowed values by checking common misspellings or variations. It returns the unit as it should be recognized according to the predefined allowed units.

---

#### `create_placeholder_image(image_save_path)`

**Purpose:**  
Creates a placeholder image when an image download fails.

**Parameters:**  
- `image_save_path` (str): Path where the placeholder image will be saved.

**Returns:**  
- None

**Description:**  
This function generates a 100x100 black placeholder image and saves it to the specified path. It is used as a fallback in case an image download fails, ensuring that there is a placeholder image at the intended location rather than leaving it empty.

**Exception Handling:**  
Prints an error message if the placeholder image creation fails.

---

#### `download_image(image_link, index, entity_name, save_folder, retries=3, delay=3)`

**Purpose:**  
Downloads an image from a URL and saves it to a specified folder. 

**Parameters:**  
- `image_link` (str): URL of the image to be downloaded.
- `index` (int): Index for creating a unique filename.
- `entity_name` (str): Entity name for creating a descriptive filename.
- `save_folder` (str): Directory where the image will be saved.
- `retries` (int, optional): Number of times to retry the download in case of failure (default is 3).
- `delay` (int, optional): Delay between retries in seconds (default is 3).

**Returns:**  
- None

**Description:**  
Attempts to download the image from the provided URL and save it with a filename formatted as `index_entity_name.jpg`. If the download fails, it will retry up to the specified number of times with a delay between attempts. If all retries fail, it creates a placeholder image at the same path.

**Exception Handling:**  
Retries download on failure and creates a placeholder image if download attempts fail.

---

#### `download_image_with_index(image_link, index, save_folder, retries=3, delay=3)`

**Purpose:**  
Helper function to download an image with a filename based on its index.

**Parameters:**  
- `image_link` (str): URL of the image to be downloaded.
- `index` (int): Index for creating a unique filename.
- `save_folder` (str): Directory where the image will be saved.
- `retries` (int, optional): Number of times to retry the download in case of failure (default is 3).
- `delay` (int, optional): Delay between retries in seconds (default is 3).

**Returns:**  
- None

**Description:**  
Similar to `download_image`, but used specifically for downloading images with filenames formatted as `image_{index:04d}.jpg` where `index` is zero-padded. This function is designed to work with multiprocessing, ensuring unique filenames and efficient downloading.

**Exception Handling:**  
Retries download on failure and creates a placeholder image if download attempts fail.

---

#### `download_images(df, download_folder, allow_multiprocessing=True)`

**Purpose:**  
Manages the download of multiple images as specified in a DataFrame.

**Parameters:**  
- `df` (pd.DataFrame): DataFrame containing image URLs and associated metadata.
- `download_folder` (str): Directory where the images will be saved.
- `allow_multiprocessing` (bool, optional): Whether to use multiprocessing for image downloading (default is True).

**Returns:**  
- None

**Description:**  
Downloads images listed in the DataFrame `df`. If `allow_multiprocessing` is `True`, it uses multiprocessing to speed up the downloading process. Each image is downloaded with a unique filename based on its index in the DataFrame. 

**Exception Handling:**  
Handles file existence checks to avoid redundant downloads. Retries downloads in case of failure.

---

#### `preprocess_image(image_path, output_folder, base_width=500)`

**Purpose:**  
Preprocesses an image by converting it to grayscale, resizing it, and applying noise removal.

**Parameters:**  
- `image_path` (str): Path of the image to be preprocessed.
- `output_folder` (str): Directory where the preprocessed image will be saved.
- `base_width` (int, optional): Target width for resizing the image (default is 500).

**Returns:**  
- (str or None): Path of the preprocessed image if successful, otherwise `None`.

**Description:**  
Processes an image by:
1. Converting it to grayscale.
2. Resizing it to a specified width while maintaining aspect ratio.
3. Applying Gaussian blur and thresholding to remove noise.
The processed image is saved to the output folder with the same filename as the original.

**Exception Handling:**  
Prints an error message if preprocessing fails.

---

#### `preprocess_all_images(image_folder, output_folder)`

**Purpose:**  
Preprocesses all images in a specified folder.

**Parameters:**  
- `image_folder` (str): Directory containing the images to be preprocessed.
- `output_folder` (str): Directory where the preprocessed images will be saved.

**Returns:**  
- (list): List of paths to preprocessed images.

**Description:**  
Loops through all JPEG images in the specified folder, processes each image using `preprocess_image`, and saves the result to the output folder. Collects and returns paths to all successfully preprocessed images.

**Exception Handling:**  
Handles file existence and image format issues by filtering out non-JPEG files.

---

#### `label_images(df, preprocessed_folder)`

**Purpose:**  
Labels images based on metadata from a DataFrame.

**Parameters:**  
- `df` (pd.DataFrame): DataFrame containing image metadata.
- `preprocessed_folder` (str): Directory containing preprocessed images.

**Returns:**  
- (list): List of dictionaries with image labels and paths.

**Description:**  
Matches preprocessed images with metadata from the DataFrame. Creates a list of dictionaries containing:
- `index`: Index from the DataFrame.
- `preprocessed_image_path`: Path to the preprocessed image.
- `entity_name`: Name of the entity.
- `group_id`: Group ID of the entity.

---

#### `process_images(data_csv, download_folder, preprocessed_folder)`

**Purpose:**  
Combines the image processing steps: downloading, preprocessing, and labeling.

**Parameters:**  
- `data_csv` (str): Path to the CSV file containing image URLs and metadata.
- `download_folder` (str): Directory where the downloaded images will be saved.
- `preprocessed_folder` (str): Directory where preprocessed images will be saved.

**Returns:**  
- (pd.DataFrame): DataFrame containing labeled image data.

**Description:**  
Executes the entire image processing pipeline:
1. Downloads images from URLs in the CSV file.
2. Preprocesses the downloaded images.
3. Labels the preprocessed images based on the metadata in the CSV file.
Returns a DataFrame with the results.

---

#### `process_train_and_test(train_csv, test_csv, base_folder)`

**Purpose:**  
Processes both training and test datasets by calling `process_images` for each.

**Parameters:**  
- `train_csv` (str): Path to the CSV file for training data.
- `test_csv` (str): Path to the CSV file for test data.
- `base_folder` (str): Root directory for storing processed data.

**Returns:**  
- None

**Description:**  
Processes the training and test datasets separately by:
1. Downloading images from training and test CSV files.
2. Preprocessing downloaded images.
3. Labeling the preprocessed images.
Saves labeled data as CSV files in the base folder.