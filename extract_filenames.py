import os

def extract_text_from_filenames(folder_path, output_file):
    extracted_texts = []
    
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            parts = filename.split('_')
            if len(parts) > 1:
                extracted_text = parts[1].replace('.json', '')
                extracted_texts.append(extracted_text)
    
    with open(output_file, 'w') as file:
        for text in extracted_texts:
            file.write(f"{text}\n")

# Define the folder path and the output file
folder_path = 'jsons'
output_file = 'extracted_texts.txt'

# Call the function to extract text and save to file
extract_text_from_filenames(folder_path, output_file)

print(f"Extracted text has been saved to {output_file}")
