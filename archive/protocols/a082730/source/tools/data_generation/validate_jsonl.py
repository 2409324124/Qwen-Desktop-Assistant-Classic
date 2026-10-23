import json, sys, argparse

parser = argparse.ArgumentParser()
parser.add_argument("path", default="train_mamut.jsonl", nargs="?")
args = parser.parse_args()

with open(args.path, encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            print(f'JSON decode error at line {i}: {e}')
            sys.exit(1)
        for key in ('instruction', 'input', 'output'):
            if key not in obj:
                print(f'Missing key "{key}" at line {i}')
                sys.exit(1)
print(f'All lines in {args.path} are valid.')
