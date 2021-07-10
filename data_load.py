# -*- coding: utf-8 -*-
"""프로젝트데이터로드

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1BsqMDOFIrALLMGIn2M90YI3ldxPlGM-W
"""

#데이터 다운위해 캐글 연결
!pip install kaggle
from google.colab import files
files.upload()

ls -1ha kaggle.json

!mkdir -p ~/.kaggle
!cp kaggle.json ~/.kaggle/
!chmod 600 ~/.kaggle/kaggle.json

#파일 다운로드
!kaggle datasets download -d praveengovi/coronahack-chest-xraydataset

#현재 파일 확인
!ls

#압축해제 /data/폴더 생성해서 넣어줌
!unzip coronahack-chest-xraydataset.zip -d ./data

import numpy as np # linear algebra
import os # accessing directory structure
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

meta_data = pd.read_csv('./data/Chest_xray_Corona_Metadata.csv', delimiter=',')
meta_data.dataframeName = 'Chest_xray_Corona_Metadata.csv'

nRow, nCol = meta_data.shape
print(len(meta_data))
print(f'There are {nRow} rows and {nCol} columns')


#교수님이 성능 비교해보라고 한거중에 ARDS는 없어서 ARDS행 2개 제거 
idx = meta_data[meta_data['Label_2_Virus_category'] == 'ARDS'].index
meta_data=meta_data.drop(idx)
idx2 = meta_data[meta_data['X_ray_image_name'] == 'D5ACAA93-C779-4E22-ADFA-6A220489F840.jpeg'].index
idx3 = meta_data[meta_data['X_ray_image_name'] == '4C4DEFD8-F55D-4588-AAD6-C59017F55966.jpeg'].index
idx4 = meta_data[meta_data['X_ray_image_name'] == '44C8E3D6-20DA-42E9-B33B-96FA6D6DE12F.jpeg'].index
idx5 = meta_data[meta_data['X_ray_image_name'] == '35AF5C3B-D04D-4B4B-92B7-CB1F67D83085.jpeg'].index
meta_data=meta_data.drop(idx2)
meta_data=meta_data.drop(idx3)
meta_data=meta_data.drop(idx4)
meta_data=meta_data.drop(idx5)
nRow2, nCol2 = meta_data.shape

print(len(meta_data))
print(f'There are {nRow2} rows and {nCol2} columns')

# 각 set 폴더와 메타데이.csv 에서의 이미지 개수가 다르다.
# 혜림님 말로는 위에서 찍은 사진이 csv에는 없는 것 같다고 함

# 경로 설정
data_path = "./data/Coronahack-Chest-XRay-Dataset/Coronahack-Chest-XRay-Dataset/"

train_path = os.path.join(data_path, 'train')+'/' # data_dir 로 되어있길래 path 로 바꿨어요
test_path = os.path.join(data_path, 'test')+'/'

# 레이블 정의
# y1 :  Normal (0), Pnemonia (1)
# y2 : Normal (0), Pnemonia-Virs (1), Pnemonia-COVID19 (2), Pnemonia-bacteria (3)

meta_data['y1']=''
meta_data['y2']=''

meta_data.loc[meta_data['Label'] == 'Normal','y1'] = 0
meta_data.loc[meta_data['Label'] == 'Pnemonia','y1'] = 1

meta_data.loc[meta_data['Label'] == 'Normal','y2'] = 0
meta_data.loc[(meta_data['Label'] == 'Pnemonia') & (meta_data['Label_1_Virus_category'] == 'Virus') & (meta_data['Label_2_Virus_category'] != 'COVID-19'), 'y2'] = 1
meta_data.loc[(meta_data['Label'] == 'Pnemonia') & (meta_data['Label_2_Virus_category'] == 'COVID-19'), 'y2'] = 2
meta_data.loc[(meta_data['Label'] == 'Pnemonia') & (meta_data['Label_1_Virus_category'] == 'bacteria'), 'y2'] = 3

#print(len(y2_train))
#print(len(y2_test))
#print(meta_data_train)
#print(len(meta_data_train))
#meta_data.head(10)

# 메타데이터 이용해서 train test 데이터프레임 준비하기
meta_data_train = meta_data.loc[meta_data["Dataset_type"] == "TRAIN"]
meta_data_test = meta_data.loc[meta_data["Dataset_type"] == "TEST"]

