import json
import requests
import os
import shutil
import tqdm
from tqdm import tqdm

def get_data_to_upload():
    path = os.getcwd()
    name_folder = path.split("\\")[-1]
    return name_folder

def checking_the_directory(album):
    if not os.path.isdir(album):
        os.mkdir(album)
        os.chdir(album)
    else:
        shutil.rmtree(album)
        os.mkdir(album)
        os.chdir(album)

def get_photo(name_file):
    with open(f'{name_file}.json', 'r') as file:
        json_data = json.load(file)
    list_photo =  json_data['response']['items']
    count = []
    data_photos = {}
    checking_the_directory(name_file)
    for i in tqdm(list_photo, desc='Получаем фотографии с VK'):
        photo = i['sizes'][-1]['url']
        type_size = i['sizes'][-1]['type']
        name_photos = i['likes']['count']
        response = requests.get(photo)
        if f'{name_photos}.jpg' in count:
            ind = count.count(f'{name_photos}.jpg')
            count.append(f'{name_photos}.jpg')

            data_photos.setdefault(f'{name_photos}({ind}).jpg', [{'file_name': f'{name_photos}({ind}).jpg', 'size': type_size}])
            with open(f'{name_photos}({ind}).jpg', 'wb') as file:
                file.write(response.content)
        else:
            count.append(f'{name_photos}.jpg')
            data_photos.setdefault(f'{name_photos}.jpg', [{'file_name': f'{name_photos}.jpg', 'size': type_size}])
            with open(f'{name_photos}.jpg', 'wb') as file:
                file.write(response.content)
    with open(f'Data_photos.json', 'w') as file:
        json.dump(data_photos, file, ensure_ascii=False,indent=4)

def index_photo(ph):
    with open('Data_photos.json', 'r') as file:
        json_data = json.load(file)
        response = json_data[ph][0]
        return response

class VK:
    def __init__(self, token, user_id):
        self.token = token
        self.user_id = user_id

    def common_params(self):
        return {
            'access_token': self.token,
            'v': '5.131'
        }

    def get_user_list_photo(self):
        URL = 'https://api.vk.com/method/photos.get'
        params = self.common_params()
        params.update({
            'owner_id': self.user_id,
            'album_id': 'profile',
            'extended': 1,
            'photo_sizes': 1
        })
        response = requests.get(URL, params=params)
        with open(f'{params["album_id"]}.json', 'w') as file:
            json.dump(response.json(), file, ensure_ascii=False, indent=4)
        get_photo('profile')

class Yandex:
    url = 'https://cloud-api.yandex.net/v1/disk/resources'

    def __init__(self, token):
        self.token = token

    def common_headers(self):
        return {"Authorization": self.token}

    def checking_the_folder(self):
        params = {'path': f'{get_data_to_upload()}'}
        response = requests.get(self.url, params=params, headers=self.common_headers())
        return response.status_code

    def folder(self):
        params = {'path': f'{get_data_to_upload()}'}
        response = requests.put(self.url, params=params, headers=self.common_headers())
        return response.status_code

    def new_folder(self):
        list_uploaded_photos = []
        for photo in tqdm(os.listdir()[:-1], desc='Загрузка фотографий на Яндекс.Диск'):
            self.update(photo)
            list_uploaded_photos.append(index_photo(photo))
            pass
        os.chdir('../')
        with open('Uploaded photos.json', 'w') as file:
            json.dump(list_uploaded_photos, file, ensure_ascii=False, indent=4)


    def delete_a_folder(self):
        params = {'path': f'{get_data_to_upload()}'}
        response = requests.delete(self.url, params=params, headers=self.common_headers())
        return response.status_code

    def uploading_photos(self, ph):
        params = {'path': f'{get_data_to_upload()}/{ph}'}
        data = requests.get(f'{self.url}/upload', params=params, headers=self.common_headers())
        path_to_url = data.json().get('href', '')
        return path_to_url

    def update(self, p):
        path = os.getcwd()
        with open(f'{p}', 'rb') as file:
            res = requests.put(self.uploading_photos(p), files={'file': file})
        return path

    def auto_save_photos(self):
        if self.checking_the_folder() != 404:
            if self.delete_a_folder() != 423:
                while self.delete_a_folder() == 202:
                    self.delete_a_folder()
                else:
                    if self.delete_a_folder() ==423:
                        print('Код 423. Технические работы. Попробуйте запустить программу еще раз.')
                    else:
                        self.folder()
                        self.new_folder()
            else:
                print('Код 423. Технические работы. Попробуйте запустить программу еще раз.')
        else:
            self.folder()
            self.new_folder()


if __name__ == '__main__':

    token = ('')
    user_id = input('Введите свой id пользователя vk: ')
    TOKEN_YD = input('Введите свой токен с Полигона Яндекс.Диска. : ')
    vk_client = VK(token, user_id)
    yd_client = Yandex(TOKEN_YD)
    vk_client.get_user_list_photo()
    yd_client.auto_save_photos()
















