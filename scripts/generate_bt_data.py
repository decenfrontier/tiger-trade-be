from datetime import datetime

import pandas as pd


def gen_triangular_bt_data(start_dt='2023-01-01', end_dt='2023-01-02'):
    start_dt = datetime.strptime(start_dt, '%Y-%m-%d')
    end_dt = datetime.strptime(end_dt, '%Y-%m-%d')
    total_seconds = int((end_dt - start_dt).total_seconds())
    start_ts = int(start_dt.timestamp() * 1000)
    timestamps = [start_ts + i*1000 for i in range(total_seconds)]
    df = pd.DataFrame(timestamps, columns=['timestamp'])
    df.to_csv('bt_data.csv', index=False)
    print('done!')


if __name__ == '__main__':
    gen_triangular_bt_data(start_dt='2023-01-01', end_dt='2023-01-02')
