import pandas as pd


def data_dropna():
    data = pd.read_csv(r'./data/ev_score.csv')
    data_na = data[data['date'].isna()]
    data.dropna(subset=['date'], inplace=True)
    data.reset_index(drop=True, inplace=True)
    data.to_csv('./data/ev_score_dropna.csv', sep=',', encoding='utf-8_sig')


if __name__ == '__main__':
    data_dropna()
