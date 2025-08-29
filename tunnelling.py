import pymysql
from sshtunnel import SSHTunnelForwarder
import pandas as pd

# --- (접속 정보는 이전과 동일) ---
ssh_host = '175.45.194.216'
ssh_port = 22
ssh_user = 'root'
ssh_password = 'M6bdM*Tc!H5?h'

mysql_host = '192.168.6.6'
mysql_port = 3306
mysql_user = 'addd'
mysql_password = '!@addd1004'
mysql_db = 'bus_operation_logs'
target_table_name = 'bus_operation_logs'

try:
    with SSHTunnelForwarder(
        (ssh_host, ssh_port),
        ssh_username=ssh_user,
        ssh_password=ssh_password,
        remote_bind_address=(mysql_host, mysql_port)
    ) as tunnel:
        print("✅ SSH 터널이 성공적으로 생성되었습니다!")
        
        conn = pymysql.connect(
            host='127.0.0.1', 
            port=tunnel.local_bind_port,
            user=mysql_user,
            password=mysql_password,
            db=mysql_db,
            charset='utf8'
        )
        print("✅ 데이터베이스에 성공적으로 접속했습니다!")

        # 1. 테이블 데이터만 가져오기
        curs = conn.cursor()
        data_query = f"SELECT * FROM {target_table_name} LIMIT 1000"
        curs.execute(data_query)
        
        # 2. 결과 출력
        column_names = [desc[0] for desc in curs.description]
        results = curs.fetchall()
        
        df_data = pd.DataFrame(results, columns=column_names)
        
        print(f"\n--- 📊 '{target_table_name}' 테이블 데이터 (상위 {len(results)}개) ---")
        print(df_data)

                # 1. 테이블 정보(스키마)만 가져오기
        curs = conn.cursor()
        # INFORMATION_SCHEMA를 조회하여 테이블의 상세 정보를 가져옵니다.
        schema_query = f"""
            SELECT 
                COLUMN_NAME, 
                DATA_TYPE, 
                CHARACTER_MAXIMUM_LENGTH,
                COLUMN_DEFAULT,
                IS_NULLABLE
            FROM 
                INFORMATION_SCHEMA.COLUMNS 
            WHERE 
                TABLE_SCHEMA = '{mysql_db}' AND TABLE_NAME = '{target_table_name}';
        """
        curs.execute(schema_query)
           # 2. 결과 출력
        column_info = curs.fetchall()
        column_names = [desc[0] for desc in curs.description]
        
        df_schema = pd.DataFrame(column_info, columns=column_names)
        
        print(f"\n--- 📋 '{target_table_name}' 테이블 정보 ---")
        print(df_schema)
        

finally:
    if 'conn' in locals() and conn.open:
        conn.close()
        print("\n⏹️ 데이터베이스 연결이 종료되었습니다.")