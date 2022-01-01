import pandas as pd



target = pd.read_csv('data/final/datajoin2.csv',encoding='euc-kr')
target = target.drop(['가족수','주소','이름'],axis=1).dropna().reset_index(drop=True)

target['플라스틱'] = target['BigPET..bottle..EA.']/33 + target['PET.유색.'] + target['PET.판컵.']\
                 + target['PE'] + target['PP'] + target['PS'] + target['other']
target['캔'] = target['알루미늄캔'] + target['철캔']
target['종이'] = target['종이팩'] + target['서적'] + target['일반종이']
target['섬유'] = target['섬유'] + target['의류']
target['유리'] = target['기타.투명병'] + target['기타.갈색병'] + target['기타.녹색병']\
                + target['소주병.ea.'] + target['맥주병.ea.']
target = target[['거점명','플라스틱','비닐','캔','종이','섬유','유리','연령대','성별','금액']]
target['연령대'] = target['연령대'].astype(int).astype(str)+'대'

def sex(x):
    if x=='W':
        return '여'
    else:
        return '남'
target['성별'] = target['성별'].apply(lambda x:sex(x))


연령대별참여자수 = pd.DataFrame(target.groupby(['연령대']).count()['플라스틱'])
연령대별참여자수.columns = ['참여자수']
연령대별 = pd.concat([target.groupby(['연령대']).sum(),연령대별참여자수], axis=1).reset_index()
연령대별['플라스틱_인당'] = 연령대별['플라스틱']/연령대별['참여자수']
연령대별['비닐_인당'] = 연령대별['비닐']/연령대별['참여자수']
연령대별['캔_인당'] = 연령대별['캔']/연령대별['참여자수']
연령대별['종이_인당'] = 연령대별['종이']/연령대별['참여자수']
연령대별['섬유_인당'] = 연령대별['섬유']/연령대별['참여자수']
연령대별['유리_인당'] = 연령대별['유리']/연령대별['참여자수']
연령대별['금액_인당'] = 연령대별['금액']/연령대별['참여자수']
