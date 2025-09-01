# reporter.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import logging
import re
import holidays # 공휴일 라이브러리 임포트

# Matplotlib 한글 폰트 설정 (없을 경우 기본 폰트로 동작)
try:
    plt.rcParams['font.family'] = 'Malgun Gothic'
except:
    pass
plt.rcParams['axes.unicode_minus'] = False

def get_regular_exposure_count(filepath):
    """
    CSV 파일에서 'watched_time' > 1 인 라인 수를 계산하여 '정규노출수'를 반환합니다.
    """
    if not filepath or pd.isna(filepath): return 0
    try:
        df = pd.read_csv(filepath, low_memory=False)
        # 'watched_time' 컬럼이 없으면 0을 반환
        if 'watched_time' not in df.columns:
            logging.warning(f"'watched_time' 컬럼 없음: {filepath}")
            return 0
        
        # 'watched_time'을 숫자로 변환 (변환 불가 시 NaN으로 처리)
        watched_time_numeric = pd.to_numeric(df['watched_time'], errors='coerce')
        
        # NaN이 아닌 값 중에서 1보다 큰 라인의 수를 계산
        count = watched_time_numeric[watched_time_numeric > 1].count()
        return count

    except (FileNotFoundError, pd.errors.EmptyDataError):
        return 0
    except Exception as e:
        logging.warning(f"정규노출수 계산 오류 ({filepath}): {e}")
        return 0

