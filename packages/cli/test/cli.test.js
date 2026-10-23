import test, { after, before } from 'node:test';
import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { spawn } from 'node:child_process';
import { once } from 'node:events';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs, run } from '../lib/cli.js';
import { Readable } from 'node:stream';

const bin = fileURLToPath(new URL('../bin/qwen-latex.js', import.meta.url));
let server, baseUrl, directory;
const requests = [];
const completion = (text = 'x^2 + y^2', finish = 'stop') => ({ model: 'test-model', choices: [{ message: { content: text }, finish_reason: finish }], usage: { completion_tokens: 9 } });
before(async () => {
  directory = await mkdtemp(join(tmpdir(), 'qwen-latex-test-'));
  server = createServer(async (req, res) => {
    let raw = '';
    for await (const part of req) raw += part;
    const body = raw ? JSON.parse(raw) : undefined;
    requests.push({ path: req.url, method: req.method, body });
    if (body?.model === 'slow') return;
    if (body?.model === 'http-error') { res.writeHead(503); res.end('do not leak backend details'); return; }
    if (body?.model === 'invalid-json') { res.end('oops'); return; }
    if (body?.model === 'invalid-completion') { res.end(JSON.stringify({ choices: [] })); return; }
    if (req.url === '/invalid/models') { res.end(JSON.stringify({ data: [null] })); return; }
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify(req.url.endsWith('/models') ? { data: [{ id: 'test-model' }, { id: 'second' }] } : completion(undefined, body?.model === 'length' ? 'length' : 'stop')));
  });
  server.listen(0, '127.0.0.1');
  await once(server, 'listening');
  baseUrl = `http://127.0.0.1:${server.address().port}/v1`;
});
after(async () => {
  server.closeAllConnections();
  server.close();
  await rm(directory, { recursive: true, force: true });
});
function child(args, input = '', env = {}) {
  const environment = { ...process.env };
  delete environment.QWEN_LATEX_MODEL;
  delete environment.QWEN_LATEX_BASE_URL;
  const process_ = spawn(process.execPath, [bin, ...args], { env: { ...environment, ...env }, stdio: ['pipe', 'pipe', 'pipe'], timeout: 10000 });
  let stdout = '', stderr = '';
  process_.stdout.on('data', chunk => { stdout += chunk; });
  process_.stderr.on('data', chunk => { stderr += chunk; });
  process_.stdin.end(input);
  const done = new Promise((resolve, reject) => {
    process_.once('error', reject);
    process_.once('close', (code, signal) => resolve({ code, signal, stdout, stderr }));
  });
  return { process: process_, done };
}
function correct(args = [], input = '', env = {}) {
  return child(['correct', '--base-url', baseUrl, '--model', 'test-model', ...args], input, env).done;
}

test('positional text: exact shared prompt, default budget, clean stdout', async () => {
  const result = await correct(['x平方加y平方']);
  assert.deepEqual(result, { code: 0, signal: null, stdout: 'x^2 + y^2\n', stderr: '' });
  const request = requests.at(-1);
  assert.equal(request.path, '/v1/chat/completions');
  assert.equal(request.method, 'POST');
  assert.deepEqual(request.body, {
    model: 'test-model', messages: [{ role: 'system', content: await readFile(new URL('../../../src/latex_sft/core/resources/latex-correction.txt', import.meta.url), 'utf8') }, { role: 'user', content: 'x平方加y平方' }], stream: false, temperature: 0, max_tokens: 256,
  });
});

test('UTF-8 file is one complete request', async () => {
  const path = join(directory, 'input with spaces.txt');
  const input = '第一行 x\n第二行 y\n';
  await writeFile(path, input);
  assert.equal((await correct(['--file', path])).code, 0);
  assert.equal(requests.at(-1).body.messages[1].content, input);
});

test('stdin is preserved and JSON includes endpoint usage', async () => {
  const input = 'x+y\n第二行';
  const result = await correct(['--json', '--max-tokens', '512'], input);
  assert.equal(result.code, 0);
  assert.equal(result.stderr, '');
  assert.deepEqual(JSON.parse(result.stdout), { text: 'x^2 + y^2', model: 'test-model', finish_reason: 'stop', usage: { completion_tokens: 9 } });
  assert.equal(requests.at(-1).body.max_tokens, 512);
  assert.equal(requests.at(-1).body.messages[1].content, input);
});

test('model/base environment and flags override them', async () => {
  const env = { QWEN_LATEX_MODEL: 'environment-model', QWEN_LATEX_BASE_URL: baseUrl };
  const result = await child(['correct', 'x'], '', env).done;
  assert.equal(result.code, 0);
  assert.equal(requests.at(-1).body.model, 'environment-model');
  assert.equal((await correct(['x'], '', { QWEN_LATEX_MODEL: 'wrong-model', QWEN_LATEX_BASE_URL: 'http://127.0.0.1:1' })).code, 0);
  assert.equal(requests.at(-1).body.model, 'test-model');
});

