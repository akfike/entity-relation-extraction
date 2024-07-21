import os

def remove_unwanted_files(input_folder, skipped_files_log):
    # Read the list of skipped files
    with open(skipped_files_log, 'r') as f:
        skipped_files = f.read().splitlines()

    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)
        if not filename.endswith("_fix.json") and filename not in skipped_files:
            try:
                os.remove(file_path)
                print(f"Removed {file_path}")
            except Exception as e:
                print(f"Error removing {file_path}: {e}")

# Set the input folder path and skipped files log
input_folder = 'jsons'
skipped_files_log = 'skipped_files.txt'

# Remove unwanted files
remove_unwanted_files(input_folder, skipped_files_log)
