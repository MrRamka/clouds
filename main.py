import requests

from config import get_config_variables


def get_lat_and_lat_by(data_obj):
    return {
        "lat": data_obj['geo_lat'],
        "lon": data_obj['geo_lon']
    }


def send_dadata_query(data: str, api_key: str, secret_key: str):
    dadata_api_link = "https://cleaner.dadata.ru/api/v1/clean/address"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {api_key}",
        "X-Secret": f"{secret_key}",
    }
    request = requests.post(dadata_api_link, json=[data], headers=headers)
    return request.json()[0]


def get_weather(lat, lon, weather_token):
    link = f"http://api.openweathermap.org/data/2.5/weather?lon={lon}&lat={lat}&appid={weather_token}&units=metric"
    return requests.get(link).json()


def get_voice_ans_from_yandex(message, filename, yandex_key):
    headers = {
        "Authorization": f"Api-Key {yandex_key}",
    }
    api_link = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
    data = {
        "text": message
    }
    request = requests.post(api_link, data=data, headers=headers)
    file = open(filename, "wb")
    file.write(request.content)


def get_voice_input(filename, yandex_key):
    file = open(filename, "rb")
    headers = {
        "Authorization": f"Api-Key {yandex_key}",
    }
    api_link = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"
    request = requests.post(api_link, data=file.read(), headers=headers)
    return request.json()['result']


def main():
    config = get_config_variables("keys.ini")
    yandex_key = config["yacloud"]["api_key"]
    recognised_text = get_voice_input("address.ogg", yandex_key)

    secret_key = config["dadata"]["api_secret"]
    api_key = config["dadata"]["api_key"]
    data_obj = send_dadata_query(recognised_text, api_key, secret_key)

    weather_token = config["weather"]["api_key"]
    lat_lon = get_lat_and_lat_by(data_obj)
    weather = get_weather(lat_lon.get("lat"), lat_lon.get("lon"), weather_token)
    ans_text = f"Температура в {recognised_text} {weather['main']['temp']} градусов по цельсию"
    get_voice_ans_from_yandex(ans_text, "ans.ogg", yandex_key)


if __name__ == "__main__":
    main()
