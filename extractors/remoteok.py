from bs4 import BeautifulSoup
import csv
import logging
from playwright.sync_api import sync_playwright
import time
from extractors.job_data_remoteok import JobDataRemoteOK

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RemoteOKJobSearch:
    """
    RemoteOK 웹사이트에서 구직 정보를 스크래핑하는 클래스
    """
    
    def __init__(self):
        self.keywords = []
        self.base_url = "https://remoteok.com/remote-{}-jobs"
        self.proxies = [
            # 예시 프록시 리스트 (실제 사용할 때는 유효한 프록시로 교체해야 함)
            # 무료 프록시는 자주 변경되므로 사용 전 체크 필요
            "103.149.162.195:80", 
            "47.242.3.214:8081",
            "135.181.29.13:3128"
        ]
        self.current_proxy_index = 0
        
    def add_keyword(self, keyword):
        """단일 키워드 추가"""
        self.keywords.append(keyword.strip())
        
    def add_keywords_from_input(self, keyword_input):
        """쉼표로 구분된 키워드 문자열에서 키워드 추가"""
        keywords = keyword_input.split(',')
        for keyword in keywords:
            self.add_keyword(keyword)
            
    def get_proxy(self):
        """프록시 서버 목록에서 다음 프록시 반환"""
        if not self.proxies:
            return None
            
        proxy = self.proxies[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
        return proxy
        
    def run_playwright(self, url, scroll_count=4, scroll_delay=5, retry_count=2, use_proxy=False, manual_captcha=False):
        """Playwright를 사용하여 웹 페이지 콘텐츠 가져오기"""
        logger.info(f"RemoteOK 웹사이트 접속 중: {url}")
        
        for attempt in range(retry_count + 1):
            try:
                with sync_playwright() as p:
                    # 프록시 설정
                    proxy_settings = None
                    if use_proxy:
                        proxy = self.get_proxy()
                        if proxy:
                            logger.info(f"프록시 서버 사용: {proxy}")
                            proxy_settings = {
                                "server": f"http://{proxy}"
                                # 필요시 인증 추가:
                                # "username": "사용자명",
                                # "password": "비밀번호"
                            }
                    
                    # 1. 스텔스 모드 설정
                    browser = p.chromium.launch(
                        headless=True,  # 헤드리스 모드 비활성화 (봇 감지 회피에 도움)
                        args=[
                            '--disable-blink-features=AutomationControlled',  # 자동화 감지 비활성화
                            '--no-sandbox',
                            '--disable-setuid-sandbox',
                            '--disable-infobars',
                            '--disable-dev-shm-usage',
                            '--disable-accelerated-2d-canvas',
                            '--no-first-run',
                            '--no-zygote',
                            '--disable-gpu'
                        ]
                    )
                    
                    # 2. 더 현실적인 브라우저 컨텍스트 설정
                    context = browser.new_context(
                        viewport={'width': 1920, 'height': 1080},  # 일반적인 데스크톱 해상도
                        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
                        locale='ko-KR',  # 한국어 로케일 설정
                        proxy=proxy_settings
                    )
                    
                    # 더 사람처럼 보이게 하는 스크립트
                    context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => false,
                    });
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5],
                    });
                    """)
                    
                    page = context.new_page()
                    
                    # 3. 더 인간적인 헤더 설정
                    page.set_extra_http_headers({
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
                        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                        'Referer': 'https://www.google.com/',  # 구글에서 방문한 것처럼 설정
                        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="111", "Google Chrome";v="111"',
                        'sec-ch-ua-platform': '"Windows"',
                        'sec-ch-ua-mobile': '?0'
                    })
                    
                    # 4. 쿠키 허용 및 로컬 스토리지 설정
                    page.goto(url)
                    
                    # 5. 필요시 쿠키 수락 버튼 클릭 (사이트에 쿠키 다이얼로그가 있는 경우)
                    try:
                        cookie_buttons = page.locator('button:has-text("Accept") , button:has-text("Agree"), button:has-text("Accept all cookies")')
                        if cookie_buttons.count() > 0:
                            cookie_buttons.first.click()
                            logger.info("쿠키 수락 버튼 클릭 완료")
                    except Exception as e:
                        logger.info(f"쿠키 수락 버튼 처리 중 오류 (무시): {e}")
                    
                    # 6. 인간처럼 동작하기 위한 무작위 대기
                    time.sleep(2 + 2 * (0.1 * time.time() % 1.0))  # 2-4초 랜덤 대기
                    
                    # 7. 로봇 체크/캡차 감지 및 처리
                    page_content = page.content().lower()
                    if "captcha" in page_content or "robot" in page_content or "cloudflare" in page_content:
                        logger.warning(f"캡차 또는 로봇 체크 감지! 시도 {attempt+1}/{retry_count+1}")
                        
                        # 수동 캡차 해결 옵션이 켜져 있는 경우
                        if manual_captcha:
                            try:
                                # 캡차 화면 저장
                                screenshot_path = f"captcha_detected_{attempt}.png"
                                page.screenshot(path=screenshot_path)
                                logger.info(f"캡차 화면이 {screenshot_path}로 저장되었습니다")
                                
                                # 사용자에게 캡차 해결 요청
                                import os
                                print("\n" + "="*60)
                                print(f"캡차가 감지되었습니다! 스크린샷: {os.path.abspath(screenshot_path)}")
                                print("브라우저 창에서 캡차를 수동으로 해결해주세요.")
                                print("해결 후 아무 키나 입력하면 계속 진행합니다...")
                                print("="*60 + "\n")
                                
                                # 사용자 입력 대기
                                input("캡차 해결 후 Enter 키를 누르세요...")
                                
                                # 캡차가 해결되었는지 확인
                                updated_content = page.content().lower()
                                if "captcha" in updated_content or "robot" in updated_content:
                                    logger.warning("캡차가 여전히 존재합니다. 다시 시도하세요.")
                                    # 세션 종료 후 재시도
                                    context.close()
                                    browser.close()
                                    time.sleep(2)
                                    continue
                                else:
                                    logger.info("캡차가 성공적으로 해결되었습니다!")
                            except Exception as e:
                                logger.error(f"캡차 수동 해결 중 오류: {e}")
                                # 수동 해결 실패 시 자동 처리 시도
                        else:
                            # 자동 처리: 캡차 화면 저장 후 세션 종료
                            try:
                                # 캡차가 있는지 확인하고 이미지 저장 (디버깅 용도)
                                page.screenshot(path=f"captcha_detected_{attempt}.png")
                                logger.info(f"캡차 화면이 captcha_detected_{attempt}.png로 저장되었습니다")
                                
                                # 이 시도 실패 처리
                                context.close()
                                browser.close()
                                
                                if attempt < retry_count:
                                    # 프록시 사용 여부 변경
                                    use_proxy = not use_proxy
                                    logger.info(f"다음 시도에서 프록시 사용: {use_proxy}")
                                    time.sleep(5 + 5 * attempt)  # 대기 시간 증가
                                    continue
                                else:
                                    logger.error("모든 시도 실패 - 캡차 또는 봇 감지로 인해 차단됨")
                                    return None
                            except Exception as e:
                                logger.error(f"캡차 화면 저장 중 오류: {e}")
                    
                    # 스크롤 다운으로 더 많은 구직 정보 로드 - 사람처럼 부드럽게 스크롤
                    for i in range(scroll_count):
                        logger.info(f"스크롤 다운 {i+1}/{scroll_count}")
                        
                        # 부드러운 스크롤 시뮬레이션 (일반 End 키 대신)
                        current_height = page.evaluate("document.body.scrollHeight")
                        target_height = current_height * (i + 1) / scroll_count
                        
                        # 여러 단계로 스크롤하여 자연스럽게 만들기
                        steps = 10
                        for step in range(1, steps + 1):
                            page.evaluate(f"window.scrollTo(0, {target_height * step / steps})")
                            # 불규칙한 시간 간격으로 대기
                            time.sleep(0.1 + 0.2 * (0.1 * time.time() % 1.0))
                        
                        # 스크롤 후 무작위 시간 대기
                        wait_time = scroll_delay * (0.8 + 0.4 * (0.1 * time.time() % 1.0))
                        time.sleep(wait_time)
                    
                    # 추가 대기 시간 - 모든 동적 콘텐츠가 로드될 때까지 기다림
                    logger.info("추가 로딩 대기 중...")
                    time.sleep(3)
                    
                    # 디버깅: HTML 구조 확인
                    html_content = page.content()
                    soup_debug = BeautifulSoup(html_content, 'html.parser')
                    
                    # 테이블 찾기 시도
                    tables = soup_debug.find_all('table')
                    logger.info(f"페이지에서 {len(tables)}개의 테이블 발견")
                    
                    for i, table in enumerate(tables):
                        table_id = table.get('id', '없음')
                        logger.info(f"테이블 {i+1} ID: {table_id}")
                    
                    # jobsboard 테이블 찾기 시도
                    jobsboard_debug = soup_debug.find('table', id='jobsboard')
                    if jobsboard_debug:
                        logger.info("jobsboard 테이블을 찾았습니다!")
                        job_rows = jobsboard_debug.find_all('tr', class_='job')
                        logger.info(f"job 클래스 행 {len(job_rows)}개 발견")
                        
                        # 성공! 이 시도 완료
                        content = page.content()
                        context.close()
                        browser.close()
                        logger.info("페이지 콘텐츠 로드 완료")
                        return content
                    else:
                        logger.warning("디버깅: jobsboard 테이블을 찾을 수 없습니다")
                        
                        # 실패한 경우, 재시도 여부 결정
                        if attempt < retry_count:
                            context.close()
                            browser.close()
                            logger.info(f"jobsboard를 찾지 못함, 재시도 중 ({attempt+1}/{retry_count+1})")
                            # 프록시 사용 여부 변경
                            use_proxy = not use_proxy
                            time.sleep(5 + 5 * attempt)  # 대기 시간 증가
                            continue
                    
                    # 마지막 시도에서는 결과 반환
                    content = page.content()
                    context.close()
                    browser.close()
                    logger.info("페이지 콘텐츠 로드 완료 (테이블 미발견)")
                    return content
                    
            except Exception as e:
                logger.error(f"Playwright 실행 중 오류 발생 (시도 {attempt+1}/{retry_count+1}): {e}")
                if attempt < retry_count:
                    logger.info(f"5초 후 재시도...")
                    time.sleep(5)
                    continue
                else:
                    return None
        
        return None
            
    def scrape_keyword(self, keyword, manual_captcha=False):
        """특정 키워드에 대한 구직 정보 스크래핑"""
        jobs_db = []
        url = self.base_url.format(keyword)
        
        logger.info(f"RemoteOK 스크래핑 시작: URL = {url}")
        
        # 먼저 프록시 없이 시도
        content = self.run_playwright(url, use_proxy=False, manual_captcha=manual_captcha)
        
        # 실패하면 프록시로 시도
        if not content:
            logger.warning("프록시 없이 스크래핑 실패, 프록시를 사용하여 재시도합니다.")
            content = self.run_playwright(url, use_proxy=True, manual_captcha=manual_captcha)
            
        if not content:
            logger.warning(f"키워드 '{keyword}'에 대한 콘텐츠를 가져오지 못했습니다.")
            return jobs_db
            
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # 변경된 방식: 여러 방법으로 채용공고 테이블 찾기 시도
            jobsboard = soup.find('table', id='jobsboard')
            
            # 방법 1 실패 시, 다른 방법으로 시도
            if not jobsboard:
                logger.warning("jobsboard ID로 테이블을 찾을 수 없습니다. 다른 방법으로 시도합니다.")
                # 모든 테이블 확인
                tables = soup.find_all('table')
                logger.info(f"{len(tables)}개의 테이블이 발견됨")
                
                # 가장 많은 행을 가진 테이블을 선택 (일반적으로 구직 정보 테이블)
                if tables:
                    max_rows = 0
                    for table in tables:
                        rows = table.find_all('tr')
                        if len(rows) > max_rows:
                            max_rows = len(rows)
                            jobsboard = table
                    
                    if jobsboard:
                        logger.info(f"대체 방법으로 테이블을 찾았습니다. {max_rows}개의 행이 있습니다.")
                    else:
                        logger.warning("대체 방법으로도 테이블을 찾지 못했습니다.")
            
            if not jobsboard:
                # 마지막 방법: 직접 tr 요소 찾기
                logger.warning("테이블을 찾을 수 없어 직접 tr.job 요소를 찾습니다.")
                job_rows = soup.find_all('tr', class_='job')
                
                if job_rows:
                    logger.info(f"테이블 없이 {len(job_rows)}개의 job 행을 발견했습니다.")
                else:
                    # 완전히 다른 접근법: class가 없는 tr 요소들도 검색
                    job_rows = soup.find_all('tr')
                    # data-id 또는 data-slug 속성이 있는 행만 필터링
                    job_rows = [row for row in job_rows if row.get('data-id') or row.get('data-slug')]
                    logger.info(f"속성 기반 필터링으로 {len(job_rows)}개의 tr 행을 발견했습니다.")
                    
                    if not job_rows:
                        logger.warning("구직 정보를 찾을 수 없습니다.")
                        return jobs_db
            else:
                # <tbody> 아래의 모든 tr 요소 찾기 (각 요소는 하나의 채용공고)
                job_rows = jobsboard.find_all('tr')
                # 필터링: 광고, 구분선, 일반 작업 행만 남기기
                job_rows = [row for row in job_rows if 
                          row.get('class') and ('job' in row.get('class') or 
                                              'sw-insert' in row.get('class')) or
                          row.get('data-id') or row.get('data-slug')]
                
                if not job_rows:
                    logger.warning("구직 정보를 찾을 수 없습니다.")
                    return jobs_db
            
            logger.info(f"처리할 채용공고 수: {len(job_rows)}")
            
            for job_row in job_rows:
                try:
                    # 행이 광고(sw-insert)인지 확인
                    is_ad = False
                    if job_row.get('class') and 'sw-insert' in job_row.get('class'):
                        is_ad = True
                        logger.info("광고 항목 발견")
                    
                    # 각 공고의 data-slug 속성에서 URL 슬러그 추출
                    job_slug = job_row.get('data-slug', '')
                    job_id = job_row.get('data-id', '')
                    
                    # URL 설정: 광고와 일반 공고에 따라 다르게 처리
                    if is_ad:
                        # 광고의 경우 a 태그에서 URL 추출
                        link_element = job_row.find('a')
                        url = link_element.get('href', '') if link_element else ""
                        # URL이 상대 경로인 경우 전체 URL로 변환
                        if url and not url.startswith('http'):
                            url = f"https://remoteok.com{url}"
                    else:
                        # 일반 공고는 data-slug 사용
                        url = f"https://remoteok.com/remote-jobs/{job_slug}" if job_slug else ""
                        # data-slug가 없는 경우 data-id 사용
                        if not url and job_id:
                            url = f"https://remoteok.com/remote-jobs/{job_id}"
                    
                    # URL이 없으면 계속 진행
                    if not url:
                        logger.warning("URL을 추출할 수 없습니다. 건너뜁니다.")
                        continue
                    
                    # company_and_position 클래스를 가진 td 요소 찾기
                    company_position_cell = job_row.find('td', class_='company_and_position')
                    
                    # 대체 방법: company position 클래스로 찾기
                    if not company_position_cell:
                        company_position_cell = job_row.find('td', class_='company position company_and_position')
                    
                    if not company_position_cell:
                        logger.warning("회사 및 직책 정보를 찾을 수 없습니다. 건너뜁니다.")
                        continue
                    
                    # 제목(title) 추출
                    if is_ad:
                        # 광고의 경우 strong 태그 또는 a 태그의 텍스트 사용
                        title_element = company_position_cell.find('strong')
                        if not title_element:
                            title_element = company_position_cell.find('a')
                        title = title_element.text.strip() if title_element else "광고"
                    else:
                        # 일반 공고는 h2 태그 사용
                        title_element = company_position_cell.find('h2', itemprop='title')
                        title = title_element.text.strip() if title_element else "제목 없음"
                    
                    # 회사명(company) 추출
                    if is_ad:
                        # 광고의 경우 두 번째 a 태그나 span 태그에서 추출 시도
                        company_elements = company_position_cell.find_all('a')
                        if len(company_elements) > 1:
                            company = company_elements[1].text.strip()
                        else:
                            span_element = company_position_cell.find('span')
                            company = span_element.text.strip() if span_element else "광고주"
                    else:
                        # 일반 공고는 h3 태그 사용
                        company_element = company_position_cell.find('h3', itemprop='name')
                        company = company_element.text.strip() if company_element else "회사명 없음"
                    
                    # 위치정보(location)와 급여정보(salary) 추출
                    location = "정보 없음"
                    salary = ""
                    
                    if not is_ad:
                        location_elements = company_position_cell.find_all('div', class_='location')
                        
                        # 위치정보가 있는 경우
                        if location_elements:
                            # 첫 번째 위치 요소에서 국가 정보 추출 시도
                            location_text = location_elements[0].text.strip()
                            if location_text:
                                location = location_text
                            
                            # 급여 정보 확인 및 추출
                            for loc_element in location_elements:
                                if '💰' in loc_element.text:
                                    salary = loc_element.text.strip()
                                    break
                    
                    # 태그(tags) 정보 추출
                    tags = []
                    if not is_ad:
                        tags_cell = job_row.find('td', class_='tags')
                        if tags_cell:
                            tag_elements = tags_cell.find_all('div', class_='tag')
                            for tag_element in tag_elements:
                                h3_tag = tag_element.find('h3')
                                if h3_tag:
                                    tags.append(h3_tag.text.strip())
                    
                    # 게시 날짜 추출
                    posted_date = ""
                    if not is_ad:
                        # data-epoch에서 날짜 추출
                        epoch_timestamp = job_row.get('data-epoch', '')
                        if epoch_timestamp:
                            try:
                                posted_date = time.strftime('%Y-%m-%d', time.localtime(int(epoch_timestamp)))
                            except:
                                # 날짜 정보 추출 실패 시 time 태그에서 추출 시도
                                time_element = job_row.find('time')
                                if time_element:
                                    posted_date = time_element.text.strip()
                    
                    # 종합 정보 생성
                    job_data = JobDataRemoteOK(
                        title=title, 
                        company_name=company, 
                        location=location, 
                        link=url, 
                        salary=salary, 
                        tags=tags,
                        posted_date=posted_date,
                        is_ad=is_ad
                    )
                    jobs_db.append(job_data.to_list())
                    
                except Exception as e:
                    logger.error(f"구직 항목 추출 중 오류 발생: {e}")
                    continue
                    
            logger.info(f"키워드 '{keyword}'에 대해 {len(jobs_db)}개 작업 찾음")
            return jobs_db
            
        except Exception as e:
            logger.error(f"HTML 파싱 중 오류 발생: {e}")
            return jobs_db
            
    def save_to_csv(self, keyword):
        """스크래핑한 구직 정보를 CSV 파일로 저장"""
        self.add_keywords_from_input(keyword)
        for keyword in self.keywords:
            try:
                logger.info(f"키워드 '{keyword}'에 대한 작업 스크래핑 중...")
                keyword_jobs = self.scrape_keyword(keyword)
                
                if not keyword_jobs:
                    logger.warning(f"키워드 '{keyword}'에 대한 작업을 찾을 수 없습니다")
                    continue
                    
                with open(f"remoteok_{keyword}_jobs.csv", mode="w", encoding="utf-8-sig") as file:
                    writer = csv.writer(file)
                    # 첫 번째 작업에서 JobData 인스턴스를 생성하여 헤더 가져오기
                    job_data = JobDataRemoteOK(
                        keyword_jobs[0][0], keyword_jobs[0][1], keyword_jobs[0][2], keyword_jobs[0][3]
                    )
                    writer.writerow(job_data.get_headers())
                    for job in keyword_jobs:
                        writer.writerow(job)
                        
                logger.info(f"키워드 '{keyword}'에 대한 {len(keyword_jobs)}개 작업이 CSV 파일에 저장되었습니다")
                
            except Exception as e:
                logger.error(f"CSV 저장 중 오류 발생 (키워드 '{keyword}'): {e}") 