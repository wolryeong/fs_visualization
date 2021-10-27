import pandas as pd
import os


def main():
    try:
        os.remove(r'./data/cv_list.csv')
        os.remove(r'./data/ev_list.csv')
        os.remove(r'./data/dv_list.csv')
        os.remove(r'./data/uni_region.csv')
    except:
        pass

    data = pd.read_csv(r'./data/all_uni.csv')
    data.dropna(axis=0, thresh=3, inplace=True)

    cv_teams = data.loc[data['CV_team_name'].notna(), ['University', 'CV_team_name', 'CV_link']]
    cv_teams.columns = ['University', 'CV_team_name', 'link']
    ev_teams = data.loc[data['EV_team_name'].notna(), ['University', 'EV_team_name', 'EV_link']]
    ev_teams.columns = ['University', 'EV_team_name', 'link']
    dv_teams = data.loc[data['DV_team_name'].notna(), ['University', 'DV_team_name', 'DV_link']]
    dv_teams.columns = ['University', 'DV_team_name', 'link']

    data[['Country', 'City', 'University']].to_csv(r'./data/uni_region.csv', mode='a', index=False, sep=',', encoding='utf-8_sig')
    cv_teams.to_csv(r'./data/cv_list.csv', mode='a', index=False, sep=',', encoding='utf-8_sig')
    ev_teams.to_csv(r'./data/ev_list.csv', mode='a', index=False, sep=',', encoding='utf-8_sig')
    dv_teams.to_csv(r'./data/dv_list.csv', mode='a', index=False, sep=',', encoding='utf-8_sig')


if __name__ == '__main__':
    main()
