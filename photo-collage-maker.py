"""
Photo Collage Maker
Author: Marco Ghislanzoni
License: MIT License
"""

import os
import sys
import random
from PIL import Image, ExifTags
import face_recognition
from tqdm import tqdm
from argparse import ArgumentParser, ArgumentTypeError

# Function to correct the orientation of an image based on its EXIF data
def get_image_orientation(image):
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = image._getexif()
        if exif is not None:
            orientation_value = exif.get(orientation)
            if orientation_value == 3:
                image = image.rotate(180, expand=True)
            elif orientation_value == 6:
                image = image.rotate(270, expand=True)
            elif orientation_value == 8:
                image = image.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        pass
    return image

# Function to resize an image to the target dimensions
def resize_image(image, target_width, target_height):
    return image.resize((target_width, target_height), Image.LANCZOS)

# Function to crop an image to match the target aspect ratio while trying to keep the face centered if detected
def crop_image(image, target_width, target_height, image_path):
    width, height = image.size
    aspect_ratio = width / height
    target_aspect_ratio = target_width / target_height

    # Crop the image based on the aspect ratio
    if aspect_ratio > target_aspect_ratio:
        new_width = int(target_aspect_ratio * height)
        left = (width - new_width) // 2
        right = left + new_width
        face_locations = face_recognition.face_locations(face_recognition.load_image_file(image_path))
        if face_locations:
            face_center = (face_locations[0][1] + face_locations[0][3]) // 2
            if face_center < left:
                left = 0
                right = new_width
            elif face_center > right:
                left = width - new_width
                right = width
        image = image.crop((left, 0, right, height))
    elif aspect_ratio < target_aspect_ratio:
        new_height = int(width / target_aspect_ratio)
        top = (height - new_height) // 2
        bottom = top + new_height
        face_locations = face_recognition.face_locations(face_recognition.load_image_file(image_path))
        if face_locations:
            face_center = (face_locations[0][0] + face_locations[0][2]) // 2
            if face_center < top:
                top = 0
                bottom = new_height
            elif face_center > bottom:
                top = height - new_height
                bottom = height
        image = image.crop((0, top, width, bottom))
    
    return image.resize((target_width, target_height), Image.LANCZOS)

# Function to parse RGB color string
def parse_rgb_color(color_string):
    try:
        # Remove '#' if present
        color_string = color_string.lstrip('#')
        
        # Parse the color string
        if len(color_string) == 6:
            return tuple(int(color_string[i:i+2], 16) for i in (0, 2, 4))
        elif len(color_string) == 3:
            return tuple(int(color_string[i]+color_string[i], 16) for i in (0, 1, 2))
        else:
            raise ValueError
    except ValueError:
        raise argparse.ArgumentTypeError("Invalid color format. Use '#RRGGBB' or '#RGB'")

# Main function to arrange images on a canvas
def arrange_images_on_canvas(input_folder, canvas_width=1920, canvas_height=1080, output_filename="pic_collage.jpg", num_rows=None, shuffle_images=False, padding=0, bg_color=(255, 255, 255), overwrite=False):
    # Check if the output file already exists and handle overwriting
    if not overwrite and os.path.exists(output_filename):
        response = input(f"File '{output_filename}' already exists. Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("Operation cancelled.")
            return

    # Get all image paths from the input folder
    images_paths = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.lower().endswith(('jpg', 'jpeg', 'png'))]
    if shuffle_images:
        random.shuffle(images_paths)
    if not images_paths:
        print("No images found in the folder.")
        return
    
    # Load and correct orientation for all images
    images = [(path, get_image_orientation(Image.open(path))) for path in tqdm(images_paths, desc="Loading images", ncols=70)]
    
    # Determine the number of rows and columns for the collage
    num_images = len(images)
    aspect_ratios = [img.width / img.height for _, img in images]
    avg_aspect_ratio = sum(aspect_ratios) / num_images

    if num_rows is None:
        num_rows = max(1, round((canvas_height / canvas_width) * (num_images / avg_aspect_ratio) ** 0.5))
    
    num_cols = (num_images + num_rows - 1) // num_rows
    target_height = (canvas_height - (num_rows + 1) * padding) // num_rows

    # Create a blank canvas to arrange the images
    canvas = Image.new('RGB', (canvas_width, canvas_height), bg_color)

    current_y = padding
    for row in tqdm(range(num_rows), desc="Arranging rows", ncols=70):
        # Get images for the current row and calculate scaling to fit the canvas width
        row_images = images[row * num_cols:(row + 1) * num_cols]
        total_width = sum(img.width / img.height * target_height for _, img in row_images)
        scale_factor = (canvas_width - (len(row_images) + 1) * padding) / total_width if total_width > 0 else 1

        # Adjust the widths to perfectly fit the canvas width
        adjusted_widths = [int((img.width / img.height) * target_height * scale_factor) for _, img in row_images]
        width_difference = canvas_width - sum(adjusted_widths) - (len(row_images) + 1) * padding

        # Distribute the width difference among the images to fill the entire canvas width
        if width_difference > 0 and row_images:
            for i in range(width_difference):
                adjusted_widths[i % len(adjusted_widths)] += 1

        current_x = padding
        # Paste each image onto the canvas
        for (image_path, image), target_width in zip(row_images, adjusted_widths):
            image = crop_image(image, target_width, target_height, image_path)
            canvas.paste(image, (current_x, current_y))
            current_x += target_width + padding
        current_y += target_height + padding

    # Save the final canvas image
    output_path = os.path.join(os.getcwd(), output_filename)
    canvas.save(output_path)
    print(f"Canvas saved at {output_path}")

# Main function to parse command line arguments and initiate the process
def main():

    parser = ArgumentParser(description="Arrange images on a canvas.")
    parser.add_argument("input_folder", help="Folder containing the images.")
    parser.add_argument("-w", "--width", type=int, default=1920, help="Width of the canvas (default: 1920).")
    parser.add_argument("-i", "--height", type=int, default=1080, help="Height of the canvas (default: 1080).")
    parser.add_argument("-o", "--output", default="pic_collage.jpg", help="Output filename (default: 'pic_collage.jpg').")
    parser.add_argument("-n", "--num_rows", type=int, help="Number of rows to arrange the images.")
    parser.add_argument("-s", "--shuffle", action="store_true", help="Shuffle images before arranging.")
    parser.add_argument("-p", "--padding", type=int, default=0, help="Padding around each image (default: 0).")
    parser.add_argument("-c", "--color", type=parse_rgb_color, default="#FFFFFF", help="Background color in RGB format (default: #FFFFFF).")
    parser.add_argument("-Y", "--overwrite", action="store_true", help="Overwrite the output file if it already exists.")

    args = parser.parse_args()

    # Call the function to arrange images on the canvas
    arrange_images_on_canvas(
        input_folder=args.input_folder,
        canvas_width=args.width,
        canvas_height=args.height,
        output_filename=args.output,
        num_rows=args.num_rows,
        shuffle_images=args.shuffle,
        padding=args.padding,
        bg_color=args.color,
        overwrite=args.overwrite
    )

if __name__ == "__main__":
    main()
