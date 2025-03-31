import logging
import os
import time
from extractors.remoteok import RemoteOKJobSearch

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_remoteok_manual():
    """캡차 수동 해결 모드로 RemoteOK 스크래퍼 테스트"""
    keyword = "python"
    logger.info(f"RemoteOK 테스트 시작 (수동 캡차 해결 모드): 키워드 '{keyword}'")
    
    # 스크래퍼 생성
    remoteok = RemoteOKJobSearch()
    
    # 수동 캡차 해결 모드로 스크래핑
    jobs = remoteok.scrape_keyword(keyword, manual_captcha=True)
    
    logger.info(f"검색 결과: {len(jobs)}개 작업 찾음")
    
    # 결과 출력
    if jobs:
        logger.info("첫 번째 5개 작업:")
        for i, job in enumerate(jobs[:5], 1):
            logger.info(f"작업 {i}: {job}")
        
        # CSV 파일로 저장
        try:
            import csv
            csv_filename = f"remoteok_{keyword}_manual_jobs.csv"
            with open(csv_filename, mode="w", encoding="utf-8-sig", newline='') as file:
                writer = csv.writer(file)
                
                # 헤더 작성
                from extractors.job_data_remoteok import JobDataRemoteOK
                job_data = JobDataRemoteOK(
                    title=jobs[0][0], 
                    company_name=jobs[0][1], 
                    location=jobs[0][2], 
                    link=jobs[0][3],
                    salary=jobs[0][4],
                    posted_date=jobs[0][5]
                )
                writer.writerow(job_data.get_headers())
                
                # 데이터 작성
                for job in jobs:
                    writer.writerow(job)
                
                logger.info(f"검색 결과가 {csv_filename} 파일에 저장되었습니다.")
        except Exception as e:
            logger.error(f"CSV 파일 저장 중 오류 발생: {e}")
    else:
        logger.warning("작업을 찾지 못했습니다.")
    
    return jobs

if __name__ == "__main__":
    print("\n" + "="*60)
    print("RemoteOK 직업 스크래퍼 (수동 캡차 해결 모드)")
    print("이 스크립트는 캡차가 발견되면 사용자의 입력을 기다립니다.")
    print("브라우저 창에서 캡차를 해결한 후 콘솔로 돌아와 Enter 키를 누르세요.")
    print("="*60 + "\n")
    
    input("시작하려면 Enter 키를 누르세요...")
    test_remoteok_manual() 