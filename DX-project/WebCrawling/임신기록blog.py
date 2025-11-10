from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from tqdm import tqdm
import pandas as pd

# 검색 설정
keyword = '임신 기록'
start_date = '20201101'
end_date = '20251101'
blog_search_url = f'https://search.naver.com/search.naver?ssc=tab.blog.all&query={keyword}&sm=tab_opt&nso=so%3Ar%2Cp%3Afrom{start_date}to{end_date}'

# 드라이버 설정
driver = webdriver.Chrome()
driver.get(blog_search_url)
driver.maximize_window()
time.sleep(2)

# 페이지 스크롤 (더 많은 결과 로드)
for i in range(5):
    body = driver.find_element(By.TAG_NAME, 'body')
    body.send_keys(Keys.END)
    time.sleep(1.5)

# 블로그 링크 수집 (수정된 selector)
blog_links = driver.find_elements(By.CSS_SELECTOR, 'a.title_link')
href_list = [link.get_attribute("href") for link in blog_links]

print(f"찾은 블로그 링크 수: {len(href_list)}")

# 각 블로그 크롤링
blog_data = []

for idx, href in enumerate(tqdm(href_list[:10])):  # 테스트로 10개만
    try:
        driver.get(href)
        time.sleep(2)
        
        # iframe 전환
        try:
            driver.switch_to.frame('mainFrame')
        except:
            print(f"iframe 없음: {href}")
            driver.switch_to.default_content()
        
        # 제목 가져오기 (여러 방법 시도)
        title = ""
        try:
            title = driver.find_element(By.CSS_SELECTOR, '.se-title-text').text
        except:
            try:
                title = driver.find_element(By.CSS_SELECTOR, 'h3.se-title').text
            except:
                try:
                    # 구버전 블로그
                    title = driver.find_element(By.CSS_SELECTOR, '.se-fs-.se-ff-').text
                except:
                    title = "제목 없음"
        
        # 본문 가져오기 (여러 방법 시도)
        content = ""
        try:
            content = driver.find_element(By.CLASS_NAME, 'se-main-container').text
        except:
            try:
                # 대체 방법
                content = driver.find_element(By.CSS_SELECTOR, '#postViewArea').text
            except:
                content = "본문 없음"
        
        # 날짜 가져오기
        date = ""
        try:
            date = driver.find_element(By.CSS_SELECTOR, '.se_publishDate').text
        except:
            try:
                date = driver.find_element(By.CSS_SELECTOR, '.pcol2').text
            except:
                date = "날짜 없음"
        
        blog_data.append({
            '제목': title,
            '본문': content,
            '날짜': date,
            'URL': href
        })
        
        # default content로 복귀
        driver.switch_to.default_content()
        
    except Exception as e:
        print(f"\n오류 발생 ({idx+1}번째): {str(e)[:100]}")
        blog_data.append({
            '제목': '',
            '본문': str(e),
            '날짜': '',
            'URL': href
        })
        driver.switch_to.default_content()
        continue

# 결과 저장
df = pd.DataFrame(blog_data)
df.to_csv('blog_crawling_result.csv', index=False, encoding='utf-8-sig')
print(f"\n크롤링 완료! 총 {len(df)}개 수집")

driver.quit()