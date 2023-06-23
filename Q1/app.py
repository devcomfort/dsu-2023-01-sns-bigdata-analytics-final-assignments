from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from functools import reduce
import pandas as pd
import time

print("=" * 100)
keyword = input("1.공고명으로 검색할 키워드는 무엇입니까?: ")
# keyword = "캠프"
startDt = input("2.조회 시작일자 입력(예:2019/01/01): ")
# startDt = "2019/01/01"
endDt = input("3.조회 종료일자 입력(예:2019/12/31): ")
# endDt = "2019/12/31"
filepath = input("4.파일로 저장할 폴더 이름을 쓰세요(예:c:\\temp\\): ")
# filepath = ".\\files"

# (별도로 입력 받지 않는) 공고 수 파라미터
cnt = 30

xlsx_path = f"{filepath}.xlsx"
txt_path = f"{filepath}.txt"

chrome_driver = ChromeDriverManager().install()
driver = webdriver.Chrome(chrome_driver)

driver.get("https://www.g2b.go.kr/index.jsp")
driver.implicitly_wait(30)

driver.find_element(By.CSS_SELECTOR, "#bidNm").send_keys(keyword)
driver.execute_script(
    f"""
    document.querySelector("#fromBidDt").value = "{startDt}";
    document.querySelector("#toBidDt").value = "{endDt}";
    """
)

driver.execute_script("""
    javascript:search1(); // 검색 함수 실행
""")

time.sleep(1)
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "#sub"))
)

total_results = []

while len(total_results) < cnt:
    results = driver.execute_script("""
        return [
            ...document
                .querySelector("#sub")
                .contentDocument.querySelector("html > frameset > frame:nth-child(2)")
                .contentDocument.querySelectorAll(
                "#resultForm > div.results > table > tbody > tr"
                ),
            ].map((trElement) => {
            const tdElements = trElement.querySelectorAll("td");
            const texts = [...tdElements].map((element) => element.innerText);

            return [
                ...texts.slice(0, 3),
                tdElements[3].querySelector("a")?.getAttribute("href") || "",
                ...texts.slice(3),
            ];
        });
    """)

    total_results = [*total_results, *results]

    driver.execute_script("""
        document
            .querySelector("#sub")
            .contentDocument.querySelector("html > frameset > frame:nth-child(2)")
            .contentDocument.querySelector("#pagination > a.default").click();
    """)
    
    time.sleep(1)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#sub"))
    )
    
with open(txt_path, "w", encoding="utf8") as fp:
    for i, sample in enumerate(total_results):
        fp.write(f"{i + 1}번쨰 공고내용을 추출합니다~~~~\n")
        fp.write(f"1.업무: {sample[0]}\n")
        fp.write(f"2.공고번호-치수: {sample[1]}\n")
        fp.write(f"3.분류: {sample[2]}\n")
        fp.write(f"4.공고명: {sample[3]}\n")
        fp.write(f"5.URL 주소: {sample[4]}\n")
        fp.write(f"6.공고기관: {sample[5]}\n")
        fp.write(f"7.수요기관: {sample[6]}\n")
        fp.write(f"8.계약방법: {sample[7]}\n")
        fp.write(f"9.입력일시(입찰마감일시): {sample[8]}\n")
        fp.write(f"10.공동수급: {sample[9]}\n")
        fp.write(f"11.투찰여부: {sample[10]}\n")
        fp.write("\n")

# DEBUG CODE
# print(
#     len(list(reduce(lambda acc, cur: [*acc, cur[0]], total_results, []))),
#     len(list(reduce(lambda acc, cur: [*acc, cur[1]], total_results, []))),
#     len(list(reduce(lambda acc, cur: [*acc, cur[2]], total_results, []))),
#     len(list(reduce(lambda acc, cur: [*acc, cur[3]], total_results, []))),
#     len(list(reduce(lambda acc, cur: [*acc, cur[4]], total_results, []))),
#     len(list(reduce(lambda acc, cur: [*acc, cur[5]], total_results, []))),
#     len(list(reduce(lambda acc, cur: [*acc, cur[6]], total_results, []))),
#     len(list(reduce(lambda acc, cur: [*acc, cur[7]], total_results, []))),
#     len(list(reduce(lambda acc, cur: [*acc, cur[8]], total_results, []))),
#     len(list(reduce(lambda acc, cur: [*acc, cur[9]], total_results, []))),
#     len(list(reduce(lambda acc, cur: [*acc, cur[10]], total_results, [])))
# )
    
pd.DataFrame({
    "업무": list(reduce(lambda acc, cur: [*acc, cur[0]], total_results, [])),
    "공고번호-치수": list(reduce(lambda acc, cur: [*acc, cur[1]], total_results, [])),
    "분류": list(reduce(lambda acc, cur: [*acc, cur[2]], total_results, [])),
    "공고명": list(reduce(lambda acc, cur: [*acc, cur[3]], total_results, [])),
    "URL 주소": list(reduce(lambda acc, cur: [*acc, cur[4]], total_results, [])),
    "공고기관": list(reduce(lambda acc, cur: [*acc, cur[5]], total_results, [])),
    "수요기관": list(reduce(lambda acc, cur: [*acc, cur[6]], total_results, [])),
    "계약방법": list(reduce(lambda acc, cur: [*acc, cur[7]], total_results, [])),
    "입력일시(입찰마감일시)": list(reduce(lambda acc, cur: [*acc, cur[8]], total_results, [])),
    "공동수급": list(reduce(lambda acc, cur: [*acc, cur[9]], total_results, [])),
    "투찰여부": list(reduce(lambda acc, cur: [*acc, cur[10]], total_results, []))
}).to_excel(xlsx_path)
