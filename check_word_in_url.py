import pandas as pd


def get_top_usluga_url(url: str) -> str:
    return url[:url.rfind('/')]


def get_relative_url(url: str) -> str:
    return url.replace('https://ddcar.ru', '')


def get_end_usluga_url(url: str) -> str:
    return url[url.rfind('/'):]


usluga_name = 'Замена стартера'
usluga_url = '/elektrooborudovanie/starter-zamena'

columns_list = ['Марка', 'Модель', 'Услуга', 'Регион', 'URL']
data_read = pd.read_csv('marka_model.csv', encoding='utf-8-sig', sep=';')
data_parent_usluga = pd.DataFrame(columns=columns_list)  # для родительских услуг, которые еще не созданы
# добавляем столбец с услугой к данным
data_read['Услуга'] = usluga_name
db_all_page = pd.read_csv('all.csv', encoding='cp1251', sep=';')
db_all_page = db_all_page.iloc[:, :6]

# находим родительский раздел, в котором лежит услуга
top_usluga_url = get_top_usluga_url(usluga_url)

# ищем название родительской услуги
top_usluga_name = False
data_filter_url = db_all_page[db_all_page['_URL_'].str.endswith(f'{top_usluga_url}', na=False)]
if not data_filter_url.empty:
    top_usluga_name = data_filter_url['Услуга'].reset_index(drop=True)[0]
else:
    print(f'Нет родительской услуги: {top_usluga_url}')
# если название родительской услуги есть, то ищем раздел в выгрузке с пересечением марки и модели
if top_usluga_name:
    for idx, data in data_read.iterrows():

        data_filter_marka = db_all_page[db_all_page['Марка'] == data.Марка]
        if pd.notna(data.Модель):
            data_filter_model = data_filter_marka[data_filter_marka['Модель'] == data.Модель]
        else:
            data_filter_model = data_filter_marka[pd.isna(data_filter_marka['Модель'])]
        # проверка на уже созданную услугу у марки или марки+модели
        check_page = data_filter_model[data_filter_model['Услуга'] == data.Услуга]
        if not check_page.empty:
            data_read = data_read.drop([idx])
            print(f'Уже есть услуга {data.Услуга, data.Марка, data.Модель}')
            continue
        # проверка на созданную родительскую услугу
        data_filter_model_url = data_filter_model[data_filter_model['Услуга'] == top_usluga_name]
        if not data_filter_model_url.empty:
            url_change = data_filter_model_url._URL_ + get_end_usluga_url(usluga_url)
            try:
                data_read.loc[idx, ['URL']] = url_change.item()
            except ValueError:
                print('Больше одной страницы: \n', data_filter_model_url._URL_)
        else:
            print(f'Не найдена услуга {top_usluga_name} для \n{data}')
            data_parent_usluga = data_parent_usluga.append({'Марка': data['Марка'], 'Модель': data['Модель'], 'Услуга': top_usluga_name,
                                       'URL': get_relative_url(data['URL']+top_usluga_url)}, ignore_index=True)
            data_read.loc[idx, ['URL']] = get_relative_url(data.URL + usluga_url)
            print(data_read.loc[idx, ['URL']])

print(data_read['URL'])
data_read['Регион'] = ''
data_read = data_read[columns_list]
data_read.to_csv('file_import_with_chek_for_top_usluga.csv', sep=";", encoding="utf-8-sig")
data_parent_usluga.to_csv('_parent_service.csv', sep=";", encoding="utf-8-sig")
