# main.py
import logging
import time
import pandas as pd
import config
from utils import setup_directories_and_samples, prepare_download_targets, scan_local_files # 👈 scan_local_files 임포트
from data_loader import download_data_from_api
from db_connector import fetch_operation_logs
from reporter import generate_report

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    start_time = time.time()

    try:
        setup_directories_and_samples(config)
        
        # 1. 다운로드 대상 목록 준비
        download_targets = prepare_download_targets(config)
        
        # 2. DB에서 운영 로그 조회
        dates_df = pd.read_csv(config.DATE_FILE)
        operation_logs_df = fetch_operation_logs(config, dates_df['date'].tolist())

        # ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼ 이 부분을 추가하세요 ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼
        print("\n--- DB 조회 결과 확인 ---")
        print(operation_logs_df.head())
        print(f"조회된 총 로그 수: {len(operation_logs_df)} 개")
        print("------------------------\n")
        # ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲
        
        # 3. 설정에 따라 다운로드 또는 로컬 스캔 실행
        if config.DOWNLOAD_ENABLED:
            logging.info(">> 다운로드 모드로 실행합니다.")
            results = download_data_from_api(config, download_targets)
        else:
            logging.info(">> 로컬 분석 모드로 실행합니다 (다운로드 건너뜀).")
            results = scan_local_files(config, download_targets)

        # 4. 리포트 생성
        if results:
            end_time = time.time()
            duration = end_time - start_time
            generate_report(results, operation_logs_df, config, duration)
        
        logging.info("모든 프로세스가 완료되었습니다.")

    except (FileNotFoundError, ValueError, ConnectionError) as e:
        logging.error(f"스크립트 실행 중단: {e}")