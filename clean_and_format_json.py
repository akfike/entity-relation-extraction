import os
import json

def clean_and_format_json(input_text):
    # Remove the extra text before and after the JSON object
    json_start = input_text.find('{')
    json_end = input_text.rfind('}') + 1
    json_text = input_text[json_start:json_end]

    # Load the JSON data
    try:
        json_data = json.loads(json_text)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None

    return json_data

def save_json_to_file(json_data, output_file):
    with open(output_file, 'w') as f:
        json.dump(json_data, f, indent=4)

def process_json_files(input_folder, output_folder, skipped_files_log):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    skipped_files = []

    for filename in os.listdir(input_folder):
        if filename.endswith(".json"):
            input_file_path = os.path.join(input_folder, filename)
            with open(input_file_path, 'r') as f:
                input_text = f.read()

            cleaned_json_data = clean_and_format_json(input_text)
            if cleaned_json_data:
                output_file_path = os.path.join(output_folder, filename.replace(".json", "_fix.json"))
                save_json_to_file(cleaned_json_data, output_file_path)
                print(f"Cleaned JSON data has been saved to {output_file_path}")
            else:
                skipped_files.append(filename)
                print(f"Failed to clean and format JSON data for {filename}")

    # Write skipped files to a log file
    with open(skipped_files_log, 'w') as f:
        for file in skipped_files:
            f.write(file + '\n')

# Set the input and output folder paths
input_folder = 'jsons'
output_folder = 'fixed_jsons'
skipped_files_log = 'skipped_files.txt'

# Process all JSON files in the input folder
process_json_files(input_folder, output_folder, skipped_files_log)
