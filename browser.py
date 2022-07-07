import argparse
import os
from collections import deque
import requests
import re
from bs4 import BeautifulSoup
from colorama import Fore, Style


def create_file(path_, url_, data_):
    # deletion of the all characters after the last . dot by using slicing method
    file_name_ = url_[8:url_.rfind('.')]
    file_name_ = file_name_.replace('.', '_')
    path_ = f'{path_}/{file_name_}'
    with open(path_, 'w', encoding='utf-8') as file_:
        file_.write(data_)
    return file_name_


def get_file_data(path_, url_):
    path_ = f'{path_}/{url_}'
    with open(path_, 'r') as file_:
        return file_.read()


def check_url_dot(url_):
    if '.' in url_:
        return True
    return False


def check_url_https(url_):
    if not url_.startswith('https://'):
        return f'https://{url_}'
    return url_


def check_url_using_re(url_):
    regex = re.compile(
            r'^(?:http|ftp)s?://' # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
            r'localhost|' #localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?::\d+)?' # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, f'{url_}') is not None


if __name__ == '__main__':

    files = []
    history = deque()
    file_name = None

    parser = argparse.ArgumentParser()
    parser.add_argument("directory")
    args = parser.parse_args()

    if args.directory:
        if not os.access(args.directory,  os.F_OK):
            os.mkdir(args.directory)

    while True:
        url = input()
        if url.lower() == 'exit':
            break
        elif '.' not in url and url not in files and url.lower() != 'back':
            print('Incorrect URL')
        elif check_url_dot(url):
            if file_name:
                history.append(file_name)

            url = check_url_https(url)
            r = requests.get(f'{url}')
            soup = BeautifulSoup(r.content, 'html.parser')
            tags = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'ul', 'ol', 'li'])
            if r:
                file_name = create_file(args.directory, url, soup.get_text())
                files.append(file_name)
                for t in tags:
                    if t.name == 'a':
                        print(Fore.BLUE + t.text)
                    else:
                        print(Style.RESET_ALL + t.text)
        elif url in files:
            print(get_file_data(args.directory, url))
        elif url.lower() == 'back' and history:
            print(get_file_data(args.directory, history.pop()))
        elif url.lower() == 'back' and not history:
            pass
        else:
            print('Incorrect URL')

