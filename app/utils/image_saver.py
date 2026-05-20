import errno
import os
from datetime import datetime

def save_pil_as_png(image_object):
        """
        Saves a PIL Image object as a PNG file within a specified folder.

        Args:
            image_object: The PIL Image object to save.
            folder_path: The path to the directory where the image should be saved.
            filename: The name of the file (without extension, as .png will be added).
        """
        
        folder_path = r'D:\OneDrive\OneDrive - INTERCONEXION ELECTRICA S.A. E.S.P\Escritorio\fast\RPA_Prime\testing(removable)\output_image'
        
        # Ensure the folder exists
        if not os.path.exists(folder_path):
            try:
                os.makedirs(folder_path)
                print(f"✅📂 Created directory: {folder_path}\n")
            except OSError as e:
                # Handle the case where the directory cannot be created
                if e.errno != errno.EEXIST:
                    raise
    
        # Construct the full file path with the .png extension
        # The format is automatically determined by the extension but can be specified
        file_path = os.path.join(folder_path, f"{datetime.now().strftime("%d-%m-%Y %H..%M..%S")}.png")
        
        # Save the image
        image_object.save(file_path, "PNG")
        print(f"Image successfully saved to: {file_path}")