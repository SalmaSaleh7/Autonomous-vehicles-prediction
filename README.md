# COCO Dataset Collection and Exploratory Data Analysis (EDA) Notebook

## Overview

This notebook demonstrates a complete workflow for downloading, cleaning, verifying, and analyzing a **COCO-style object detection dataset** sourced from Kaggle. It guides you through preparing the dataset for training object detection models by:

- Downloading and extracting the dataset
- Removing images without annotations
- Updating annotation files accordingly
- Performing extensive exploratory data analysis (EDA) to better understand dataset characteristics

---

## Table of Contents

1. [Setup](#setup)  
2. [Dataset Download](#dataset-download)  
3. [Data Cleaning](#data-cleaning)  
4. [Dataset Verification](#dataset-verification)  
5. [Annotation File Update](#annotation-file-update)  
6. [Exploratory Data Analysis (EDA)](#exploratory-data-analysis-eda)  
7. [Additional Notes](#additional-notes)  
8. [How to Run](#how-to-run)  
9. [Contact](#contact)

---

## Setup

This section prepares the environment for the dataset download and processing:

- **Mount Google Drive:**  
  Optionally mount Google Drive to store the dataset persistently in Google Colab.

- **Install Dependencies:**  
  Installs necessary Python packages such as `kagglehub` to interact with Kaggle API seamlessly.

- **Upload Kaggle API Token:**  
  Upload your `kaggle.json` file to authenticate API requests and enable dataset downloads.

---

## Dataset Download

This part handles fetching the dataset from Kaggle:

- Uses `kagglehub` API to programmatically download the COCO dataset from the Kaggle repository `"evilspirit05/cocococo-dataset"`.

- Extracts dataset files and moves them into a designated folder (`/content/coco_dataset`) for easier management.

---

## Data Cleaning

Here, the notebook ensures dataset consistency and readiness:

- **Identify Non-Image Files:**  
  Scans the dataset directory for any files that are not images (e.g., JSON annotation files) and organizes them.

- **Remove Unannotated Images:**  
  Cross-references image files with annotations to detect images that lack any bounding box annotations and removes them from the dataset.

- **Clean Annotations:**  
  Updates the COCO-style JSON annotation file by removing entries corresponding to deleted images and their annotations, maintaining synchronization between images and annotations.

---

## Dataset Verification

In this section, various checks are performed to confirm dataset integrity:

- Counts total image files in the dataset directory.

- Confirms all image files have valid formats (`.jpg`, `.png`, etc.).

- Validates that no unannotated images remain after cleaning.

---

## Annotation File Update

This step:

- Saves the updated and cleaned COCO annotation JSON file under the dataset root directory as `_annotations.coco.json`.

- Ensures the annotation file accurately reflects the current state of the dataset, enabling smooth downstream training.

---

## Exploratory Data Analysis (EDA)

The largest section, focusing on understanding dataset properties through visual and statistical summaries:

- **Categories and Classes:**  
  Lists all object categories/classes present in the dataset.

- **Class Distribution:**  
  Plots bar charts to show the count of instances for each class, helping identify class imbalances.

- **Image Dimensions:**  
  Analyzes image resolutions and shows the most common dimensions, providing insights on image quality and standardization needs.

- **Image Quality Check:**  
  Detects and lists low-resolution images (e.g., below 300x300 pixels), which may impact model performance.

- **Sample Visualizations:**  
  Randomly selects images and overlays bounding boxes to visually verify annotations.

- **Bounding Box Statistics:**  
  Shows distributions of bounding box widths, heights, and aspect ratios, helping assess annotation consistency.

- **Spatial Distribution Analysis:**  
  Uses heatmaps and scatter plots to visualize where objects are commonly located within images, revealing dataset biases or patterns.

---

## YOLOv8 Training

This section covers how the dataset was used to train a YOLOv8 model for object detection:

- **Dataset Conversion:**  
  Converted the cleaned COCO JSON annotations into YOLO format (text files with normalized bounding boxes) compatible with YOLOv8 training requirements.

- **Environment Setup:**  
  Installed the official YOLOv8 repository and dependencies using `pip install ultralytics`.

- **Model Configuration:**  
  Used a pre-trained YOLOv8 model (e.g., `yolov8n.pt` or `yolov8s.pt`) as a starting point to leverage transfer learning.

- **Training Process:**  
  Trained the model on the cleaned dataset with appropriate batch size, image size, and number of epochs. For example:  
  ```bash
  yolo task=detect mode=train model=yolov8s.pt data=dataset.yaml epochs=50 imgsz=640

---
## Additional Notes

- The notebook utilizes popular Python libraries such as `os`, `json`, `shutil`, `matplotlib`, `collections`, `PIL` (Pillow), `seaborn`, and `pandas`.

- The workflow ensures the dataset is clean, consistent, and ready for object detection tasks.

- Visualizations provide comprehensive insights, aiding dataset understanding and model design decisions.

---

## How to Run

### Run in Colab or Jupyter

1. Open this notebook in Google Colab or a Jupyter environment.

2. Upload your Kaggle API token (`kaggle.json`) when prompted.

3. Run cells sequentially from top to bottom to:

   * Download and extract the dataset
   * Clean the dataset by removing unannotated images
   * Update annotation files accordingly
   * Perform exploratory data analysis with visualizations

4. Review outputs and plots to gain insights about dataset characteristics.

---

### Run Locally

1. Clone the repository:

   ```bash
   git clone <repository_url>
   cd <repository_name>
   ```

2. Change the current working directory to the project folder (not the parent folder you cloned into):

   ```bash
   cd project_directory
   ```

3. Create and activate a virtual environment:

   * On Windows:

     ```bash
     python -m venv myenv
     myenv\Scripts\activate
     ```
   * On Mac/Linux:

     ```bash
     python3 -m venv myenv
     source myenv/bin/activate
     ```

4. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

5. Run the application:

   ```bash
   python app.py
   ```

6. Open your browser and navigate to `http://localhost:5000` to access the app.

7. To deactivate the environment:

   ```bash
   deactivate
   ```

Following these steps ensures a smooth setup and avoids common issues with paths or environments.
