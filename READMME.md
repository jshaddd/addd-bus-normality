pip install -r requirements.txt


버스 기기 데이터 분석 스크립트
이 스크립트는 nomality_check_devices.csv에 명시된 버스 기기들의 리포트 파일({차량번호}_{MAC}.csv)을 분석하고 결과를 보고서로 생성합니다.

프로젝트 구조
.
├── reports/
│   ├── 서울71사1225_68EDA485D5CA.csv
│   └── ...
├── data/
│   └── reference/
│       └── nomality_check_devices.csv
├── output/
│   └── analysis_report_YYYY-MM-DD_HHMM/
│       ├── report.md
│       ├── report_task1.csv
│       └── report_task2.csv
├── config.py
├── data_processor.py
└── main.py

reports/: 분석할 데이터 파일({차량번호}_{MAC}.csv)이 위치하는 폴더입니다.

data/reference/: 기기 정보가 담긴 nomality_check_devices.csv 파일이 위치하는 폴더입니다.

output/: 분석 결과가 저장되는 최상위 폴더입니다.

analysis_report_YYYY-MM-DD_HHMM/: 스크립트가 실행될 때마다 날짜와 시간을 기반으로 생성되는 고유한 결과 폴더입니다.

report.md: 모든 분석 결과를 요약한 보고서 파일입니다.

report_task1.csv: **작업 1(특정 날짜 exposure_count 체크)**의 상세 결과가 담긴 CSV 파일입니다.

report_task2.csv: **작업 2(저조 기간 확인)**의 상세 결과가 담긴 CSV 파일입니다.

config.py: 데이터 경로 및 파일명을 설정할 수 있는 파일입니다.

data_processor.py: 데이터 처리와 관련된 함수들이 정의된 모듈입니다.

main.py: 스크립트의 메인 실행 파일입니다.

실행 방법
폴더 및 파일 준비:

reports 폴더와 data/reference 폴더가 올바른 위치에 있는지 확인합니다.

nomality_check_devices.csv 파일이 data/reference 폴더에 있는지 확인합니다.

분석하고자 하는 버스번호_MAC.csv 파일들이 reports 폴더에 있는지 확인합니다.

설정 변경 (선택 사항):

config.py 파일에서 경로를 변경할 수 있습니다.

main.py 파일에서 분석 기준(날짜, exposure_count 등)을 변경할 수 있습니다.

스크립트 실행:

터미널에서 main.py를 실행합니다.

python main.py

결과 확인:

스크립트 실행이 완료되면, output 폴더 내에 새로 생성된 고유한 이름의 폴더를 확인하세요. 이 폴더 안에 report.md, report_task1.csv, report_task2.csv 파일이 생성됩니다.