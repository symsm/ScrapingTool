import requests
from bs4 import BeautifulSoup
import numpy as np
import re
import math
import tqdm
import sys
import winsound
import os

print("///スクレイピングを開始します///")

#市区町村コード(cityCode)と住所コード(townCode)を格納する配列
codeArray = np.zeros((1000, 1000))
cntCity = 0
indexFileFlg = True
#取得上限件数
MAX_REC = 100000
#レコードカウント
recCnt = 0


#市区町村コード(cityCode)と住所コード(townCode)を取得する
def getIndex(prefCode):

  #市区町村コード(cityCode)を取得
  html_doc = requests.get("https://townpage.goo.ne.jp/result.php?pref_code=" + prefCode).text
  soup = BeautifulSoup(html_doc, 'html.parser') # BeautifulSoupの初期化
  links = soup.select('a[city_code]')
  cntCity = 0
  for row in links:
    codeArray[cntCity][0] = row['city_code']
    cntCity+=1

  #住所コード(townCode)を取得
  for CC in range(0, codeArray.shape[0] - 1):
    if not codeArray[CC][0]:
      break
    html_doc = requests.get("https://townpage.goo.ne.jp/result.php?pref_code=" + prefCode + "&city_code=" + str(math.floor(codeArray[CC][0]))).text
    soup = BeautifulSoup(html_doc, 'html.parser') # BeautifulSoupの初期化
    links = soup.select('a[town_code]')
    cntTown = 1
    for row in links:
      codeArray[CC][cntTown] = row['town_code']
      cntTown+=1


#取得したコードを使用して電話帳情報を取得する
def getInfo(prefCode, cityCode, townCode):

  global recCnt

  #ファイルオープン
  fp = open('scraping_result_' + prefCode + '.txt', 'a', encoding='utf-8')
  #fp.write('会社名,業種,電話番号,住所\n')
	
  for num in range(1,500):

    #GETでデータ取ってくる
    html_doc = requests.get("https://townpage.goo.ne.jp/result.php?pref_code=" + prefCode + "&city_code=" + cityCode + "&town_code=" + townCode + "&pages=" + str(num)).text
    soup = BeautifulSoup(html_doc, 'html.parser') # BeautifulSoupの初期化

    #件数チェック。最後まで行ったら処理を中断
    elms = soup.find_all('div',class_="counter")
    #print(str(elms[0].contents[2].text) + '件')
    if str(elms[0].contents[2].text) == '0～0':
      return 0

    #抽出
    elms = soup.find_all('div', id=lambda value: value and value.startswith('resultBox_'))
    for row in elms:
      result = row.contents[0].text.splitlines()
      if str.strip(str(result[5])):
        fp.write(result[5] + ',' + result[7] + ',' + result[18] + ',' + result[22] + '\n')
        recCnt+=1
        print( '\r' + str(recCnt) + '件取得...', end='')
      else:
        break

    if recCnt > MAX_REC:
      return 0

  #ファイルクローズ
  fp.close()


#住所コード(townCode)なしで電話帳情報を取得する
def getInfo_noTC(prefCode, cityCode):

  global recCnt
  
  #ファイルオープン
  fp = open('scraping_result_' + prefCode + '.txt', 'a', encoding='utf-8')
  #fp.write('会社名,業種,電話番号,住所\n')
	
  for num in range(1,500):

    #GETでデータ取ってくる
    html_doc = requests.get("https://townpage.goo.ne.jp/result.php?pref_code=" + prefCode + "&city_code=" + cityCode + "&pages=" + str(num)).text
    soup = BeautifulSoup(html_doc, 'html.parser') # BeautifulSoupの初期化

    #件数チェック。最後まで行ったら処理を中断
    elms = soup.find_all('div',class_="counter")
    #print(str(elms[0].contents[2].text) + '件')
    if str(elms[0].contents[2].text) == '0～0':
      return 0

    #抽出
    elms = soup.find_all('div', id=lambda value: value and value.startswith('resultBox_'))
    for row in elms:
      result = row.contents[0].text.splitlines()
      if str.strip(str(result[5])):
        fp.write(result[5] + ',' + result[7] + ',' + result[18] + ',' + result[22] + '\n')
        recCnt+=1
        print( '\r' + str(recCnt) + '件取得...', end='')
      else:
        break

    if recCnt > MAX_REC:
      return 0

  #ファイルクローズ
  fp.close()


