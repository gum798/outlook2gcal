# Outlook to Google Calendar Sync

Microsoft Outlook에서 **초대받은 일정만** Google Calendar에 자동으로 동기화하는 macOS용 도구입니다.

## 기능

- 📧 **초대된 일정만** Microsoft Outlook에서 Google Calendar로 동기화
- 🔄 실시간 동기화 및 모니터링
- 📅 Google Calendar API 연동
- 🔍 중복 동기화 방지
- ⏰ 연속 모니터링 모드
- 🛡️ 안전한 OAuth 인증
- 🎯 자동 초대 이벤트 감지 (주최자 정보, 제목 키워드 분석)

## 설치

1. **저장소 클론**

   ```bash
   git clone <repository-url>
   cd outlook2gcal
   ```

2. **가상환경 생성 및 패키지 설치**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Google Calendar API 설정**
   - [Google Cloud Console](https://console.cloud.google.com) 접속
   - 새 프로젝트 생성
   - Calendar API 활성화
   - OAuth 2.0 자격증명 생성
   - `credentials.json` 파일을 `config/` 디렉토리에 저장

## 사용법

### 기본 명령어

```bash
# 가상환경 활성화
source venv/bin/activate

# 설정 확인
python run.py --setup

# 일회성 동기화
python run.py --sync

# 연속 모니터링 (5분마다)
python run.py --monitor

# 연속 모니터링 (1분마다)
python run.py --monitor --interval 60
```

### 고급 옵션

```bash
# 특정 Google Calendar에 동기화
python run.py --sync --calendar "업무일정"

# 도움말
python run.py --help
```

## 프로젝트 구조

```
outlook2gcal/
├── src/
│   ├── __init__.py
│   └── outlook2gcal.py      # 메인 동기화 로직
├── config/
│   ├── credentials.json     # Google API 자격증명 (사용자 생성)
│   ├── token.json          # OAuth 토큰 (자동 생성)
│   └── sync_state.json     # 동기화 상태 (자동 생성)
├── docs/
│   └── README.md           # 이 문서
├── venv/                   # 가상환경
├── requirements.txt        # 패키지 목록
├── run.py                 # 실행 스크립트
└── task.md               # 프로젝트 목표
```

## 초대 이벤트 감지 방식

도구는 다음 방법으로 초대받은 일정을 자동 감지합니다:

1. **주최자 정보 확인**: 이벤트에 주최자(organizer) 정보가 있는 경우
2. **제목 키워드 분석**: 다음 키워드가 포함된 경우
   - `[회의요청]`
   - `초대`
   - `Invitation`
   - `invited`

자신이 생성한 일반 일정은 동기화되지 않습니다.

## 필수 요구사항

- **macOS** (AppleScript 사용)
- **Python 3.9+**
- **Microsoft Outlook for Mac** (실행 중이어야 함)
- **Google Calendar API 자격증명**

## 문제 해결

### Outlook 관련

- Microsoft Outlook이 실행되어 있는지 확인
- Outlook이 응답하지 않으면 재시작

### Google Calendar 관련

- `config/credentials.json` 파일 존재 확인
- Google Cloud Console에서 테스트 사용자로 등록되었는지 확인
- 인증 문제 시 `config/token.json` 삭제 후 재인증

### 권한 관련

- 시스템 설정 > 개인정보 보호 및 보안 > 자동화에서 터미널 권한 확인

## 자동화 설정

### macOS LaunchAgent로 자동 실행

1. `~/Library/LaunchAgents/com.outlook2gcal.plist` 파일 생성:

   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
   <dict>
       <key>Label</key>
       <string>com.outlook2gcal</string>
       <key>ProgramArguments</key>
       <array>
           <string>/path/to/outlook2gcal/venv/bin/python</string>
           <string>/path/to/outlook2gcal/run.py</string>
           <string>--monitor</string>
       </array>
       <key>WorkingDirectory</key>
       <string>/path/to/outlook2gcal</string>
       <key>RunAtLoad</key>
       <true/>
       <key>KeepAlive</key>
       <true/>
   </dict>
   </plist>
   ```

2. LaunchAgent 로드:

   ```bash
   launchctl load ~/Library/LaunchAgents/com.outlook2gcal.plist
   ```

## 라이선스

MIT License