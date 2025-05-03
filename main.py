import io
from PIL import Image, ImageDraw, ImageFont

def main(context):
    # Ensure image data is present in the request body
    if not context.req.body_binary:
        return context.res.text("Error: No image data received.", 400)

    try:
        # 1. Load the image from request body
        img_bytes = context.req.body_binary
        img_buffer = io.BytesIO(img_bytes)
        img = Image.open(img_buffer).convert("RGBA")  # Convert to RGBA for transparency handling

        # 2. Upscale the image
        upscale_factor = 2
        new_width = img.width * upscale_factor
        new_height = img.height * upscale_factor
        # Using LANCZOS for high-quality resizing
        img_upscaled = img.resize((new_width, new_height), Image.LANCZOS)
        context.log(f"Image upscaled to {new_width}x{new_height}")

        # 3. Add watermark
        draw = ImageDraw.Draw(img_upscaled)
        
        # Try to load a font, or use default if not available
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except IOError:
            font = ImageFont.load_default()
        
        watermark_text = "YRM LABS ©"
        
        # Calculate position for watermark (bottom right)
        if hasattr(font, "getbbox"):
            text_bbox = font.getbbox(watermark_text)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
        else:
            text_width, text_height = draw.textsize(watermark_text, font=font)
            
        position = (img_upscaled.width - text_width - 20, 
                   img_upscaled.height - text_height - 20)
        
        # Add the watermark in red
        draw.text(
            position,
            watermark_text,
            fill=(255, 0, 0),  # Bright red
            font=font
        )

        # 4. Convert to WebP format
        output = io.BytesIO()
        img_upscaled.save(output, format="WEBP", quality=85)
        output.seek(0)

        # 5. Return the processed image
        return context.res.binary(
            output.getvalue(),
            headers={
                "Content-Type": "image/webp",
                "Content-Disposition": "attachment; filename=processed.webp"
            }
        )

    except Exception as e:
        context.error(f"Error processing image: {str(e)}")
        return context.res.text(f"Error processing image: {str(e)}", 500)
