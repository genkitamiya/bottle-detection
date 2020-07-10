import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def get_df(path, start=None, end=None):
    """
    期間指定 or 全期間の帳簿を取得

    Parameters
    ----------
    start: int
      起算日（年月日）
    end: int
      終了日（年月日）
    """
    df = pd.concat((pd.read_csv(path+f, index_col=0) for f in os.listdir(path)))
    df['saletime'] = [datetime.strptime(str(x), '%Y/%m/%d %H:%M:%S') for x in df['saletime']]
    tmp_df = df.set_index(['saletime'])

    if not start and not end:
        label = ''
        return tmp_df, label
    elif not end:
        label = ' between {} - {}'.format(start, datetime.today().strftime('%Y/%m/%d'))
        start = datetime.strptime(start, '%Y/%m/%d')
        end = datetime.today() + timedelta(1)
        tmp_df = tmp_df.loc[start:end]
        return tmp_df, label
    else:
        label = ' between {} - {}'.format(start, end)
        date_start = datetime.strptime(str(start), '%Y/%m/%d')
        date_end = datetime.strptime(str(end), '%Y/%m/%d') + timedelta(1)
        tmp_df = tmp_df.loc[start:end]
        return tmp_df, label


def sales_day(path, datestr=datetime.today().strftime('%Y%m%d')):
    """
    1日の売上金額を表示
    """
    file = 'sales_{}.csv'.format(datestr)
    df = pd.read_csv(path+file)
    total = df['prodprice'].sum()
    print('{}年{}月{}日の売上金額は¥{}です。'.format(datestr[:4], datestr[4:6], datestr[6:], total))


def sales_history(path, start=None, end=None):
    """
    指定期間内の売上推移を表示
    """
    df, label = get_df(path, start, end)
    # 日毎に正規化
    df.index = df.index.normalize()
    #　日毎にgroupby
    df_plt = df.groupby(df.index).sum()

    # グラフ化
    plt.bar(df_plt.index.strftime('%Y/%m/%d'), df_plt['prodprice'])
    plt.title('Total sales per day'+label)
    plt.xlabel('Day')
    plt.ylabel('Sales (JPY)')
    plt.show()


def sales_by_product(path, start=None, end=None):
    """
    商品毎の売上個数
    """
    df, label = get_df(path, start, end)

    data = df['prodname'].value_counts()
    plt.bar(data.index, data)
    plt.title('Total products sold'+label)
    plt.xlabel('Product Name')
    plt.ylabel('Quantity')
    plt.show()


def sales_by_time(path, start=None, end=None):
    """
    時間帯毎の売上個数
    """
    df, label = get_df(path, start, end)
    df_plt = df.groupby(df.index.hour).sum()

    # 1時間毎の総売上
    hours = np.arange(1,25)
    sales = np.zeros(24)
    sales[df_plt.index] = df_plt['prodprice']

    # グラフ化
    plt.bar(hours, sales)
    plt.title('Total sales per hour'+label)
    plt.xlabel('Hour')
    plt.ylabel('Sales (JPY)')
    plt.show()

def initiate(path):
    while True:
        key = input('売上の分析を開始します。「Enter」を押してください')
        key = input('ご覧になりたい項目を選択してください。\
                    \n一日の売上[1]、売上の推移[2]、商品毎の売上[3]、時間帯毎の売上[4]、操作終了[q] ')

        if key == 'q':
            print('売上の分析を終了します。')
            break

        if key == '1':
            while True:
                key = input('一日の売上を表示します。ご覧になりたい日にちを選択してください\
                               \n本日[1]、その他日にち[2]。')
                if key == '1':
                    sales_day(path)
                elif key == '2':
                    date = input('ご覧になりたい日にちを例のように入力してください（例：2020年7月10日→20200710）。')
                    sales_day(path, date)

                key = input('再度一日の売上をご覧になりますか？\
                               \nはい[y]、いいえ[n]。')
                if key == 'y':
                    continue
                else:
                    break

        if key == '2':
            while True:
                key = input('売上の推移を表示します。ご覧になりたい期間を選択してください\
                               \n全期間[1]、指定日から本日までの期間[2]、その他期間[3]。')
                if key == '1':
                    sales_history(path)
                elif key == '2':
                    date = input('ご覧になりたい期間の起算日を例のように入力してください（例：2020年7月10日→20200710）。')
                    sales_history(path, start=date)
                elif key == '3':
                    start = input('ご覧になりたい期間の起算日を例のように入力してください（例：2020年7月10日→20200710）。')
                    end = input('次にご覧になりたい期間の終了日を同様に入力してください')
                    sales_history(path, start, end)

                key = input('再度売上の推移をご覧になりますか？\
                               \nはい[y]、いいえ[n]。')
                if key == 'y':
                    continue
                else:
                    break

        if key == '3':
            while True:
                key = input('商品毎の売上個数を表示します。ご覧になりたい期間を選択してください\
                               \n全期間[1]、指定日から本日までの期間[2]、その他期間[3]。')
                if key == '1':
                    sales_by_product(path)
                elif key == '2':
                    date = input('ご覧になりたい期間の起算日を例のように入力してください（例：2020年7月10日→20200710）。')
                    sales_by_product(path, start=date)
                elif key == '3':
                    start = input('ご覧になりたい期間の起算日を例のように入力してください（例：2020年7月10日→20200710）。')
                    end = input('次にご覧になりたい期間の終了日を同様に入力してください')
                    sales_by_product(path, start, end)

                key = input('再度商品毎の売上個数をご覧になりますか？\
                               \nはい[y]、いいえ[n]。')
                if key == 'y':
                    continue
                else:
                    break

        if key == '4':
            while True:
                key = input('時間帯毎の売上を表示します。ご覧になりたい期間を選択してください\
                               \n全期間[1]、指定日から本日までの期間[2]、その他期間[3]。')
                if key == '1':
                    sales_by_time(path)
                elif key == '2':
                    date = input('ご覧になりたい期間の起算日を例のように入力してください（例：2020年7月10日→20200710）。')
                    sales_by_time(path, start=date)
                elif key == '3':
                    start = input('ご覧になりたい期間の起算日を例のように入力してください（例：2020年7月10日→20200710）。')
                    end = input('次にご覧になりたい期間の終了日を同様に入力してください')
                    sales_by_time(path, start, end)

                key = input('再度時間帯毎の売上をご覧になりますか？\
                               \nはい[y]、いいえ[n]。')
                if key == 'y':
                    continue
                else:
                    break
