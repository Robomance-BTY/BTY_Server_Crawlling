import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import html
import pandas as pd

# 검색할 단어 설정
search_word = '진격의 거인'
# 검색 결과를 저장할 리스트 생성
books_info = []

# 여러 페이지를 순회
for page in range(1, 3):  # 예시로 1페이지부터 3페이지까지 처리
    print(f'{page} 페이지 처리중...')
    # 검색 URL, 페이지 번호를 포함
    url = f'https://www.yes24.com/Product/Search?domain=ALL&query={quote(search_word)}&page={page}'
    
    # 검색 결과 페이지 요청
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html.parser')
    
    # 상품명을 선택하기 위한 셀렉터 사용
    book_elements = soup.select('a.gd_name')
    
    # 각 책에 대하여
    for book_element in book_elements:  # 페이지 내 모든 책 처리
        book_info = {}  # 각 책의 정보를 저장할 딕셔너리
        detail_url = book_element.get('href')
        
        # detail_url이 "http" 또는 "https"로 시작하지 않는 경우 앞에 추가
        if not detail_url.startswith(('http:', 'https:')):
            detail_url = f"https://www.yes24.com{detail_url}"
        
        # 상세 페이지 요청
        response = requests.get(detail_url)
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 제목 저장
        title_element = soup.select_one('h2.gd_name')
        if title_element:
            book_info['title'] = title_element.text.strip()
        else:
            continue  # '제목 없음'인 경우 다음 항목으로 이동
        
        # 저자 정보 저장
        author_element = soup.find('span', class_='gd_auth')
        book_info['author'] = author_element.find('a').text.strip() if author_element and author_element.find('a') else '저자 정보 없음'
        
        # 상품 설명 저장
        description_element = soup.find('textarea', class_='txtContentText')
        book_info['description'] = html.unescape(description_element.text.strip()) if description_element else '설명 없음'
        
        # 장르 정보 저장
        genre_element = soup.find('a', href=lambda x: x and x.startswith('/24/Category/Display/001001008'))
        book_info['genre'] = genre_element.text.strip() if genre_element else '장르 정보 없음'
        
        # 출판 날짜 저장
        published_date_element = soup.find('td', class_='txt lastCol')
        book_info['published_date'] = published_date_element.text.strip() if published_date_element else '출판 날짜 정보 없음'
        
        # 최종 정보 리스트에 추가
        books_info.append(book_info)

# 데이터 프레임 생성
df = pd.DataFrame(books_info)

# '제목 없음'인 항목이 이미 필터링되어 있으므로, 추가적인 작업 없이 바로 엑셀 파일로 저장
excel_filename = 'books_info_filtered.xlsx'
df.to_excel(excel_filename, index=False)

print(f'"{excel_filename}" 파일에 저장되었습니다.')
