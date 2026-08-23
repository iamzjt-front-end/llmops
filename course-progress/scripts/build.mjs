import { copyFile, mkdir } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const output = resolve(root, "dist");
const assets = [
  "index.html",
  "styles.css",
  "app.js",
  "cloud-sync.mjs",
  "progress-selection.mjs",
  "sync-config.js",
  "course-data.js",
  "favicon.svg",
];

await mkdir(output, { recursive: true });
await Promise.all(assets.map((asset) => copyFile(resolve(root, asset), resolve(output, asset))));
console.log(`build: copied ${assets.length} assets to ${output}`);
