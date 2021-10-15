# Homework 1

## Настройка
1. Для настройки boto3 SDK создайте в домашнем каталоге файлы конфигурации и задайте в них:

    Статический ключ в файле `.aws/credentials`:
    
        [default]
        aws_access_key_id = <id>
        aws_secret_access_key = <secretKey>

2. Установите необходимые библиотеки

   `pip install -r requirements.txt`

3. Перейдите в каталог `homework_#1`
    
    `cd homework_#1`

4. Создать файл `keys.ini`. Структура файла находится в `keys.example.ini`

## Запуск

Список доступных команд

    python helper.py -h

Отправка фотографий в облачное хранилище

    python helper.py upload -a album -p path 

Загрузка фотографий на компьютер

    python helper.py download -p path -a album

Список альбомов

    python helper.py list

Список фотографий в альбоме 

    python helper.py list -a album