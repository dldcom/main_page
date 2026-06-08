// 게임 데이터 베이스
const games = [
    { 
        titleInfo: { term: '공통', subject: '국어', unit: '어휘', name: '가로세로 낱말퍼즐' },
        description: '재미있게 어휘력을 기르는 가로세로 낱말 퍼즐',
        url: 'https://garo.dldcom.xyz', 
        grade: '전체', 
        subject: '국어/기타', 
        type: '퍼즐', 
        bgColor: '#ff90e8',
        image: 'images/garosero.webp'
    },
    { 
        titleInfo: { term: '공통', subject: '창체', unit: '한자', name: '한자 게임' },
        description: '기본 한자를 재미있게 익힐 수 있는 학습 게임',
        url: 'https://hanja.dldcom.xyz', 
        grade: '전체', 
        subject: '창체', 
        type: '학습', 
        bgColor: '#ffc900',
        image: 'images/hanjagame.webp' 
    },
    { 
        titleInfo: { term: '4-1', subject: '과학', unit: '3단원', name: '생명의 강' },
        description: '침식·운반·퇴적 작용을 직접 체험해보는 시뮬레이션 게임',
        url: 'https://science-4-1-3-1.dldcom.xyz', 
        grade: '4학년', 
        subject: '과학', 
        type: '퀴즈', 
        bgColor: '#23a094',
        image: 'images/science_4_1_3-1-.webp'
    },
    { 
        titleInfo: { term: '4-1', subject: '과학', unit: '3단원', name: '볼케이노 타이쿤' },
        description: '화산 분출물을 수집하며 마을을 키우는 타이쿤 게임',
        url: 'https://science-4-1-3-3.dldcom.xyz', 
        grade: '4학년', 
        subject: '과학', 
        type: '퀴즈', 
        bgColor: '#90a8ed',
        image: 'images/science_4_1_3-3-.webp'
    },
    { 
        titleInfo: { term: '공통', subject: '창체', unit: '수어', name: '수어 학습 게임' },
        description: '간단한 수어를 단계별로 배우고 연습하는 게임',
        url: 'https://hand.dldcom.xyz', 
        grade: '전체', 
        subject: '창체', 
        type: '학습', 
        bgColor: '#ff90e8',
        image: 'images/handgame.webp'
    },
    { 
        titleInfo: { term: '공통', subject: '창체', unit: '문화', name: '문화재 퍼즐' },
        description: '자랑스러운 우리 문화재를 알아가는 퍼즐 게임',
        url: 'https://moonhwa.dldcom.xyz', 
        grade: '전체', 
        subject: '창체', 
        type: '퍼즐', 
        bgColor: '#72D6C9',
        image: 'images/moonhwa.png'
    }
];

// 현재 필터 상태
const currentFilters = {
    grade: 'all',
    subject: 'all'
};

// DOM 요소
const gameGrid = document.getElementById('game-grid');
const filterBtns = document.querySelectorAll('.filter-btn');

// 초기 렌더링
function init() {
    renderGames(games);
    setupEventListeners();
}

// 게임 카드 렌더링 함수
function renderGames(gamesToRender) {
    gameGrid.innerHTML = '';
    
    if (gamesToRender.length === 0) {
        gameGrid.innerHTML = '<div style="grid-column: 1 / -1; text-align: center; font-weight: 700; padding: 3rem; background: #fff; border: 4px solid #000; box-shadow: 6px 6px 0 #000; border-radius: 10px;">해당하는 게임이 없습니다.</div>';
        return;
    }

    gamesToRender.forEach(game => {
        const card = document.createElement('a');
        card.href = game.url;
        card.target = '_blank'; // 새 창에서 열기
        card.className = 'game-card';
        
        card.innerHTML = `
            <div class="card-image" style="background-color: ${game.bgColor}; background-image: url('${game.image}'); background-size: cover; background-position: center; background-repeat: no-repeat;">
            </div>
            <div class="card-content">
                <div class="card-breadcrumbs">${game.titleInfo.term} / ${game.titleInfo.subject} / ${game.titleInfo.unit}</div>
                <h3 class="card-title">${game.titleInfo.name}</h3>
                <p class="card-desc">${game.description}</p>
            </div>
        `;
        
        gameGrid.appendChild(card);
    });
}

// 이벤트 리스너 설정
function setupEventListeners() {
    filterBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const category = e.target.dataset.category;
            const filterValue = e.target.dataset.filter;
            
            // 필터 상태 업데이트
            currentFilters[category] = filterValue;
            
            // UI 업데이트 (active 클래스 변경)
            updateActiveButtons(category, e.target);
            
            // 데이터 필터링 및 렌더링
            applyFilters();
        });
    });
}

// Active 버튼 UI 업데이트
function updateActiveButtons(category, clickedBtn) {
    // 해당 카테고리의 모든 버튼에서 active 제거
    const categoryBtns = document.querySelectorAll(`.filter-btn[data-category="${category}"]`);
    categoryBtns.forEach(btn => btn.classList.remove('active'));
    
    // 클릭된 버튼에 active 추가
    clickedBtn.classList.add('active');
}

// 필터 적용 로직
function applyFilters() {
    let filteredGames = games;

    // 학년 필터
    if (currentFilters.grade !== 'all') {
        filteredGames = filteredGames.filter(game => game.grade === currentFilters.grade);
    }
    
    // 과목 필터
    if (currentFilters.subject !== 'all') {
        filteredGames = filteredGames.filter(game => game.subject === currentFilters.subject);
    }

    renderGames(filteredGames);
}

// 앱 시작
init();
