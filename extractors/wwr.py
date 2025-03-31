import requests
import csv
import logging
from bs4 import BeautifulSoup
from extractors.job_data_wwr import JobDataWWR

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WWRJobSearch:
    """
    We Work Remotely 웹사이트에서 구직 정보를 스크래핑하는 클래스
    """

    def __init__(self):
        self.keywords = []
        self.base_url = "https://weworkremotely.com/remote-jobs/search?&term="
        self.jobs_page_url = "https://weworkremotely.com/remote-full-time-jobs?page={}"

    def add_keyword(self, keyword):
        """단일 키워드 추가"""
        self.keywords.append(keyword.strip())

    def add_keywords_from_input(self, keyword_input):
        """쉼표로 구분된 키워드 문자열에서 키워드 추가"""
        keywords = keyword_input.split(',')
        for keyword in keywords:
            self.add_keyword(keyword)

    def _extract_job_data(self, job):
        """job HTML 요소에서 job 데이터 추출"""
        try:
            title = job.find("h4", class_="new-listing__header__title")
            company = job.find("p", class_="new-listing__company-name")
            region = job.find("p", class_="new-listing__company-headquarters")
            categories_div = job.find("div", class_="new-listing__categories")
            url_element = job.find("div", class_="tooltip--flag-logo")

            if not all([title, company, region, url_element]):
                logger.warning("HTML 구조 일부 요소 누락")
                return None

            # 제목, 회사, 지역 추출
            title_text = title.text.strip()
            company_text = company.text.strip()
            region_text = region.text.strip()
            
            # 모든 카테고리 태그 추출
            categories = []
            if categories_div:
                category_elements = categories_div.find_all("p", class_="new-listing__categories__category")
                categories = [cat.text.strip() for cat in category_elements if cat.text.strip()]
            
            # 링크 추출
            link = job.a['href'] if job.a else None
            if not link:
                link = url_element.next_sibling['href'] if url_element.next_sibling else None
            
            if not link:
                logger.warning("링크를 찾을 수 없습니다")
                return None
                
            if not link.startswith("http"):
                link = f"https://weworkremotely.com{link}"
                
            # 급여 정보는 없으므로 "Not specified" 사용
            salary = "Not specified"
                
            job_data = JobDataWWR(title_text, company_text, region_text, salary, link, categories)
            return job_data
            
        except Exception as e:
            logger.error(f"작업 데이터 추출 중 오류 발생: {e}")
            return None

    def _get_jobs_from_soup(self, soup):
        """BeautifulSoup 객체에서 job 목록 추출 (업데이트된 HTML 구조)"""
        all_jobs = []
        try:
            # 모든 job 섹션 찾기
            job_sections = soup.find_all("section", class_="jobs")
            
            if not job_sections:
                logger.warning("jobs 섹션을 찾을 수 없습니다")
                return all_jobs
            
            # 각 섹션별로 작업 추출
            for section in job_sections:
                section_name = ""
                section_header = section.find("h2")
                if section_header and section_header.a:
                    section_name = section_header.a.text.strip()
                
                logger.info(f"섹션 처리 중: {section_name}")
                
                # 섹션 내 모든 리스트 항목 찾기
                job_elements = section.find_all("li")
                
                for job in job_elements:
                    # 'view-all' 클래스가 있는 항목 건너뛰기
                    if job.get("class") and ("view-all" in job.get("class") or "feature--ad" in job.get("class")):
                        continue
                    
                    job_data = self._extract_job_data(job)
                    if job_data:
                        # 섹션 이름 추가
                        job_data.section = section_name
                        all_jobs.append(job_data.to_list())
                    
        except Exception as e:
            logger.error(f"작업 목록 추출 중 오류 발생: {e}")
            
        return all_jobs

    def scrape_page(self, url):
        """특정 URL의 페이지에서 구직 정보 스크래핑"""
        logger.info(f"WWR 페이지 스크래핑 시작: URL = {url}")
        
        try:
            response = requests.get(url)
            if response.status_code != 200:
                logger.warning(f"페이지 요청 실패: {response.status_code} - {url}")
                return []
                
            soup = BeautifulSoup(response.content, "html.parser")
            jobs = self._get_jobs_from_soup(soup)
            logger.info(f"URL {url}에서 {len(jobs)}개 작업 스크래핑 완료")
            return jobs
        except Exception as e:
            logger.error(f"페이지 스크래핑 중 오류 발생 ({url}): {e}")
            return []

    def scrape_keyword(self, keyword):
        """특정 키워드에 대한 구직 정보 스크래핑"""
        url = f"{self.base_url}{keyword}"
        logger.info(f"WWR 키워드 스크래핑 시작: URL = {url}")
        
        try:
            response = requests.get(url)
            if response.status_code != 200:
                logger.warning(f"키워드 검색 요청 실패: {response.status_code} - {url}")
                return []
                
            soup = BeautifulSoup(response.text, "html.parser")
            jobs = self._get_jobs_from_soup(soup)
            logger.info(f"키워드 '{keyword}'에 대해 {len(jobs)}개 작업 스크래핑 완료")
            return jobs
        except Exception as e:
            logger.error(f"키워드 스크래핑 중 오류 발생 ({keyword}): {e}")
            return []

    def get_pages(self, url=None):
        """페이지네이션 정보 가져오기"""
        if url is None:
            url = self.jobs_page_url.format(1)
            
        try:
            response = requests.get(url)
            if response.status_code != 200:
                logger.warning(f"페이지네이션 정보 요청 실패: {response.status_code}")
                return 1
                
            soup = BeautifulSoup(response.content, "html.parser")
            pagination = soup.find("div", class_="pagination")
            if not pagination:
                return 1
                
            pages = pagination.find_all("span", class_="page")
            return len(pages) if pages else 1
        except Exception as e:
            logger.error(f"페이지 수 확인 중 오류 발생: {e}")
            return 1

    def pages_save_to_csv(self):
        """모든 페이지의 구직 정보를 CSV 파일로 저장"""
        try:
            num_of_pages = self.get_pages()
            all_jobs = []
            
            for i in range(num_of_pages):
                url = self.jobs_page_url.format(i+1)
                jobs = self.scrape_page(url)
                all_jobs.extend(jobs)
                logger.info(f"페이지 {i+1}/{num_of_pages} 스크래핑 완료: {len(jobs)}개 작업 가져옴")
                
            if not all_jobs:
                logger.warning("저장할 작업이 없습니다.")
                return
                
            with open(f"wwr_jobs.csv", mode="w", encoding="utf-8") as file:
                writer = csv.writer(file)
                # 한 개의 작업을 인스턴스화하여 헤더 가져오기
                if all_jobs:
                    job_data = JobDataWWR(
                        position=all_jobs[0][0],
                        company=all_jobs[0][1],
                        location=all_jobs[0][2],
                        salary=all_jobs[0][3],
                        link=all_jobs[0][4]
                    )
                    writer.writerow(job_data.get_headers())
                    for job in all_jobs:
                        writer.writerow(job)
                        
            logger.info(f"총 {len(all_jobs)}개 작업이 wwr_jobs.csv 파일에 저장되었습니다.")
        except Exception as e:
            logger.error(f"전체 페이지 저장 중 오류 발생: {e}")

    def keyword_search_save_to_csv(self, keyword):
        """키워드 검색 결과를 CSV 파일로 저장"""
        self.add_keywords_from_input(keyword)
        for keyword in self.keywords:
            try:
                keyword_jobs = self.scrape_keyword(keyword)
                if not keyword_jobs:
                    logger.warning(f"키워드 '{keyword}'에 대한 작업을 찾을 수 없습니다.")
                    continue
                    
                with open(f"wwr_{keyword}_jobs.csv", mode="w", encoding="utf-8") as file:
                    writer = csv.writer(file)
                    # 한 개의 작업을 인스턴스화하여 헤더 가져오기
                    job_data = JobDataWWR(
                        position=keyword_jobs[0][0],
                        company=keyword_jobs[0][1],
                        location=keyword_jobs[0][2],
                        salary=keyword_jobs[0][3],
                        link=keyword_jobs[0][4]
                    )
                    writer.writerow(job_data.get_headers())
                    for job in keyword_jobs:
                        writer.writerow(job)
                        
                logger.info(f"키워드 '{keyword}'에 대한 {len(keyword_jobs)}개 작업이 CSV 파일에 저장되었습니다.")
            except IOError as e:
                logger.error(f"키워드 '{keyword}'에 대한 CSV 파일 저장 중 오류 발생: {e}")
            except Exception as e:
                logger.error(f"키워드 '{keyword}' 저장 중 예기치 않은 오류 발생: {e}")
