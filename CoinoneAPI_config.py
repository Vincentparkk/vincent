import configparser
from time import strftime           

def config_generator():
    # 설정파일 만들기
    config = configparser.ConfigParser()

    # 설정파일 오브젝트 만들기
    config['COINONE_V2'] = {}
    config['COINONE_V2']['access_token'] = '0b55a589-d648-4e58-8486-4c665fabff1d'
    config['COINONE_V2']['secret_key'] = 'ec58aa6f-ce82-41ad-8657-69c908984ed2'
    #config['COINONE_V2']['update'] = strftime('%Y-%m-%d %H:%M:%S')         #refresh할 때만 업그레이드 하도록 사용

    # 설정파일 저장
    with open('config.ini', 'w', encoding='utf-8') as configfile:
        config.write(configfile)

def config_read():
    # 설정파일 읽기
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')

    return config['COINONE_V2']['access_token'], config['COINONE_V2']['secret_key']
    # 설정파일의 색션 확인


#access_token, secret_key = config_read()
#print(access_token, secret_key)

#refresh token도 추가할 예정