const http = require('http');
const fs = require('fs');
const path = require('path');

const port = process.env.PORT || 8000;
const root = path.resolve(__dirname, '..');

const mime = {
  '.html': 'text/html',
  '.css': 'text/css',
  '.js': 'application/javascript',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.webp': 'image/webp',
  '.ico': 'image/x-icon'
};

http.createServer((req, res) => {
  let reqPath = decodeURIComponent(req.url.split('?')[0]);
  if (reqPath === '/') reqPath = '/index.html';
  const filePath = path.join(root, reqPath.replace(/^\//, ''));
  fs.stat(filePath, (err, stat) => {
    if (err) {
      res.statusCode = 404;
      res.end('Not found');
      return;
    }
    if (stat.isDirectory()) {
      res.statusCode = 302;
      res.setHeader('Location', reqPath + '/index.html');
      res.end();
      return;
    }
    const ext = path.extname(filePath).toLowerCase();
    const type = mime[ext] || 'application/octet-stream';
    res.setHeader('Content-Type', type);
    const stream = fs.createReadStream(filePath);
    stream.pipe(res);
    stream.on('error', () => {
      res.statusCode = 500;
      res.end('Server error');
    });
  });
}).listen(port, () => console.log(`Serving ${root} on http://localhost:${port}`));
