#!/usr/bin/env node
/**
 * Generate PNG icons for SAGE Chrome/Firefox extension.
 * Uses Node canvas-less approach: generates raw PNG data.
 *
 * Run: node generate-icons.js
 * Outputs: icon16.png, icon48.png, icon128.png
 */

const fs = require("fs");
const path = require("path");

// Minimal PNG encoder — generates valid PNGs from RGBA pixel data
function createPNG(width, height, pixels) {
  const SIGNATURE = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);

  function crc32(buf) {
    let crc = 0xffffffff;
    for (let i = 0; i < buf.length; i++) {
      crc ^= buf[i];
      for (let j = 0; j < 8; j++) {
        crc = (crc >>> 1) ^ (crc & 1 ? 0xedb88320 : 0);
      }
    }
    return (crc ^ 0xffffffff) >>> 0;
  }

  function chunk(type, data) {
    const len = Buffer.alloc(4);
    len.writeUInt32BE(data.length, 0);
    const typeAndData = Buffer.concat([Buffer.from(type), data]);
    const crc = Buffer.alloc(4);
    crc.writeUInt32BE(crc32(typeAndData), 0);
    return Buffer.concat([len, typeAndData, crc]);
  }

  function adler32(buf) {
    let a = 1, b = 0;
    for (let i = 0; i < buf.length; i++) {
      a = (a + buf[i]) % 65521;
      b = (b + a) % 65521;
    }
    return ((b << 16) | a) >>> 0;
  }

  // IHDR
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(width, 0);
  ihdr.writeUInt32BE(height, 4);
  ihdr[8] = 8; // bit depth
  ihdr[9] = 6; // color type RGBA
  ihdr[10] = 0; // compression
  ihdr[11] = 0; // filter
  ihdr[12] = 0; // interlace

  // IDAT — raw filtered pixel data wrapped in zlib
  const rawRows = [];
  for (let y = 0; y < height; y++) {
    rawRows.push(Buffer.from([0])); // filter byte: None
    rawRows.push(pixels.slice(y * width * 4, (y + 1) * width * 4));
  }
  const raw = Buffer.concat(rawRows);

  // Minimal zlib wrapper (uncompressed deflate blocks)
  const blocks = [];
  const BLOCK_SIZE = 65535;
  for (let i = 0; i < raw.length; i += BLOCK_SIZE) {
    const end = Math.min(i + BLOCK_SIZE, raw.length);
    const isLast = end === raw.length;
    const blockData = raw.slice(i, end);
    const header = Buffer.alloc(5);
    header[0] = isLast ? 1 : 0;
    header.writeUInt16LE(blockData.length, 1);
    header.writeUInt16LE(~blockData.length & 0xffff, 3);
    blocks.push(header);
    blocks.push(blockData);
  }

  const zlibHeader = Buffer.from([0x78, 0x01]); // CMF, FLG
  const deflated = Buffer.concat(blocks);
  const adler = Buffer.alloc(4);
  adler.writeUInt32BE(adler32(raw), 0);
  const idat = Buffer.concat([zlibHeader, deflated, adler]);

  // IEND
  const iend = Buffer.alloc(0);

  return Buffer.concat([
    SIGNATURE,
    chunk("IHDR", ihdr),
    chunk("IDAT", idat),
    chunk("IEND", iend),
  ]);
}