test('models output and JSON mode', async () => {
  const result = await child(['models', '--base-url', baseUrl]).done;
  assert.deepEqual(result, { code: 0, signal: null, stdout: 'test-model\nsecond\n', stderr: '' });
  const json = await child(['models', '--base-url', baseUrl, '--json']).done;
  assert.deepEqual(JSON.parse(json.stdout), { data: [{ id: 'test-model' }, { id: 'second' }] });
  const malformed = await child(['models', '--base-url', baseUrl.replace('/v1', '/invalid')]).done;
  assert.equal(malformed.code, 1);
  assert.match(malformed.stderr, /invalid model list/);
});

test('input sources conflict, empty input, invalid UTF-8, missing file', async () => {
  for (const args of [['x', '--file', 'ignored'], ['x'], ['--file', 'ignored']]) {
    const result = await correct(args, 'piped');
    assert.equal(result.code, 1);
    assert.equal(result.stdout, '');
    assert.match(result.stderr, /only one input/);
  }
  assert.match((await correct()).stderr, /Input is empty/);
  assert.match((await correct([], Buffer.from([0xff]))).stderr, /valid UTF-8/);
  const path = join(directory, 'invalid.txt');
  await writeFile(path, Buffer.from([0xff]));
  assert.match((await correct(['--file', path])).stderr, /valid UTF-8/);
  assert.equal((await correct(['--file', join(directory, 'missing')])).code, 1);
});

test('input/options are validated before network access', async () => {
  const count = requests.length;
  assert.equal((await child(['correct', 'x']).done).code, 1);
  for (const args of [['--max-tokens', '0'], ['--max-tokens', '1.5'], ['--max-tokens', '-2'], ['--timeout-ms', '0'], ['--timeout-ms', '2147483648'], ['--unknown'], ['--file'], ['x', 'y']]) {
    assert.equal((await correct(args)).code, 1);
  }
  assert.throws(() => parseArgs(['correct', '--model', 'a', '--model', 'b', 'x'], {}), /Duplicate/);
  assert.throws(() => parseArgs(['models', '--base-url', 'file:///tmp'], {}), /HTTP/);
  assert.throws(() => parseArgs(['models', '--base-url', 'http://user:secret@localhost'], {}), /credentials/);
  assert.throws(() => parseArgs(['models', '--max-tokens', '4'], {}), /does not accept/);
  assert.equal(requests.length, count);
});

test('HTTP error, malformed JSON/completion fail cleanly and do not retry', async () => {
  for (const [model, message] of [['http-error', /HTTP 503/], ['invalid-json', /invalid JSON/], ['invalid-completion', /invalid completion/]]) {
    const count = requests.length;
    const result = await child(['correct', 'x', '--base-url', baseUrl, '--model', model]).done;
    assert.equal(result.code, 1);
    assert.equal(result.stdout, '');
    assert.match(result.stderr, message);
    assert.equal(requests.length, count + 1);
  }
});

test('timeout aborts a request without retry', async () => {
  const count = requests.length;
  const result = await child(['correct', 'x', '--base-url', baseUrl, '--model', 'slow', '--timeout-ms', '1000']).done;
  assert.equal(result.code, 1);
  assert.match(result.stderr, /timed out/);
  assert.equal(requests.length, count + 1);
});

test('length finish preserves response but fails in text and JSON modes', async () => {
  for (const extra of [[], ['--json']]) {
    const result = await child(['correct', 'x', '--base-url', baseUrl, '--model', 'length', ...extra]).done;
    assert.equal(result.code, 2);
    assert.match(result.stderr, /truncated/);
    if (extra.length) assert.equal(JSON.parse(result.stdout).finish_reason, 'length');
    else assert.equal(result.stdout, 'x^2 + y^2\n');
  }
});

test('SIGINT handler aborts request and returns 130 (portable signal simulation)', async () => {
  let stdout = '', stderr = '';
  const count = requests.length;
  const result = run(['correct', 'x', '--base-url', baseUrl, '--model', 'slow'], {
    env: {}, stdin: Readable.from([]), stdout: { write: value => { stdout += value; } }, stderr: { write: value => { stderr += value; } },
  });
  // Wait for the request, not a startup-duration guess. process.emit works on Windows too.
  let code;
  const deadline = Date.now() + 5000;
  try {
    while (requests.length === count) {
      assert.ok(Date.now() < deadline, 'Mock request did not arrive within 5 seconds');
      await new Promise(resolve => setTimeout(resolve, 10));
    }
  } finally {
    process.emit('SIGINT');
    code = await result;
  }
  assert.equal(code, 130);
  assert.equal(stdout, '');
  assert.equal(stderr, 'Request interrupted.\n');
  assert.equal(requests.length, count + 1);
});

test('help works without model or endpoint', async () => {
  const result = await child(['--help']).done;
  assert.equal(result.code, 0);
  assert.match(result.stdout, /qwen-latex correct/);
  assert.equal(result.stderr, '');
});
