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