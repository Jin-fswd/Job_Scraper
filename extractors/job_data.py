"""
구직 정보를 표현하는 기본 클래스 모듈
"""

class JobData:
    """구직 정보의 기본 클래스"""
    
    def __init__(self, position, company, link, **kwargs):
        """
        기본 구직 정보 초기화
        
        Args:
            position (str): 직무 이름
            company (str): 회사 이름
            link (str): 지원 링크
            **kwargs: 추가 정보 (reward, location, salary 등)
        """
        self.position = position
        self.company = company
        self.link = link
        
        # 추가 정보 설정
        self.location = kwargs.get('location', 'Not specified')
        self.salary = kwargs.get('salary', 'Not specified')
        self.reward = kwargs.get('reward', 'Not specified')
        
        # 기타 추가 정보
        self.additional_info = {k: v for k, v in kwargs.items() 
                              if k not in ['location', 'salary', 'reward']}
        
    def get_headers(self):
        """CSV 헤더 반환"""
        headers = ["Position", "Company"]
        # 기본 추가 필드
        if self.location != 'Not specified':
            headers.append("Location")
        if self.salary != 'Not specified':
            headers.append("Salary")
        if self.reward != 'Not specified':
            headers.append("Reward")
        # 기타 추가 정보가 있으면 헤더에 추가
        for key in sorted(self.additional_info.keys()):
            headers.append(key.title())
        headers.append("Link")
        return headers
        
    def to_list(self):
        """리스트 형식으로 데이터 반환"""
        data = [self.position, self.company]
        # 기본 추가 필드
        if self.location != 'Not specified':
            data.append(self.location)
        if self.salary != 'Not specified':
            data.append(self.salary)
        if self.reward != 'Not specified':
            data.append(self.reward)
        # 기타 추가 정보가 있으면 데이터에 추가
        for key in sorted(self.additional_info.keys()):
            data.append(self.additional_info[key])
        data.append(self.link)
        return data
        
    def __str__(self):
        """문자열 표현"""
        info = [f"{self.position} at {self.company}"]
        if self.location != 'Not specified':
            info.append(f"Location: {self.location}")
        if self.salary != 'Not specified':
            info.append(f"Salary: {self.salary}")
        if self.reward != 'Not specified':
            info.append(f"Reward: {self.reward}")
        for key, value in sorted(self.additional_info.items()):
            info.append(f"{key}: {value}")
        info.append(f"Link: {self.link}")
        return " | ".join(info)
        
    def __repr__(self):
        """개발자를 위한 표현"""
        return f"JobData(position='{self.position}', company='{self.company}', link='{self.link}', location='{self.location}', salary='{self.salary}', reward='{self.reward}', **{self.additional_info})"
