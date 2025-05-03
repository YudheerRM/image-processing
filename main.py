import io
# from PIL import Image, ImageDraw, ImageFont # Temporarily remove PIL imports

def main(context):
    req = context.req
    res = context.res

    try:
        context.log("--- Request Start ---")
        context.log(f"Request method: {req.method}")
        context.log(f"Request headers: {req.headers}")
        
        # Log different potential body/data attributes
        if hasattr(req, 'body'):
            context.log(f"Request body type: {type(req.body)}")
            # Avoid logging large bodies directly unless necessary
            # context.log(f"Request body: {req.body}") 
        else:
            context.log("Request has no 'body' attribute.")
            
        if hasattr(req, 'payload'):
             context.log(f"Request payload type: {type(req.payload)}")
             # context.log(f"Request payload: {req.payload}")
        else:
             context.log("Request has no 'payload' attribute.")

        if hasattr(req, 'data'):
             context.log(f"Request data type: {type(req.data)}")
             # context.log(f"Request data: {req.data}")
        else:
             context.log("Request has no 'data' attribute.")

        # Check req.files
        if hasattr(req, 'files') and req.files:
            context.log(f"Request files keys: {list(req.files.keys())}")
            context.log(f"Contents of req.files: {req.files}") # Log the structure
            
            # Check specifically for 'image' key
            if 'image' in req.files:
                 context.log("Found 'image' key in req.files.")
                 image_file = req.files['image']
                 context.log(f"Type of image_file: {type(image_file)}")
                 context.log(f"Attributes of image_file: {dir(image_file)}")
                 if isinstance(image_file, dict):
                     context.log(f"Keys in image_file dict: {image_file.keys()}")
                 # Try to get size if possible
                 if hasattr(image_file, 'size'):
                     context.log(f"image_file size: {image_file.size}")
                 elif isinstance(image_file, dict) and 'size' in image_file:
                     context.log(f"image_file dict size: {image_file['size']}")

                 # Return simple success if file found
                 return res.json({'success': True, 'message': 'File received in req.files'})
            else:
                 context.log("Key 'image' NOT found in req.files, but req.files is not empty.")
                 return res.json({'success': False, 'message': 'req.files populated, but missing "image" key.'}, 400)
        else:
            context.log("Request has no 'files' attribute or req.files is empty.")
            # If no files, maybe the raw body has data? Check size.
            raw_body = None
            if hasattr(req, 'body_raw'):
                 raw_body = req.body_raw
                 context.log(f"Request body_raw type: {type(raw_body)}")
                 context.log(f"Request body_raw length: {len(raw_body) if raw_body else 0}")
            elif hasattr(req, 'body'):
                 raw_body = req.body
                 context.log(f"Request body length: {len(raw_body) if raw_body else 0}")

            if raw_body:
                 # If there's a raw body, maybe FormData parsing failed upstream in Appwrite?
                 return res.json({'success': False, 'message': 'req.files empty, but raw body has content.'}, 400)
            else:
                 return res.json({'success': False, 'message': 'req.files empty and raw body is empty.'}, 400)

    except Exception as e:
        context.error(f"Error during request inspection: {e}")
        return res.json({'success': False, 'message': str(e)}, 500)
    finally:
        context.log("--- Request End ---")
