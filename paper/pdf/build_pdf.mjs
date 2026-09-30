// Build paper/ADT_foundations.pdf from paper/ADT_foundations.md.
//
//   cd paper/pdf && npm install && node build_pdf.mjs [output.pdf]
//
// Mathematics is rendered server-side with KaTeX, Markdown with markdown-it,
// and the page is printed to A4 by Playwright's Chromium. If Playwright's own
// browser is not installed, set CHROMIUM_PATH to a Chromium executable.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import katex from "katex";
import MarkdownIt from "markdown-it";
import { chromium } from "playwright";

const here = path.dirname(fileURLToPath(import.meta.url));
const paperDir = path.resolve(here, "..");
const srcPath = path.join(paperDir, "ADT_foundations.md");
const outPath = path.resolve(process.argv[2] || path.join(paperDir, "ADT_foundations.pdf"));

// 1. Take the mathematics out before Markdown sees it.
const math = [];
let md = fs.readFileSync(srcPath, "utf8");
md = md.replace(/\$\$([\s\S]+?)\$\$/g, (_, tex) => `MATHXD${math.push({ tex, display: true }) - 1}X`);
md = md.replace(/\$([^$\n]+?)\$/g, (_, tex) => `MATHXI${math.push({ tex, display: false }) - 1}X`);

// 2. Markdown.
const mdit = new MarkdownIt({ html: false, linkify: false, typographer: false });

// Numbered level-2 headings get stable ids "sec-N"; the contents list links to them.
mdit.core.ruler.push("section_ids", (state) => {
  const t = state.tokens;
  for (let i = 0; i < t.length - 1; i++) {
    if (t[i].type === "heading_open" && t[i].tag === "h2") {
      const m = t[i + 1].content.match(/^(\d+)\./);
      if (m) t[i].attrSet("id", `sec-${m[1]}`);
    }
  }
});

// In-document anchors are rewritten; links to repository files become plain text.
mdit.renderer.rules.link_open = (tokens, idx, options, env, self) => {
  const href = tokens[idx].attrGet("href") || "";
  env.dropped = env.dropped || [];
  if (href.startsWith("#")) {
    const m = href.match(/^#(\d+)-/);
    if (m) tokens[idx].attrSet("href", `#sec-${m[1]}`);
    env.dropped.push(false);
    return self.renderToken(tokens, idx, options);
  }
  if (/^https?:\/\//.test(href)) {
    env.dropped.push(false);
    return self.renderToken(tokens, idx, options);
  }
  env.dropped.push(true);
  return "";
};
mdit.renderer.rules.link_close = (tokens, idx, options, env, self) =>
  env.dropped.pop() ? "" : self.renderToken(tokens, idx, options);

// Figures are embedded so the PDF is self-contained.
mdit.renderer.rules.image = (tokens, idx) => {
  const src = path.resolve(paperDir, tokens[idx].attrGet("src"));
  const data = fs.readFileSync(src).toString("base64");
  const alt = tokens[idx].content.replace(/"/g, "&quot;");
  return `<img class="fig" alt="${alt}" src="data:image/png;base64,${data}">`;
};

let html = mdit.render(md, {});

// 3. Front matter: date line under the subtitle, abstract block.
const date = new Date().toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" });
html = html.replace(/(<\/h1>\s*<p>[\s\S]*?<\/p>)/, `$1\n<p class="dateline">Draft manuscript · ${date}</p>`);
html = html.replace(
  /(<p><strong>Abstract\.<\/strong>[\s\S]*?<p><strong>MSC 2020\.<\/strong>[\s\S]*?<\/p>)/,
  '<div class="abstract">$1</div>'
);

// 4. Put the mathematics back.
const render = (i) =>
  katex.renderToString(math[+i].tex, { displayMode: math[+i].display, throwOnError: true, strict: false, output: "html" });
html = html.replace(/<p>MATHXD(\d+)X<\/p>/g, (_, i) => render(i));
html = html.replace(/MATHX[DI](\d+)X/g, (_, i) => render(i));
if (/MATHX[DI]\d+X/.test(html)) throw new Error("unreplaced math placeholder");

// 5. Print.
const katexCss = pathToFileURL(path.join(here, "node_modules", "katex", "dist", "katex.min.css")).href;
const css = fs.readFileSync(path.join(here, "style.css"), "utf8");
const page = `<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Arithmetic Dynamical Tomography</title>
<link rel="stylesheet" href="${katexCss}"><style>${css}</style></head>
<body>${html}</body></html>`;
const htmlPath = path.join(here, "manuscript.html");
fs.writeFileSync(htmlPath, page);

const browser = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
const tab = await browser.newPage();
await tab.goto(pathToFileURL(htmlPath).href, { waitUntil: "load" });
await tab.evaluate(() => document.fonts.ready);
const footer = `<div style="width:100%;font-size:7.5pt;color:#666;text-align:center;font-family:'DejaVu Serif',serif;">
Arithmetic Dynamical Tomography — draft manuscript · <span class="pageNumber"></span> / <span class="totalPages"></span></div>`;
await tab.pdf({
  path: outPath,
  format: "A4",
  printBackground: true,
  displayHeaderFooter: true,
  headerTemplate: "<span></span>",
  footerTemplate: footer,
  margin: { top: "20mm", bottom: "20mm", left: "21mm", right: "21mm" },
  outline: true,
  tagged: true,
});
await browser.close();
console.log(`wrote ${outPath} (${math.length} formulas)`);
