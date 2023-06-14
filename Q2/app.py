from typing import Union, List
from dataclasses import dataclass
from datetime import datetime
import requests
import pandas as pd
import json


@dataclass
class Thumbnail:
    url: str
    virthumbnail: bool
    videoThumbnail: bool


@dataclass
class Post:
    # 작성자 아이디
    domainIdOrBlogId: str
    # 작성자 닉네임
    nickname: str
    # 블로그 이름
    blogName: str
    
    # 포스트 시간
    date: int

    # 블로그 포스트 주소
    postUrl: str
    # 블로그 제목
    title: str
    noTagTitle: str
    # 블로그 내용 (간단히)
    contents: str

    # 프로필 이미지 주소
    profileImageUrl: str

    # 썸네일 보유 여부
    hasThumbnail: bool
    # 썸네일 리스트
    thumbNails: List[Thumbnail]

    product: any
    marketPost: bool

    logNo: int
    gdid: str


def query_post(keyword: str, page_no: int, count: int, startDt: str, endDt: str) -> Union[dict, Exception]:
    response = requests.get(
        "https://section.blog.naver.com/ajax/SearchList.naver",
        headers={
            "Referer": "https://section.blog.naver.com/Search/Post.naver?pageNo=1&rangeType=ALL&orderBy=sim&keyword=%EC%88%98%EB%AC%B8%EB%8B%AC%EA%B8%B0%EC%B2%B4%ED%97%98"
        },
        params={
            "countPerPage": count,
            "currentPage": page_no,
            "keyword": keyword,
            "startDate": startDt,
            "endDate": endDt,
        }
    )

    # 요청 실패 시, AssertionError 반환
    if not response.ok:
        return AssertionError("요청을 성공적으로 실행하지 못 했습니다.")

    # print(response.text)

    # 네이버는 응답에서 5글자의 접미사를 추가하여 JSON 텍스트를 반환하기 때문에
    # 접미사 5글자를 생략한 텍스트를 다시 json으로 해석해야 합니다.
    text = response.text[5:]
    _json = json.loads(text)

    # 요청에 문제가 있어서, 오류가 발생한 경우
    # _json["result"]["message"]에 서버로부터 전달된 오류 메시지가 담겨 있음 (예시: "에러가 발생하였습니다")
    # 오류가 아닌 경우 _json["results"]는 존재하지만, _json["results"]["code"]가 존재하지 않음.
    if "code" in _json["result"].keys() and _json["result"]["code"] == "error":
        return AssertionError("입력 값에 문제가 있어 응답이 성공적으로 이루어지지 않았습니다.")

    return _json

"""
data 문자열 내에서 keywords의 요소 중 얼마나 포함되어 있는가를 반환함
"""
def is_contains(data: str, keywords: str) -> int:
    return sum(map(lambda keyword: 1 if keyword in data else 0, keywords))

print('='*100)
print("연습문제 6-5: 블로그 크롤러 : 여러건의 네이버 블로그 정보 추출하여 저장하기".center(65))
print('='*100)

# keyword = input("1.크롤링할 키워드는 무엇입니까?(예:여행): ")
# must_contains = input(
#     "2.결과에서 반드시 포함하는 단어를 입력하세요(예:국내,바닷가)\n(여러개일 경우 ,로 구분해서 입력하고 없으면 엔터를 입력하세요): ")
# must_excludes = input(
#     "3.결과에서 제외할 단어를 입력하세요(예:분양권,해외)\n(여러개일 경우 ,로 구분해서 입력하고 없으면 엔터 입력하세요): ")
# startDt = input("4.조회 시작일자 입력(예:2017-01-01):")
# endDt = input("5.조회 종료일자 입력(예:2017-12-31):")
# crawlCnt = input("6.크롤링 할 건수는 몇건입니까?(최대 1000건): ") or "5"
# filepath = input("7.파일을 저장할 폴더명만 쓰세요(예:c:\\temp\\):")

keyword = "여행"
must_contains=[]
must_excludes=[]
startDt="2017-01-01"
endDt="2017-12-31"
crawlCnt=10
filepath="./file"

# filepath 가공
xlsx_path = f"{filepath}.xlsx"
txt_path = f"{filepath}.txt"

"""
데이터 요청 및 결과 가져오기 -> dataclass 구현체에 저장
"""

results = query_post(keyword, 1, crawlCnt, startDt, endDt)

if isinstance(results, AssertionError):
    print("파라미터에 문제가 있어 요청이 정상적으로 수행되지 않았습니다.")
    print(results)

raw_posts = results["result"]["searchList"]
posts: List[Post] = list(map(lambda post: Post(
        post["domainIdOrBlogId"],
        post["nickName"],
        post["blogName"],
        post["addDate"],
        post["postUrl"],
        post["title"],
        post["noTagTitle"],
        post["contents"],
        post["profileImgUrl"],
        post["hasThumbnail"],
        post["thumbnails"],
        post["product"],
        post["marketPost"],
        post["logNo"],
        post["gdid"]),
        raw_posts)
    )

"""
포함되야 하는 단어, 제외되어야 하는 단어 처리
"""

filtered_posts = list(filter(lambda post: 
    # 포함해야 하는 단어 목록에 있는 것을 모두 포함하였으며
    is_contains(post.contents, must_contains) == len(must_contains) and
    # 제외할 단어에 포함된 것을 모두 포함하지 않은 경우
    is_contains(post.contents, must_excludes) == 0, posts))

"""
저장할 데이터 추출 및 데이터프레임화
"""

df = pd.DataFrame({
    "블로그주소": [post.postUrl for post in posts],
    "작성자이름": [post.nickname for post in posts],
    "작성일자": [datetime.fromtimestamp(post.date / 1000).strftime("%Y.%m.%d %H:%M:%S") for post in posts],
    "블로그내용": [post.contents for post in posts]
})

with open(txt_path, "w", encoding="utf8") as fp:
    for rownum in range(df.shape[0]):
        fp.write(f"총 {df.shape[0]} 건 중 {rownum + 1} 번째 블로그 데이터를 수집합니다".ljust(100, '=') + '\n')
        fp.write(f"1.블로그 주소:{df['블로그주소'][rownum]}\n")
        fp.write(f"2.작성자:{df['작성자이름'][rownum]}\n")
        fp.write(f"3.작성 일자:{df['작성일자'][rownum]}\n")
        fp.write(f"4.블로그 내용:{df['블로그내용'][rownum]}\n")
        fp.write("\n")
    

df.to_excel(xlsx_path)