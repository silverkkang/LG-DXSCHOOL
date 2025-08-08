from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import time

url = 'https://search.hankyung.com/search/news?query=%EC%A7%80%EC%97%AD+%EB%B6%88%EA%B7%A0%ED%98%95&sort=DATE%2FDESC%2CRANK%2FDESC&period=DATE&area=ALL&sdate=2024.01.01&edate=2025.06.30&exact=%EC%A7%80%EB%B0%A9%2C+%EB%B6%88%EA%B7%A0%ED%98%95&include=&except=%EC%8B%9C%EC%A7%84%ED%95%91&hk_only='
driver = webdriver.Chrome()
driver.get(url)

driver.find_element(By.XPATH, '//*[@id="content"]/div[1]/div/div[2]/div/span/a[1]').click()

f_url = []
for i in range(1,15):
    url = f'https://search.hankyung.com/search/news?query=%EC%A7%80%EC%97%AD+%EA%B7%A0%ED%98%95+%EB%B0%9C%EC%A0%84&sort=DATE%2FDESC%2CRANK%2FDESC&period=DATE&area=ALL&sdate=2023.01.01&edate=2025.06.30&exact=&include=%EC%A7%80%EB%B0%A9%2C+%EB%B6%88%EA%B7%A0%ED%98%95&except=&hk_only=&sdate=2023.01.01&edate=2025.06.30&page={i}'
    driver.get(url)
    driver.implicitly_wait(10)
    aTags = driver.find_elements(By.CSS_SELECTOR, '#content > div.left_cont > div > div.section.hk_news > div.section_cont > ul > li > div > a')
    for tag in aTags:
        f_url.append(tag.get_attribute('href'))

driver = webdriver.Chrome()
driver.get(f_url[0])
time.sleep(1)

df=[]
for url in f_url[:140]:
    driver.get(url)
    driver.implicitly_wait(15)

    
    try:
        title = driver.find_element(By.CLASS_NAME, 'headline').text
        content = driver.find_element(By.CLASS_NAME, 'article-body').text
        df.append([title, content])

    except NoSuchElementException:
        continue

hk_df = pd.DataFrame(df, columns=['제목','내용'])

!pip install konlpy
from konlpy.tag import Okt

hk_df['내용'] = hk_df['내용'].str.replace('\n','')

okt = Okt()
def extract_nouns(text):
    nouns=[]
    for word, tag in okt.pos(text):
        if tag == "Noun" and len(word) >=2:
            nouns.append(word)
    return nouns

hk_df["nouns"] = hk_df["내용"].apply(extract_nouns)

from collections import Counter

stopwords= ["지역"]
filtered_nouns = []
for nouns in all_nouns:
    if nouns not in stopwords:
        filtered_nouns.append(nouns)

freq_dict = Counter(filtered_nouns)
top30 = freq_dict.most_common(30)

hk_df.to_excel('한경_지역균형발전.xlsx')

import matplotlib.font_manager as fm

font_path = 'C:/Windows/Fonts/malgunbd.ttf' # <-- 추가 2
font_name = fm.FontProperties(fname=font_path).get_name()
plt.rc('font', family=font_name)

df = pd.read_excel('한경_지역균형발전.xlsx')
text = ' '.join(df['내용'].dropna().astype(str))

negative_keywords = [
    '문제', '불균형', '필요', '부족', '집중', '격차', '차별',
    '한계', '침체', '인구 감소', '열악', '낙후', '소외', '불만', '과밀',
    '편중', '부진', '저조'
]

keyword_counts = {word: text.count(word) for word in negative_keywords}
sorted_counts = dict(sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True))

plt.figure(figsize=(10, 6))
bars = plt.bar(sorted_counts.keys(), sorted_counts.values(), color='tomato')
plt.title('지역 불균형 관련 부정 키워드 빈도', fontsize=14)
plt.xlabel('키워드')
plt.ylabel('등장 횟수')
plt.xticks(rotation=45)

for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, height + 2, str(height), 
             ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.show()