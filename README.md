## SOLIDbros

### Repository for HACKATON 2024

Contributors:
 - Ivan Kirspu - Captain
 - Andrew Shmakov
 - Osipov Egor
 - Kopylov Egor
 - Denis Zhereshtiev

# Инструкция по запуску телеграмм-бота по управлению домофонами
Необходимые библиотеки:
- pyTelegramBotAPI
- requests
- Flask

В файле config.py в переменные BOT_TOKEN и DOM_API_TOKEN нужно занести электронный ключ бота (если его ещё нет) и "SecretToken" соответственно.

Для эффективной работы приложения необходимо установить специальное ПО для автоматизации, развёртывания и управления приложениями - [Doker Desktop](https://www.docker.com/).

После установки докера, необходимо создать образ и контейнер, содержащий скопированные файлы приложения. Для создания образа на основе Dockerfile, прописать в консоль: 
```shell
docker build -t <название образа> 
```
Пример команды:
```shell
docker build -t image . (точка указывает на текущую директорию)
```
Для создания контейнера из образа можно использовать команду:
```shell
docker run -d -p <порт на хостовой машине>:<порт внутри контейнера> --name <название контейнера> <название уже созданного образа>.
```
Пример команды:
```shell
docker run -d -p 5000:5000 --name solid-container image
```