def generate_report(results, operation_logs_df, config, duration_seconds):
    """정규노출수 및 공휴일 정보가 포함된 리포트를 생성합니다."""
    if not results:
        logging.warning("분석할 다운로드 결과가 없어 리포트를 생성하지 않습니다.")
        return

    # 1. 고유한 리포트 폴더 생성
    now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    report_dir = config.OUTPUT_DIR / now
    graphs_dir = report_dir / "graphs"
    reports_dir = report_dir / "reports"
    graphs_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(exist_ok=True)
    logging.info(f"리포트가 다음 폴더에 저장됩니다: {report_dir}")

    # 2. 결과 데이터와 운영 로그 병합 및 가공
    summary_df = pd.DataFrame(results)
    print('summary_df',summary_df)
    merged_df = pd.merge(summary_df, operation_logs_df, on=['차량번호', 'date'], how='left')
    merged_df['운영여부'].fillna('판단실패', inplace=True)
    
    logging.info("다운로드된 파일들의 정규노출수를 계산합니다...")
    merged_df['exposure_count'] = merged_df.apply(
        lambda row: get_regular_exposure_count(row['filepath']) if row['status'] in ['Success', 'Skipped'] else 0,
        axis=1
    )
    
    merged_df['status_code'] = merged_df['status'].apply(lambda s: 1 if s in ['Success', 'Skipped'] else 0)
    merged_df['operation_code'] = merged_df['운영여부'].map({'운영': 1, '미운영': 0.5, '판단실패': 0})
    
    # 3. '판단실패' 목록 로그 저장
    failure_log_df = merged_df[merged_df['운영여부'] == '판단실패']
    if not failure_log_df.empty:
        failure_log_path = report_dir / "judgement_failures.csv"
        failure_log_df[['차량번호', 'date']].to_csv(failure_log_path, index=False, encoding='utf-8-sig')
        logging.info(f"-> '판단실패' 목록 저장 완료: {failure_log_path}")

    # 4. 피벗 테이블 생성 및 저장
    try:
        status_pivot = merged_df.pivot_table(index='date', columns='mac', values='status_code', fill_value=0)
        status_pivot.to_csv(report_dir / "download_status.csv", encoding='utf-8-sig')
        logging.info(f"-> 상태 피벗 테이블 저장 완료: {report_dir / 'download_status.csv'}")

        exposure_pivot = merged_df.pivot_table(index='date', columns='mac', values='exposure_count', fill_value=0)
        exposure_pivot.to_csv(report_dir / "exposure_count.csv", encoding='utf-8-sig')
        logging.info(f"-> 정규노출수 피벗 테이블 저장 완료: {report_dir / 'exposure_count.csv'}")
    except Exception as e:
        logging.error(f"피벗 테이블 생성 중 오류 발생: {e}")

    # 5. 기기별 CSV 리포트 및 그래프 생성
    logging.info(f"각 기기별 CSV 리포트 및 그래프를 생성합니다...")
    kr_holidays = holidays.KR() # 대한민국 공휴일 객체 생성
    
    unique_macs = merged_df['mac'].unique()
    for mac_id in unique_macs:
        device_df = merged_df[merged_df['mac'] == mac_id].sort_values('date')
        
        if device_df.empty:
            continue
            
        bus_number = device_df['차량번호'].iloc[0]
        sanitized_bus_number = re.sub(r'[^a-zA-Z0-9가-힣]', '', bus_number)
        sanitized_mac = re.sub(r'[^a-zA-Z0-9]', '', mac_id)
        
        # 기기별 CSV 저장
        report_cols = ['date', 'status', 'exposure_count', '운영여부']
        device_df[report_cols].to_csv(reports_dir / f"{sanitized_bus_number}_{sanitized_mac}.csv", index=False, encoding='utf-8-sig')

        # 기기별 그래프 생성
        fig, ax1 = plt.subplots(figsize=(16, 8))

        # 그래프 1: 정규노출수 (좌측 Y축)
        sns.lineplot(x='date', y='exposure_count', data=device_df, ax=ax1, marker='o', label='정규노출수', color='dodgerblue', errorbar=None)
        ax1.set_ylabel('정규노출수', color='dodgerblue', fontsize=12)
        ax1.tick_params(axis='y', labelcolor='dodgerblue')
        ax1.set_xlabel('날짜', fontsize=12)
        ax1.set_ylim(bottom=0)
        ax1.grid(True, linestyle='--', alpha=0.6)

        # 그래프 2: 운영여부 (우측 Y축)
        ax2 = ax1.twinx()
        sns.lineplot(x='date', y='operation_code', data=device_df, ax=ax2, marker='s', linestyle='--', label='운영여부 (1:운영, 0.5:미운영, 0:실패)', color='red', alpha=0.7, errorbar=None)
        ax2.set_ylabel('운영 여부', color='red', fontsize=12)
        ax2.tick_params(axis='y', labelcolor='red')
        ax2.set_ylim(-0.1, 1.1)
        ax2.set_yticks([0, 0.5, 1])
        ax2.set_yticklabels(['판단실패', '미운영', '운영'])
        
        # 주말 및 공휴일 음영 및 텍스트 추가
        for i, date_str in enumerate(device_df['date']):
            date_obj = pd.to_datetime(date_str)
            weekday = date_obj.weekday()
            holiday_name = kr_holidays.get(date_obj)

            if holiday_name and weekday != 6: # 공휴일 (일요일 제외)
                ax1.axvspan(i - 0.5, i + 0.5, color='red', alpha=0.1)
                ax1.text(i, ax1.get_ylim()[1]*0.95, holiday_name, ha='center', va='top', fontsize=10, color='darkred', weight='bold')
            elif weekday == 6: # 일요일
                ax1.axvspan(i - 0.5, i + 0.5, color='red', alpha=0.1)
            elif weekday == 5: # 토요일
                ax1.axvspan(i - 0.5, i + 0.5, color='blue', alpha=0.1)

        ax1.set_title(f"일별 정규노출수 및 운영 상태 ({bus_number} / {mac_id})", fontsize=16, pad=20)
        ax1.tick_params(axis='x', rotation=45, labelsize=10)
        fig.legend(loc="upper right", bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)
        fig.tight_layout()
        plt.savefig(graphs_dir / f"exposure_count_{sanitized_bus_number}_{sanitized_mac}.png")
        plt.close(fig)
        
    logging.info(f"-> 총 {len(unique_macs)}개의 기기별 CSV 및 그래프 저장 완료.")

    # 6. 메타 정보 요약 파일 생성
    total_attempts = len(summary_df)
    success_count = (summary_df['status'] == 'Success').sum()
    skipped_count = (summary_df['status'] == 'Skipped').sum()
    failure_count = (summary_df['status'] == 'Failure').sum()
    total_exposures = merged_df['exposure_count'].sum()
    
    summary_content = f"""
# 실행 결과 요약 (메타 정보)
- 리포트 생성 시간: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 총 실행 시간: {duration_seconds:.2f} 초
---
## 다운로드 통계
- 총 시도 파일 수: {total_attempts} 개
- 성공: {success_count} 개
- 건너뜀 (이미 파일 존재 시): {skipped_count} 개
- 실패: {failure_count} 개
---
## 데이터 통계
- 총 수집된 정규노출수: {int(total_exposures)} 건
"""
    summary_path = report_dir / "summary.md"
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary_content)
    logging.info(f"-> 메타 정보 요약 파일 저장 완료: {summary_path}")

    return report_dir