# 테스트 셋에 코로나 이미지가 없기 때문에
# meta_data_train 데이터프레임에서 코로나이미지 10개를 선택해 새 데이터프레임에 저장
meta_data_covid_test = meta_data_train[meta_data_train['Label_2_Virus_category']=='COVID-19'].sample(10,random_state=1004)
meta_data_covid_test['Dataset_type'] = 'TEST'

# 위에서 선택된 10개를 원래 train 데이터프레임에서는 삭제 후 새 train 데이터프레임에 저장
meta_new_train = meta_data_train[~meta_data_train['X_ray_image_name'].isin(meta_data_covid_test['X_ray_image_name'])]

# 선택된 10개와 원래 test 데이터프레임를 합쳐서 새 test 데이터프레임에 저장
meta_new_test = pd.concat([meta_data_covid_test,meta_data_test],ignore_index=False)

# DataFrame을 리스트로 변환 (validation set은 더 아래에)
# 리스트로 계속 변환하는 이유는 현주님이 이미지 파일 여실 때 리스트로 처리하셔서 그에 맞게 변환해줬습니다
x_train = meta_new_train["X_ray_image_name"].to_list()
y1_train = meta_new_train['y1'].to_list()
y2_train = meta_new_train['y2'].to_list()

x_test = meta_new_test["X_ray_image_name"].to_list()
y1_test = meta_new_test['y1'].to_list()
y2_test = meta_new_test['y2'].to_list()

# 이미지들 옮기기 전 후로 갯수 확인

# 트레인 셋에서 벨리데이션 셋에 넣을 레이블들 비율에 참고하기 위해
# 트레인 셋에서 코로나 개수
print(" ===== Train set ===== ")
print("Virus, COVID-19 : ", len(meta_data_train[meta_data_train['Label_2_Virus_category']=='COVID-19']))
# 코로나 아닌 바이러스 개수
print("Virus, not COVID-19 : ", len(meta_data_train[(meta_data_train['Label_1_Virus_category']=='Virus') & (meta_data_train['Label_2_Virus_category']!='COVID-19')]))
# 박테리아 개수
print("Bacteria : ", len(meta_data_train[meta_data_train['Label_1_Virus_category']=='bacteria']))
# 정상 개수
print("Normal : ", len(meta_data_train[meta_data_train['Label']=='Normal']))
print(" * Train TOTAL : ", len(meta_data_train))

print("\n ===== NEW Train set ===== ")
print("Virus, COVID-19 : ", len(meta_new_train[meta_new_train['Label_2_Virus_category']=='COVID-19']))
print("Virus, not COVID-19 : ", len(meta_new_train[(meta_new_train['Label_1_Virus_category']=='Virus') & (meta_new_train['Label_2_Virus_category']!='COVID-19')]))
print("Bacteria : ", len(meta_new_train[meta_new_train['Label_1_Virus_category']=='bacteria']))
print("Normal : ", len(meta_new_train[meta_new_train['Label']=='Normal']))
print(" * Train TOTAL : ", len(meta_new_train))

# 테스트 셋에서 코로나 개수
print("\n ===== Test set ===== ")
print("Virus, COVID-19 : ", len(meta_data_test[meta_data_test['Label_2_Virus_category']=='COVID-19']))
# 코로나 아닌 바이러스 개수
print("Virus, not COVID-19 : ", len(meta_data_test[(meta_data_test['Label_1_Virus_category']=='Virus') & (meta_data_test['Label_2_Virus_category']!='COVID-19')]))
# 박테리아 개수
print("Bacteria : ", len(meta_data_test[meta_data_test['Label_1_Virus_category']=='bacteria']))
# 정상 개수
print("Normal : ", len(meta_data_test[meta_data_test['Label']=='Normal']))
print(" * Test TOTAL : ", len(meta_data_test))

print("\n ===== NEW Test set ===== ")
print("Virus, COVID-19 : ", len(meta_new_test[meta_new_test['Label_2_Virus_category']=='COVID-19']))
print("Virus, not COVID-19 : ", len(meta_new_test[(meta_new_test['Label_1_Virus_category']=='Virus') & (meta_new_test['Label_2_Virus_category']!='COVID-19')]))
print("Bacteria : ", len(meta_new_test[meta_new_test['Label_1_Virus_category']=='bacteria']))
print("Normal : ", len(meta_new_test[meta_new_test['Label']=='Normal']))
print(" * Test TOTAL : ", len(meta_new_test))

