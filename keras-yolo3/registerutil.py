from datetime import datetime

# utilities for self register system 

def y_n_input() -> bool:
    """
    y/Y or n/Nでどちらかを入力するまで聞き続ける
    boolを返す
    y/Y -> True
    n/N -> False
    """
    while True:
        input_key = input('はい[y/Y]、いいえ[n/N]？')
        if input_key == 'y' or input_key == 'Y':
            return True
        elif input_key == 'n' or input_key == 'N':
            return False
        else:
            print('y/Y もしくは n/N で入力してください。')

def date_format_checker(slash=True):
    """
    正しい日付formatで入力するまで入力させ続ける
    if slash == True:
        example 2020/7/14
    elif slash == False:
        example 20200714

    *入力形式は揃えたいしスラッシュありでしか使わなさそう*
    """
    todayobj = datetime.now()

    dateformat_str = '%Y/%m/%d'
    
    # スラッシュ入れない教の場合
    if not slash:
        dateformat_str = dateformat_str.replace('/', '')

    example_str = '[例：{}年{}月{}日 → {}]: '.format(todayobj.year, todayobj.month, todayobj.day, todayobj.strftime(dateformat_str))

    while True:
        datestr = input(example_str)
        # format check
        try:
            dateobj = datetime.strptime(datestr, dateformat_str)
        except:
            print('正しいフォーマットで入力してください。', end='')
            continue
        else:
            if todayobj < dateobj:
                print('本日以前の日付を入力してください。', end='')
                continue
        # チェック抜けたらreturn
        return dateobj