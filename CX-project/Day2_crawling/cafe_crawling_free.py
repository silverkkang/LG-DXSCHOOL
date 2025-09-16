from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pickle
import os

# ========== 로그인 관련 함수들 ==========

def save_cookies(driver, filename="naver_cookies.pkl"):
    """쿠키 저장"""
    with open(filename, "wb") as file:
        pickle.dump(driver.get_cookies(), file)
    print("쿠키가 저장되었습니다.")

def load_cookies(driver, filename="naver_cookies.pkl"):
    """쿠키 불러오기"""
    if os.path.exists(filename):
        driver.get("https://naver.com")
        with open(filename, "rb") as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)
        print("쿠키가 로드되었습니다.")
        return True
    return False

def check_login_status(driver):
    """로그인 상태 확인"""
    try:
        driver.get("https://www.naver.com")
        time.sleep(2)
        # 로그인된 상태에서 나타나는 요소 확인
        driver.find_element(By.CLASS_NAME, "MyView-module__link_logout___HoWax")
        print("로그인 상태입니다.")
        return True
    except:
        print("로그인이 필요합니다.")
        return False

def manual_login(driver):
    """수동 로그인"""
    print("수동 로그인을 진행합니다...")
    driver.get("https://nid.naver.com/nidlogin.login")
    
    print("브라우저에서 로그인을 완료해주세요.")
    input("로그인 완료 후 엔터키를 눌러주세요...")
    
    # 로그인 성공 확인
    if check_login_status(driver):
        save_cookies(driver)
        return True
    else:
        print("로그인 확인에 실패했습니다.")
        return False

def auto_login(driver, user_id, password):
    """자동 로그인 (보안 주의!)"""
    print("자동 로그인을 진행합니다...")
    driver.get("https://nid.naver.com/nidlogin.login")
    
    try:
        wait = WebDriverWait(driver, 10)
        
        # 아이디 입력
        id_input = wait.until(EC.presence_of_element_located((By.ID, "id")))
        id_input.clear()
        id_input.send_keys(user_id)
        
        # 비밀번호 입력
        pw_input = driver.find_element(By.ID, "pw")
        pw_input.clear()
        pw_input.send_keys(password)
        
        # 로그인 버튼 클릭
        login_btn = driver.find_element(By.ID, "log.login")
        login_btn.click()
        
        time.sleep(3)
        
        # 캡챠나 추가 인증 확인
        if "captcha" in driver.current_url or "secure" in driver.current_url:
            print("추가 인증이 필요합니다. 수동으로 처리해주세요.")
            input("인증 완료 후 엔터키를 눌러주세요...")
        
        if check_login_status(driver):
            save_cookies(driver)
            return True
        else:
            return False
            
    except Exception as e:
        print(f"자동 로그인 실패: {e}")
        return False

# ========== 메인 크롤링 코드 ==========

# 웹드라이버 설정
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

