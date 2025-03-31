import logging
import os
import time
from extractors.remoteok import RemoteOKJobSearch

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_remoteok():
    """RemoteOK 스크래퍼 테스트"""
    keyword = "python"
    logger.info(f"RemoteOK 테스트 시작: 키워드 '{keyword}'")
    
    # RemoteOKJobSearch에 캡차 처리 메서드 추가
    class RemoteOKJobSearchWithCaptchaHandler(RemoteOKJobSearch):
        def run_playwright(self, url, scroll_count=4, scroll_delay=5, retry_count=2, use_proxy=False):
            """캡차 인식 시 수동 입력 대기 기능이 추가된 Playwright 실행 메서드"""
            logger.info(f"RemoteOK 웹사이트 접속 중 (캡차 처리 포함): {url}")
            
            for attempt in range(retry_count + 1):
                try:
                    with sync_playwright() as p:
                        # 브라우저 및 컨텍스트 설정 (기존 코드와 동일)
                        browser = p.chromium.launch(headless=False)
                        page = browser.new_page()
                        
                        # User-Agent와 추가적인 헤더 설정
                        page.set_extra_http_headers({
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
                            'Accept-Language': 'en-US,en;q=0.9',
                            'Referer': 'https://www.google.com/'
                        })
                        
                        # 사이트 방문
                        page.goto(url)
                        time.sleep(3)  # 초기 로딩 대기
                        
                        # 캡차 확인
                        page_content = page.content().lower()
                        if "captcha" in page_content or "robot" in page_content or "cloudflare" in page_content:
                            logger.warning(f"캡차 또는 로봇 체크 감지! 시도 {attempt+1}/{retry_count+1}")
                            
                            # 캡차 화면 저장
                            screenshot_path = f"captcha_detected_{attempt}.png"
                            page.screenshot(path=screenshot_path)
                            logger.info(f"캡차 화면이 {screenshot_path}로 저장되었습니다")
                            
                            # 사용자에게 캡차 해결 요청
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
                                continue
                            else:
                                logger.info("캡차가 성공적으로 해결되었습니다!")
                        
                        # 스크롤 다운으로 더 많은 구직 정보 로드
                        for i in range(scroll_count):
                            logger.info(f"스크롤 다운 {i+1}/{scroll_count}")
                            page.keyboard.down('End')
                            time.sleep(scroll_delay)
                        
                        # 페이지 콘텐츠 가져오기
                        content = page.content()
                        browser.close()
                        logger.info("페이지 콘텐츠 로드 완료")
                        return content
                        
                except Exception as e:
                    logger.error(f"Playwright 실행 중 오류 발생: {e}")
                    if attempt < retry_count:
                        logger.info(f"5초 후 재시도...")
                        time.sleep(5)
                        continue
                    else:
                        return None
            
            return None
    
    # 캡차 처리가 가능한 스크래퍼 생성
    remoteok = RemoteOKJobSearchWithCaptchaHandler()
    jobs = remoteok.scrape_keyword(keyword)
    
    logger.info(f"검색 결과: {len(jobs)}개 작업 찾음")
    
    # 결과 출력
    if jobs:
        logger.info("첫 번째 5개 작업:")
        for i, job in enumerate(jobs[:5], 1):
            logger.info(f"작업 {i}: {job}")
    else:
        logger.warning("작업을 찾지 못했습니다.")
    
    return jobs

if __name__ == "__main__":
    test_remoteok() 