# data_loader.py
import os
import logging
import requests
import shutil

def download_data_from_api(config, targets):
    """API를 통해 데이터를 다운로드하고 상세 결과 리스트를 반환합니다."""
    total_files = sum(len(devices) for date_map in targets.values() for devices in date_map.values())
    
    mode_info = f"(다운로드: {config.DOWNLOAD_MODE}, 오류 처리: {config.DOWNLOAD_ERROR_MODE})"
    logging.info(f"1. API를 통한 데이터 다운로드를 시작합니다. (총 {total_files}개 파일) {mode_info}")
    
    base_folder = config.SOURCE_DIR
    results = [] # 👈 모든 시도 결과를 담을 리스트
    current_file_count = 0

    if config.DOWNLOAD_MODE == 'OVERWRITE_ALL' and os.path.exists(base_folder):
        logging.info(f"  - [OVERWRITE_ALL 모드]: 기존 buslight 폴더를 모두 삭제합니다 -> {base_folder}")
        shutil.rmtree(base_folder)
    base_folder.mkdir(parents=True, exist_ok=True)

    for route, date_device_map in targets.items():
        route_folder = base_folder / str(route)
        
        if config.DOWNLOAD_MODE == 'OVERWRITE_ROUTE' and route_folder.exists():
            shutil.rmtree(route_folder)
        route_folder.mkdir(exist_ok=True)

        for date, device_list in date_device_map.items():
            for device in device_list:
                current_file_count += 1
                progress = f"({current_file_count}/{total_files}) "
                
                bus_number, mac, ctn, imei = device['차량번호'], device['MAC'], device['CTN'], device['IMEI']
                mac_sanitized = mac.replace(":", "")
                filename = f"{date}_{ctn}_{imei}_{mac_sanitized}.csv"
                file_path = route_folder / filename
                
                result_entry = {'차량번호': bus_number, 'route': route, 'date': date, 'mac': mac, 'ctn': ctn, 'imei': imei, 'filename': filename, 'filepath': None, 'status': '', 'reason': ''}

                if config.DOWNLOAD_MODE == 'SKIP_EXISTING' and file_path.exists():
                    logging.info(f"  - {progress}[SKIP 모드]: 파일이 이미 존재하여 건너뜁니다 -> {filename}")
                    result_entry.update({'status': 'Skipped', 'filepath': str(file_path)})
                    results.append(result_entry)
                    continue

                logging.info(f"  - {progress}다운로드 시도: 노선[{route}], 날짜[{date}], MAC[{mac}]")
                try:
                    payload = {'date': date, 'mac': mac, 'ctn': ctn, 'imei': imei}
                    response = requests.post(config.API_ENDPOINT, data=payload, timeout=30)
                    
                    if response.status_code != 200 or not response.content:
                        raise ConnectionError(f"API 응답 오류 (상태 코드: {response.status_code})")

                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    
                    logging.info(f"    -> 성공. 파일 저장: '{file_path}'")
                    result_entry.update({'status': 'Success', 'filepath': str(file_path)})

                except Exception as e:
                    error_msg = f"다운로드 중 예외 발생: {e}"
                    logging.warning(f"    -> {error_msg} (건너뜀).")
                    result_entry.update({'status': 'Failure', 'reason': str(e)})
                
                results.append(result_entry)

    logging.info("데이터 다운로드 시도 완료.\n")
    return results