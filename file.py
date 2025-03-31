import csv
from io import BytesIO, TextIOWrapper


def save_to_file(keyword, jobs=[], headers=None):
    """
    구직 데이터를 CSV 파일로 저장하는 함수
    
    Args:
        keyword: 검색 키워드 (파일명에 사용)
        jobs: 구직 데이터 목록
        headers: CSV 헤더 (기본값: ["Title", "Company", "Link"])
    
    Returns:
        생성된 파일 경로
    """
    file_path = f"{keyword}_jobs.csv"
    if headers is None:
        headers = ["Title", "Company", "Link"]
        
    try:
        with open(f"{file_path}", mode="w", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            for job in jobs:
                writer.writerow(job)
    except IOError as e:
        print(f"Error writing to file {keyword}_jobs.csv: {e}")
    return file_path


def save_file_to_memory(keyword, jobs=[], headers=None):
    """
    구직 데이터를 메모리 내 CSV 파일로 저장하는 함수
    
    Args:
        keyword: 검색 키워드 (사용하지 않지만 일관성을 위해 유지)
        jobs: 구직 데이터 목록
        headers: CSV 헤더 (기본값: ["Title", "Company", "Link"])
    
    Returns:
        메모리 내 파일 객체
    """
    if headers is None:
        headers = ["Title", "Company", "Link"]
        
    output = BytesIO()
    wrapper = TextIOWrapper(output, encoding='utf-8', newline="")
    writer = csv.writer(wrapper)
    writer.writerow(headers)
    for job in jobs:
        writer.writerow(job)
    wrapper.flush()
    output.seek(0)
    wrapper.detach()
    return output
