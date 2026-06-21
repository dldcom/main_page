# 🚀 GitHub Pages & Cloudflare DNS 배포 자동화 가이드

이 문서는 로컬 환경에서 작업한 코드를 GitHub에 업로드하여 무료 호스팅(GitHub Pages)을 적용하고, Cloudflare를 통해 커스텀 하위 도메인(예: `sub.dldcom.xyz`)을 자동으로 연결하는 전체 과정에 대한 안내서입니다. 이 과정을 한 번의 명령어로 처리할 수 있도록 `deploy.py` 자동화 스크립트가 준비되어 있습니다.

---

## 1. 파이프라인 아키텍처 이해하기

본 자동화 배포 시스템은 다음과 같은 흐름으로 작동합니다.
1. **GitHub 저장소 자동 생성**: 지정한 이름으로 Public 저장소를 생성합니다.
2. **코드 및 CNAME 업로드**: 로컬 폴더의 코드를 커밋하고, 사용할 하위 도메인 주소가 적힌 `CNAME` 파일을 자동으로 생성해 함께 푸시합니다.
3. **GitHub Pages 활성화**: API를 호출해 업로드된 저장소의 GitHub Pages 기능을 켭니다. (이를 통해 코드가 웹사이트로 호스팅됩니다.)
4. **Cloudflare DNS 레코드 추가**: Cloudflare API를 통해 `dldcom.xyz` 도메인 설정에 접근하여, 새로 만든 하위 도메인이 GitHub Pages(`dldcom.github.io`)를 가리키도록 **CNAME DNS 레코드(DNS Only 모드)**를 자동 추가합니다.

---

## 2. 배포 자동화 스크립트 (`deploy.py`) 사용법

### 사전 준비사항
- 로컬 환경에 **Python**과 **Git**이 설치되어 있어야 합니다.
- 파이썬 패키지인 `requests`가 필요합니다. 터미널을 열고 아래 명령어를 실행해 설치합니다.
  ```bash
  pip install requests
  ```
- 스크립트 내부에 유효한 `GITHUB_TOKEN`과 `CLOUDFLARE_TOKEN`이 정상적으로 기입되어 있어야 합니다. (발급받은 토큰은 보안상 절대 외부에 노출되지 않도록 주의하세요.)

### 스크립트 실행
배포할 코드가 담긴 폴더가 준비되었다면, 터미널에서 다음 명령어를 실행합니다.

```bash
# 기본 사용법
python deploy.py --project-name "새프로젝트명" --dir "로컬코드경로" --domain "연결할서브도메인.dldcom.xyz"

# 실행 예시
python deploy.py --project-name "my-awesome-game" --dir "./my-game-folder" --domain "game1.dldcom.xyz"
```

> [!TIP]
> 명령어 실행이 완료되면 대략 **1~3분** 정도의 대기 시간이 필요합니다. 이는 GitHub 측에서 Pages 빌드를 완료하고, Cloudflare의 DNS 정보가 전 세계로 전파되는 데 걸리는 자연스러운 시간입니다.

---

## 3. 에듀 게임 포털 (`main_page`)에 새 게임 등록하기

위 과정을 통해 게임 웹사이트가 성공적으로 배포(`https://game1.dldcom.xyz`)되었다면, 이제 통합 게임 포털 메인 화면에 이 게임을 노출시킬 차례입니다.

1. **포털 저장소 준비**
   - 포털 코드가 있는 `main_page` 디렉토리로 이동하거나, 클론(`git clone https://github.com/dldcom/main_page.git`) 받습니다.
2. **썸네일 이미지 준비 및 압축**
   - 게임의 대표 스크린샷(`.png` 또는 `.jpg`)을 `main_page` 폴더 최상단에 넣습니다. (예: `new_game.png`)
   - `convert.js` 파일을 열고 `mapping` 객체 안에 파일명 변환 규칙을 추가합니다.
     ```javascript
     const mapping = {
         // ...기존 항목들
         'new_game.png': 'new_game.webp'
     };
     ```
   - 터미널에서 `node convert.js` 명령어를 실행하면, 이미지가 네오 브루탈리즘 포털 디자인에 맞게 가벼운 WebP 포맷으로 압축되어 `images/` 폴더에 자동 저장됩니다.
3. **데이터베이스 등록**
   - `app.js` 파일을 엽니다.
   - 상단의 `const games = [...]` 배열 안에 새로 배포한 게임의 정보를 아래 형식에 맞춰 추가합니다.
     ```javascript
     { 
         titleInfo: { term: '대상학년', subject: '과목', unit: '단원', name: '게임 제목' },
         description: '게임에 대한 간단하고 매력적인 설명',
         url: 'https://배포된도메인.dldcom.xyz', 
         grade: '필터용 학년', 
         subject: '필터용 과목', 
         type: '분류', 
         bgColor: '#ff90e8', // 썸네일 뒤에 깔릴 톡톡 튀는 배경색 (Neo-brutalism 스타일)
         image: 'images/new_game.webp' // 변환된 썸네일 이미지 경로
     }
     ```
4. **반영하기 (Push)**
   - `main_page`에서 수정한 내역을 커밋하고 푸시(`git push origin main`)하면 모든 작업이 완료됩니다!
   - 포털 메인 페이지를 새로고침하면 새롭게 추가된 게임이 감각적인 디자인으로 전시된 것을 확인할 수 있습니다.
