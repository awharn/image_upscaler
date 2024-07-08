import os
import logging
from PIL import Image, ImageSequence

def process_image(input_path, output_path, logger):
    try:
        with Image.open(input_path) as img:
            if img.format == 'GIF' and img.is_animated:
                frames = []
                needs_upscaling = False
                for frame in ImageSequence.Iterator(img):
                    frame = frame.convert("RGBA")  # Convert to RGBA for uniform processing
                    frame, upscaled = process_single_frame(frame)
                    if upscaled:
                        needs_upscaling = True
                    frames.append(frame)

                if needs_upscaling:
                    # Save the frames as a new GIF
                    base, ext = os.path.splitext(output_path)
                    output_path = f"{base}_upscaled{ext}"
                    frames[0].save(output_path, save_all=True, append_images=frames[1:], loop=0)
                    print(f"Processed multi-frame GIF and saved: {output_path}")
                    logger.info(f"Processed multi-frame GIF and saved: {output_path}")
            else:
                img, needs_upscaling = process_single_frame(img)
                if needs_upscaling:
                    base, ext = os.path.splitext(output_path)
                    output_path = f"{base}_upscaled{ext}"
                    img.save(output_path)
                    print(f"Processed and saved: {output_path}")
                    logger.info(f"Processed and saved: {output_path}")

    except Exception as e:
        print(f"Error processing {input_path}: {e}")
        logger.error(f"Error processing {input_path}: {e}")

def process_single_frame(img):
    width, height = img.size
    if width < 250 or height < 250:
        scale_factor = 2
        if min(width, height) * 2 < 250:
            scale_factor = 4

        new_width = width * scale_factor
        new_height = height * scale_factor
        img = img.resize((new_width, new_height), Image.LINEAR)
        
        return img, True
    else:
        return img, False

def process_folder(input_folder, output_folder):
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith(('.bmp', '.png', '.gif', '.jpg', '.jpeg')):
                input_path = os.path.join(root, file)
                relative_path = os.path.relpath(root, input_folder)
                output_path = os.path.join(output_folder, relative_path, file)

                # Ensure the output directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                process_image(input_path, output_path)

if __name__ == "__main__":
    input_folder = 'path_to_input_folder'  # Replace with your input folder path
    output_folder = 'path_to_output_folder'  # Replace with your output folder path
    logging_file = 'path_to_logging_file'    # Replace with your logging file

    logging.basicConfig(filename=logging_file, filemode='w', format='%(asctime)s %(message)s')
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    process_folder(input_folder, output_folder, logger)
