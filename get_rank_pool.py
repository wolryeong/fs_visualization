import requests
import os
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool as ThreadPool


COL_NAME = ['University', 'date', 'event', 'C', 'teams', 'place', 'cost', 'bp', 'ed', 'acc', 'sp',
            'autox', 'endu', 'fuel', 'pen', 'total', 'wrl']
# COUNT = 0


def get_one_page(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/'
                          '90.0.4430.93 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.text
        else:
            print(response.status_code)
            return None
    except:
        print('访问 http 发生错误... ')
        return None


def get_table(arg):
    uni_name, url = arg
    all_html = get_one_page(url)
    soup = BeautifulSoup(all_html, 'html.parser')
    table = soup.find_all(name='table')

    if url.startswith('tid', 8):
        if len(table) > 1:
            rank_table = table[1]
            df = get_rank(rank_table, uni_name)
        else:
            df = no_data(uni_name)
    else:
        if len(table) >= 1:
            rank_table = table[0]
            df = get_rank(rank_table, uni_name)
        else:
            df = no_data(uni_name)
    return df


def get_rank(rank_table, uni_name):
    rows = rank_table.find_all('tr')
    cols = rows[0].text.split('\n')[1:-1]

    df = pd.DataFrame(columns=cols)
    for i_row in range(1, len(rows) - 1):
        i_d = pd.DataFrame(rows[i_row].text.split('\n')[1:-1]).T
        i_d.columns = df.columns
        df = df.append(i_d)
    df.reset_index(drop=True, inplace=True)

    df['University'] = uni_name
    df = df.reindex(columns=COL_NAME)

    # duplication check
    print(uni_name, df.duplicated(subset=['date', 'event']).any())

    # outlier handling
    if df.duplicated(subset=['date', 'event']).any():
        df.drop(index=df[df.duplicated(subset=['date', 'event'])].index[0], inplace=True, axis=0)
    df.replace('-', np.nan, inplace=True)

    # reset data type
    df['date'] = pd.to_datetime(df.date).map(lambda x: x.strftime('%Y-%m'))
    df = df.apply(pd.to_numeric, errors='ignore')

    return df


def no_data(uni):
    df = pd.DataFrame(columns=COL_NAME)
    df.loc[0, :] = ''
    df['University'] = uni
    df = df.apply(pd.to_numeric, errors='ignore')
    return df


def pool_rank(root_in, root_out):
    data = pd.read_csv(root_in)
    data_in = data.loc[:, ['University', 'link']]
    data_in = data_in.apply(lambda x: tuple(x), axis=1).values.tolist()

    pool = ThreadPool(8)
    result = pool.map(get_table, data_in)
    pool.close()
    pool.join()

    result_df = pd.concat(result, ignore_index=True)
    result_df.to_csv(root_out, mode='a', index=False, sep=',', encoding='utf-8_sig')


def main():
    try:
        os.remove(r'./data/cv_rank.csv')
        os.remove(r'./data/ev_rank.csv')
        os.remove(r'./data/dv_rank.csv')
    except:
        pass

    data_root = ['./data/cv_list.csv', './data/ev_list.csv', './data/dv_list.csv']
    save_root = ['./data/cv_rank.csv', './data/ev_rank.csv', './data/dv_rank.csv']
    for i in range(2):
        print('------------------------------------------   ------------------------------------------')
        print('------------------------------------------', i, '------------------------------------------')
        print('------------------------------------------   ------------------------------------------')
        pool_rank(data_root[i], save_root[i])
    # pool_rank(data_root[0], save_root[0])


if __name__ == '__main__':
    main()

