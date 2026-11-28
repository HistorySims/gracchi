// Renders trailer.html frame by frame and encodes it to MP4 with ffmpeg.
//   node promo/trailer/render.js            -> promo/regnum_trailer.mp4
//   node promo/trailer/render.js preview    -> a few still frames for checking
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const FPS = 30;
(async () => {
  const preview = process.argv[2] === 'preview';
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  await p.goto('file://' + path.join(__dirname, 'trailer.html'));
  await p.evaluate(() => window.ready); await p.waitForTimeout(500);
  const dur = await p.evaluate(() => window.DURATION);
  if (preview) {
    for (const t of (process.argv[3] || '3,9,18,27,37,47,51,58,66').split(',').map(Number)) {
      await p.evaluate(t => render(t), t);
      await p.screenshot({ path: path.join(__dirname, `frame_${t}.jpg`), type: 'jpeg', quality: 80 });
    }
    await b.close(); return;
  }
  const out = path.join(__dirname, '..', 'regnum_trailer.mp4');
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const n = Math.round(dur * FPS);
  for (let i = 0; i < n; i++) {
    await p.evaluate(t => render(t), i / FPS);
    const buf = await p.screenshot({ type: 'jpeg', quality: 92 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 300 === 0) console.log(`frame ${i}/${n}`);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
  await b.close(); console.log('wrote', out);
})();
