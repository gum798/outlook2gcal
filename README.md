# Outlook2GCal - Outlook to Google Calendar Sync

Outlook 일정을 Google Calendar로 자동 동기화하는 Python 도구입니다.

## 주요 기능

- Microsoft Outlook 초대 이벤트를 Google Calendar로 자동 동기화
- 실시간 모니터링으로 새로운 일정 자동 감지
- 삭제된 일정 자동 정리
- "2.업무" 캘린더에 일정 저장 (설정 가능)

## 설치 및 설정

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. Google Calendar API 설정
1. [Google Cloud Console](https://console.cloud.google.com/)에서 프로젝트 생성
2. Calendar API 활성화
3. OAuth 2.0 클라이언트 ID 생성
4. `credentials.json` 파일을 `config/` 폴더에 저장

### 3. 초기 설정
```bash
python run.py --setup
```

## 사용법

### 일회성 동기화
```bash
python run.py --sync --quiet
```

### 지속적인 모니터링 (권장)
```bash
python run.py --monitor --quiet
```

### 백그라운드 실행
```bash
python start_daemon.py
```

### 모니터링 중지
```bash
python stop_monitor.py
```

### 상태 확인
```bash
python check_status.py
```

## 파일 구조

```
outlook2gcal/
├── src/
│   └── outlook2gcal.py      # 메인 동기화 로직
├── config/
│   ├── credentials.json     # Google API 인증 파일
│   ├── token.json          # OAuth 토큰 (자동 생성)
│   └── sync_state.json     # 동기화 상태 저장
├── run.py                   # 메인 실행 스크립트
├── start_daemon.py          # 백그라운드 시작
├── stop_monitor.py          # 모니터링 중지
├── check_status.py          # 상태 확인
└── requirements.txt         # Python 패키지 목록
```

## 동기화 로직

1. **Outlook 일정 수집**: AppleScript를 통해 Outlook 초대 이벤트 수집
2. **중복 확인**: 이미 동기화된 이벤트는 건너뛰기
3. **Google Calendar 생성**: 새로운 이벤트를 Google Calendar에 생성
4. **상태 저장**: 동기화 상태를 JSON 파일에 저장
5. **삭제된 일정 정리**: Outlook에서 삭제된 이벤트를 Google Calendar에서도 삭제

## 개선 사항

최근 다음과 같은 문제를 해결했습니다:

- **google_event_id가 null로 저장되는 문제**: 기존 이벤트 발견 시에도 정확한 Google 이벤트 ID 저장
- **오류 처리 강화**: 동기화 실패 시 적절한 오류 메시지 및 경고 출력
- **중복 이벤트 처리**: 이미 존재하는 이벤트의 정확한 ID 추적

## 문제 해결

### 동기화가 안 될 때
```bash
# 상태 확인
python check_status.py

# 강제 재동기화 (특정 이벤트 문제 시)
# sync_state.json에서 해당 이벤트 제거 후
python run.py --sync --quiet
```

### 로그 확인
- 모니터링 로그: `/tmp/outlook2gcal_*.log`
- PID 파일: `/tmp/outlook2gcal_monitor.pid`

## 요구사항

- macOS (AppleScript를 통한 Outlook 연동)
- Microsoft Outlook 실행 중
- Python 3.7+
- Google Calendar API 액세스

## 라이선스

MIT License