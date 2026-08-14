const fs = require('fs');
const path = require('path');

const workspaceRoot = path.resolve(__dirname, '..');
const cssDir = path.join(workspaceRoot, 'css');
const jsDir = path.join(workspaceRoot, 'js');
const outCss = path.join(workspaceRoot, 'css', 'site.bundle.min.css');
const outJs = path.join(workspaceRoot, 'js', 'site.bundle.min.js');

function simpleMinifyCss(src) {
  return src
    .replace(/\/\*[\s\S]*?\*\//g, '')
    .replace(/\n+/g, ' ')
    .replace(/\s{2,}/g, ' ')
    .trim();
}

function simpleMinifyJs(src) {
  return src
    .replace(/\/\*[\s\S]*?\*\//g, '')
    .replace(/\/\/.*$/gm, '')
    .replace(/\n+/g, ' ')
    .replace(/\s{2,}/g, ' ')
    .trim();
}

function buildCssBundle() {
  const preferred = [
    'variables.css',
    'style.css',
    'app.min.css',
    'enhancements.min.css',
    'site-responsive.css',
    'responsive.css',
    'html-utilities.css',
    'trust-network.css',
    'animations.css'
  ];
  let out = '';
  preferred.forEach(f => {
    const p = path.join(cssDir, f);
    if (fs.existsSync(p)) out += '\n/* ' + f + ' */\n' + fs.readFileSync(p, 'utf8');
  });
  fs.writeFileSync(outCss, simpleMinifyCss(out), 'utf8');
  console.log('Wrote CSS bundle:', outCss);
}

function buildJsBundle() {
  const preferred = [
    'utils.js',
    'theme.js',
    'site-enhancements.js',
    'main.js',
    'app.min.js'
  ];
  let out = '';
  preferred.forEach(f => {
    const p = path.join(jsDir, f);
    if (fs.existsSync(p)) out += '\n/* ' + f + ' */\n' + fs.readFileSync(p, 'utf8');
  });
  fs.writeFileSync(outJs, simpleMinifyJs(out), 'utf8');
  console.log('Wrote JS bundle:', outJs);
}

function getAllHtml(dir) {
  let results = [];
  const list = fs.readdirSync(dir);
  list.forEach(file => {
    const p = path.join(dir, file);
    const stat = fs.statSync(p);
    if (stat && stat.isDirectory()) results = results.concat(getAllHtml(p));
    else if (path.extname(p) === '.html') results.push(p);
  });
  return results;
}

const headerPartial = fs.readFileSync(path.join(__dirname, 'partials', 'header-snippet.html'), 'utf8');
const footerPartial = fs.readFileSync(path.join(__dirname, 'partials', 'footer-snippet.html'), 'utf8');

function replaceHeadAndFooter(filePath) {
  let src = fs.readFileSync(filePath, 'utf8');

  const titleMatch = src.match(/<title[^>]*>[\s\S]*?<\/title>/i);
  const descMatch = src.match(/<meta\s+name=["']description["'][^>]*>/i);
  const title = titleMatch ? titleMatch[0] : '';
  const description = descMatch ? descMatch[0] : '';

  const newHead = headerPartial.replace('<!--PAGE_TITLE-->', title).replace('<!--PAGE_DESCRIPTION-->', description);

  src = src.replace(/<head[\s\S]*?<\/head>/i, newHead);

  if (src.match(/<footer[\s\S]*?<\/footer>/i)) {
    src = src.replace(/<footer[\s\S]*?<\/footer>/i, footerPartial);
  } else {
    src = src.replace(/<\/body>/i, footerPartial + '\n</body>');
  }

  fs.writeFileSync(filePath, src, 'utf8');
  console.log('Patched', filePath);
}

function ensurePartialsDir() {
  const p = path.join(__dirname, 'partials');
  if (!fs.existsSync(p)) fs.mkdirSync(p, { recursive: true });
}

function main() {
  ensurePartialsDir();
  buildCssBundle();
  buildJsBundle();

  const htmlFiles = getAllHtml(workspaceRoot);
  htmlFiles.forEach(f => {
    if (f.includes(path.join('scripts', 'partials'))) return;
    replaceHeadAndFooter(f);
  });
  console.log('All done. Updated', htmlFiles.length, 'HTML files.');
}

if (require.main === module) main();
