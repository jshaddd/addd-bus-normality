# db_connector.py
import pandas as pd
import pymysql
from sshtunnel import SSHTunnelForwarder
import logging

def fetch_operation_logs(config, dates_to_fetch):
    """SSH 터널링으로 DB에 접속하여 운영 로그를 가져와 '운영 여부'를 판단합니다."""
    logging.info("DB에서 버스 운영 로그 조회를 시작합니다...")
    
    try:
        with SSHTunnelForwarder(
            (config.SSH_HOST, config.SSH_PORT),
            ssh_username=config.SSH_USERNAME,
            ssh_password=config.SSH_PASSWORD,
            remote_bind_address=(config.DB_HOST, config.DB_PORT)
        ) as tunnel:
            logging.info("SSH 터널이 성공적으로 생성되었습니다!")
            
            connection = pymysql.connect(
                host='127.0.0.1',
                port=tunnel.local_bind_port,
                user=config.DB_USERNAME,
                passwd=config.DB_PASSWORD,
                db=config.DB_NAME,
                charset='utf8'
            )
            logging.info("데이터베이스에 성공적으로 접속했습니다!")

            # 조회할 날짜들을 튜플 형태로 변환
            dates_tuple = tuple(dates_to_fetch)
            query = f"""
                SELECT 
                    bus_number, 
                    operation_date, 
                    is_morning_operating, 
                    is_lunch_operating, 
                    is_dinner_operating 
                FROM 
                    bus_operation_logs 
                WHERE 
                    operation_date IN {dates_tuple}
            """
            
            db_df = pd.read_sql(query, connection)
            connection.close()
            
            if db_df.empty:
                logging.warning("해당 날짜에 대한 DB 운영 로그가 없습니다.")
                return pd.DataFrame(columns=['차량번호', 'date', '운영여부'])

            # '운영 여부' 판단 로직
            # is_morning/lunch/dinner_operating 중 하나라도 1이면 '운영', 모두 0이면 '미운영'

            def check_and_print_row(row):
                # # --- 여기서 row의 내용이 출력됩니다 ---
                # print("--- 처리 중인 row ---")
                # print(row)
                # print("---------------------\n")
                
                # 기존의 조건문 로직
                if (row['is_morning_operating'] == 1 or 
                    row['is_lunch_operating'] == 1 or 
                    row['is_dinner_operating'] == 1):
                    return '운영'
                else:
                    return '미운영'
                


            # apply 함수에 정의한 함수를 적용
            db_df['운영여부']= db_df.apply(check_and_print_row, axis=1)
            
            # db_df['운영여부'] = db_df.apply(
            #     lambda row: '운영' if (row['is_morning_operating'] == 1 or 
            #                          row['is_lunch_operating'] == 1 or 
            #                          row['is_dinner_operating'] == 1) else '미운영',
            #     axis=1
            # )
            
            # 컬럼명 변경 (병합을 위해)
            db_df.rename(columns={'bus_number': '차량번호', 'operation_date': 'date'}, inplace=True)
            logging.info(f"DB에서 총 {len(db_df)}개의 운영 로그를 성공적으로 조회했습니다.")
            
            return db_df[['차량번호', 'date', '운영여부']]

    except Exception as e:
        logging.error(f"DB 조회 중 심각한 오류 발생: {e}")
        # 오류 발생 시 빈 데이터프레임 반환하여 나머지 프로세스 진행
        return pd.DataFrame(columns=['차량번호', 'date', '운영여부'])