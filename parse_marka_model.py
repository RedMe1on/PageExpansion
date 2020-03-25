import pandas as pd
from bs4 import BeautifulSoup
import requests
import urllib3


def get_response(url: str) -> BeautifulSoup:
    try:
        r = requests.get(url, verify=False)
    except Exception:
        print('That impossible!')
    return BeautifulSoup(r.text)


def parse_mark(soup: BeautifulSoup) -> list:
    """Парсит марки с соответствующими им URL главной страницы.

    soup - BeautifulSoup объект структуры данных главной страницы (пример: https://ddcar.ru/).

    Возвращает список моделей по порядку."""

    mark_list = [item.text for item in soup.findAll('div', attrs={'class': 'b-form_field'})]
    # срезаем два последних элемента, потому что они не относятся к моделям, но парсятся тоже (быстрее,
    # чем прописывать исключения)
    return mark_list[:-2]


def parse_model(soup: BeautifulSoup) -> list:
    """Парсит модели со страниц марок.

    soup - BeautifulSoup объект  структуры данных одной из страниц марок (пример: https://ddcar.ru/acura).

    Возвращает список моделей по порядку."""

    model_list = [item.text for item in soup.findAll('div', attrs={'class': 'b-form_field model'})]
    return model_list


def get_url_mark(soup: BeautifulSoup) -> list:
    """Парсит ссылки на страницы марок.

    soup - BeautifulSoup объект структуры данных главной страницы (пример: https://ddcar.ru/).

    Возвращает список URL страниц марок по порядку."""

    bs_list = [item for item in soup.findAll('div', attrs={'class': 'b-form_field'})]
    url_mark_list = []
    for href in bs_list[:-2]:
        url_mark_list.append('https://ddcar.ru' + href.find('a').get('href'))
    return url_mark_list


def get_url_model(soup: BeautifulSoup) -> list:
    bs_list = [item for item in soup.findAll('div', attrs={'class': 'b-form_field model'})]
    url_model_list = []
    for href in bs_list:
        url_model_list.append('https://ddcar.ru' + href.find('a').get('href'))
    return url_model_list


def get_data_marka_model(mark_list: list, url_mark_list: list) -> pd:
    data = pd.DataFrame(columns=['Марка', 'Модель', 'URL'])
    mark_and_urlmark_dict = dict(zip(url_mark_list, mark_list))
    for url, mark in mark_and_urlmark_dict.items():
        data = data.append({"Марка": mark, "URL": url}, ignore_index=True)
        soup = get_response(url)
        model_list = parse_model(soup)
        url_model_list = get_url_model(soup)
        model_and_url = dict(zip(url_model_list, model_list))
        for url, model in model_and_url.items():
            data = data.append({"Марка": mark, "Модель": model, "URL": url}, ignore_index=True)
    return data


if __name__ == "__main__":
    urllib3.disable_warnings()
    url = 'https://ddcar.ru/'

    soup = get_response(url)
    mark_list = parse_mark(soup)
    url_mark_list = get_url_mark(soup)
    data = get_data_marka_model(mark_list, url_mark_list)
    data.to_csv('marka_model.csv', encoding='utf-8-sig', sep=';', index=False)
