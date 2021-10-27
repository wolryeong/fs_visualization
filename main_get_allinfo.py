import requests
import os
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup


def get_one_page(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/90.0.4430.93 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.text
        else:
            print(response.status_code)
            return None
    except:
        print('访问 http 发生错误... ')
        return None


def get_info():
    all_univ = 'https://www.formulastudent.de/teams/all-universities/'
    all_html = get_one_page(all_univ)
    soup = BeautifulSoup(all_html, 'html.parser')
    all_info = soup.find_all(name='tr')
    return all_info


def get_region(geo_module):
    city = geo_module.find('small').string
    country = geo_module.text.replace(geo_module.find('small').string, '')
    if country == '':
        country = city
    return country, city


def cv_judge(team_name):
    if ('CV-team' in team_name) or (team_name == 'WRL-Combustion'):
        return True
    else:
        return False


def ev_judge(team_name):
    if ('EV-team' in team_name) or (team_name == 'WRL-Electric'):
        return True
    else:
        return False


def dv_judge(team_name):
    if 'DV-team' in team_name:
        return True
    else:
        return False


def get_cv_name(team_name):
    if 'CV-team' in team_name:
        return team_name.split(': ')[1]
    else:
        return team_name


def get_ev_name(team_name):
    if 'EV-team' in team_name:
        return team_name.split(': ')[1]
    else:
        return team_name


def get_dv_name(team_name):
    return team_name.split(': ')[1]


def get_uni_info(uni_module):
    uni_name = uni_module.find('b').string

    teams = uni_module.text.split('\n')[1:]
    if ',' in ''.join(teams):
        teams = ''.join(teams).split(', ')
    url = uni_module.find_all('a')

    cv_name, ev_name = np.nan, np.nan
    cv_link, ev_link = np.nan, np.nan
    dv_name, dv_link = np.nan, np.nan
    for i_team in range(len(teams)):
        if cv_judge(teams[i_team]):
            cv_name = get_cv_name(teams[i_team])
            cv_link = url[i_team].get('href')
        elif ev_judge(teams[i_team]):
            ev_name = get_ev_name(teams[i_team])
            ev_link = url[i_team].get('href')
        elif dv_judge(teams[i_team]):
            dv_name = get_dv_name(teams[i_team])
            dv_link = url[i_team].get('href')
    return uni_name, cv_name, cv_link, ev_name, ev_link, dv_name, dv_link


def save_df():
    info = get_info()
    uni_team_info_df = pd.DataFrame(columns=['Country', 'City', 'University',
                                             'CV_team_name', 'CV_link', 'EV_team_name',
                                             'EV_link', 'DV_team_name', 'DV_link'])

    for i_row in range(1, len(info)):
        #     print(i_row)
        row = info[i_row].find_all('td')

        geo = row[0]
        ctry, cty = get_region(geo)
        uni_team_info_df.loc[i_row, 'Country'] = ctry
        uni_team_info_df.loc[i_row, 'City'] = cty

        uni = row[1]
        if uni.text == '':
            continue
        uni_name, cv_name, cv_link, ev_name, ev_link, dv_name, dv_link = get_uni_info(uni)
        print(uni_name)

        uni_team_info_df.loc[i_row, 'University'] = uni_name
        uni_team_info_df.loc[i_row, 'CV_team_name'] = cv_name
        uni_team_info_df.loc[i_row, 'CV_link'] = cv_link
        uni_team_info_df.loc[i_row, 'EV_team_name'] = ev_name
        uni_team_info_df.loc[i_row, 'EV_link'] = ev_link
        uni_team_info_df.loc[i_row, 'DV_team_name'] = dv_name
        uni_team_info_df.loc[i_row, 'DV_link'] = dv_link

    uni_team_info_df.to_csv(r'./data/all_uni.csv', mode='a', index=False, sep=',', encoding='utf-8_sig')


if __name__ == '__main__':
    print("当前路径 -  %s" %os.getcwd())
    try:
        os.remove(r'./data/all_uni.csv')
    except:
        pass

    save_df()
