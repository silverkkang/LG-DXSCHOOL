from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from tqdm import tqdm
import pandas as pd

# 검색 설정
keyword = '임신 기록'
url = f'https://search.naver.com/search.naver?where=blog&query={keyword}'

# 크롬 드라이버 시작
driver = webdriver.Chrome()
driver.get(url)
driver.maximize_window()
time.sleep(3)

# 페이지 스크롤로 더 많은 결과 로드
print("페이지 스크롤 중...")
for i in range(5):
    body = driver.find_element(By.TAG_NAME, 'body')
    body.send_keys(Keys.END)
    time.sleep(1.5)

# blog.naver.com 링크 수집
print("블로그 링크 수집 중...")
all_links = driver.find_elements(By.TAG_NAME, 'a')
href_list = []

for link in all_links:
    href = link.get_attribute('href')
    if href and 'blog.naver.com' in href:
        # 실제 블로그 글만 (MyBlog.naver, section 등 제외)
        if '/PostView.naver' in href or '/PostList.naver' in href or ('/22' in href or '/23' in href):
            href_list.append(href)

# 중복 제거
href_list = list(set(href_list))
print(f"총 {len(href_list)}개의 블로그 글 발견")

if len(href_list) == 0:
    print("블로그 링크를 찾지 못했습니다.")
    driver.quit()
    exit()

# 각 블로그 크롤링
blog_data = []
success_count = 0
fail_count = 0

for idx, href in enumerate(tqdm(href_list)):
    try:
        driver.get(href)
        time.sleep(2)
        
        # iframe 전환 시도
        try:
            driver.switch_to.frame('mainFrame')
        except:
            pass
        
        # 제목 가져오기
        title = ""
        for selector in ['.se-title-text', 'h3.se-title', '.se-fs-', '.pcol1', 'div.se-module.se-module-text h3']:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                title = element.text
                if title:
                    break
            except:
                continue
        
        # 본문 가져오기
        content = ""
        for selector in ['.se-main-container', '#postViewArea', 'div.se-main-container']:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                content = element.text
                if content:
                    break
            except:
                continue
        
        # 날짜 가져오기
        date = ""
        for selector in ['.se_publishDate', '.pcol2', 'span.se_publishDate']:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                date = element.text
                if date:
                    break
            except:
                continue
        
        # 결과 저장
        if title or content:  # 제목이나 본문 하나라도 있으면 저장
            blog_data.append({
                '제목': title if title else "제목 없음",
                '본문': content[:1000] if content else "본문 없음",  # 처음 1000자
                '날짜': date if date else "날짜 없음",
                'URL': href
            })
            success_count += 1
        else:
            fail_count += 1
        
        # default content로 복귀
        driver.switch_to.default_content()
        
    except Exception as e:
        fail_count += 1
        print(f"\n오류 발생 ({idx+1}번째): {str(e)[:100]}")
        driver.switch_to.default_content()
        continue

print(f"\n크롤링 완료!")
print(f"성공: {success_count}개 | 실패: {fail_count}개")

# DataFrame으로 변환 및 저장
if len(blog_data) > 0:
    df = pd.DataFrame(blog_data)
    
    # CSV 저장
    df.to_csv('임신기록_블로그_크롤링.csv', index=False, encoding='utf-8-sig')
    print(f"\n결과 저장 완료: 임신기록_블로그_크롤링.csv ({len(df)}개)")
    
    # 미리보기
    print("\n=== 데이터 미리보기 ===")
    print(df.head())
else:
    print("크롤링된 데이터가 없습니다.")

driver.quit()
