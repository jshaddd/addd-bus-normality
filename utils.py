# utils.py
import pandas as pd
import logging

def setup_directories_and_samples(config):
    """프로젝트 폴더와 샘플 파일을 준비합니다."""
    logging.info("프로젝트 구조 및 샘플 파일 준비 중...")
    config.REFERENCE_DIR.mkdir(parents=True, exist_ok=True)
    config.SOURCE_DIR.mkdir(parents=True, exist_ok=True)

    # 샘플 기기 파일 생성
    device_csv_content = """차량번호,노선코드,노선명,CTN,IMEI,MAC,설치등록일시,최종수정일시
서울74사1599,104000014,40,01236249809,86301807354296,68:ED:A4:85:D8:FC,,
서울74사5025,104000014,40,01236258954,86301807354646,68:ED:A4:85:DC:52,,
서울74사3483,100100549,100,01236244698,86301807354258,68:ED:A4:85:D7:20,,
서울74사6357,100100549,100,01236243669,86301807354250,68:ED:A4:85:DE:78,,"""
    if not config.DEVICE_FILE.exists():
        with open(config.DEVICE_FILE, 'w', encoding='utf-8-sig') as f:
            f.write(device_csv_content)
        logging.info(f"샘플 기기 파일 생성: {config.DEVICE_FILE}")

    # 샘플 날짜 파일 생성
    date_csv_content = "date\n2025-08-20\n2025-08-21"
    if not config.DATE_FILE.exists():
        with open(config.DATE_FILE, 'w', encoding='utf-8') as f:
            f.write(date_csv_content)
        logging.info(f"샘플 날짜 파일 생성: {config.DATE_FILE}")

def prepare_download_targets(config):
    """CSV 파일들을 읽어 다운로드 대상 목록 딕셔너리를 생성하여 반환합니다."""
    logging.info("입력 파일(기기, 날짜)을 읽어 다운로드 대상을 구성합니다.")
    try:
        devices_df = pd.read_csv(config.DEVICE_FILE)
        dates_df = pd.read_csv(config.DATE_FILE)
    except FileNotFoundError as e:
        logging.error(f"필수 입력 파일이 없습니다: {e}")
        raise
        
    targets = {}
    # ✅ '노선명'을 필수 컬럼에 추가
    required_cols = ['차량번호', '노선명', 'CTN', 'IMEI', 'MAC']
    for col in required_cols:
        if col not in devices_df.columns:
            raise ValueError(f"기기 파일에 필수 컬럼이 없습니다: '{col}'")

    device_info_df = devices_df[required_cols]

    for _, row in device_info_df.iterrows():
        # ✅ '노선코드' 대신 '노선명'을 키로 사용
        route_name = row['노선명'] 
        device_info = {'차량번호': row['차량번호'], 'MAC': row['MAC'], 'CTN': str(row['CTN']), 'IMEI': str(row['IMEI'])}
        
        if route_name not in targets:
            targets[route_name] = {}
        
        for date in dates_df['date']:
            if date not in targets[route_name]:
                targets[route_name][date] = []
            targets[route_name][date].append(device_info)
    
    logging.info("다운로드 대상 구성 완료.")
    return targets


def scan_local_files(config, targets):
    """로컬 디렉토리를 스캔하여 다운로드 결과 리스트를 생성합니다 (로컬 분석 모드)."""
    logging.info("로컬 파일 스캔을 시작합니다 (다운로드 건너뜀).")
    results = []
    base_folder = config.SOURCE_DIR
    total_targets = sum(len(devices) for date_map in targets.values() for devices in date_map.values())
    current_file_count = 0

    for route, date_device_map in targets.items():
        route_folder = base_folder / str(route)
        for date, device_list in date_device_map.items():
            for device in device_list:
                current_file_count += 1
                progress = f"({current_file_count}/{total_targets}) "

                bus_number, mac, ctn, imei = device['차량번호'], device['MAC'], device['CTN'], device['IMEI']
                mac_sanitized = mac.replace(":", "")
                filename = f"{date}_{ctn}_{imei}_{mac_sanitized}.csv"
                file_path = route_folder / filename

                result_entry = {
                    '차량번호': bus_number, 'route': route, 'date': date, 'mac': mac, 
                    'ctn': ctn, 'imei': imei, 'filename': filename, 
                    'filepath': None, 'status': '', 'reason': ''
                }

                if file_path.exists():
                    logging.info(f"  - {progress}파일 발견: {filename}")
                    result_entry.update({'status': 'Success', 'filepath': str(file_path)})
                else:
                    logging.info(f"  - {progress}파일 없음: {filename}")
                    result_entry.update({'status': 'Failure', 'reason': 'File not found locally'})
                
                results.append(result_entry)
                
    logging.info("로컬 파일 스캔 완료.")
    return results