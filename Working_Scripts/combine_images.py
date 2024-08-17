# this file was written by Seamus Flannery with help from ChatGPT.
# The goal of this file is to provide me with a function that will combine two png files into a single png
# with the images side by side.It is the only one made with the help of ChatGPT, because I did not feel that
# spending time digging around endlessly on stack overflow to figure out how to animate subplots was a valuable
# use of my limited dissertation time.

from PIL import Image


def combine_images_side_by_side(image1_path, image2_path, output_path):
    """
    Combines two images side by side and saves the result.

    Parameters:
    image1_path (str): Path to the first image.
    image2_path (str): Path to the second image.
    output_path (str): Path to save the combined image.
    """
    # Open the images
    image1 = Image.open(image1_path)
    image2 = Image.open(image2_path)

    # Get the dimensions of the images
    width1, height1 = image1.size
    width2, height2 = image2.size

    # Create a new image with a width that is the sum of both images and height that is the max height of both images
    combined_width = width1 + width2
    combined_height = max(height1, height2)
    combined_image = Image.new('RGB', (combined_width, combined_height))

    # Paste the images side by side
    combined_image.paste(image1, (0, 0))
    combined_image.paste(image2, (width1, 0))

    # Save the combined image
    combined_image.save(output_path)

# Example usage:
# combine_images_side_by_side('image1.png', 'image2.png', 'combined_image.png')