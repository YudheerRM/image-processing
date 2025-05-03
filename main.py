import io
from PIL import Image, ImageDraw, ImageFont

def main(context):
    req = context.req
    res = context.res

    try:
        context.log(f"Request method: {req.method}")
        context.log(f"Request headers: {req.headers}")
        context.log(f"Request files keys: {list(req.files.keys()) if hasattr(req, 'files') else 'No files attribute'}")

        if req.method != "POST":
            return res.json({'success': False, 'message': 'Only POST allowed'}, 405)

        # Check if the 'image' file was sent in FormData
        if not hasattr(req, 'files') or 'image' not in req.files:
            context.error("Missing 'image' file in FormData")
            # Log the entire req.files object if it exists, for debugging
            if hasattr(req, 'files'):
                 context.log(f"Contents of req.files: {req.files}")
            return res.json({'success': False, 'message': 'Missing "image" file in form data'}, 400)

        # Get the file object from req.files
        image_file = req.files['image']
        
        # Log details about the received file object
        context.log(f"Type of image_file: {type(image_file)}")
        context.log(f"Attributes of image_file: {dir(image_file)}")
        if isinstance(image_file, dict):
            context.log(f"Keys in image_file dict: {image_file.keys()}")

        try:
            # Read the image data directly from the file object
            # Try reading directly from the object, or adjust based on logged attributes
            if hasattr(image_file, 'read'):
                image_data = image_file.read()
            elif isinstance(image_file, dict) and 'file' in image_file and hasattr(image_file['file'], 'read'):
                # Fallback to previous attempt if direct read fails
                image_data = image_file['file'].read()
            else:
                # If neither works, log an error - structure is unexpected
                context.error("Could not find a readable attribute or method on image_file.")
                raise ValueError("Unexpected file object structure")
        except Exception as e:
            context.error(f"Error reading image file data: {e}")
            return res.json({'success': False, 'message': 'Could not read image file data'}, 400)

        image = Image.open(io.BytesIO(image_data))
          
        # Upscale the image by 2x
        width, height = image.size
        upscaled_image = image.resize((width*2, height*2), Image.LANCZOS)
        
        # Create a drawing object to add watermark
        draw = ImageDraw.Draw(upscaled_image)
        
        # Try to load a font, or use default if not available
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except IOError:
            font = ImageFont.load_default()
        
        watermark_text = "YRM LABS ©"
        
        # Calculate position for watermark (bottom right)
        if hasattr(font, "getbbox"):
            # For newer Pillow versions
            text_bbox = font.getbbox(watermark_text)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
        else:
            # Fallback for older Pillow versions
            text_width, text_height = draw.textsize(watermark_text, font=font)
            
        position = (upscaled_image.width - text_width - 20, 
                   upscaled_image.height - text_height - 20)
        
        # Add the watermark in red
        draw.text(
            position,
            watermark_text,
            fill=(255, 0, 0),  # Bright red
            font=font
        )
        
        # Convert to WebP format
        output = io.BytesIO()
        upscaled_image.save(output, format='WEBP', quality=85)
        output.seek(0)

        return res.send(output.getvalue(), content_type='image/webp')

    except Exception as e:
        context.error(f"Error processing image: {e}")
        return res.json({'success': False, 'message': str(e)}, 500)
