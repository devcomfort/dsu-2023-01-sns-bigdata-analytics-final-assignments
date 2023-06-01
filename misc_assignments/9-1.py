"""
네이버 블로그에서 KEY를 검색하여 검색 결과로 나온 블로그의 제목과 아이디를 출력하는 코드입니다.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

def naver_blog_url(keyword: str, pageNo: int = 1) -> str:
    return f"https://section.blog.naver.com/Search/Blog.naver?pageNo=1&orderBy=sim&keyword={keyword}"
    
chrome_driver = ChromeDriverManager().install()
driver = webdriver.Chrome(chrome_driver)

KEY = "동서대학교"

driver.get(naver_blog_url(KEY))
driver.implicitly_wait(30)

blogs = driver.find_elements(By.CSS_SELECTOR, "#content > section > div.area_list_search > div")
blog_profiles = list(map(lambda elem: elem.text.replace('\n', ' '), blogs))
print('\n'.join(blog_profiles))

time.sleep(30)  # 정상적으로 나오는지 확인해보세요!