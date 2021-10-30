import base64
import io
import json
import os
import uuid
import boto3
import requests
from PIL import Image
from requests.structures import CaseInsensitiveDict

file_suffix = (".jpg", ".jpeg")

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
API_KEY = os.environ.get('API_KEY')

YANDEX_VISION_TYPE = "FACE_DETECTION"
YANDEX_VISION_API = "https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze"

SOURCE_PREFIX = "source_"


def get_bucket_id_by_event(event) -> str:
    return event['messages'][0]['details']['bucket_id']


def get_object_id_by_event(event) -> str:
    return event['messages'][0]['details']['object_id']


def get_s3_clients():
    session = boto3.session.Session()
    s3 = session.client(
        service_name='s3',
        endpoint_url='https://storage.yandexcloud.net',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,

    )
    sqs = session.resource(
        service_name='sqs',
        endpoint_url='https://message-queue.api.cloud.yandex.net',
        region_name='ru-central1',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
    return s3


def send_image_vision_request(image):
    request_json = json.dumps(
        {"analyze_specs": [
            {"content": image, "features": [{"type": YANDEX_VISION_TYPE}]}]},
    )

    authorization_headers = CaseInsensitiveDict()
    authorization_headers["Authorization"] = f"Api-Key {API_KEY}"
    authorization_headers["Content-Type"] = "application/json"
    yandex_vision_response = requests.post(
        YANDEX_VISION_API,
        headers=authorization_headers,
        data=request_json
    )
    return yandex_vision_response.json()


def crop_and_upload_image(s3, yandex_vision_json_response, object_content, object_id, bucket_id):
    faces_json = yandex_vision_json_response['results'][0]['results'][0]['faceDetection']['faces']

    pillow_image = Image.open(io.BytesIO(object_content))
    faces_objects_names = []
    for (index, face) in enumerate(faces_json):
        coordinate_1 = face['boundingBox']['vertices'][0]
        coordinate_2 = face['boundingBox']['vertices'][2]
        x1 = int(coordinate_1['x'])
        y1 = int(coordinate_1['y'])
        x2 = int(coordinate_2['x'])
        y2 = int(coordinate_2['y'])
        cropped_image = pillow_image.crop((x1, y1, x2, y2))
        imgByteArr = io.BytesIO()
        cropped_image.save(imgByteArr, format='jpeg')
        imgByteArr = imgByteArr.getvalue()
        album_name = object_id[:object_id.find('/')]
        object_name = object_id[object_id.rfind('/') + 1:]
        object_storage_name = f"{album_name}/{object_name}-{uuid.uuid4()}.jpeg"

        upload_face_image(s3, imgByteArr, bucket_id, object_storage_name)
        faces_objects_names.append(object_storage_name)
    return faces_objects_names


def get_bucket_image(s3, bucket_id, object_id):
    s3_response_object = s3.get_object(Bucket=bucket_id, Key=object_id)
    object_content = s3_response_object['Body'].read()
    image = base64.b64encode(object_content)
    return image, object_content


def upload_face_image(s3, image, bucket_id, object_storage_name):
    s3.upload_fileobj(io.BytesIO(image), bucket_id, object_storage_name)


def is_correct_object(object_id: str) -> bool:
    return (object_id.startswith(SOURCE_PREFIX)) and (
            object_id.endswith(file_suffix[0]) or object_id.endswith(file_suffix[1]))


def handler(event, context):
    print(event)
    bucket_id = get_bucket_id_by_event(event)
    object_id = get_object_id_by_event(event)
    print(bucket_id)
    print(object_id)
    if is_correct_object(object_id):

        s3 = get_s3_clients()

        image, object_content = get_bucket_image(s3, bucket_id, object_id)
        yandex_vision_json_response = send_image_vision_request(image.decode('ascii'))

        try:
            faces_objects_names = crop_and_upload_image(s3, yandex_vision_json_response, object_content, object_id,
                                                        bucket_id)
            faces_objects_names_string = str(faces_objects_names)
            message_body = {"uploaded": faces_objects_names_string, "parent": object_id}
            print(message_body)

        except KeyError as err:
            print(err)

