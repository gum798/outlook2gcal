# 🚀 Outlook2GCal 간단 실행 가이드

## 📱 마우스로 실행하기

### 방법 1: Applications 폴더에서 실행
1. **Finder** → **Applications** 폴더 열기
2. **"Outlook2GCal Sync"** 앱 더블클릭
3. 원하는 옵션 선택:
   - **Setup Check**: 설정 확인
   - **One-time Sync**: 일회성 동기화
   - **Start Monitoring**: 연속 모니터링

### 방법 2: 바탕화면에서 실행
1. 바탕화면의 **"📧 Outlook2GCal Sync"** 더블클릭
2. 원하는 옵션 선택

### 방법 3: Dock에 추가 (권장)
1. 바탕화면의 **"📧 Outlook2GCal Sync"**를 Dock으로 드래그
2. 언제든지 Dock에서 클릭하여 실행

## 🎯 실행 옵션 설명

### 1️⃣ Setup Check (설정 확인)
- Outlook 연결 상태 확인
- Google Calendar 연결 상태 확인
- 사용 가능한 캘린더 목록 표시

### 2️⃣ One-time Sync (일회성 동기화)
- 현재 초대받은 이벤트를 Google "2.업무" 캘린더에 동기화
- 완료 후 결과 알림 표시

### 3️⃣ Start Monitoring (연속 모니터링)
- 5분마다 자동으로 새 초대 이벤트 확인
- 터미널 창이 열리며 실시간 로그 표시
- 터미널 창을 닫으면 모니터링 중지

## ⚠️ 주의사항

- **Microsoft Outlook이 실행되어 있어야 합니다**
- 처음 실행 시 Google 계정 인증이 필요할 수 있습니다
- 모니터링 모드는 컴퓨터가 켜져 있는 동안 계속 실행됩니다

## 🆘 문제 해결

### 앱이 실행되지 않을 때
1. Microsoft Outlook이 실행되어 있는지 확인
2. 터미널에서 수동 실행:
   ```bash
   cd /Users/jhseo/Desktop/0020.project/outlook2gcal
   source venv/bin/activate
   python run.py --setup
   ```

### 권한 오류가 발생할 때
- 시스템 설정 > 개인정보 보호 및 보안 > 자동화
- 터미널 또는 앱에 필요한 권한 허용

## 📞 지원

문제가 발생하면 터미널에서 다음 명령어로 상세 로그 확인:
```bash
cd /Users/jhseo/Desktop/0020.project/outlook2gcal
source venv/bin/activate
python run.py --setup
```