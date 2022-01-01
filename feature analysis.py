import pandas as pd



datajoin = pd.read_csv('data/final/datajoin2.csv',encoding='euc-kr')
datajoin = datajoin.drop(['가족수','주소','이름'],axis=1).dropna().reset_index(drop=True)
# datajoin.groupby(['연령대']).sum().reset_index()
datajoin['플라스틱'] = datajoin['BigPET..bottle..EA.']/33+datajoin['PET.유색.']+datajoin['PET.판컵.']+datajoin['PE']+datajoin['PP']+datajoin['PS']+datajoin['other']
datajoin['캔'] = datajoin['알루미늄캔']+datajoin['철캔']
datajoin['종이'] = datajoin['종이팩']+datajoin['서적']+datajoin['일반종이']
datajoin['섬유'] = datajoin['섬유']+datajoin['의류']
datajoin['유리'] = datajoin['기타.투명병']+datajoin['기타.갈색병']+datajoin['기타.녹색병']+datajoin['소주병.ea.']+datajoin['맥주병.ea.']
datajoin = datajoin[['거점명','플라스틱','비닐','캔','종이','섬유','유리','연령대','성별','금액']]
datajoin['연령대'] = datajoin['연령대'].astype(int).astype(str)+'대'

def sex(x):
    if x=='W':
        return '여'
    else:
        return '남'
datajoin['성별'] = datajoin['성별'].apply(lambda x:sex(x))

