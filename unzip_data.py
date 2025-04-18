import zipfile
import os

# Paths to the zip files
UD_zip_file = os.path.join(os.getcwd(), 'data/UD-01_FoV_2_B2_recon_2Dtif.zip')
Mock_zip_file = os.path.join(os.getcwd(), 'data/Mock-01_FoV_2_B2_recon_2Dtif.zip')

# Output directories for extracted files
output_dir_UD = os.path.join(os.getcwd(), 'data')
output_dir_Mock = os.path.join(os.getcwd(), 'data')

# Ensure output directories exist
os.makedirs(output_dir_UD, exist_ok=True)
os.makedirs(output_dir_Mock, exist_ok=True)

# Unzip the first file
with zipfile.ZipFile(UD_zip_file, 'r') as zip_ref:
    zip_ref.extractall(output_dir_UD)

# Unzip the second file
with zipfile.ZipFile(Mock_zip_file, 'r') as zip_ref:
    zip_ref.extractall(output_dir_Mock)

print("Files extracted successfully!")