# validation 셋을 위해 트레인 셋에서 각 레이블마다 적절한 비율로 가져옴
meta_data_val1 = meta_new_train[meta_new_train['Label_2_Virus_category']=='COVID-19'].sample(5,random_state=1004)
meta_data_val2 = meta_new_train[(meta_new_train['Label_1_Virus_category']=='Virus') & (meta_new_train['Label_2_Virus_category']!='COVID-19')].sample(300,random_state=1004)
meta_data_val3 = meta_new_train[meta_new_train['Label_1_Virus_category']=='bacteria'].sample(500,random_state=1004)
meta_data_val4 = meta_new_train[meta_new_train['Label']=='Normal'].sample(300,random_state=1004)

meta_new_val = pd.concat([meta_data_val1,meta_data_val2,meta_data_val3,meta_data_val4],ignore_index=False)

meta_new_train2 = meta_new_train[~meta_new_train['X_ray_image_name'].isin(meta_new_val['X_ray_image_name'])]

# 리스트로 변환하기
x_val = meta_new_val["X_ray_image_name"].to_list()
y1_val = meta_new_val['y1'].to_list()
y2_val = meta_new_val['y2'].to_list()

# 새로 정의된 meta_new_train2 때문에 한번 더 정의
x_train = meta_new_train2["X_ray_image_name"].to_list()
y1_train = meta_new_train2['y1'].to_list()
y2_train = meta_new_train2['y2'].to_list()


print("--V check--")
print("train set : ", len(x_train))
print("val set : ", len(x_val))
print("train + val : ", len(x_train) + len(x_val))

# 최종 set 비교
print(" ===== meta_new_train set ===== ")
print("Virus, COVID-19 : ", len(meta_new_train[meta_new_train['Label_2_Virus_category']=='COVID-19']))
print("Virus, not COVID-19 : ", len(meta_new_train[(meta_new_train['Label_1_Virus_category']=='Virus') & (meta_new_train['Label_2_Virus_category']!='COVID-19')]))
print("Bacteria : ", len(meta_new_train[meta_new_train['Label_1_Virus_category']=='bacteria']))
print("Normal : ", len(meta_new_train[meta_new_train['Label']=='Normal']))
print(" * Train TOTAL : ", len(meta_new_train))
print(" * Train TOTAL += ? : ", len(meta_new_train2)+len(meta_new_val))

print("\n ===== meta_new_train2 set ===== ")
print("Virus, COVID-19 : ", len(meta_new_train2[meta_new_train2['Label_2_Virus_category']=='COVID-19']))
print("Virus, not COVID-19 : ", len(meta_new_train2[(meta_new_train2['Label_1_Virus_category']=='Virus') & (meta_new_train2['Label_2_Virus_category']!='COVID-19')]))
print("Bacteria : ", len(meta_new_train2[meta_new_train2['Label_1_Virus_category']=='bacteria']))
print("Normal : ", len(meta_new_train2[meta_new_train2['Label']=='Normal']))
print(" * Train TOTAL : ", len(meta_new_train2))
print(" * x_train TOTAL : ", len(x_train))

print("\n ===== meta_new_val set ===== ")
print("Virus, COVID-19 : ", len(meta_new_val[meta_new_val['Label_2_Virus_category']=='COVID-19']))
print("Virus, not COVID-19 : ", len(meta_new_val[(meta_new_val['Label_1_Virus_category']=='Virus') & (meta_new_val['Label_2_Virus_category']!='COVID-19')]))
print("Bacteria : ", len(meta_new_val[meta_new_val['Label_1_Virus_category']=='bacteria']))
print("Normal : ", len(meta_new_val[meta_new_val['Label']=='Normal']))
print(" * Train TOTAL : ", len(meta_new_val))
print(" * x_val TOTAL : ", len(x_val))

print("\n ===== meta_new_test set ===== ")
print("Virus, COVID-19 : ", len(meta_new_test[meta_new_test['Label_2_Virus_category']=='COVID-19']))
print("Virus, not COVID-19 : ", len(meta_new_test[(meta_new_test['Label_1_Virus_category']=='Virus') & (meta_new_test['Label_2_Virus_category']!='COVID-19')]))
print("Bacteria : ", len(meta_new_test[meta_new_test['Label_1_Virus_category']=='bacteria']))
print("Normal : ", len(meta_new_test[meta_new_test['Label']=='Normal']))
print(" * Test TOTAL : ", len(meta_new_test))
print(" * x_test TOTAL : ", len(x_test))



