from PIL import Image, ImageOps

import datetime
import pprint
import io

from winrt.windows.media.ocr import OcrEngine
from winrt.windows.graphics.imaging import BitmapDecoder
from winrt.windows.storage.streams import InMemoryRandomAccessStream
from winrt.windows.graphics.imaging import BitmapPixelFormat, BitmapAlphaMode, SoftwareBitmap

from PyQt6.QtCore import QObject

# from utils.image_saver import save_pil_as_png


class OcrModel(QObject):
    # image_data_ready = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.masks = (
        (
            (282, 264, 120, 34),    #'Plan de trabajo'
            (428, 264, 632, 34),    #'Descripción': ima
            (282, 299, 292, 30),    #'Activo Principal'
            (282, 328, 40, 38),     #'Estado Plan Trab'
            (1129, 536, 237, 39)    #'Clasificación'
        ),
        (
            (1238, 266, 253, 64),   # 'Fecha-Hora Inicio' 'Fecha-Hora Final'
        )
    )

    async def extracting_image_data(self, async_items):

        image_items = async_items[:2]   ## Change this way
        str_item = async_items[2]
        
        # save_pil_as_png(async_items[0])
        # save_pil_as_png(async_items[1])
        print(f'🔎  str_item: {str_item}\n')

        # CPU-bound image processing? Offload.
        print(f"🎞️  Starting croping and merging of image...\n")       
        crop_image = self.process_and_combine_crops_(image_items)  #TODO: Increase the amount of maintenances per image -> More maintenances per trip

        # save_pil_as_png(crop_image)
        # Network I/O via sync client? Offload too.
        # text_data = await asyncio.to_thread(self.ocr_with_cloud_api_, crop_image)
        print(f"🔠  Starting OCR process...\n")       
        text_data = await self.run_windows_ocr(crop_image)
        text_data.append(str_item)  # Adding item from the str_time
        if text_data is None:
            return {}
        # print(f'🔎 text_data: {text_data}\n')

        # Label might be CPU-bound; offload if heavy
        print(f"✍️  Starting labeling...\n")       
        text_data_labeled = self.labeling_image_data_(text_data)

        pprint.pprint(text_data_labeled, indent=4, sort_dicts=False)
        print()

        print(f"✅🔰  A piece of data sent\n")
        return text_data_labeled

    def labeling_image_data_(self, image_texts: list[str]):

        print(f"✅✍️  Image data labeled\n")
        return {    #TODO: Change this kind of dicts for class entities
            'Plan de trabajo': image_texts[0],
            'Descripción': image_texts[1],
            'Activo Principal': image_texts[2],
            'Estado Plan Trab': image_texts[3],
            'Clasificación': image_texts[4],
            'Fecha-Hora Inicio': f'{image_texts[5]} {image_texts[6]}:00',
            'Fecha-Hora Final': f'{image_texts[7]} {image_texts[8]}:00',
            'Observaciones de ops': image_texts[9]
        }

    async def run_windows_ocr(self, pil_image: Image.Image):
        """Performs OCR using the native Windows engine with 100% reliability tweaks."""
        try:
            # --- [STEP 1] PRE-PROCESSING (PILLOW) ---
            # 1. Upscale if the image is small (crucial for UI/Screenshots)
            if pil_image.width < 1000:
                pil_image = pil_image.resize(
                    (pil_image.width * 2, pil_image.height * 2), 
                    resample=Image.Resampling.LANCZOS
                )
            
            # 2. Convert to Grayscale to improve contrast
            pil_image = pil_image.convert('L') 

            # Convert PIL to bytes
            img_byte_arr = io.BytesIO()
            pil_image.save(img_byte_arr, format='PNG')
            
            # Use Windows Streams
            stream = InMemoryRandomAccessStream()
            await stream.write_async(img_byte_arr.getvalue())
            stream.seek(0)
            
            # Decode
            decoder = await BitmapDecoder.create_async(stream)
            software_bitmap = await decoder.get_software_bitmap_async()
            
            # --- [STEP 2] FORMAT COMPATIBILITY (WINRT) ---
            # Ensure the bitmap is in the exact format the OCR engine prefers
            if (software_bitmap.bitmap_pixel_format != BitmapPixelFormat.BGRA8 or 
                software_bitmap.bitmap_alpha_mode != BitmapAlphaMode.PREMULTIPLIED):
                software_bitmap = SoftwareBitmap.convert(
                    software_bitmap, 
                    BitmapPixelFormat.BGRA8, 
                    BitmapAlphaMode.PREMULTIPLIED
                )

            # Recognize
            engine = OcrEngine.try_create_from_user_profile_languages()
            if engine is None:
                raise RuntimeError("OCR Engine could not be initialized.")

            result = await engine.recognize_async(software_bitmap)
            return [line.text for line in result.lines]

        except Exception as e:
            print(f"🟥 OCR Error: {e}")


    # async def run_windows_ocr(self, pil_image: Image.Image):
    #     """Performs OCR using the native Windows engine."""
    #     try:

    #         # Pre-processing the images for better 
    #         # 1. Upscale if the image is small (crucial for UI/Screenshots)
    #         if pil_image.width < 1000:
    #             pil_image = pil_image.resize(
    #                 (pil_image.width * 2, pil_image.height * 2), 
    #                 resample=Image.Resampling.LANCZOS
    #             )
            
    #         # 2. Convert to Grayscale to improve contrast
    #         pil_image = pil_image.convert('L') 
    #         #

    #         # Convert PIL to bytes
    #         img_byte_arr = io.BytesIO()
    #         pil_image.save(img_byte_arr, format='PNG')
            
    #         # Use Windows Streams
    #         stream = InMemoryRandomAccessStream()
    #         await stream.write_async(img_byte_arr.getvalue())
    #         stream.seek(0)
            
    #         # Decode and Recognize
    #         decoder = await BitmapDecoder.create_async(stream)
    #         software_bitmap = await decoder.get_software_bitmap_async()
            
    #         engine = OcrEngine.try_create_from_user_profile_languages()
            
    #         if engine is None:
    #             raise RuntimeError("🟥🔠  OCR Engine could not be initialized. Check Windows Language settings.")

    #         result = await engine.recognize_async(software_bitmap)

    #         print(f"✅🔠  OCR extracted {len(result.lines)} lines.\n")       

    #         return [line.text for line in result.lines]
    #     except Exception as e:
    #         print(f"🟥🔠  Error when extracting lines with OCR  |   {e}\n")
        
    def process_and_combine_crops_(self, image_objects):
        try:
            cropped_images = []
            for i, image_object in enumerate(image_objects):
                #--Load the original image
                    
                # Extract each rectangular region
                for rect in self.masks[i]:
                    x, y, w, h = rect
                    # Pillow's crop uses (left, top, right, bottom) coordinates
                    box = (x, y, x + w, y + h)
                    cropped_images.append(image_object.crop(box))

            #--Concatenate images vertically

            # Calculate final dimensions
            total_width = max(c.width for c in cropped_images)
            total_height = sum(c.height for c in cropped_images)
            
            # Create a new blank canvas
            new_img = Image.new('RGBA', (total_width, total_height))
            
            # Paste each crop one below the other
            y_offset = 0
            for crop in cropped_images:
                new_img.paste(crop, (0, y_offset))
                y_offset += crop.height

            print(f"✅🎞️  Image cut successfully\n")
            return new_img

        except Exception as e:
            print(f"🟥🎞️  An error occurred when combining images | {e}\n")
            return []