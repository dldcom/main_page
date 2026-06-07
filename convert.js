const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

try {
    require.resolve('sharp');
} catch (e) {
    console.log('sharp 설치 중...');
    execSync('npm install sharp', { stdio: 'inherit' });
}

const sharp = require('sharp');

const mapping = {
    'garo.png': 'garosero.webp',
    'hanja.png': 'hanjagame.webp',
    'science1.png': 'science_4_1_3-1-.webp',
    'science3.png': 'science_4_1_3-3-.webp',
    'hand.png': 'handgame.webp',
    'test_deploy_site.png': 'test_deploy_site.webp'
};

async function convertAll() {
    const dir = __dirname;
    const outDir = path.join(dir, 'images');
    
    // 폴더 생성
    if (!fs.existsSync(outDir)) {
        fs.mkdirSync(outDir);
    }

    const files = fs.readdirSync(dir).filter(f => f.endsWith('.png'));
    let count = 0;

    for (const file of files) {
        if (!mapping[file]) continue;
        
        const inputPath = path.join(dir, file);
        const outputPath = path.join(outDir, mapping[file]);
        
        console.log(`[작업중] ${file} -> ${mapping[file]}`);
        try {
            await sharp(inputPath)
                .webp({ quality: 80 })
                .toFile(outputPath);
            console.log(`[성공] ${mapping[file]} 생성 완료!`);
            
            // 압축이 끝난 원본 파일은 삭제
            fs.unlinkSync(inputPath);
            count++;
        } catch (error) {
            console.error(`[에러] ${file} 변환 실패:`, error.message);
        }
    }
    console.log(`\n총 ${count}개의 이미지 변환 완료!`);
}

convertAll();