from PIL import Image

x_img_train = []
x_img_val = []
x_img_test = []

# train image 불러오기
for img_name in x_train :
  img = Image.open(train_path + img_name).convert("LA")
  resize_img = img.resize((128, 128))
  re_img_arr=np.asarray(resize_img)/255
  x_img_train.append(re_img_arr)

print(np.array(x_img_train).shape)

# val image 불러오기
for img_name in x_val :
  img = Image.open(train_path + img_name).convert("LA")
  resize_img = img.resize((128, 128))
  re_img_arr=np.asarray(resize_img)/255
  x_img_val.append(re_img_arr)

print(np.array(x_img_val).shape)

# test image 불러오기
for img_name in x_test :
  try:
    img = Image.open(test_path + img_name).convert("LA")
  except:
    # test 셋에 covid가 없어서 train에서 10개 빼온것 때문에
    img = Image.open(train_path + img_name).convert("LA")
  resize_img = img.resize((128, 128))
  re_img_arr=np.asarray(resize_img)/255
  x_img_test.append(re_img_arr)

print(np.array(x_img_test).shape)

# 변수 정리
# 전부 리스트

# 이미지 값 set
print(len(x_img_train))
print(len(x_img_val))
print(len(x_img_test))

# normal - pnemonia 분류기 훈련 따로, 그후 pnenomia 내부 분류기 따로 훈련하여 조합을 위한 레이블
print(y1_train)
print(y1_val)
print(y1_test)

# 바로 4클래스 분류 Normal - Pnemonia(vir)) - Pnemonia(Covid19) - Pnemonia(Bacteria) 를 위한 레이블 
print(y2_train)
print(y2_val)
print(y2_test)

# 경우에 따라 배열로 바꾸든 텐서로 바꾸든해서 처리

import torch

x_np_train=np.array(x_img_train)
x_np_val=np.array(x_img_val)
x_np_test=np.array(x_img_test)

x_tensor_train = torch.from_numpy(x_np_train).clone()
x_tensor_val = torch.from_numpy(x_np_val).clone()
x_tensor_test = torch.from_numpy(x_np_test).clone()

x_tensor_train.shape

from keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import classification_report, confusion_matrix
from mlxtend.plotting import plot_confusion_matrix
import matplotlib.pyplot as plt

def plot_imgs(item_dir, num_imgs=25):
    all_item_dirs = os.listdir(item_dir)
    item_files = [os.path.join(item_dir, file) for file in all_item_dirs][:num_imgs]

    plt.figure(figsize=(30, 30))
    for idx, img_path in enumerate(item_files):
        plt.subplot(5, 5, idx+1)

        img =Image.open(img_path)
        resize_img = img.resize((128, 128))
        plt.imshow(resize_img)

    plt.tight_layout()
plot_imgs(train_path)

# tensor로 변환된 x 저장
from google.colab import drive
drive.mount('/content/drive') #  안되면 '/content/gdrive' 사용

import pickle

os.listdir('/content/drive/Shared drives/통계적 기계 학습') # check 해보기, 역시 안되면 gdrive로 사용

train = {'x' : x_tensor_train,
         'y1' : y1_train,
         'y2' : y2_train}

val = {'x' : x_tensor_val,
         'y1' : y1_val,
         'y2' : y2_val}

test = {'x' : x_tensor_test,
         'y1' : y1_test,
         'y2' : y2_test}

# train.pickle : 저장하게 될 이름
# train : 저장하고 싶은 dictionary (ex) data_dict, data_dict2

with open('/content/drive/Shared drives/통계적 기계 학습/data/train.pickle', 'wb') as handle:
    pickle.dump(train, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('/content/drive/Shared drives/통계적 기계 학습/data/val.pickle', 'wb') as handle:
    pickle.dump(val, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('/content/drive/Shared drives/통계적 기계 학습/data/test.pickle', 'wb') as handle:
    pickle.dump(test, handle, protocol=pickle.HIGHEST_PROTOCOL)