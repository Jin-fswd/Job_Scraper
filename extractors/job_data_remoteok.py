"""
RemoteOK 구직 정보를 표현하는 클래스
"""
from extractors.job_data import JobData

class JobDataRemoteOK(JobData):
    """RemoteOK 구직 정보 클래스"""
    
    def __init__(self, position, company, location, link, salary=None):
        """
        RemoteOK 구직 정보 초기화
        
        Args:
            position (str): 직무 이름
            company (str): 회사 이름
            location (str): 근무 위치
            link (str): 지원 링크
            salary (str, optional): 급여 정보
        """
        super().__init__(
            position=position,
            company=company,
            link=link,
            location=location,
            salary=salary if salary else "Not specified"
        )
    
    def to_list(self):
        # 기본 필드
        result = [self.title, self.company_name, self.location, self.link, self.salary, self.posted_date]
        # 태그를 쉼표로 구분된 문자열로 변환
        tags_str = ", ".join(self.tags) if self.tags else ""
        result.append(tags_str)
        # 광고 여부 추가
        result.append("광고" if self.is_ad else "")
        return result
        
    def get_headers(self):
        return ["Title", "Company", "Location", "Link", "Salary", "Posted Date", "Tags", "Ad"] 