import os
import shutil
import random

# =================================================================
# 1. DATASET DOWNLOAD & SETUP
# =================================================================

# Full path to the original image and label folders
DATASET_DIR = os.path.expanduser("~/somars_data/train")
OUTPUT_DIR = os.path.join(os.path.dirname(DATASET_DIR), 'roboData-splits')

# Define the split ratios (must sum to 1.0)
TRAIN_RATIO = 0.70  # 70% for training
VAL_RATIO = 0.20    # 20% for validation
TEST_RATIO = 0.10   # 10% for testing (for final performance evaluation)

# Define the target structure
splits = {
    'train': TRAIN_RATIO,
    'val': VAL_RATIO,
    'test': TEST_RATIO
}

split_paths = {
    s: {
        'images': os.path.join(OUTPUT_DIR, s, 'images'),
        'labels': os.path.join(OUTPUT_DIR, s, 'labels')
    } for s in splits
}

def create_dirs():
    """Create all necessary output directories."""
    print(f"Creating output structure in: {OUTPUT_DIR}")
    if os.path.exists(OUTPUT_DIR):
        print(f"Warning: {OUTPUT_DIR} already exists. Deleting and recreating...")
        return
        #shutil.rmtree(OUTPUT_DIR)
    # Creates image and label folders for each split
    for s in splits:
        os.makedirs(split_paths[s]['images'], exist_ok=True)
        os.makedirs(split_paths[s]['labels'], exist_ok=True)


def split_and_copy():
    """Load, split, and copy files."""
    
    # 1. Get all image files (assuming common image extensions)
    imgCount = 0
    for fileN in os.listdir(DATASET_DIR):
        if fileN.lower().endswith('.jpg'):
            print(f"Found image file: {fileN}")
            imgCount+=1
    image_files = [
        f for f in os.listdir(DATASET_DIR) if f.lower().endswith('.jpg')
    ]
    random.shuffle(image_files)
    
    total_images = len(image_files)
    print(f"Found {total_images} total images.")
    
    # Calculate the number of files for each split
    train_count = int(total_images * TRAIN_RATIO)
    val_count = int(total_images * VAL_RATIO)
    
    # Ensure all remaining files go to test to handle float rounding
    # test_count = total_images - train_count - val_count

    # Define the file subsets, using python list splitting
    current_idx = 0
    subsets = {
        'train': image_files[current_idx: current_idx + train_count],
        'val': image_files[current_idx + train_count: current_idx + train_count + val_count],
        'test': image_files[current_idx + train_count + val_count: total_images]
    }

    # 2. Iterate and copy files
    for split_name, files in subsets.items():
        if not files:
            continue
        # print(f"Processing {split_name} ({len(files)} files)...")
        
        for image_filename in files:
            # Construct the corresponding label filename (e.g., 'img.jpg' -> 'img.txt')
            base_name = os.path.splitext(image_filename)[0]
            label_filename = base_name + '.txt'
            
            original_image_path = os.path.join(DATASET_DIR, image_filename)
            original_label_path = os.path.join(DATASET_DIR, label_filename)
            
            # Destination paths
            dest_image_path = os.path.join(split_paths[split_name]['images'], image_filename)
            dest_label_path = os.path.join(split_paths[split_name]['labels'], label_filename)
            
            # Check if label exists before copying
            if os.path.exists(original_label_path):
                # Copy Image
                shutil.copy2(original_image_path, dest_image_path)
                # Copy Label
                shutil.copy2(original_label_path, dest_label_path)
            else:
                print(f"Warning: Label file for {image_filename} not found. Skipping.")


if __name__ == "__main__":
    create_dirs()
    split_and_copy()
    print("\n✅ Data split complete!")
    print(f"New dataset structure is ready at: {OUTPUT_DIR}")