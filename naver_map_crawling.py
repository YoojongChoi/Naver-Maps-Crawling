'''
간단한 소개
사용자의 현재 위치를 기반으로 네이버 지도에서 주변 맛집 정보를 수집하고,
평점 및 리뷰 수를 기준으로 각 상위 3개의 맛집을 선정하여 정보를 제공합니다.
'''

import requests
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import re

def get_geolocation():
    '''
    사용자의 IP 주소를 확인합니다.
    해당 IP 주소를 기반으로 위치 정보를 추적하는 기능을 수행합니다.
    '''
    try:
        # IP 주소 확인
        ip_response = requests.get("https://api64.ipify.org?format=json")
        ip_address = ip_response.json()['ip']

        # IP 주소 기반 위치 추적
        geo_response = requests.get(f"https://ipinfo.io/{ip_address}/geo")
        geo_data = geo_response.json()
        print("ip: ", ip_address, "city: ", geo_data.get("city"),"location: ", geo_data.get("loc"))
        return {
            "ip": ip_address,
            "city": geo_data.get("city"),
            "location": geo_data.get("loc")  # 위도 및 경도
        }
    except Exception as e:
        return {"error": str(e)}

def time_wait(timeout, code):
    '''
    주어진 시간 ('timeout') 내에 특정 CSS 선택자 'code'를 사용하여
    웹 페이지에서 요소가 나타날 때까지 기다리는 기능을 수행합니다.
    '''
    try:
        wait = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, code)))
        return wait
    except TimeoutException:
        print(code, '태그를 찾지 못하였습니다.')
        driver.quit()
        return None


def switch_frame(frame):
    '''
    주어진 프레임 ID로 전환하는 함수입니다.
    '''
    try:
        # 프레임 ID로 찾기
        iframe = driver.find_element(By.ID, frame)
        # 해당 프레임으로 전환
        driver.switch_to.frame(iframe)
        print(f"Switched to frame: {frame}")
    except Exception as e:
        print(f"Error switching to frame: {frame}. Exception: {e}")

def page_down(num):
    '''
    웹 페이지를 지정된 횟수만큼 아래로 스크롤하는 함수입니다.
    '''
    try:
        # 웹 페이지의 body 요소 찾기
        body = driver.find_element(By.CSS_SELECTOR, 'body')
        # 페이지를 활성화하기 위해 body 요소를 여러 번 클릭
        for _ in range(10):
            body.click()
            time.sleep(0.3)
        # 지정된 횟수만큼 페이지를 아래로 스크롤
        for i in range(num):
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.3)
    except Exception as e:
        print(f"Error while scrolling down. Exception: {e}")

def set_top_3(top_list, num, title):
    '''
    상위 3개의 항목을 관리하는 함수입니다.

    top_list: 상위 3개 항목을 저장하는 리스트
    num: 새로운 식당의 숫자 값 (별점 or 리뷰 개수)
    title: 새로운 식당 이름
    '''
    # top_list의 길이가 3 미만인 경우 새로운 항목 추가
    if len(top_list) <3:
        top_list.append([num, title])
    else:
        # 새로운 항목의 숫자 값이 가장 작은 항목보다 큰 경우 갱신
        if num > top_list[2][0]:
            top_list[2] = [num, title]

    # 내림차순으로 정렬
    top_list.sort(reverse=True, key =lambda x: x[0])
    return top_list
def extract_number(string):
    # 정규 표현식을 사용하여 문자열에서 숫자 부분 추출 (쉼표 제거)
    cleaned_string = re.sub(r',','',string)
    match = re.search(r'\d+', cleaned_string)
    if match:
        #추출한 숫자 부분을 정수형으로 변환하여 반환
        return int(match.group())
    else:
        # 숫자가 없는 경우 None 반환
        return None
