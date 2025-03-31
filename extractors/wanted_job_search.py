from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
import csv
from utils.logger import setup_logger
from extractors.job_data import JobData

# 로거 설정
logger = setup_logger(__name__)

class WantedJobSearch:
    """
    Wanted 웹사이트에서 구직 정보를 스크래핑하는 클래스
    """
    def __init__(self, headless=False):
        self.keywords = []
        self.base_url = "https://www.wanted.co.kr/search?query={}&tab=position"
        self.headless = headless
        logger.info(f"WantedJobSearch 초기화: headless 모드 = {self.headless}")

    def add_keyword(self, keyword):
        """단일 키워드 추가"""
        self.keywords.append(keyword.strip())

    def add_keywords_from_input(self, keyword_input):
        """쉼표로 구분된 키워드 문자열에서 키워드 추가"""
        keywords = keyword_input.split(',')
        for keyword in keywords:
            self.add_keyword(keyword)

    def run_playwright(self, url, scroll_count=5, scroll_delay=1.5, max_retries=3):
        """Playwright를 사용하여 웹 페이지 콘텐츠 가져오기"""
        for attempt in range(max_retries):
            try:
                with sync_playwright() as p:
                    # 기본 브라우저 설정
                    browser = p.chromium.launch(
                        headless=self.headless
                    )
                    
                    # 기본 컨텍스트 설정
                    context = browser.new_context(
                        viewport={'width': 1920, 'height': 1080}
                    )
                    
                    # 새 페이지 생성
                    page = context.new_page()
                    
                    # 페이지 로드
                    logger.info(f"페이지 로드 중: {url}")
                    page.goto(url)
                    time.sleep(2)
                    
                    # 스크롤 다운
                    logger.info("페이지 스크롤 시작")
                    for i in range(scroll_count):
                        # 페이지 끝까지 스크롤
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        time.sleep(scroll_delay)
                    
                    # 콘텐츠 추출
                    content = page.content()
                    browser.close()
                    return content
                    
            except Exception as e:
                logger.error(f"Playwright 실행 중 오류 발생 (시도 {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    logger.info("5초 후 재시도...")
                    time.sleep(5)
                else:
                    return None
        
        return None
    
    def _check_for_bot_detection(self, page):
        """봇 감지 메커니즘이 페이지에 있는지 확인"""
        content = page.content().lower()
        detection_strings = [
            'captcha', 'robot', 'automated', 'automation', 'bot detection',
            '인증', '로봇', '자동화', '차단'
        ]
        
        for string in detection_strings:
            if string in content:
                return True
                
        # 추가 확인: 예상되는 콘텐츠가 없는 경우
        if not page.query_selector('div[class*="JobCard_container"]'):
            url = page.url
            if 'position' in url and not page.query_selector('div[class*="JobList"]'):
                return True
                
        return False
        
    def _scroll_page(self, page, scroll_count, scroll_delay):
        """페이지를 자연스럽게 스크롤하는 메서드"""
        for i in range(scroll_count):
            # 페이지 높이 확인
            height = page.evaluate("document.body.scrollHeight")
            viewport_height = page.evaluate("window.innerHeight")
            
            # 자연스러운 스크롤을 위한 랜덤 요소 추가
            scroll_amount = min(height, viewport_height * (i + 1))
            
            # 드래그하듯이 스크롤 (더 자연스러움)
            for step in range(10):
                current_pos = page.evaluate("window.scrollY")
                target_pos = scroll_amount * (step + 1) / 10
                distance = target_pos - current_pos
                
                if distance > 0:
                    page.evaluate(f"window.scrollBy(0, {distance/10})")
                    # 불규칙한 지연으로 자연스러움 향상
                    time.sleep(0.02 + 0.01 * (step % 3))
            
            # 잠시 콘텐츠 탐색하는 것처럼 일시 정지
            time.sleep(scroll_delay)
            
            # 가끔 작은 위/아래 스크롤 추가 (실제 사용자처럼)
            if i % 2 == 1:
                page.evaluate("window.scrollBy(0, -100)")
                time.sleep(0.3)
                page.evaluate("window.scrollBy(0, 120)")
                time.sleep(0.2)
    
    def scrape_keyword(self, keyword):
        """특정 키워드에 대한 구직 정보 스크래핑"""
        jobs_db = []
        url = self.base_url.format(keyword)
        
        logger.info(f"Wanted 스크래핑 시작: URL = {url}")
        
        content = self.run_playwright(url)
        if not content:
            logger.warning(f"키워드 '{keyword}'에 대한 콘텐츠를 가져오지 못했습니다.")
            return jobs_db
            
        soup = BeautifulSoup(content, "html.parser")
        
        # 클래스명이 'JobCard_container'로 시작하는 모든 div 요소 찾기
        jobs = soup.find_all("div", class_=lambda x: x and x.startswith("JobCard_container"))
        
        logger.info(f"{len(jobs)}개의 채용 공고 요소 발견")
        
        for job in jobs:
            try:
                # a 태그 찾기 (링크)
                link_element = job.find("a")
                if not link_element:
                    continue
                    
                partial_link = link_element.get("href", "")
                link = f"https://www.wanted.co.kr{partial_link}" if partial_link.startswith("/") else partial_link
                
                # 제목 찾기 - 클래스명이 'JobCard_title'로 시작하는 strong 태그
                title_element = job.find(lambda tag: tag.name == "strong" and tag.get('class') and any(c.startswith("JobCard_title") for c in tag.get('class', [])))
                title = title_element.text.strip() if title_element else "제목 없음"
                
                # 회사명 찾기 - 클래스명이 'JobCard_companyName'으로 시작하는 span 태그
                company_element = job.find(lambda tag: tag.name == "span" and tag.get('class') and any(c.startswith("JobCard_companyName") for c in tag.get('class', [])))
                company_name = company_element.text.strip() if company_element else "회사명 없음"
                
                # 보상금 찾기 - 클래스명이 'JobCard_reward'로 시작하는 span 태그
                reward_element = job.find(lambda tag: tag.name == "span" and tag.get('class') and any(c.startswith("JobCard_reward") for c in tag.get('class', [])))
                reward = reward_element.text.strip() if reward_element else "보상금 정보 없음"
                
                # 디버깅 로그 추가
                logger.info(f"채용 정보 추출: {title} - {company_name}")
                
                job_data = JobData(title, company_name, link, reward=reward)
                jobs_db.append(job_data.to_list())
            except Exception as e:
                logger.error(f"작업 추출 중 오류 발생: {e}")

        return jobs_db

    def save_to_csv(self, keyword):
        """스크래핑한 구직 정보를 CSV 파일로 저장"""
        self.add_keywords_from_input(keyword)
        for keyword in self.keywords:
            try:
                keyword_jobs = self.scrape_keyword(keyword)
                if not keyword_jobs:
                    logger.warning(f"키워드 '{keyword}'에 대한 작업을 찾을 수 없습니다")
                    continue
                    
                with open(f"wanted_{keyword}_jobs.csv", mode="w", encoding="utf-8") as file:
                    writer = csv.writer(file)
                    # 첫 번째 작업에서 JobData 인스턴스를 생성하여 헤더 가져오기
                    job_data = JobData(keyword_jobs[0][0], keyword_jobs[0][1], keyword_jobs[0][-1], reward=keyword_jobs[0][2])
                    writer.writerow(job_data.get_headers())
                    for job in keyword_jobs:
                        writer.writerow(job)
                logger.info(f"키워드 '{keyword}'에 대한 {len(keyword_jobs)}개 작업이 CSV 파일에 저장되었습니다")
            except Exception as e:
                logger.error(f"CSV 저장 중 오류 발생 (키워드 '{keyword}'): {e}")
