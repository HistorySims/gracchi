// Prints every scene's image and hotspot positions from index.html as JSON,
// so the art generator can draw each object where its hotspot sits.
const fs = require('fs');
const html = fs.readFileSync(process.argv[2] || 'index.html', 'utf8');
const src = html.match(/<script>([\s\S]*)<\/script>/)[1];
const G = eval('(' + src.match(/const GAME_DATA = (\{[\s\S]*?\n\});/)[1].replace(/;$/, '') + ')');
const out = Object.values(G.scenes).map(s => ({
  id: s.id, image: s.image,
  hotspots: s.hotspots.map(h => ({ id: h.id, x: h.x, y: h.y, type: h.type }))
}));
process.stdout.write(JSON.stringify(out, null, 1));
