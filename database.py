"""
인메모리 데이터베이스 구현을 위한 모듈
"""
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

class Database:
    """
    간단한 인메모리 키-값 데이터베이스 클래스
    """
    def __init__(self):
        """데이터베이스 초기화"""
        self._data = {}
        logger.info("인메모리 데이터베이스 초기화됨")
    
    def __getitem__(self, key):
        """키에 해당하는 값 가져오기"""
        return self._data.get(key, [])
    
    def __setitem__(self, key, value):
        """키-값 쌍 저장"""
        self._data[key] = value
        logger.info(f"키 '{key}'에 {len(value)}개 항목 저장됨")
    
    def __contains__(self, key):
        """키가 데이터베이스에 있는지 확인"""
        return key in self._data
    
    def clear(self):
        """모든 데이터 삭제"""
        self._data = {}
        logger.info("데이터베이스 초기화됨")
    
    def keys(self):
        """모든 키 목록 반환"""
        return self._data.keys()
    
    def values(self):
        """모든 값 목록 반환"""
        return self._data.values()
    
    def items(self):
        """모든 키-값 쌍 반환"""
        return self._data.items()
    
    def get(self, key, default=None):
        """키에 해당하는 값 가져오기 (기본값 지정 가능)"""
        return self._data.get(key, default) 