try:
    # 1단계: 로그인 처리
    print("=== 로그인 처리 ===")
    
    # 먼저 쿠키로 로그인 시도
    if load_cookies(driver):
        if not check_login_status(driver):
            print("쿠키가 만료되었습니다. 다시 로그인해주세요.")
            # 수동 로그인
            if not manual_login(driver):
                print("로그인에 실패했습니다. 프로그램을 종료합니다.")
                exit()
    else:
        print("저장된 쿠키가 없습니다.")
        # 수동 로그인
        if not manual_login(driver):
            print("로그인에 실패했습니다. 프로그램을 종료합니다.")
            exit()
    
    # 자동 로그인을 원하는 경우 (보안상 권장하지 않음)
    # user_id = "your_id"
    # password = "your_password" 
    # auto_login(driver, user_id, password)
    
    print("로그인이 완료되었습니다!")
    print("=== 크롤링 시작 ===")
    
    # 2단계: 카페 페이지로 이동 및 검색
    url = 'https://cafe.naver.com/f-e/cafes/10114233/menus/3?viewType=L'
    driver.get(url)
    
    # 페이지 로딩 대기
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="cafe_content"]/div[5]/div[2]/div[3]/input')))
    
    # 검색 실행
    search_box = driver.find_element(By.XPATH, '//*[@id="cafe_content"]/div[5]/div[2]/div[3]/input')
    keywords = '운동'
    
    # 검색어 입력 및 검색
    search_box.click()
    search_box.send_keys(keywords + Keys.ENTER)
    
    # 검색 결과 페이지 로딩 대기
    time.sleep(3)
    
    # 첫 번째 페이지 URL 수집
    url_elements = driver.find_elements(By.CSS_SELECTOR, 'td:nth-child(2) > div > div > a')
    
    url_list = []
    for href in url_elements:
        href_value = href.get_attribute("href")
        if href_value:
            url_list.append(href_value)
    
    print(f"첫 번째 페이지에서 {len(url_list)}개 URL 수집")
    
    # 다음 페이지로 이동 (기존 코드 유지)
    try:
        driver.find_element(By.CSS_SELECTOR,'#cafe_content > div.SearchBoxLayout.type_bottom > div.Pagination > button:nth-child(3)').click()
        time.sleep(2)
        
        url2 = driver.find_elements(By.CSS_SELECTOR, 'div > a.article')
        url2_list = []
        
        for href in url2:
            href_value = href.get_attribute("href")
            if href_value:
                url2_list.append(href_value)
        
        print(f"두 번째 페이지에서 {len(url2_list)}개 URL 수집")
    except:
        print("다음 페이지 버튼을 찾을 수 없습니다.")
        url2_list = []
    
    # 3단계: f-string을 사용한 여러 페이지 URL 수집 (기존 코드 개선)
    print("여러 페이지에서 URL을 수집합니다...")
    
    f_url = []
    for i in range(1, 30):
        try:
            page_url = f'https://cafe.naver.com/f-e/cafes/10114233/menus/3?viewType=L&ta=SUBJECT&q=%EC%9A%B4%EB%8F%99&page={i}'
            driver.get(page_url)
            
            # 페이지 로딩 대기 (implicit wait 대신 explicit wait 사용)
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.article')))
            except:
                print(f"페이지 {i}에서 게시물을 찾을 수 없습니다. 크롤링을 종료합니다.")
                break
            
            aTags = driver.find_elements(By.CSS_SELECTOR, '.article')
            
            if not aTags:  # 게시물이 없으면 중단
                print(f"페이지 {i}에서 더 이상 게시물이 없습니다.")
                break
            
            page_count = 0
            for tag in aTags:
                href_value = tag.get_attribute('href')
                if href_value:
                    f_url.append(href_value)
                    page_count += 1
            
            print(f"페이지 {i}: {page_count}개 URL 수집 (총 {len(f_url)}개)")
            
            # 요청 간격 조절 (서버 부하 방지)
            time.sleep(1)
            
        except Exception as e:
            print(f"페이지 {i} 처리 중 오류: {e}")
            continue
    
    # 4단계: 결과 출력
    print("\n=== 수집 결과 ===")
    print(f"첫 번째 방법으로 수집한 URL: {len(url_list)}개")
    print(f"두 번째 방법으로 수집한 URL: {len(url2_list)}개") 
    print(f"f-string 방법으로 수집한 URL: {len(f_url)}개")
    
    # 전체 URL 리스트 합치기 (중복 제거)
    all_urls = list(set(url_list + url2_list + f_url))
    print(f"중복 제거 후 총 URL: {len(all_urls)}개")
    
    # 5단계: 게시물 내용 크롤링 (처음 5개만 테스트)
    print("\n=== 게시물 내용 크롤링 (샘플 5개) ===")
    
    for i, post_url in enumerate(all_urls[:5]):
        try:
            print(f"\n[{i+1}/5] 게시물 크롤링 중...")
            driver.get(post_url)
            
            # 게시물 로딩 대기
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ArticleContentBox')))
            
            # 제목 추출
            try:
                title = driver.find_element(By.CSS_SELECTOR, '.ArticleTitle').text
            except:
                title = "제목을 가져올 수 없습니다"
            
            # 내용 추출
            try:
                content = driver.find_element(By.CSS_SELECTOR, '.ArticleContentBox').text
            except:
                content = "내용을 가져올 수 없습니다"
            
            # 작성자 추출
            try:
                author = driver.find_element(By.CSS_SELECTOR, '.profile_info .nick').text
            except:
                author = "작성자를 가져올 수 없습니다"
            
            print(f"제목: {title}")
            print(f"작성자: {author}")
            print(f"내용 미리보기: {content[:100]}...")
            print(f"URL: {post_url}")
            print("-" * 80)
            
            time.sleep(1)  # 요청 간격 조절
            
        except Exception as e:
            print(f"게시물 크롤링 중 오류: {e}")
            continue
    
    print("\n크롤링이 완료되었습니다!")
    
    # URL을 파일로 저장 (선택사항)
    with open("collected_urls.txt", "w", encoding="utf-8") as f:
        for url in all_urls:
            f.write(url + "\n")
    print(f"수집된 URL이 'collected_urls.txt' 파일에 저장되었습니다.")

except Exception as e:
    print(f"크롤링 중 오류 발생: {e}")

finally:
    # 브라우저 종료
    driver.quit()
    print("브라우저가 종료되었습니다.")