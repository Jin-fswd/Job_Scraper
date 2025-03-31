"""
We Work Remotely 구직 정보를 표현하는 클래스
"""
from extractors.job_data import JobData

class JobDataWWR(JobData):
    """WWR 구직 정보 클래스"""
    
    def __init__(self, position, company, location, salary, link, categories=None):
        """
        WWR 구직 정보 초기화
        
        Args:
            position (str): 직무 이름
            company (str): 회사 이름
            location (str): 근무 위치
            salary (str): 급여 정보
            link (str): 지원 링크
            categories (list, optional): 카테고리 목록
        """
        super().__init__(
            position=position,
            company=company,
            link=link,
            location=location,
            salary=salary
        )
        self.categories = categories if categories else []
        self.section = ""  # 직무가 속한 섹션 이름 (예: "Full-Stack Programming Jobs")
    
    def set_section(self, section_name):
        """섹션 이름 설정"""
        self.section = section_name
    
    def to_list(self):
        """리스트 형식으로 데이터 반환"""
        return [
            self.position,
            self.company,
            self.location,
            self.salary,
            self.link
        ]
        
    def get_headers(self):
        """CSV 헤더 반환"""
        return ["Position", "Company", "Location", "Salary", "Link"]