function drawIcon(size) {
  const pixels = Buffer.alloc(size * size * 4);

  function setPixel(x, y, r, g, b, a) {
    x = Math.round(x);
    y = Math.round(y);
    if (x < 0 || x >= size || y < 0 || y >= size) return;
    const i = (y * size + x) * 4;
    // Alpha blend
    const sa = a / 255;
    const da = pixels[i + 3] / 255;
    const oa = sa + da * (1 - sa);
    if (oa === 0) return;
    pixels[i + 0] = Math.round((r * sa + pixels[i + 0] * da * (1 - sa)) / oa);
    pixels[i + 1] = Math.round((g * sa + pixels[i + 1] * da * (1 - sa)) / oa);
    pixels[i + 2] = Math.round((b * sa + pixels[i + 2] * da * (1 - sa)) / oa);
    pixels[i + 3] = Math.round(oa * 255);
  }

  function fillCircle(cx, cy, radius, r, g, b, a) {
    const r2 = radius * radius;
    for (let y = Math.floor(cy - radius); y <= Math.ceil(cy + radius); y++) {
      for (let x = Math.floor(cx - radius); x <= Math.ceil(cx + radius); x++) {
        const d2 = (x - cx) * (x - cx) + (y - cy) * (y - cy);
        if (d2 <= r2) {
          const edge = Math.max(0, 1 - Math.abs(Math.sqrt(d2) - radius));
          setPixel(x, y, r, g, b, Math.round(a * Math.min(1, edge + (d2 < (radius - 1) * (radius - 1) ? 1 : 0))));
        }
      }
    }
  }

  function drawLine(x1, y1, x2, y2, r, g, b, a, width) {
    const dx = x2 - x1, dy = y2 - y1;
    const len = Math.sqrt(dx * dx + dy * dy);
    const steps = Math.max(Math.ceil(len * 2), 1);
    for (let i = 0; i <= steps; i++) {
      const t = i / steps;
      const px = x1 + dx * t;
      const py = y1 + dy * t;
      fillCircle(px, py, width / 2, r, g, b, a);
    }
  }

  const cx = size / 2, cy = size / 2;

  // Background — dark purple circle
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const d = Math.sqrt((x - cx) * (x - cx) + (y - cy) * (y - cy));
      if (d <= size / 2) {
        const t = d / (size / 2);
        const r = Math.round(26 * (1 - t) + 13 * t);
        const g = Math.round(15 * (1 - t) + 8 * t);
        const b = Math.round(48 * (1 - t) + 24 * t);
        setPixel(x, y, r, g, b, 255);
      }
    }
  }

  // Outer ring
  const ringWidth = Math.max(1, size / 24);
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const d = Math.sqrt((x - cx) * (x - cx) + (y - cy) * (y - cy));
      const ringDist = Math.abs(d - (size / 2 - ringWidth));
      if (ringDist < ringWidth) {
        const alpha = Math.round(255 * (1 - ringDist / ringWidth));
        setPixel(x, y, 167, 139, 250, alpha);
      }
    }
  }

  // Neural nodes
  const nodes = [
    [cx - size * 0.2, cy - size * 0.15],
    [cx + size * 0.2, cy - size * 0.15],
    [cx - size * 0.25, cy + size * 0.1],
    [cx + size * 0.25, cy + size * 0.1],
    [cx, cy - size * 0.28],
    [cx, cy + size * 0.25],
  ];

  // Draw connections to center
  const lineW = Math.max(0.5, size / 32);
  for (const [nx, ny] of nodes) {
    drawLine(cx, cy, nx, ny, 167, 139, 250, 150, lineW);
  }

  // Cross connections (deterministic)
  const crossPairs = [[0, 4], [1, 4], [2, 5], [3, 5], [0, 2], [1, 3]];
  for (const [i, j] of crossPairs) {
    drawLine(nodes[i][0], nodes[i][1], nodes[j][0], nodes[j][1], 124, 92, 191, 80, lineW * 0.7);
  }

  // Draw outer nodes
  const nodeR = size * 0.05;
  for (const [nx, ny] of nodes) {
    fillCircle(nx, ny, nodeR, 124, 92, 191, 255);
  }

  // Center glow
  const glowR = size * 0.15;
  for (let y = Math.floor(cy - glowR); y <= Math.ceil(cy + glowR); y++) {
    for (let x = Math.floor(cx - glowR); x <= Math.ceil(cx + glowR); x++) {
      const d = Math.sqrt((x - cx) * (x - cx) + (y - cy) * (y - cy));
      if (d < glowR) {
        const alpha = Math.round(100 * (1 - d / glowR));
        setPixel(x, y, 167, 139, 250, alpha);
      }
    }
  }

  // Center node
  fillCircle(cx, cy, size * 0.08, 167, 139, 250, 255);
  fillCircle(cx, cy, size * 0.04, 233, 213, 255, 230);

  return pixels;
}

// Generate all sizes
const outDir = path.dirname(process.argv[1] || __filename);
for (const size of [16, 48, 128]) {
  const pixels = drawIcon(size);
  const png = createPNG(size, size, pixels);
  const outPath = path.join(outDir, `icon${size}.png`);
  fs.writeFileSync(outPath, png);
  console.log(`Generated ${outPath} (${png.length} bytes)`);
}
