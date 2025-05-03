import io
import base64 # Restore base64 import
import json # Restore json import
from PIL import Image, ImageDraw, ImageFont # Restore PIL imports

def main(context):
    req = context.req
    res = context.res

    try:
        context.log(f"Request method: {req.method}")
        context.log(f"Request headers: {req.headers}")

        if req.method != "POST":
            return res.json({'success': False, 'message': 'Only POST allowed'}, 405)

        # Check for payload attribute (used by Appwrite for JSON body)
        if not hasattr(req, 'payload') or not req.payload:
            context.error("Missing or empty request payload")
            return res.json({'success': False, 'message': 'Empty request body or missing payload'}, 400)

        # Parse JSON and decode Base64 image
        try:
            body = json.loads(req.payload)
        except Exception as e:
            context.error(f"JSON decode error: {e}")
            return res.json({'success': False, 'message': 'Invalid JSON payload'}, 400)

        if 'image' not in body:
            context.error("Missing 'image' field in JSON payload")
            return res.json({'success': False, 'message': 'Missing "image" field'}, 400)

        try:
            image_data = base64.b64decode(body['image'])
        except Exception as e:
            context.error(f"Base64 decode error: {e}")
            return res.json({'success': False, 'message': 'Invalid Base64 image'}, 400)

        # --- Image Processing Logic (Restored) ---
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
        # --- End Image Processing Logic ---

    except Exception as e:
        context.error(f"Error processing image: {e}")
        return res.json({'success': False, 'message': str(e)}, 500)
