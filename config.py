# config.py
from pathlib import Path

# --- 기본 경로 설정 ---
BASE_DIR = Path(__file__).resolve().parent
REFERENCE_DIR = BASE_DIR / "data" / "reference"
SOURCE_DIR = BASE_DIR / "data" / "raw" / "buslight"
OUTPUT_DIR = BASE_DIR / "output"

# --- 입력 파일 경로 ---
DEVICE_FILE = REFERENCE_DIR / "devices.csv"
DATE_FILE = REFERENCE_DIR / "dates.csv"

# --- API 및 다운로드 설정 ---
API_ENDPOINT = "https://api.addd.co.kr/csv-file/download"

# ===============================================================
# ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼ 실행 모드 설정 (신규 추가 및 수정) ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼
# ===============================================================
# True: API를 통해 데이터를 다운로드합니다.
# False: 다운로드를 건너뛰고 'data/raw/buslight'에 있는 기존 파일로만 분석/리포트를 실행합니다.
DOWNLOAD_ENABLED = False

# DOWNLOAD_ENABLED가 True일 때만 아래 설정이 의미가 있습니다.
# 'SKIP_EXISTING' : 파일이 이미 존재하면 다운로드를 건너뜁니다.
# 'OVERWRITE_ALL' : 기존 데이터를 모두 지우고 항상 새로 다운로드합니다.
DOWNLOAD_MODE = 'OVERWRITE_ALL'

DOWNLOAD_ERROR_MODE = 'continue'

# ===============================================================
# ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼ DB 및 SSH 접속 정보 (여기를 채워주세요) ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼
# ===============================================================
SSH_HOST = '175.45.194.216'          # 예: 123.45.67.89
SSH_PORT = 22                       # SSH 포트
SSH_USERNAME = 'root'  # SSH 접속 유저명
SSH_PASSWORD = 'M6bdM*Tc!H5?h'  # SSH 비밀번호

DB_HOST = '192.168.6.6'               # 보통 localhost (127.0.0.1)
DB_PORT = 3306                      # DB 포트
DB_USERNAME = 'addd'    # DB 유저명
DB_PASSWORD = '!@addd1004'    # DB 비밀번호
DB_NAME = 'bus_operation_logs'            # 데이터베이스 이름
# ===============================================================