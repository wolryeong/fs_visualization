import requests
import os
import pandas as pd
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool as ThreadPool
from requests.adapters import HTTPAdapter


COL_NAME = ['University', 'date', 'event', 'C', 'teams', 'place', 'cost', 'bp', 'ed', 'acc', 'sp',
            'autox', 'endu', 'fuel', 'pen', 'total', 'wrl']
# COUNT = 0


def get_one_page(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/'
                          '90.0.4430.93 Safari/537.36'}

        # 由于连接方在一段时间后没有正确答复或连接的主机没有反应，连接尝试失败解决方法
        # 增加max_retries参数，同时使用requests.session.mount
        s = requests.session()
        s.mount('http://', HTTPAdapter(max_retries=5))
        s.mount('https://', HTTPAdapter(max_retries=5))

        response = s.request("GET", url=url, headers=headers, timeout=30)
        # response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.text
        else:
            print(response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        print('访问 http 发生错误... ')
        print(e)
        return None


def get_table(arg):
    uni_name, url = arg
    all_html = get_one_page(url)
    soup = BeautifulSoup(all_html, 'html.parser')
    table = soup.find_all(name='table')

    if url.startswith('tid', 8):
        if len(table) > 1:
            rank_table = table[1]
            df = get_score(rank_table, uni_name)
        else:
            df = no_data(uni_name)
    else:
        if len(table) >= 1:
            rank_table = table[0]
            df = get_score(rank_table, uni_name)
        else:
            df = no_data(uni_name)
    return df


def get_score(rank_table, uni_name):
    rows = rank_table.find_all('tr')
    cols = rows[0].text.split('\n')[1:-1]

    df = pd.DataFrame(columns=cols)
    for i_row in range(1, len(rows) - 1):
        i_d = pd.DataFrame(rows[i_row].text.split('\n')[1:-1]).T
        i_d.columns = df.columns

        score = rows[i_row].find_all('div')
        for i_grid in range(4, 12):
            if score[i_grid].get('title') is not None:
                i_d.iloc[0, i_grid + 1] = score[i_grid].get('title')[:-7]
            else:
                if score[i_grid].find('b'):
                    i_d.iloc[0, i_grid + 1] = score[i_grid].find('b').get('title')[:-7]
                else:
                    i_d.iloc[0, i_grid + 1] = 0

        df = df.append(i_d)
    df.reset_index(drop=True, inplace=True)

    df['University'] = uni_name
    df = df.reindex(columns=COL_NAME)

    # duplication check
    print(uni_name, df.duplicated(subset=['date', 'event']).any())

    # outlier handling
    if df.duplicated(subset=['date', 'event']).any():
        df.drop(index=df[df.duplicated(subset=['date', 'event'])].index[0], inplace=True, axis=0)

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
        os.remove(r'./data/cv_score.csv')
        os.remove(r'./data/ev_score.csv')
        os.remove(r'./data/dv_score.csv')
    except:
        pass

    data_root = ['./data/cv_list.csv', './data/ev_list.csv', './data/dv_list.csv']
    save_root = ['./data/cv_score.csv', './data/ev_score.csv', './data/dv_score.csv']
    # pool_rank(data_root[0], save_root[0])
    for i in range(2):
        print('------------------------------------------   ------------------------------------------')
        print('------------------------------------------', i, '------------------------------------------')
        print('------------------------------------------   ------------------------------------------')
        pool_rank(data_root[i], save_root[i])


if __name__ == '__main__':
    main()
