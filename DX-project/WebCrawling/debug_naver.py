from selenium import webdriver
from selenium.webdriver.common.by import By
import time

keyword = '임신 기록'
url = f'https://search.naver.com/search.naver?where=blog&query={keyword}'

driver = webdriver.Chrome()
driver.get(url)
time.sleep(3)

print("=== 페이지 정보 ===")
print(f"현재 URL: {driver.current_url}")
print(f"페이지 제목: {driver.title}")

# iframe 찾기
iframes = driver.find_elements(By.TAG_NAME, 'iframe')
print(f"\n찾은 iframe 개수: {len(iframes)}")
for i, iframe in enumerate(iframes):
    print(f"  iframe {i}: id='{iframe.get_attribute('id')}', name='{iframe.get_attribute('name')}'")

# 링크 찾기 시도
print("\n=== 링크 찾기 시도 ===")

# 시도 1
try:
    links1 = driver.find_elements(By.CSS_SELECTOR, 'a.title_link')
    print(f"1. a.title_link: {len(links1)}개")
except Exception as e:
    print(f"1. 실패: {e}")

# 시도 2
try:
    links2 = driver.find_elements(By.CSS_SELECTOR, 'a.api_txt_lines')
    print(f"2. a.api_txt_lines: {len(links2)}개")
except Exception as e:
    print(f"2. 실패: {e}")

# 시도 3 - blog.naver.com 포함된 모든 링크
try:
    all_links = driver.find_elements(By.TAG_NAME, 'a')
    blog_links = [l for l in all_links if l.get_attribute('href') and 'blog.naver.com' in l.get_attribute('href')]
    print(f"3. blog.naver.com 링크: {len(blog_links)}개")
    
    # 처음 3개만 출력
    for i, link in enumerate(blog_links[:3]):
        print(f"   - {link.get_attribute('href')}")
except Exception as e:
    print(f"3. 실패: {e}")

# 페이지 소스 일부 출력
print("\n=== 페이지 구조 확인 ===")
print(driver.page_source[:1000])

driver.quit()
