from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from functools import reduce
import pandas as pd
import time
import json
import os

def create_youtube_search_url(keyword: str):
    return f"https://www.youtube.com/results?search_query={keyword}&sp=EgIQAQ%253D%253D"

print('=' * 100)
print("연습문제 8-3 유튜브 영상의 댓글 수집하기")
print('=' * 100)

keyword = input("1.유튜브에서 검색할 주제 키워드를 입력하세요(예:롯데마트): ")
# keyword = "자바스크립트"
count = int(input("2.위 주제로 댓글을 크롤링할 유튜브 영상은 몇건입니까?: "))
# count = 3
comment_cnt = int(input("3.각 동영상에서 추출할 댓글은 몇건입니까?: "))
# comment_cnt = 10
filepath = input("4.크롤링 결과를 저장할 폴더명만 쓰세요(예: c:\\temp\\): ")
# filepath = '.\\files'

# 해당 경로에 폴더가 없다면 폴더 만들기
if not os.path.isdir(filepath):
    os.mkdir(filepath)

addrs = []

chrome_driver = ChromeDriverManager().install()
driver = webdriver.Chrome(chrome_driver)

driver.get(create_youtube_search_url(keyword))
driver.implicitly_wait(30)

while True:    
    addrs = driver.execute_script("""
        return [...document.querySelectorAll("#contents > ytd-video-renderer a#thumbnail")].map(element => element.getAttribute("href"));
    """)
    
    if len(addrs) >= count:
        break
    
    driver.find_element(By.CSS_SELECTOR, 'body').send_keys(Keys.PAGE_DOWN)    
    driver.implicitly_wait(30)
    
    
full_urls = list(map(lambda url: f"https://youtube.com{url}", addrs))[0:count]
names = []
contents = []
dates = []

for url in full_urls:
    driver.get(url)
    
    # body의 로드 시점까지 대기
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
    )
    
    # body 로드 이후에도 추가적인 로드가 있음
    time.sleep(1)
    
    # 댓글 로드를 위해 스크롤 다운
    driver.find_element(By.CSS_SELECTOR, 'body').send_keys(Keys.PAGE_DOWN)
        
    # 댓글 로드 대기
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#body"))
    )
    
    _names = []
    _contents = []
    _dates = []
    
    while True:
        (_names, _contents, _dates) = driver.execute_script("""
            return [
                [...document.querySelectorAll("#header-author > h3")].map(element => element.innerText),
                [...document.querySelectorAll("#content-text")].map(element => element.innerText),
                [...document.querySelectorAll("#header-author > yt-formatted-string > a")].map(element => element.innerText) 
            ]
        """)        
                
        # 필요한 수의 댓글을 로드했거나, 이미 가장 아래로 스크롤을 내려서 더 이상 로드 할 댓글이 없다면 종료
        # TODO: 더 이상 로드 할 댓글이 없음을 검증할 조건자가 필요함. (스크롤이 가장 아래에 있는지 여부는 lazy-load로 인하여 적용할 수 없음)
        if min([len(_names), len(_contents), len(_dates)]) >= comment_cnt and driver.execute_script("return window.scrollY >= document.body.scrollHeight - document.body.clientHeight;"):
            break

        # 댓글 로드를 위해 스크롤 다운
        driver.find_element(By.CSS_SELECTOR, 'body').send_keys(Keys.PAGE_DOWN)
            
        # 댓글 로드 대기
        driver.implicitly_wait(30)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#body"))
        )

    names = [*names, _names[0:comment_cnt]]
    contents = [*contents, _contents[0:comment_cnt]]
    dates = [*dates, _dates[0:comment_cnt]]

print(json.dumps(full_urls, indent=4, ensure_ascii=False))
print(json.dumps(names, indent=4, ensure_ascii=False))
print(json.dumps(dates, indent=4, ensure_ascii=False))
print(json.dumps(contents, indent=4, ensure_ascii=False))
print(json.dumps(list(map(len, names)), indent=4, ensure_ascii=False))
print(json.dumps(list(map(len, dates)), indent=4, ensure_ascii=False))
print(json.dumps(list(map(len, contents)), indent=4, ensure_ascii=False))

xlsx_path = f"{filepath}.xlsx"
csv_path = f"{filepath}.csv"
txt_path = f"{filepath}.txt"

df_base_data = {
    "URL 주소": [],
    "댓글작성자명": [],
    "댓글작성일자": [],
    "댓글 내용": []
}

with open(txt_path, "w", encoding="utf8") as fp:
    # URL별 반복
    for i, url in enumerate(full_urls):
        # 영상별 반복 및 저장
        for name, content, date in zip(names[i], contents[i], dates[i]):
            # csv, excel 데이터용 데이터 형성
            df_base_data["URL 주소"] = [*df_base_data["URL 주소"], url]
            df_base_data["댓글작성자명"] = [*df_base_data["댓글작성자명"], name]
            df_base_data["댓글작성일자"] = [*df_base_data["댓글작성일자"], date]
            df_base_data["댓글 내용"] = [*df_base_data["댓글 내용"], content]

            # 텍스트 데이터 저장
            fp.write(f"{'-'*100}\n")
            fp.write(f"1.유튜브 URL주소: {url}\n")
            fp.write(f"2.댓글 작성자명: {name}\n")
            fp.write(f"3.댓글 작성일자: {date}\n")
            fp.write(f"4.댓글 내용: {content}\n")
            fp.write("\n")

df = pd.DataFrame(df_base_data)
df.to_excel(xlsx_path)
df.to_csv(csv_path, encoding="utf8")