def search_restaurants(location):
    '''
    사용자의 위치를 기반으로 네이버 지도에서
    맛집을 검색하고 정보를 수집하는 함수입니다.

    Parameters:
    location: 사용자의 위치

    Returns:
    list: 평점 기준 상위 3개 맛집
    list: 리뷰 수 기준 상위 3개 맛집
    '''

    driver.maximize_window()    #화면 최대화
    driver.get("https://map.naver.com/")    # 네이버 지도 사이트 주소
    time.sleep(3)

    # 검색창 대기 및 찾기
    time_wait(10, 'div.input_box > input.input_search')
    search = driver.find_element(By.CSS_SELECTOR, 'div.input_box > input.input_search')

    # 위치 검색
    search.send_keys(location)
    search.send_keys(Keys.ENTER)
    time.sleep(3)

    # 사용자 위치 출력
    location = driver.find_element(By.CLASS_NAME,'title')
    print("사용자의 현위치: ", location.text)

    # 맛집 검색
    search.send_keys("맛집")
    search.send_keys(Keys.RETURN)
    time.sleep(3)

    # searchIframe 프레임으로 전환
    switch_frame('searchIframe')
    # 더 많은 식당을 얻기 위해 스크롤 다운
    page_down(40)
    time.sleep(3)

    # 크롤링 하려는 식당 개수 파악 위함
    restaurant_list = driver.find_elements(By.XPATH, "//li[@class='UEzoS rTjJo']")
    # TOP 3 리스트 초기화
    rate_list, review_list = list(), list()

    print('크롤링 시작')
    '''
    프레임 전환
    searchIframe 에서 해당 식당 클릭 해야,
    entryIframe 이 생성되고 해당 식당에 대한 정보가 표시됩니다.
    '''
    for i in range(len(restaurant_list)):
        # 프레임 초기화 및 searchIframe 프레임으로 전환
        driver.switch_to.default_content()
        switch_frame('searchIframe')

        print(f"----------{i+1}/{len(restaurant_list)}번 째 식당----------")
        # i번 째 식당 클릭 위함
        name = restaurant_list[i].find_element(By.XPATH,".//span[@class='place_bluelink TYaxT']")
        name.click()
        time.sleep(3)

        # i번 째 식당의 정보를 크롤링하기 위함
        # 프레임 초기화 및 entryIframe 프레임으로 변경
        driver.switch_to.default_content()
        switch_frame('entryIframe')
        time.sleep(3)

        # 페이지 소스 가져오기
        '''
        일반적으로 entryIframe 의 탭 기본값은 "홈" 입니다.
        따라서 페이지 소스를 가져올 때, "홈" 탭의 페이지 소스가 가져와 집니다.
        
        예외) 첫 번째 식당의 entryIframe의 탭이 가끔 "홈"이 아닐 때가 존재합니다.
        '''
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')    # "홈" 탭이 아닐 수 있음

        # 시작 시 "홈" 탭인지 확인 및 클릭
        '''
        실제 "홈" 탭은 (탭 이동) 버튼 뒤에 위치합니다.
        따라서 (탭 이동) 버튼이 화면에 존재하면서 "홈" 탭으로 이동하고자 한다면, 
        (탭 이동) 버튼을 먼저 누른 후에 "홈" 탭을 클릭합니다.        
        '''
        tabs = soup.find('div', class_='flicking-camera')
        overlapping_element = soup.find('a', class_='PznE8')
        if overlapping_element and tabs:
            tabs = driver.find_elements(By.XPATH, "//a[@class='tpj9w _tab-menu']")
            overlapping_element = driver.find_element(By.CLASS_NAME, 'PznE8').find_element(By.CLASS_NAME,'nK_aH')

            if overlapping_element.is_displayed():  # overlapping 이 화면에 있는 경우
                overlapping_element.click()  # (탭 이동) 버튼 클릭
                time.sleep(3)

            for tab in tabs:  # 탭 (홈, 소식(may not exist), 메뉴, 리뷰, 사진, 정보)
                if tab.find_element(By.CLASS_NAME, 'veBoZ').text.strip() == '홈':
                    tab.click()
                    time.sleep(3)

                    # "홈" 탭의 페이지 소스 가져오기
                    page_source = driver.page_source
                    soup = BeautifulSoup(page_source, 'html.parser')
                    break

        #식당 이름
        title = soup.find('span', class_='GHAhO').text.strip()
        print("식당 이름:", title)
        if title in restaurants.keys():
            continue
        else:
            restaurants[title] = []

        # 타입
        type = soup.find('span', class_='lnJFt').text.strip()
        type = f"타입: {type}"
        print(type)
        restaurants[title].append(type)

        # 영업 상태
        '''
        영업 상태가 종료면, 
        추천 목록에서 이 식당을 제외합니다. 
        '''
        condition = soup.find('div', class_='A_cdD')
        if not condition or condition.find('em').text.strip() == '영업 종료':
            del restaurants[title]
            print(f"{title}은 영업 종료 되어 추천 목록에서 제외됩니다.\n")
            continue
        condition = f"{condition.find('em').text.strip()} ({soup.find('time', {'aria-hidden': 'true'}).text.strip()})"
        print(condition)
        restaurants[title].append(condition)

        # 별점
        rate = soup.find('span', class_='PXMot LXIwF')
        if rate:
            rate = float(rate.text[2:].strip())
            rate_list = set_top_3(rate_list, rate, title)   # 별점 TOP 3 리스트 갱신
        else:
            rate = None
        rate = f"평점: {rate}"
        print(rate)
        restaurants[title].append(rate)

        # 리뷰 총 수 (방문자 리뷰 수 + 블로그 리뷰 수)
        review_parent = soup.find('div', class_='dAsGb')
        if review_parent:
            review_types = review_parent.find_all('span', class_='PXMot')
            reviews_tot = 0
            for review_type in review_types:  # 방문자 리뷰 & 블로그 리뷰
                review_type = review_type.find('a', {'role': 'button'})
                if review_type:     # 없을 수도 있기 때문
                    number = extract_number(review_type.text.strip())
                    if number is not None:
                        reviews_tot += number
            review_list = set_top_3(review_list, reviews_tot, title)    # 리뷰 수 TOP 3 리스트 갱신
        else:
            reviews_tot = None
        reviews_tot = f"리뷰 총 수: {reviews_tot}"
        print(reviews_tot)
        restaurants[title].append(reviews_tot)

        # 위치
        res_loc = soup.find('span', class_='LDgIH')
        if res_loc:
            res_loc = res_loc.text.strip()
        else:
            res_loc = None
        res_loc = f"위치: {res_loc}"
        print(res_loc)
        restaurants[title].append(res_loc)

        # 자세한 위치
        '''
        정보가 너무 많다면 ...으로 생략되어 있습니다.
        클릭을 통해 생략된 정보를 확인 할 수 있습니다.
        '''
        detail_loc = soup.find('span',class_= 'zPfVt')
        if detail_loc:
            detail_loc_click = driver.find_element(By.CLASS_NAME,'zPfVt')
            detail_loc_click.click()
            detail_loc = driver.find_element(By.CLASS_NAME,'zPfVt').text.strip()
        else:
            detail_loc = None
        detail_loc = f"상세 위치:\n{detail_loc}"
        print(detail_loc)
        restaurants[title].append(detail_loc)

        # 리뷰 표현 (n 명/ 총 방문자 수)
        '''
        리뷰 탭으로 이동하여 방문자들의 리뷰 중 
        가장 많은 투표 수를 받은 표현,
        그 표현에 투표한 인원 수,
        참여한 모든 인원 수를 가져옵니다.
        '''
        tabs = soup.find('div', class_='flicking-camera')
        exp = None
        if tabs:
            tabs = driver.find_elements(By.XPATH,"//a[@class='tpj9w _tab-menu']")
            for tab in tabs:        # 탭 (홈, 소식(may not exist), 메뉴, 리뷰, 사진, 정보)
                if tab.find_element(By.CLASS_NAME, 'veBoZ').text.strip() == '리뷰':
                    tab.click()     # "리뷰" 탭 클릭
                    time.sleep(3)
                    page_source = driver.page_source    # "리뷰" 탭 페이지 소스 가져오기
                    soup = BeautifulSoup(page_source, 'html.parser')

                    # 가장 많은 투표 수를 받은 표현
                    expression = soup.find('span', class_='t3JSf')
                    if expression:
                        expression = expression.text.strip()
                    else:
                        expression = None

                    # 그 표현에 투표한 인원
                    expressed_num = soup.find('span', class_='CUoLy')
                    if expressed_num:
                        expressed_num = expressed_num.text.strip()
                    else:
                        expressed_num = None

                    # 방문자 총 인원
                    expressed_tot = soup.find('div', class_='jypaX')
                    if expressed_tot:
                        expressed_tot = expressed_tot.find('em').text.strip()
                    else:
                        expressed_tot = None
                    exp = f"{expression}: ({expressed_num}/{expressed_tot})"

        exp = f"리뷰 표현: {exp}"
        print(exp)
        restaurants[title].append(exp)

        # i 번째 식당 완료
        print(f"{i+1}번째 식당 완료\n")

    # 정리
    rate_list = [x[1] for x in rate_list]
    review_list = [x[1] for x in review_list]
    print("----------Summary----------")
    print('총', len(restaurant_list), '개의 식당을 조회 하였습니다.')
    print('모든 식당 담은 딕셔너리: ', restaurants)
    print('별점 높은 TOP 3 식당 이름: ', rate_list)
    print('리뷰 수 많은 TOP 3 식당 이름: ', review_list, '\n')
    return rate_list, review_list
