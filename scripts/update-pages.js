const fs = require('fs');
const path = require('path');

const workspaceRoot = path.resolve(__dirname, '..');
const cssDir = path.join(workspaceRoot, 'css');
const jsDir = path.join(workspaceRoot, 'js');
const outCss = path.join(workspaceRoot, 'css', 'site.bundle.min.css');
const outJs = path.join(workspaceRoot, 'js', 'site.bundle.min.js');

function listFiles(dir, exts) {
  return fs.readdirSync(dir).filter(f => exts.includes(path.extname(f))).map(f => path.join(dir, f));
}

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

  // extract title and meta description if present
  const titleMatch = src.match(/<title[^>]*>[\s\S]*?<\/title>/i);
  const descMatch = src.match(/<meta\s+name=["']description["'][^>]*>/i);
  const title = titleMatch ? titleMatch[0] : '';
  const description = descMatch ? descMatch[0] : '';

  // build new head by injecting page-specific title/description
  const relativeRoot = path.relative(path.dirname(filePath), workspaceRoot).replaceAll('\\', '/');
  const rootPrefix = relativeRoot ? relativeRoot + '/' : '';
  const newHead = headerPartial.replace('<!--PAGE_TITLE-->', title).replace('<!--PAGE_DESCRIPTION-->', description).replaceAll('<!--ROOT-->', rootPrefix);
  const newFooter = footerPartial.replaceAll('<!--ROOT-->', rootPrefix);

  // replace existing head
  src = src.replace(/<head[\s\S]*?<\/head>/i, newHead);

  // replace footer
  if (src.match(/<footer[\s\S]*?<\/footer>/i)) {
    src = src.replace(/<footer[\s\S]*?<\/footer>/i, newFooter);
  } else {
    // append footer before closing body
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
  if (!fs.existsSync(path.join(cssDir, 'site.min.css')) || !fs.existsSync(path.join(jsDir, 'app.min.js'))) {
    throw new Error('Run the site normalizer first so css/site.min.css and js/app.min.js exist.');
  }

  const htmlFiles = getAllHtml(workspaceRoot);
  htmlFiles.forEach(f => {
    // skip the partials folder if it's inside workspace root
    if (f.includes(path.join('scripts', 'partials'))) return;
    replaceHeadAndFooter(f);
  });
  console.log('All done. Updated', htmlFiles.length, 'HTML files.');
}

if (require.main === module) main();
