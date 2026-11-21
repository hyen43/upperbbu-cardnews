// 메모장 스타일 릴스용 이미지 (1080×1920)
// 사용법: node render_notes.js <notes.json> <출력폴더>
// notes.json: { "handle": "@upperbbu_", "date": "2026년 11월 19일 오후 7:00",
//   "notes": [ { "html": "...{{meme:파일명|빈칸일 때 안내 문구}}..." } ] }
// 밈 파일은 notes.json 옆 memes/ 폴더에서 찾고, 없으면 점선 빈칸으로 표시
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const [, , input, outDir = 'out'] = process.argv;
const base = path.dirname(path.resolve(input));
const data = JSON.parse(fs.readFileSync(input, 'utf8'));

const meme = (_, file, hint) => {
  const p = path.join(base, 'memes', file);
  return fs.existsSync(p)
    ? `<div class="meme" style="background-image:url('file://${p}')"></div>`
    : `<div class="meme empty">밈 자리<br>${hint || file}</div>`;
};

(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  for (let i = 0; i < data.notes.length; i++) {
    const body = data.notes[i].html.replace(/\{\{meme:([^|}]+)(?:\|([^}]*))?\}\}/g, meme);
    const html = `<!doctype html><html><head><meta charset="utf-8">
      <link rel="stylesheet" href="file://${path.join(__dirname, 'template.css')}">
      <link rel="stylesheet" href="file://${path.join(__dirname, 'notes.css')}"></head>
      <body><section class="note"><div class="bar"><span>‹ 메모</span><span>완료</span></div>
      <div class="date">${data.date || ''}</div><div class="page">${body}</div>
      <div class="handle">${data.handle}</div></section></body></html>`;
    const tmp = path.join(__dirname, `.tmp_n${i}.html`);
    fs.writeFileSync(tmp, html);
    await page.goto('file://' + tmp);
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: path.join(outDir, `n${String(i + 1).padStart(2, '0')}.jpg`), type: 'jpeg', quality: 92 });
    fs.unlinkSync(tmp);
  }
  await browser.close();
})();
