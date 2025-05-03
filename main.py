import io
from PIL import Image, ImageDraw, ImageFont
import math # Needed for gradient calculation

# Helper function to interpolate between two colors
def lerp_color(color1, color2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(color1, color2))

# Helper function to convert hex to RGB
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

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

        # 3. Add watermark with gradient
        
        # Try to load the Tangerine font
        try:
            # IMPORTANT: Ensure 'Tangerine-Regular.ttf' (or correct filename) 
            # is included in 'function/fonts/' directory.
            font_path = "function/fonts/Tangerine-Regular.ttf" 
            font_size = 200 # Keep or adjust size as needed
            font = ImageFont.truetype(font_path, font_size) 
            context.log(f"Successfully loaded font: {font_path} with size {font_size}")
        except IOError:
            context.log(f"Warning: Could not load font {font_path}. Falling back to default font.")
            # Default font likely won't look good or scale well
            font = ImageFont.load_default() 
        
        context.log(f"Using font: {font}")

        watermark_text = "YRM LABS ©"
        
        # Calculate text bounding box
        if hasattr(font, "getbbox"):
            text_bbox = font.getbbox(watermark_text)
            # For TrueType fonts, bbox includes space below baseline, adjust if needed
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1] 
            # Offset might be needed depending on font metrics for precise placement
            offset_x = text_bbox[0]
            offset_y = text_bbox[1]
        else:
            # Fallback for default font (less accurate)
            text_width, text_height = ImageDraw.Draw(Image.new('RGB', (1,1))).textsize(watermark_text, font=font)
            offset_x, offset_y = 0, 0

        if text_width <= 0 or text_height <= 0:
             context.log("Warning: Text size is zero or negative. Skipping watermark.")
        else:
            # Create mask image for text
            mask = Image.new('L', (text_width, text_height), 0)
            mask_draw = ImageDraw.Draw(mask)
            # Draw text onto mask (adjust position for bbox offset)
            mask_draw.text((-offset_x, -offset_y), watermark_text, font=font, fill=255)

            # Create gradient image
            gradient = Image.new('RGBA', (text_width, text_height))
            gradient_draw = ImageDraw.Draw(gradient)

            # Define gradient colors
            color1 = hex_to_rgb("#380606")
            color2 = hex_to_rgb("#920808")
            color3 = color1 # Back to the start color

            for x in range(text_width):
                if x < text_width / 2:
                    # Interpolate from color1 to color2
                    t = x / (text_width / 2)
                    color = lerp_color(color1, color2, t)
                else:
                    # Interpolate from color2 to color3
                    t = (x - text_width / 2) / (text_width / 2)
                    color = lerp_color(color2, color3, t)
                
                # Draw a vertical line with the calculated color
                gradient_draw.line([(x, 0), (x, text_height)], fill=color, width=1)

            # Calculate paste position (bottom right)
            margin = 20
            paste_x = img_upscaled.width - text_width - margin
            paste_y = img_upscaled.height - text_height - margin
            position = (paste_x, paste_y)

            # Paste the gradient onto the upscaled image using the mask
            img_upscaled.paste(gradient, position, mask)

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
