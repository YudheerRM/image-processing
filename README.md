# YRM Portfolio Python Image Processing
# Image Processing Function

An Appwrite serverless function that processes images by:
1. Upscaling them (2x)
2. Adding a "YRM LABS ©" watermark in red
3. Converting to WebP format

## Usage

Send a POST request to this function with an image file in the 'image' field.
The function will return the processed image in WebP format.

