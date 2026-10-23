import { readFile, mkdir, writeFile } from 'node:fs/promises';

// This is a build artifact, not a separately maintained prompt.
const source = new URL('../../../src/latex_sft/core/resources/latex-correction.txt', import.meta.url);
const destination = new URL('../assets/latex-correction.txt', import.meta.url);
const bytes = await readFile(source);
if (!bytes.length) throw new Error('Canonical correction prompt is empty');
await mkdir(new URL('../assets/', import.meta.url), { recursive: true });
await writeFile(destination, bytes);
if (!bytes.equals(await readFile(destination))) throw new Error('Packaged prompt differs from canonical prompt');
