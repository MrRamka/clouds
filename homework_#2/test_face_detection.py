import base64
import json

import requests

YANDEX_VISION_TYPE = "FACE_DETECTION"
YANDEX_VISION_API = "https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze"
API_KEY = "API_KEY"
image = "images\\source_images.jpg"


def send_image_vision_request(image):
    request_json = json.dumps(
        {"analyze_specs": [
            {"content": image, "features": [{"type": YANDEX_VISION_TYPE}]}]},
    )

    authorization_headers = {
        "Authorization": f"Api-Key {API_KEY}",
        "Content-Type": "application/json"
    }
    yandex_vision_response = requests.post(
        YANDEX_VISION_API,
        headers=authorization_headers,
        data=request_json
    )
    return yandex_vision_response.json()


def encode_file(file):
    with open(file, 'rb') as f:
        file_content = f.read()
    return base64.b64encode(file_content).decode('utf-8')


file = encode_file(image)
print(send_image_vision_request(file))