#///メイン処理///
try:
  print('\nスクレイピング対象の県コードを入力してください(01 - 47)')
  PC = input()
  if not PC.isdecimal():
    print('数値で入力してください')
    input()
    sys.exit()
  elif int(PC) < 1 and int(PC) > 47:
    print('01 - 47 の範囲で入力してください')
    input()
    sys.exit()

  #フォルダパス
  fldPath = './indexFiles'
  #インデックスファイルパス
  indPath = './indexFiles/indexFile_' + str(PC) + '.txt'
  #一時ファイルパス
  curPath = './indexFiles/indexFile_onProc.txt'

  #indexFilesフォルダ存在確認
  if not os.path.exists(fldPath):
    print('!!! ディレクトリ内に"indexFiles"フォルダを作成してください !!!')
    input()
    sys.exit('') 
  #インデックスファイルの書き出し有無
  indexFileFlg = not os.path.exists(indPath)

  if indexFileFlg:

    #必要なコード取得
    print("\nページ情報を読み込んでいます…")
    getIndex(PC.zfill(2)) 

    #インデックスファイル書き込み
    numCC = 0
    for cntNum in range(1, codeArray.shape[1]):
      if codeArray[cntNum][0]:
        numCC+=1

    fp = open(indPath, 'w', encoding='utf-8')
    for CC in range(0, numCC):
      if not codeArray[CC][0]:
        break
      for TC in range(1, codeArray.shape[1] - 1):
        if not codeArray[CC][TC]:
          if TC == 1:
            fp.write(PC.zfill(2) + ',' + str(CC).zfill(3) + ',,\n')
          break
        fp.write(PC.zfill(2) + ',' + str(math.floor(codeArray[CC][0])).zfill(3) + ',' + str(math.floor(codeArray[CC][TC])).zfill(3) + ',\n')
    fp.close()

  #取得したコードで回しながらスクレイピング
  print("\n電話帳情報を読み込んでいます…")
  fp = open(indPath, 'r+', encoding='utf-8')
  
  while True:
    readLine = str(fp.readline())
    fp2 = open(curPath, 'a', encoding='utf-8')
    if not readLine:
      break
    elif recCnt > MAX_REC:
      fp2.write(readLine)
    elif readLine.split(',')[3] == 'done\n':
      fp2.write(readLine)
    elif not readLine.split(',')[2]:
      getInfo_noTC(readLine.split(',')[0], readLine.split(',')[1])
      if recCnt <= MAX_REC:
        fp2.write(readLine.split(',')[0] + ',' + readLine.split(',')[1] + ',,done\n')
      else:
        fp2.write(readLine.split(',')[0] + ',' + readLine.split(',')[1] + ',,\n')
    else:
      getInfo(readLine.split(',')[0], readLine.split(',')[1], readLine.split(',')[2])
      if recCnt <= MAX_REC:
        fp2.write(readLine.split(',')[0] + ',' + readLine.split(',')[1] + ',' + readLine.split(',')[2] + ',done\n')
      else:
        fp2.write(readLine.split(',')[0] + ',' + readLine.split(',')[1] + ',' + readLine.split(',')[2] + ',\n')
    fp2.close()

  if recCnt > MAX_REC:
    print('\n!!! 取得上限に達しました。IPを変更して続きを取得してください !!!\n')

  #後処理 
  fp.close() 
  os.remove(indPath)
  os.rename(curPath, indPath) 

  #終了音
  winsound.Beep(1500, 100)
  winsound.Beep(2000, 100)
  winsound.Beep(2400, 100)
  winsound.Beep(3000, 100)

  print("///スクレイピング処理完了!///")
  input()


except requests.exceptions.RequestException as e:
  print("\n\nWebから情報を取得できません！：")
  print(e)
  input()
except IOError as e:
  print("\n\nファイルに書き出せません！：")
  print(e)
  input()
except Exception as e:
  print(e)
  input()