def show_info(rate_top_3, review_top_3):
    '''
    주어진 평점 상위 3개와 리뷰 상위 3개
    식당 정보를 출력하는 함수입니다.
    '''
    for top_3 in (rate_top_3, review_top_3):
        if top_3 == rate_top_3:
            type = 'Rate'
        else:
            type = 'Review'
        print(f"----------{type} TOP----------")    # 타입별 상위 3개 식당 제목 출력
        # 식당 정보 출력
        for i in range(len(top_3)):
            print(f"평점 TOP {i + 1}")
            print(f"식당 이름: {top_3[i]}")
            for info in restaurants[top_3[i]]:
                print(info)
            print()

if __name__ == '__main__':
    # ChromeDriver 경로 설정
    driver = webdriver.Chrome()
    
    # 식당 정보를 저장할 딕셔너리
    # 형식) 식당 이름: [타입, 영업 상태, 별점, 리뷰 수, 위치, 자세한 위치, 표현]
    restaurants = dict()
    location_info = get_geolocation()   # 현재 위치 정보 가져오기
    # 위치 정보 기반으로 식당 검색
    rate_top_3, review_top_3 = search_restaurants(location_info['location'])
    driver.quit()   # 웹 드라이버 종료
    show_info(rate_top_3, review_top_3) # 정보 출력