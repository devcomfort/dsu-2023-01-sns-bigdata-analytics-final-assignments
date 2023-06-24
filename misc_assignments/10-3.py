"""
    네이버에서 특정 검색어를 검색하여
    최상단 10개의 포스트를 txt, csv, xlsx 형태로 저장하기
"""

from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
import pandas as pd
import time

print("=" * 100)
print("연습 문제 : 저장할 내용을 목록으로 만들어서 xlsx, csv 형식으로 저장하기")
print("=" * 100)

keyword = input("1. 크롤링 할 키워드는 무엇입니까?: ")
text_path = input("2. txt 형태로 저장할 경로와 파일명, 확장자를 포함하여 쓰세요: ")
csv_path = input("3. csv 형태로 저장할 경로와 파일명, 확장자를 포함하여 쓰세요: ")
xlsx_path = input("4. xlsx 형태로 저장할 경로와 파일명, 확장자를 포함하여 쓰세요: ")

def create_naver_search_url(keyword: str) -> str:
  return f"https://search.naver.com/search.naver?where=view&sm=tab_jum&query={keyword}"

chrome = ChromeDriverManager().install()
driver = webdriver.Chrome(chrome)

driver.get(create_naver_search_url(keyword))
driver.implicitly_wait(30)
time.sleep(1)

(titles, descs, dates, names) = driver.execute_script("""
return (() => {
  const posts = document.querySelectorAll(
    "#main_pack > section > div > div._list > panel-list > div:nth-child(1) > more-contents > div > ul > li"
  );

  const titles = [...posts].map(
    (element) =>
      element.querySelector(".api_txt_lines.total_tit._cross_trigger")?.innerText
  );

  const descs = [...posts].map(
    (element) => element.querySelector(".api_txt_lines.dsc_txt")?.innerText
  );

  const dates = [...posts].map(
    (element) => element.querySelector(".sub_time.sub_txt")?.innerText
  );

  const names = [...posts].map(
    (element) => element.querySelector(".elss.etc_dsc_inner")?.innerText
  );

  return [titles, descs, dates, names];
})();
""")

with open(text_path, "w", encoding='utf8') as fp:
    for i, (title, desc, date, name) in enumerate(list(zip(titles, descs, dates, names))[:10]):
        fp.write(f"1.번호:{i+1}\n")
        fp.write(f"2.제목:{title}\n")
        fp.write(f"3.내용:{desc}\n")
        fp.write(f"4.작성일자:{date}\n")
        fp.write(f"5.블로그닉네임:{name}\n")
        fp.write("\n")

        if i < len(titles) - 1:
            fp.write('=' * 100 + '\n')

df = pd.DataFrame({
    "번호": [i + 1 for i in range(10)],
    "제목": titles[:10],
    "내용": descs[:10],
    "작성일자": dates[:10],
    "블로그닉네임": names[:10]
})

df.to_csv(csv_path)
df.to_excel(xlsx_path)