import io
import base64
from PIL import Image, ImageDraw, ImageFont
import json

def main(context):
    req = context.req
    res = context.res

    try:
        context.log(f"Request method: {req.method}")
        context.log(f"Request headers: {req.headers}")

        if req.method != "POST":
            return res.json({'success': False, 'message': 'Only POST allowed'}, 405)

        if not req.payload:
            return res.json({'success': False, 'message': 'Empty request body'}, 400)

        # Parse JSON and decode Base64 image
        body = json.loads(req.payload)
        if 'image' not in body:
            return res.json({'success': False, 'message': 'Missing "image" field'}, 400)

        try:
            image_data = base64.b64decode(body['image'])
        except Exception as e:
            context.error(f"Base64 decode error: {e}")
            return res.json({'success': False, 'message': 'Invalid Base64 image'}, 400)

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
