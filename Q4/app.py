from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
from os.path import basename
import time
import os

def create_google_search_url(keyword: str):
    return f"https://www.google.com/search?q={keyword}"

driver = webdriver.Chrome(ChromeDriverManager().install())

def next_page():
    elem = driver.execute_script("""
        return document.querySelector("#botstuff > div > div:nth-child(2) > table > tbody > tr > td.YyVfkd")?.nextElementSibling?.childNodes[0];
    """)
    print(elem)
    elem.click()
    driver.implicitly_wait(30)
    

print("=" * 100)
print("연습문제 7-4. 구글 사이트에서 pdf 파일을 검색하여 수집하는 크롤러")
print("=" * 100)

keyword = input("1.크롤링할 키워드는 무엇입니까?: ")
# keyword = "fhe pdfs"
count = int(input("2.크롤링 할 건 수는 몇건입니까?: "))
# count = 10
filepath = input("3.파일을 저장할 경로만 쓰세요(예:c:\\temp\\): ")
# filepath = '.\\files'

# 해당 경로에 폴더가 없다면 폴더 만들기
if not os.path.isdir(filepath):
    os.mkdir(filepath)

driver.get(create_google_search_url(keyword))
driver.implicitly_wait(30)

# 구글이 "수정된 검색어로 검색" 처리하는 경우, 자동으로 원래 검색어를 사용하도록 클릭함
driver.execute_script("""
   document.querySelector("#fprs > a.spell_orig")?.click()                   
""")
driver.implicitly_wait(30)

# TODO: 중복 파일 다운로드 무시 설정 필요 (완료)
# TODO: 더 이상 페이지가 없다면 자동 종료 (미구현, 구현 예시 케이스 없음: PDF 파일을 제공하는 주제이면서 검색 결과가 몇 페이지 없는 검색어가 없음)

failed_cnt = 0

while True:
    pdfs = driver.execute_script("""
        return [...document.querySelectorAll("#rso > div > div")]
            .filter((elem) =>
                elem.querySelector(".ZGwO7.s4H5Cf.C0kchf.NaCKVc.yUTMj.VDgVie")
            )
            .map((elem) => elem.querySelector("a").getAttribute("href"));                   
    """)
    
    print((len(pdfs), failed_cnt))
    
    if len(pdfs) == 0:
        failed_cnt = failed_cnt + 1

        # 다음 페이지로 진행
        next_page()
        
        # 10 페이지 이상 PDF가 나오지 않는다면 자동으로 종료
        if failed_cnt >= 10:
            print("10 페이지 이상 PDF가 검출되지 않아 자동으로 종료됩니다.")
            break
        continue
    else:
        failed_cnt = 0

    for i, pdf_url in enumerate(pdfs):
        _filepath = os.path.join(filepath, basename(pdf_url))
        
        if os.path.isfile(_filepath):
            print(f"{basename(pdf_url)} 파일 무시됨.")
            continue
        
        response = requests.get(pdf_url, verify=False)
        with open(_filepath, "wb") as fp:
            fp.write(response.content)
            print(f"발견된 {len(pdfs)} 개의 페이지 중 {i + 1}개 다운로드 완료.")

        if len(os.listdir(filepath)) >= count:
            print("지정된 수의 파일이 다운로드 되어 프로그램을 종료합니다.")
            exit(0)

    # 다음 페이지로 이동
    try:
        next_page()
    except Exception as e:
        print("더 이상 페이지가 존재하지 않아, 자동으로 종료합니다.")