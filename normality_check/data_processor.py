# data_processor.py
import os
import pandas as pd

def check_file_existence(device_data, reports_path):
    """
    nomality_check_devices.csv의 기기 정보와 reports 폴더 내의 파일 존재 여부를 확인합니다.
    """
    file_status = []
    
    # 보고서 폴더가 존재하지 않으면 생성
    if not os.path.exists(reports_path):
        os.makedirs(reports_path)
    
    for _, row in device_data.iterrows():
        # 파일명은 '차량번호_MAC.csv' 형식입니다.
        file_name = f"{row['차량번호']}_{row['MAC']}.csv"
        file_path = os.path.join(reports_path, file_name)
        
        status = '존재함' if os.path.exists(file_path) else '존재하지 않음'
        file_status.append({
            '차량번호': row['차량번호'],
            'MAC': row['MAC'],
            '파일이름': file_name,
            '상태': status,
            '경로': file_path
        })
        
    return pd.DataFrame(file_status)

def task_check_single_day(file_path, target_date, min_exposure_count):
    """
    작업 1: 특정 날짜에 운영 여부와 exposure_count를 확인하고 결과를 반환합니다.
    - '운영' 상태가 아니면 리포트에 포함하지 않습니다.
    """
    result_data = {
        '차량번호': os.path.basename(file_path).split('_')[0],
        'MAC': os.path.basename(file_path).split('_')[1].replace('.csv', ''),
        '기준_날짜': target_date,
        '최소_exposure_count': min_exposure_count,
        '결과': '',
        'exposure_count': None,
        '운영여부': None
    }
    
    try:
        df = pd.read_csv(file_path)
        df['date'] = pd.to_datetime(df['date'])
        
        target_data = df[df['date'] == pd.to_datetime(target_date)]
        
        if target_data.empty:
            result_data['결과'] = "해당 날짜 데이터 없음"
            return "해당 날짜 데이터 없음", result_data
            
        row = target_data.iloc[0]
        result_data['exposure_count'] = row['exposure_count']
        result_data['운영여부'] = row['운영여부']
        
        is_operational = row['운영여부'] == '운영'
        
        if not is_operational:
            result_data['결과'] = f"분석 제외 - '운영' 상태 아님 ({row['운영여부']})"
            return result_data['결과'], result_data
            
        # '운영' 상태일 경우에만 기준치 체크
        if row['exposure_count'] >= min_exposure_count:
            result_data['결과'] = f"통과 - '운영' 중, exposure_count: {row['exposure_count']}"
        else:
            result_data['결과'] = f"실패 - '운영' 중, exposure_count가 기준치({min_exposure_count}) 미달 ({row['exposure_count']})"
            
        return result_data['결과'], result_data
            
    except FileNotFoundError:
        result_data['결과'] = "파일 없음"
        return "파일 없음", result_data
    except Exception as e:
        result_data['결과'] = f"데이터 처리 중 오류 발생: {e}"
        return result_data['결과'], result_data

def task_check_period(file_path, target_date, check_period_days, max_fail_days, min_exposure_count):
    """
    작업 2: 특정 날짜부터 검사 기간 동안 exposure_count가 낮은 날이 한계 기간 개수 이상인지 확인하고 결과를 반환합니다.
    - '운영' 상태이면서 기준치를 만족하지 않는 경우만 실패 일수에 포함됩니다.
    """
    result_data = {
        '차량번호': os.path.basename(file_path).split('_')[0],
        'MAC': os.path.basename(file_path).split('_')[1].replace('.csv', ''),
        '기준_날짜': target_date,
        '검사_기간_일': check_period_days,
        '한계_기간_일': max_fail_days,
        '최소_exposure_count': min_exposure_count,
        '결과': '',
        '미달_일수': None
    }
    
    try:
        df = pd.read_csv(file_path)
        df['date'] = pd.to_datetime(df['date'])
        
        target_dt = pd.to_datetime(target_date)
        start_date = target_dt - pd.DateOffset(days=check_period_days)
        
        period_data = df[(df['date'] > start_date) & (df['date'] <= target_dt)]
        
        if period_data.empty:
            result_data['결과'] = "해당 기간 데이터 없음"
            return "해당 기간 데이터 없음", result_data

        # '운영' 상태이면서 exposure_count가 기준치 미달인 날만 카운트
        low_count_days = period_data[
            (period_data['exposure_count'] < min_exposure_count) &
            (period_data['운영여부'] == '운영')
        ]
        result_data['미달_일수'] = len(low_count_days)
        
        if len(low_count_days) >= max_fail_days:
            result_data['결과'] = f"실패 - 운영 중 기준치({min_exposure_count}) 미달 일수: {len(low_count_days)}일 (한계기간 {max_fail_days}일 초과)"
        else:
            result_data['결과'] = f"통과 - 운영 중 기준치({min_exposure_count}) 미달 일수: {len(low_count_days)}일"
            
        return result_data['결과'], result_data
            
    except FileNotFoundError:
        result_data['결과'] = "파일 없음"
        return "파일 없음", result_data
    except Exception as e:
        result_data['결과'] = f"데이터 처리 중 오류 발생: {e}"
        return result_data['결과'], result_data
