import pandas as pd
import os
from datetime import datetime
from normality_check.data_processor import (
    check_file_existence, 
    task_check_single_day, 
    task_check_period
)
from config import REFERENCE_PATH, DEVICES_FILE, REPORT_FILE, CHECK_DATE,CHECK_PERIOD_DAYS

# --------------------------------------------------
# 사용자 입력 설정
# --------------------------------------------------
# 작업 1을 위한 설정

TARGET_DATE_TASK1 = CHECK_DATE
MIN_EXPOSURE_COUNT_TASK1 = 500

# 작업 2를 위한 설정
TARGET_DATE_TASK2 = CHECK_DATE
MAX_FAIL_DAYS = 3
MIN_EXPOSURE_COUNT_TASK2 = 500
# --------------------------------------------------

def analyze_yesterday_data_integrity(REPORT_PATH):
    
    
    # 고유한 보고서 폴더 이름 생성 및 경로 설정
    report_folder_name = f"{'analyze_data_integrity'}"
    report_folder_path = os.path.join(REPORT_PATH, report_folder_name)
    os.makedirs(report_folder_path, exist_ok=True)
    report_file_path = os.path.join(report_folder_path, REPORT_FILE)
    
    report_content = []
    task1_results_list = []
    task2_results_list = []
    
    print("보고서 작성을 시작합니다...")
    report_content.append(f"# 데이터 분석 보고서 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    # --------------------------------------------------
    # 1. nomality_check_devices.csv 로드 및 파일 존재 여부 확인
    # --------------------------------------------------
    print("1. 기기 정보 파일을 로드하고 리포트 파일 존재 여부를 확인합니다.")
    devices_file_path = os.path.join(REFERENCE_PATH, DEVICES_FILE)
    if not os.path.exists(devices_file_path):
        error_msg = f"오류: 기기 정보 파일 '{devices_file_path}'이(가) 존재하지 않습니다. 작업을 중단합니다."
        print(error_msg)
        report_content.append("## 1. 파일 존재 여부\n\n")
        report_content.append(f"- {error_msg}\n")
        with open(report_file_path, 'w', encoding='utf-8') as f:
            f.writelines(report_content)
        return

    device_data = pd.read_csv(devices_file_path)

    report_full_path = os.path.join(REPORT_PATH, 'reports')
    file_existence_df = check_file_existence(device_data, report_full_path)
    
    
    report_content.append("## 1. 파일 존재 여부\n\n")
    report_content.append("| 차량번호 | MAC | 파일이름 | 상태 |\n")
    report_content.append("|---|---|---|---|\n")
    for _, row in file_existence_df.iterrows():
        report_content.append(f"| {row['차량번호']} | {row['MAC']} | {row['파일이름']} | {row['상태']} |\n")
    
    # 존재하는 파일에 대해서만 작업 수행
    existing_files_df = file_existence_df[file_existence_df['상태'] == '존재함']
    
    if existing_files_df.empty:
        print("경고: 작업을 수행할 리포트 파일이 존재하지 않습니다.")
        report_content.append("\n**경고: 작업을 수행할 리포트 파일이 존재하지 않습니다.**\n")
        with open(report_file_path, 'w', encoding='utf-8') as f:
            f.writelines(report_content)
        return
        
    print(f"{len(existing_files_df)}개의 파일에 대해 작업을 수행합니다.\n")
    
    # --------------------------------------------------
    # 2. 작업 1: 특정 날짜 exposure_count 체크
    # --------------------------------------------------
    print("2. 작업 1 - 특정 날짜 exposure_count 체크를 시작합니다.")
    
    for _, row in existing_files_df.iterrows():
        result_text, result_data = task_check_single_day(row['경로'], TARGET_DATE_TASK1, MIN_EXPOSURE_COUNT_TASK1)
        task1_results_list.append(result_data)
        
    # '실패' 항목만 필터링
    filtered_task1_results = [result for result in task1_results_list if "실패" in result['결과']]

    report_content.append("\n## 2. 작업 1: 특정 날짜 exposure_count 체크 (실패 항목)\n\n")
    report_content.append(f"- 기준 날짜: `{TARGET_DATE_TASK1}`\n")
    report_content.append(f"- 최소 exposure_count: `{MIN_EXPOSURE_COUNT_TASK1}`\n\n")
    report_content.append("| 차량번호 | MAC | 결과 |\n")
    report_content.append("|---|---|---|\n")
    
    for result in filtered_task1_results:
        report_content.append(f"| {result['차량번호']} | {result['MAC']} | {result['결과']} |\n")


    
        
    # --------------------------------------------------
    # 3. 작업 2: 저조 기간 확인
    # --------------------------------------------------
    print("\n3. 작업 2 - 저조 기간 확인을 시작합니다.")
    
    for _, row in existing_files_df.iterrows():
        result_text, result_data = task_check_period(row['경로'], TARGET_DATE_TASK2, CHECK_PERIOD_DAYS, MAX_FAIL_DAYS, MIN_EXPOSURE_COUNT_TASK2)
        task2_results_list.append(result_data)

    # '실패' 항목만 필터링
    filtered_task2_results = [result for result in task2_results_list if "실패" in result['결과']]
    
    report_content.append("\n## 3. 작업 2: 저조 기간 확인 (실패 항목)\n\n")
    report_content.append(f"- 기준 날짜: `{TARGET_DATE_TASK2}`\n")
    report_content.append(f"- 검사 기간: `{CHECK_PERIOD_DAYS}`일\n")
    report_content.append(f"- 한계 기간: `{MAX_FAIL_DAYS}`일\n")
    report_content.append(f"- 최소 exposure_count: `{MIN_EXPOSURE_COUNT_TASK2}`\n\n")
    report_content.append("| 차량번호 | MAC | 결과 |\n")
    report_content.append("|---|---|---|\n")

    for result in filtered_task2_results:
        report_content.append(f"| {result['차량번호']} | {result['MAC']} | {result['결과']} |\n")
        
    # --------------------------------------------------
    # 4. CSV 보고서 생성
    # --------------------------------------------------
    print("\n4. CSV 보고서를 생성합니다.")
    df_task1 = pd.DataFrame(filtered_task1_results)
    df_task2 = pd.DataFrame(filtered_task2_results)
    
    csv_path_task1 = os.path.join(report_folder_path, 'report_task1.csv')
    csv_path_task2 = os.path.join(report_folder_path, 'report_task2.csv')
    
    df_task1.to_csv(csv_path_task1, index=False, encoding='utf-8-sig')
    df_task2.to_csv(csv_path_task2, index=False, encoding='utf-8-sig')
    
    report_content.append("\n## 4. 추가 보고서\n\n")
    report_content.append(f"- 작업 1에 대한 상세 결과는 [`report_task1.csv`](./report_task1.csv) 파일을 확인해주세요.\n")
    report_content.append(f"- 작업 2에 대한 상세 결과는 [`report_task2.csv`](./report_task2.csv) 파일을 확인해주세요.\n")
    
    print("\n보고서 작성을 완료했습니다.")
    print(f"결과는 '{report_folder_path}' 폴더 안의 '{REPORT_FILE}' 및 CSV 파일들을 확인해주세요.")
    
    # 최종 보고서 파일 저장
    with open(report_file_path, 'w', encoding='utf-8') as f:
        f.writelines(report_content)

