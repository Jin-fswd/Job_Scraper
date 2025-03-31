"""
애플리케이션 전체에서 사용할 로깅 설정
"""
import logging
import os
from datetime import datetime

def setup_logger(name=None):
    """
    로거 설정 및 반환
    
    Args:
        name (str, optional): 로거 이름. 기본값은 None (루트 로거 사용)
        
    Returns:
        logging.Logger: 설정된 로거 인스턴스
    """
    # 로그 디렉토리 생성
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 로그 파일명에 날짜 포함
    log_file = os.path.join(log_dir, f"scraper_{datetime.now().strftime('%Y%m%d')}.log")
    
    # 로거 가져오기
    logger = logging.getLogger(name)
    
    # 이미 핸들러가 설정되어 있다면 추가 설정하지 않음
    if logger.handlers:
        return logger
        
    # 상위 로거로부터 메시지 전파 방지
    logger.propagate = False
    
    # 로그 레벨 설정
    logger.setLevel(logging.INFO)
    
    # 파일 핸들러 설정
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # 콘솔 핸들러 설정
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 포맷터 설정
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 핸들러 추가
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger 