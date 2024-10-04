# Photo Collage Maker

This project is a Python script designed to arrange images from a specified folder into a collage on a customizable canvas. The script allows for flexible options such as setting canvas dimensions, specifying the number of rows, shuffling the order of images, and handling output file overwriting.

## Features
- Corrects image orientation based on EXIF metadata.
- Automatically adjusts image aspect ratios to fit a given canvas.
- Distributes images across rows to fill the entire width of the canvas without gaps.
- Supports custom canvas dimensions and row specifications.
- Uses face recognition to crop images while trying to keep the subjects in view.
- Option to shuffle images before arranging them.
- Provides a progress bar to visualize the loading and arranging processes.
- Includes an overwrite check to prevent accidental loss of previous output files.

## Requirements
- Python 3.6 or higher
- Required Python packages:
  - `Pillow`: For image processing.
  - `face_recognition`: To detect faces for image cropping.
  - `tqdm`: To display a progress bar.

To install the required packages, run:
```sh
pip install Pillow face_recognition tqdm
```

## Usage
Run the script from the command line with the following parameters:

```sh
python photo-collage-maker.py <input_folder> [options]
```

### Arguments
- `<input_folder>`: The folder containing the images to be arranged on the canvas.

### Options
- `-w`, `--width` (default: 1920): Width of the canvas.
- `-i`, `--height` (default: 1080): Height of the canvas.
- `-o`, `--output` (default: "pic_collage.jpg"): The name of the output file.
- `-n`, `--num_rows`: Number of rows to arrange the images. If not provided, the script will calculate an optimal value.
- `-s`, `--shuffle`: Shuffle the images before arranging them.
- `-Y`, `--overwrite`: Overwrite the output file if it already exists.

### Example
```sh
python photo-collage-maker.py "C:\Users\<username>\Pictures\MyFolder" -w 1920 -i 1200 -o my_collage.jpg -n 3 -s -Y
```
This command will:
- Create a collage using images from the specified folder.
- Set the canvas size to 1920x1200 pixels.
- Output the result as "my_collage.jpg".
- Arrange the images in 3 rows.
- Shuffle the images before arranging them.
- Overwrite the output file if it already exists.

## How It Works
1. **Load Images**: The script loads all images from the specified folder and corrects their orientation using EXIF data if available.
2. **Calculate Layout**: It calculates the number of rows and columns required to fit the images on the canvas, adjusting to match the provided canvas size.
3. **Resize and Crop**: Each image is resized or cropped to match the aspect ratio of its designated space while attempting to keep any detected faces centered.
4. **Create Canvas**: A blank canvas is created, and the images are pasted onto it row by row.
5. **Save Output**: The final collage is saved as the specified output file.

## Notes
- The script uses face detection to attempt to keep people's faces centered in the cropped images. This helps create a visually pleasing arrangement when the collage contains portraits.
- The progress of the script is displayed using `tqdm`, so you can track the loading and arranging of images in real-time.
- If an output file with the same name already exists, you will be prompted to confirm overwriting unless the `-Y` flag is used.

## License
This project is licensed under the MIT License. Feel free to use and modify it as you see fit.

## Author
This script was created to provide a simple and effective way to generate image collages for a variety of purposes. Contributions and suggestions for improvements are always welcome!


