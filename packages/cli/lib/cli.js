import { readFile } from 'node:fs/promises';
import { TextDecoder } from 'node:util';

export const help = `Usage:
  qwen-latex correct "text" --model <installed-model>
  qwen-latex correct --file input.txt --model <installed-model>
  cat input.txt | qwen-latex correct --model <installed-model>
  qwen-latex models

Options:
  --model NAME       Required for correct; or QWEN_LATEX_MODEL
  --base-url URL     Default http://localhost:11434/v1; or QWEN_LATEX_BASE_URL
  --max-tokens N     Positive integer output budget (default 256)
  --timeout-ms N     Positive integer request timeout (default 120000)
  --json             Machine-readable response
  --help            Show help

Calls your existing Ollama endpoint. No model downloads or server startup.
Generated formulas are not independently verified for mathematical correctness.
`;

function integer(value, name) {
  if (!/^[1-9]\d*$/.test(value) || !Number.isSafeInteger(Number(value))) {
    throw new Error(`${name} must be a positive integer`);
  }
  return Number(value);
}

export function parseArgs(argv, env = process.env) {
  const options = { model: env.QWEN_LATEX_MODEL, baseUrl: env.QWEN_LATEX_BASE_URL || 'http://localhost:11434/v1', maxTokens: 256, timeoutMs: 120000, json: false };
  if (argv.length === 0 || argv[0] === '--help' || argv[0] === '-h') return { help: true };
  options.command = argv[0];
  if (!['correct', 'models'].includes(options.command)) throw new Error(`Unknown command: ${options.command}`);
  const positional = [];
  const seen = new Set();
  for (let i = 1; i < argv.length; i++) {
    const argument = argv[i];
    if (argument === '--help' || argument === '-h') return { help: true };
    if (argument === '--') { positional.push(...argv.slice(i + 1)); break; }
    if (!argument.startsWith('--')) { positional.push(argument); continue; }
    if (seen.has(argument)) throw new Error(`Duplicate option: ${argument}`);
    seen.add(argument);
    if (argument === '--json') { options.json = true; continue; }
    if (!['--model', '--base-url', '--max-tokens', '--timeout-ms', '--file'].includes(argument)) throw new Error(`Unknown option: ${argument}`);
    const value = argv[++i];
    if (value === undefined || value.startsWith('--')) throw new Error(`Missing value for ${argument}`);
    if (argument === '--model') options.model = value;
    if (argument === '--base-url') options.baseUrl = value;
    if (argument === '--file') options.file = value;
    if (argument === '--max-tokens') options.maxTokens = integer(value, argument);
    if (argument === '--timeout-ms') options.timeoutMs = integer(value, argument);
  }
  if (options.timeoutMs > 2147483647) throw new Error('--timeout-ms must be at most 2147483647');
  if (positional.length > 1) throw new Error('Quote input text as one argument');
  options.text = positional[0];
  if (options.command === 'models' && (positional.length || seen.has('--file') || seen.has('--model') || seen.has('--max-tokens'))) throw new Error('models does not accept correction input, --model or --max-tokens');
  if (options.command === 'correct' && !options.model?.trim()) throw new Error('Specify --model or QWEN_LATEX_MODEL with an installed model name');
  const url = new URL(options.baseUrl);
  if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password || url.search || url.hash) throw new Error('--base-url must be an HTTP(S) URL without credentials, query or fragment');
  options.baseUrl = url.href.replace(/\/+$/, '');
  return options;
}

function decode(bytes, label) {
  try { return new TextDecoder('utf-8', { fatal: true }).decode(bytes); }
  catch { throw new Error(`${label} must contain valid UTF-8`); }
}

export async function inputText(options, stdin) {
  if (options.file !== undefined && options.text !== undefined) throw new Error('Use only one input: text, --file, or stdin');
  let piped = '';
  if (!stdin.isTTY) {
    const chunks = [];
    for await (const chunk of stdin) chunks.push(Buffer.from(chunk));
    piped = decode(Buffer.concat(chunks), 'stdin');
  }
  if (piped.length && (options.file !== undefined || options.text !== undefined)) throw new Error('Use only one input: text, --file, or stdin');
  const text = options.file !== undefined ? decode(await readFile(options.file), 'Input file') : options.text ?? piped;
  if (!text.trim()) throw new Error('Input is empty; provide text, --file, or stdin');
  return text;
}

async function request(options, route, body, signal) {
  const response = await fetch(`${options.baseUrl}/${route}`, {
    method: body ? 'POST' : 'GET',
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
    signal,
  });
  if (!response.ok) throw new Error(`Ollama HTTP ${response.status} ${response.statusText}`);
  try { return await response.json(); }
  catch (error) { if (signal.aborted) throw error; throw new Error('Ollama returned invalid JSON'); }
}

export async function run(argv, { env = process.env, stdin = process.stdin, stdout = process.stdout, stderr = process.stderr } = {}) {
  const controller = new AbortController();
  let interrupted = false;
  let timedOut = false;
  let timer;
  const onInterrupt = () => { interrupted = true; controller.abort(); };
  try {
    const options = parseArgs(argv, env);
    if (options.help) { stdout.write(help); return 0; }
    // Input is collected before the HTTP timeout; an interactive terminal uses text or --file.
    const text = options.command === 'correct' ? await inputText(options, stdin) : undefined;
    process.once('SIGINT', onInterrupt);
    timer = setTimeout(() => { timedOut = true; controller.abort(); }, options.timeoutMs);
    if (options.command === 'models') {
      const response = await request(options, 'models', undefined, controller.signal);
      if (!Array.isArray(response.data) || response.data.some(item => !item || typeof item.id !== 'string')) throw new Error('Ollama returned an invalid model list');
      stdout.write(options.json ? `${JSON.stringify(response)}\n` : response.data.map(item => `${item.id}\n`).join(''));
      return 0;
    }
    const prompt = await readFile(new URL('../assets/latex-correction.txt', import.meta.url), 'utf8');
    const response = await request(options, 'chat/completions', {
      model: options.model,
      messages: [{ role: 'system', content: prompt }, { role: 'user', content: text }],
      stream: false,
      temperature: 0,
      max_tokens: options.maxTokens,
    }, controller.signal);
    const choice = response.choices?.[0];
    if (!choice || typeof choice.message?.content !== 'string' || typeof choice.finish_reason !== 'string') throw new Error('Ollama returned an invalid completion');
    const result = { text: choice.message.content, model: response.model || options.model, finish_reason: choice.finish_reason };
    if (response.usage !== undefined) result.usage = response.usage;
    stdout.write(options.json ? `${JSON.stringify(result)}\n` : `${result.text}\n`);
    if (choice.finish_reason === 'length') { stderr.write('Output truncated: model reached the token limit; increase --max-tokens if needed.\n'); return 2; }
    if (choice.finish_reason !== 'stop') { stderr.write(`Completion ended with ${choice.finish_reason}; output may be incomplete.\n`); return 2; }
    return 0;
  } catch (error) {
    stderr.write(`${interrupted ? 'Request interrupted.' : timedOut ? 'Request timed out.' : error.message}\n`);
    return interrupted ? 130 : 1;
  } finally {
    clearTimeout(timer);
    process.removeListener('SIGINT', onInterrupt);
  }
}
