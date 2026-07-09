# Cloudflare Pages 배포 가이드

이 문서는 게임 프로젝트를 GitHub에 올린 뒤, 실제 웹 호스팅은 Cloudflare Pages가 담당하도록 연결하는 절차를 정리합니다.

기본 구조는 다음과 같습니다.

```text
로컬 프로젝트 -> GitHub 저장소 -> Cloudflare Pages 자동 빌드/배포 -> dldcom.xyz 하위 도메인
```

GitHub는 코드 저장소로만 사용하고, 학생들이 접속하는 사이트는 Cloudflare Pages에서 제공합니다.

---

## 1. 배포 흐름

1. **GitHub 저장소 생성**
   - 새 게임 프로젝트용 저장소를 만듭니다.
   - 예: `science_4_1_4-3-`, `society-4-1-2-3-`

2. **코드 푸시**
   - 로컬 프로젝트를 GitHub `main` 브랜치에 push합니다.

3. **Cloudflare Pages에서 GitHub 저장소 연결**
   - Cloudflare Pages가 GitHub 저장소를 읽고 직접 빌드/배포합니다.

4. **커스텀 도메인 연결**
   - 예: `science-4-1-4-3.dldcom.xyz`
   - Cloudflare Pages 프로젝트의 Custom domains에서 연결합니다.

5. **포털에 등록**
   - `main_page/app.js`의 `games` 배열에 새 게임 URL과 썸네일을 추가합니다.

---

## 2. Cloudflare Pages 설정

Cloudflare CLI(`wrangler`)로 직접 배포할 때 필요한 API 토큰은 프로젝트 루트의 `.env` 파일을 참고합니다. `.env`에는 실제 토큰 값이 들어 있으므로 저장소에 공개하지 않습니다.

### Vite / React 프로젝트

`package.json`이 있고 `npm run build` 후 `dist` 폴더가 생기는 프로젝트는 아래처럼 설정합니다.

```text
Framework preset: Vite
Production branch: main
Build command: npm run build
Build output directory: dist
Root directory: 비워두기
```

### 정적 HTML 프로젝트

루트에 `index.html`, `style.css`, `app.js`, `assets/`, `images/` 등이 있고 `package.json`이 없는 프로젝트는 빌드가 필요 없습니다.

```text
Framework preset: None 또는 Custom
Production branch: main
Build command: 비워두기
Build output directory: .
Root directory: 비워두기
```

정적 프로젝트에 `npm run build`를 넣으면 실패합니다.

---

## 3. 커스텀 도메인 연결

Cloudflare Pages 프로젝트에서:

1. **Custom domains**로 이동
2. **Set up a custom domain** 선택
3. 사용할 주소 입력
   - 예: `science-4-1-4-3.dldcom.xyz`
4. Cloudflare가 DNS 레코드를 추가하거나 수정하도록 진행

정상 연결되면 DNS는 대략 아래처럼 됩니다.

```text
CNAME science-4-1-4-3 -> science-4-1-4-3.pages.dev
Proxy status: Proxied
```

---

## 4. 에듀 게임 포털에 새 게임 등록하기

게임 웹사이트가 Cloudflare Pages에서 정상 배포되었다면, `main_page`에 등록합니다.

1. **썸네일 이미지 준비**
   - 게임 대표 스크린샷을 `main_page` 폴더에 넣습니다.
   - 예: `new_game.png`

2. **썸네일 압축**
   - `convert.js`의 `mapping` 객체에 변환 규칙을 추가합니다.

   ```javascript
   const mapping = {
       // 기존 항목들
       'new_game.png': 'new_game.webp'
   };
   ```

   - 터미널에서 실행:

   ```bash
   node convert.js
   ```

3. **게임 데이터 등록**
   - `app.js`의 `const games = [...]` 배열에 추가합니다.

   ```javascript
   {
       titleInfo: { term: '대상학년', subject: '과목', unit: '단원', name: '게임 제목' },
       description: '게임에 대한 간단한 설명',
       url: 'https://배포된도메인.dldcom.xyz',
       grade: '필터용 학년',
       subject: '필터용 과목',
       type: '분류',
       bgColor: '#ff90e8',
       image: 'images/new_game.webp'
   }
   ```

4. **포털 반영**
   - `main_page` 변경사항을 GitHub에 push합니다.
   - `main_page`도 Cloudflare Pages에 연결되어 있다면 push 후 자동 배포됩니다.
