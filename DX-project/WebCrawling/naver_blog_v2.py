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

# VIEW 탭 URL 사용 (iframe 구조)
blog_search_url = f'https://section.blog.naver.com/BlogHome.naver?directoryNo=0&currentPage=1&groupId=0'
# 또는 직접 검색 URL
search_url = f'https://search.naver.com/search.naver?where=blog&sm=tab_jum&query={keyword}'

# 드라이버 설정
options = webdriver.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(options=options)
driver.get(search_url)
time.sleep(3)

print("페이지 로드 완료")

# iframe 확인 및 전환 시도
try:
    # VIEW 탭 클릭 (있는 경우)
    view_tab = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "VIEW"))
    )
    view_tab.click()
    time.sleep(2)
    print("VIEW 탭 클릭 완료")
except:
    print("VIEW 탭 없음 (직접 검색 결과)")

# iframe 전환 시도
iframe_switched = False
for iframe_name in ['mainFrame', 'main_pack']:
    try:
        driver.switch_to.frame(iframe_name)
        iframe_switched = True
        print(f"iframe 전환 성공: {iframe_name}")
        break
    except:
        continue

if not iframe_switched:
    print("iframe 없음 - 직접 크롤링 시도")

# 페이지 스크롤
for i in range(5):
    body = driver.find_element(By.TAG_NAME, 'body')
    body.send_keys(Keys.END)
    time.sleep(1)

# 블로그 링크 수집 (다양한 selector 시도)
href_list = []

# 방법 1: CSS selector
try:
    blog_links = driver.find_elements(By.CSS_SELECTOR, 'a.title_link')
    href_list = [link.get_attribute("href") for link in blog_links]
    print(f"방법1 성공: {len(href_list)}개")
except Exception as e:
    print(f"방법1 실패: {e}")

# 방법 2: a 태그 중 blog.naver.com 포함
if len(href_list) == 0:
    try:
        all_links = driver.find_elements(By.TAG_NAME, 'a')
        href_list = [link.get_attribute("href") for link in all_links 
                     if link.get_attribute("href") and 'blog.naver.com' in link.get_attribute("href")]
        print(f"방법2 성공: {len(href_list)}개")
    except Exception as e:
        print(f"방법2 실패: {e}")

# 방법 3: 다른 CSS selector
if len(href_list) == 0:
    try:
        blog_links = driver.find_elements(By.CSS_SELECTOR, 'a.api_txt_lines')
        href_list = [link.get_attribute("href") for link in blog_links]
        print(f"방법3 성공: {len(href_list)}개")
    except Exception as e:
        print(f"방법3 실패: {e}")

# 중복 제거
href_list = list(set(href_list))
print(f"\n총 {len(href_list)}개의 고유 블로그 링크 발견")

if len(href_list) == 0:
    print("\n현재 페이지 HTML 구조 확인:")
    print(driver.page_source[:500])
    driver.quit()
    exit()

# default content로 복귀
driver.switch_to.default_content()

# 각 블로그 크롤링
blog_data = []

for idx, href in enumerate(tqdm(href_list[:10])):
    try:
        driver.get(href)
        time.sleep(2)
        
        # iframe 전환
        try:
            driver.switch_to.frame('mainFrame')
        except:
            pass
        
        # 제목
        title = ""
        for selector in ['.se-title-text', 'h3.se-title', '.se-fs-.se-ff-', '.pcol1']:
            try:
                title = driver.find_element(By.CSS_SELECTOR, selector).text
                if title:
                    break
            except:
                continue
        
        # 본문
        content = ""
        for selector in ['.se-main-container', '#postViewArea', '.se-module', '__se_module_data']:
            try:
                content = driver.find_element(By.CSS_SELECTOR, selector).text
                if content:
                    break
            except:
                continue
        
        # 날짜
        date = ""
        for selector in ['.se_publishDate', '.pcol2', '.se_date']:
            try:
                date = driver.find_element(By.CSS_SELECTOR, selector).text
                if date:
                    break
            except:
                continue
        
        blog_data.append({
            '제목': title if title else "제목 없음",
            '본문': content[:500] if content else "본문 없음",  # 처음 500자만
            '날짜': date if date else "날짜 없음",
            'URL': href
        })
        
        driver.switch_to.default_content()
        
    except Exception as e:
        print(f"\n오류 ({idx+1}): {str(e)[:50]}")
        driver.switch_to.default_content()
        continue

# 결과 저장
df = pd.DataFrame(blog_data)
df.to_csv('blog_result.csv', index=False, encoding='utf-8-sig')
print(f"\n완료! {len(df)}개 수집")

driver.quit()
