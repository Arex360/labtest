from flask import Flask, request, jsonify, send_from_directory
import base64
from PIL import Image
from io import BytesIO
import os
#from super_image import EdsrModel, ImageLoader
from PIL import Image
from flask_cors import CORS,cross_origin
app = Flask(__name__)
CORS(app, support_credentials=False)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/postPhoto', methods=['POST'])
@cross_origin(supports_credentials=False)
def post_photo():
    try:
        data = request.get_json()

        # Check if the required fields are present in the request
        if 'clientID' not in data or 'sourceImage' not in data or 'targetImage' not in data:
            return jsonify({'error': 'clientID, sourceImage, and targetImage are required fields'}), 400

        # Extract values from the request
        client_id = data['clientID']
        source_image_data = data['sourceImage']
        target_image_data = data['targetImage']
        # Decode base64 data (assuming it's an image)
        source_image_data = base64.b64decode(source_image_data)
        target_image_data = base64.b64decode(target_image_data)

        # Open the source and target images using Pillow
        source_image = Image.open(BytesIO(source_image_data))
        target_image = Image.open(BytesIO(target_image_data))

        # Save the source and target images using the clientID as the filename
        source_filename = f"images/source_{client_id}.png"  # You can use other formats like JPEG if needed
        target_filename = f"images/target_{client_id}.png"
        source_image.save(os.path.join('.', source_filename))
        target_image.save(os.path.join('.', target_filename))

        # Run your processing script here
        os.system(f"python3 run.py --target {target_filename} --source {source_filename} -o images/{client_id}.png --execution-provider cpu")
        image = Image.open(f"images/{client_id}.png")
        #model = EdsrModel.from_pretrained('eugenesiow/edsr-base', scale=2)
        #inputs = ImageLoader.load_image(image)
        #preds = model(inputs)
        #ImageLoader.save_image(preds, f'images/{client_id}.png')
        #processed_filename = f"{client_id}.png"
        processed_url = f"{request.url_root}get/{client_id}.png"

        return jsonify({'processed_url': processed_url})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get/<id>', methods=['GET'])
def get_processed_photo(id):
    print(id)
    return send_from_directory('images', id)

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=False, port=443)
