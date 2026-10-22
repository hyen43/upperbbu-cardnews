// 사용법: node render.js <slides.json> <출력폴더>
// slides.json: { "handle": "@upperbbu_", "slides": [ { "type": "photo|paper", "bg": "assets/x.png", "dim": "css gradient", "html": "..." } ] }
// html 안에서 {{cloud}}, {{burst}} 를 쓰면 말풍선/별 스티커 SVG로 바뀜
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const [, , input, outDir = 'out'] = process.argv;
const base = path.dirname(path.resolve(input));
const data = JSON.parse(fs.readFileSync(input, 'utf8'));

const CLOUD = `<svg viewBox="0 0 440 270"><path fill="#fff" d="M95 225c-50 0-80-35-70-75 8-30 35-45 60-42 0-45 40-80 90-72 20-35 70-45 105-20 35-25 90-10 100 35 40-2 65 35 50 70 25 20 15 70-30 80-10 30-55 40-85 22-30 20-80 15-100-8-35 18-85 10-120 10z"/></svg>`;
const BURST = (() => {
  const pts = [];
  for (let i = 0; i < 16; i++) {
    const r = i % 2 ? 70 : 160, a = (Math.PI * i) / 8 - Math.PI / 2;
    pts.push(`${160 + r * Math.cos(a)},${160 + r * Math.sin(a)}`);
  }
  return `<svg viewBox="0 0 320 320"><polygon points="${pts.join(' ')}" fill="#FFF07A" stroke="#141414" stroke-width="4" stroke-linejoin="round"/></svg>`;
})();

const slideHtml = (s) => {
  const bg = s.bg ? `background-image:url('file://${path.resolve(base, s.bg)}');` : '';
  const dim = s.dim ? `--dim:${s.dim};` : '';
  const html = s.html.replaceAll('{{cloud}}', CLOUD).replaceAll('{{burst}}', BURST)
    // html 안의 상대 경로 이미지도 slides.json 위치 기준으로
    .replace(/url\('(?!file:|https?:)([^']+)'\)/g, (_, p) => `url('file://${path.resolve(base, p)}')`);
  return `<section class="slide ${s.type}" style="${bg}${dim}">${s.handle === false ? '' : `<div class="handle">${data.handle}</div>`}${html}</section>`;
};

(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1350 } });
  for (let i = 0; i < data.slides.length; i++) {
    const html = `<!doctype html><html><head><meta charset="utf-8">
      <link rel="stylesheet" href="file://${path.join(__dirname, 'template.css')}"></head>
      <body>${slideHtml(data.slides[i])}</body></html>`;
    const tmp = path.join(__dirname, `.tmp_${i}.html`);
    fs.writeFileSync(tmp, html);
    await page.goto('file://' + tmp);
    await page.evaluate(() => document.fonts.ready);
    // 인스타 Graph API는 JPEG만 받음
    await page.screenshot({ path: path.join(outDir, `${String(i + 1).padStart(2, '0')}.jpg`), type: 'jpeg', quality: 92 });
    fs.unlinkSync(tmp);
  }
  await browser.close();
})();
