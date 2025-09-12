# 🎨 앱 아이콘 가이드

## 현재 아이콘

✅ 파란색 배경에 캘린더 + 동기화 화살표 아이콘이 설치되었습니다.

## 🌟 더 이쁜 아이콘 찾기

### 추천 무료 아이콘 사이트

1. **SF Symbols (Apple 공식)**
   - https://developer.apple.com/sf-symbols/
   - macOS 스타일 아이콘
   - 키워드: `calendar`, `envelope`, `arrow.triangle.2.circlepath`

2. **Iconduck (무료)**
   - https://iconduck.com/
   - 키워드: "calendar sync", "outlook", "google calendar"

3. **Flaticon (무료/유료)**
   - https://www.flaticon.com/
   - 키워드: "calendar synchronization", "email calendar"

4. **Icons8 (무료/유료)**
   - https://icons8.com/
   - 키워드: "calendar integration", "sync"

### 🎯 추천 아이콘 스타일

1. **캘린더 + 화살표**: 동기화 개념
2. **이메일 + 캘린더**: Outlook → Google Calendar
3. **두 개의 캘린더**: 양방향 동기화
4. **시계 + 캘린더**: 자동 동기화

## 📥 아이콘 교체 방법

### 1단계: 아이콘 다운로드
- **크기**: 1024x1024 픽셀 이상
- **형식**: PNG (투명 배경 추천)
- **스타일**: macOS Big Sur/Monterey 스타일 (둥근 모서리)

### 2단계: 아이콘 변환 및 설치

```bash
# 다운로드한 PNG 파일을 바탕화면에 'new_icon.png'로 저장 후

cd /Users/jhseo/Desktop/0020.project/outlook2gcal

# 가상환경 활성화
source venv/bin/activate

# 아이콘 변환 스크립트 실행
python -c "
import subprocess
from pathlib import Path

png_path = Path.home() / 'Desktop' / 'new_icon.png'
iconset_dir = Path.home() / 'Desktop' / 'new_icon.iconset'
icns_path = Path.home() / 'Desktop' / 'new_icon.icns'

# Create iconset
subprocess.run(['mkdir', '-p', str(iconset_dir)])

# Generate sizes
sizes = [
    (16, 'icon_16x16.png'),
    (32, 'icon_16x16@2x.png'), 
    (32, 'icon_32x32.png'),
    (64, 'icon_32x32@2x.png'),
    (128, 'icon_128x128.png'),
    (256, 'icon_128x128@2x.png'),
    (256, 'icon_256x256.png'), 
    (512, 'icon_256x256@2x.png'),
    (512, 'icon_512x512.png'),
    (1024, 'icon_512x512@2x.png')
]

for size, filename in sizes:
    subprocess.run(['sips', '-z', str(size), str(size), str(png_path), '--out', str(iconset_dir / filename)])

# Convert to icns
subprocess.run(['iconutil', '-c', 'icns', str(iconset_dir), '-o', str(icns_path)])

# Install to app
subprocess.run(['cp', str(icns_path), '/Applications/Outlook2GCal Sync.app/Contents/Resources/AppIcon.icns'])

# Refresh
subprocess.run(['touch', '/Applications/Outlook2GCal Sync.app'])
subprocess.run(['killall', 'Finder'])

print('✅ 새 아이콘이 설치되었습니다!')
"
```

## 🎨 커스텀 아이콘 아이디어

### 색상 조합
- **파란색 + 흰색**: 신뢰감, 전문성
- **초록색 + 흰색**: 성공, 동기화 완료
- **주황색 + 흰색**: 활동성, Outlook 컬러
- **그라데이션**: 현대적, 세련된 느낌

### 디자인 요소
- 📧 **이메일 아이콘**: Outlook 연상
- 📅 **캘린더 아이콘**: Google Calendar 연상  
- ↔️ **동기화 화살표**: 양방향 연동
- ⚡ **번개**: 빠른 동기화
- 🔄 **새로고침**: 자동 업데이트

## 💡 Pro Tips

1. **macOS 스타일**: 둥근 모서리 + 그림자
2. **단순함**: 작은 크기에서도 알아볼 수 있게
3. **대비**: 배경과 아이콘 요소의 명확한 구분
4. **일관성**: 다른 macOS 앱들과 어울리는 스타일

## 🔧 문제 해결

### 아이콘이 바뀌지 않을 때
```bash
# 아이콘 캐시 강제 새로고침
sudo rm -rf /Library/Caches/com.apple.iconservices.store
killall Finder
killall Dock
```

### 앱이 실행되지 않을 때
- 아이콘 교체 후에도 앱 기능은 동일하게 작동합니다
- 문제가 있다면 원본 앱을 다시 생성하세요