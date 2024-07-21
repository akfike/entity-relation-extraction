import json
import os
import pandas as pd

# Function to extract the related variable from the filename
def extract_related_variable(filename):
    parts = filename.split('_')
    if len(parts) > 1:
        return parts[1]
    return ''

# Function to process JSON files in a given folder
def process_json_folder(folder_path, dataset_name, year):
    entities_data = []
    
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            related_variable = extract_related_variable(filename)
            json_file_path = os.path.join(folder_path, filename)
            with open(json_file_path, 'r') as file:
                data = json.load(file)
                
                # Process entities
                if 'entities' in data:
                    for entity in data['entities']:
                        entity['Dataset'] = dataset_name
                        entity['Year'] = year
                        entity['Related Variable'] = related_variable
                        entities_data.append(entity)
    
    return entities_data

# Process NIBRS_jsonblock folder
nibrs_folder_path = 'jsons'
nibrs_entities_data = process_json_folder(nibrs_folder_path, 'NIBRS', 2019)

# Create a DataFrame from the entities data
entities_df = pd.DataFrame(nibrs_entities_data)

# Rename columns to match the required format
entities_df.rename(columns={'entity': 'Entity', 'description': 'Entity Description'}, inplace=True)

# Remove duplicate entities, keeping only the first occurrence
entities_df.drop_duplicates(subset=['Entity'], keep='first', inplace=True)

# Add the additional required columns if not already present
required_entity_columns = ['Entity', 'Dataset', 'Year', 'Entity Description', 'Related Variable', 'Related Variable Description', 'Page Number', 'Reason (optional)']
for col in required_entity_columns:
    if col not in entities_df.columns:
        entities_df[col] = ''

# Reorder columns to match the specified format
entities_df = entities_df[required_entity_columns]

# Load the existing Excel file
excel_file_path = 'datasets_statistics.xlsx'
existing_entities_df = pd.read_excel(excel_file_path, sheet_name='EntityFormat')

# Append the new data to the existing data
combined_entities_df = pd.concat([existing_entities_df, entities_df], ignore_index=True)

# Remove duplicate entities again after combining
combined_entities_df.drop_duplicates(subset=['Entity'], keep='first', inplace=True)

# Write the combined DataFrame to the specified sheet
with pd.ExcelWriter(excel_file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    combined_entities_df.to_excel(writer, sheet_name='EntityFormat', index=False)

print("Data has been successfully written to the Excel sheet.")
