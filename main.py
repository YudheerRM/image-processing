import io
from PIL import Image, ImageDraw, ImageFont
import json

def main(context):
    """
    Process an image by upscaling it, adding a watermark, and converting to WebP
    """
    # Get request and response objects
    req = context.req
    res = context.res
    
    try:
        # Debug the request
        context.log(f"Request method: {req.method}")
        context.log(f"Request headers: {req.headers}")
        
        # Try to access the uploaded file from request body
        if req.method == "POST":
            # Get the uploaded image from body
            if not req.body:
                return res.json({
                    'success': False, 
                    'message': 'No request body found'
                }, 400)
            
            # Get binary data directly from body    
            image_data = req.body
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
        
        # Return the processed image
        return res.send(
            output.getvalue(),
            content_type='image/webp'
        )
        
    except Exception as e:
        context.error(f"Error processing image: {str(e)}")
        return res.json({
            'success': False,
            'message': f'Error processing image: {str(e)}'
        }, 500)
