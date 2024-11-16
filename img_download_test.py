import requests

img_data = requests.get("https://cctv-streamer-12.profintel.ru/snapshot/image.jpg?st=0kKaoJxnWNz7ZRgy0nJO3Q&e=1731933802&id=11274").content
with open('image_name.jpg', 'wb') as handler:
    handler.write(img_data)