# Dynamic Job Scraper: Automating Job Search with Efficiency

## Project Overview

**Dynamic Job Scraper** is a tool designed to automatically collect and integrate job listings from various job sites. Looking for remote work opportunities or location-based positions? This scraper helps you save time and effort by managing job data in easy-to-use CSV files.

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Environment Variables](#environment-variables)
- [License](#license)
- [Contributing](#contributing)
- [Contact](#contact)

## Features

- **Multiple Keyword Search**: Search multiple keywords simultaneously using comma separation
- **Real-Time Scraping**: Collect job information in real-time from Wanted and We Work Remotely
- **CSV Export**: Save search results as CSV files for easy sharing and analysis
- **User-Friendly Interface**: Clean and intuitive web interface built with PicoCSS
- **In-Memory Caching**: Cache search results in memory for quick access
- **Auto Scrolling**: Collect more job listings through automatic scrolling on Wanted site

## Project Structure

```
dynamic-job-scraper/
│
├── extractors/
│   ├── job_data.py        # Base job data class
│   ├── job_data_wwr.py    # WWR specific job data class
│   ├── wanted_job_search.py # Wanted scraper
│   └── wwr.py             # We Work Remotely scraper
│
├── templates/
│   ├── export.html        # Export page
│   ├── home.html          # Homepage
│   └── search.html        # Search results page
│
├── static/
│   └── images/            # Image files
│
├── utils/
│   └── logger.py          # Logging configuration
│
├── main.py                # Flask application
├── requirements.txt       # Dependencies
├── .env.example          # Environment variables example
└── README.md             # Project documentation
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Steps

1. Clone repository:

   ```bash
   git clone https://github.com/minhosong88/dynamic-job-scraper.git
   cd dynamic-job-scraper
   ```

2. Create and activate virtual environment:

   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. Install required packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Install Playwright browsers:
   ```bash
   playwright install
   ```

## Usage

1. Start Flask server:

   ```bash
   python main.py
   ```

2. Access http://localhost:8080 in your web browser

3. Enter keywords in the search box (separate multiple keywords with commas)
   Example: python, java, javascript

4. View results and export to CSV file

## Environment Variables

Create a `.env` file with the following settings:

```bash
# Scraper headless mode configuration
# true = Run in background (suitable for server environment)
# false = Show browser window (for development and debugging)
SCRAPER_HEADLESS=false
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

If you're interested in improving the project, feel free to open an issue or submit a pull request. Your contributions are welcome!

## Contact

- **Name**: Minho Song
- **Email**: [hominsong@naver.com](mailto:hominsong@naver.com)
- **GitHub**: [minhosong88](https://github.com/minhosong88)

=======================================================================================

# Dynamic Job Scraper: 효율적인 구직 정보 자동화 도구

## 프로젝트 개요

**Dynamic Job Scraper**는 다양한 구직 사이트에서 자동으로 채용 정보를 수집하고 통합하는 도구입니다. 원격 근무 기회나 지역 기반 채용 정보를 찾고 계신가요? 이 스크래퍼를 통해 시간과 노력을 절약하면서 구직 데이터를 CSV 파일로 쉽게 관리할 수 있습니다.

## 목차

- [기능](#기능)
- [프로젝트 구조](#프로젝트-구조)
- [설치 방법](#설치-방법)
- [사용 방법](#사용-방법)
- [환경 변수](#환경-변수)
- [라이선스](#라이선스)
- [기여하기](#기여하기)
- [연락처](#연락처)

## 기능

- **다중 키워드 검색**: 쉼표로 구분된 여러 키워드로 동시에 검색 가능
- **실시간 스크래핑**: Wanted와 We Work Remotely에서 실시간으로 채용 정보 수집
- **CSV 내보내기**: 검색 결과를 CSV 파일로 저장하여 쉽게 공유 및 분석
- **사용자 친화적 인터페이스**: PicoCSS로 구현된 깔끔하고 직관적인 웹 인터페이스
- **인메모리 캐싱**: 검색 결과를 메모리에 캐싱하여 빠른 접근 가능
- **자동 스크롤링**: Wanted 사이트에서 자동 스크롤을 통한 더 많은 채용 정보 수집

## 프로젝트 구조

```
dynamic-job-scraper/
│
├── extractors/
│   ├── job_data.py        # 기본 구직 정보 클래스
│   ├── job_data_wwr.py    # WWR 전용 구직 정보 클래스
│   ├── wanted_job_search.py # Wanted 스크래퍼
│   └── wwr.py             # We Work Remotely 스크래퍼
│
├── templates/
│   ├── export.html        # 내보내기 페이지
│   ├── home.html          # 홈페이지
│   └── search.html        # 검색 결과 페이지
│
├── static/
│   └── images/            # 이미지 파일
│
├── utils/
│   └── logger.py          # 로깅 설정
│
├── main.py                # Flask 애플리케이션
├── requirements.txt       # 의존성 패키지
├── .env.example          # 환경 변수 예제
└── README.md             # 프로젝트 문서
```

## 설치 방법

### 필수 요구사항

- Python 3.8 이상
- pip (Python 패키지 관리자)

### 설치 단계

1. 저장소 클론:

   ```bash
   git clone https://github.com/minhosong88/dynamic-job-scraper.git
   cd dynamic-job-scraper
   ```

2. 가상환경 생성 및 활성화:

   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. 필수 패키지 설치:

   ```bash
   pip install -r requirements.txt
   ```

4. Playwright 브라우저 설치:
   ```bash
   playwright install
   ```

## 사용 방법

1. Flask 서버 실행:

   ```bash
   python main.py
   ```

2. 웹 브라우저에서 http://localhost:8080 접속

3. 검색창에 키워드 입력 (쉼표로 구분하여 여러 키워드 입력 가능)
   예: python, java, javascript

4. 검색 결과 확인 및 CSV 파일로 내보내기

## 환경 변수

`.env` 파일을 생성하여 다음 설정을 지정할 수 있습니다:

```bash
# 스크래퍼 헤드리스 모드 설정
# true = 백그라운드 실행 (서버 환경에 적합)
# false = 브라우저 창 표시 (개발 및 디버깅용)
SCRAPER_HEADLESS=false
```

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 기여하기

프로젝트 개선에 관심이 있으시다면 언제든 이슈를 등록하거나 풀 리퀘스트를 보내주세요. 여러분의 기여를 환영합니다!

## 연락처

- **이름**: 송민호
- **이메일**: [hominsong@naver.com](mailto:hominsong@naver.com)
- **GitHub**: [minhosong88](https://github.com/minhosong88)
