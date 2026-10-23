"""Small command router; training and inference remain explicit opt-in operations."""
import argparse
import json
import os
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, add_help=False)
    parser.add_argument('--root', help='Research checkout (or LATEX_SFT_ROOT)')
    parser.add_argument('command', nargs='?', choices=('train', 'evaluate', 'score', 'infer', 'data'))
    args, rest = parser.parse_known_args(argv)
    if args.command is None:
        if rest and not any(flag in rest for flag in ('-h', '--help')):
            parser.error('a command is required')
        parser.print_help()
        return
    wants_help = any(flag in rest for flag in ('-h', '--help'))
    if args.root:
        os.environ['LATEX_SFT_ROOT'] = args.root
    if args.command in {'train', 'evaluate'}:
        from latex_sft.experiments import run_v5_experiment as workflow
        from latex_sft.paths import repository_root
        if not wants_help:
            workflow.ROOT = repository_root()
        if not any(a == '--data-version' or a.startswith('--data-version=') for a in rest):
            rest += ['--data-version', 'v5.2']
        workflow.main([args.command, *rest])
    elif args.command == 'data':
        from latex_sft.experiments.run_v5_experiment import verify_dataset
        from latex_sft.experiments.provenance import verify_snapshot
        from latex_sft.paths import repository_root
        data = argparse.ArgumentParser(prog='latex-sft data')
        data.add_argument('action', choices=('verify',))
        data.add_argument('--data-version', choices=('v5', 'v5.2'), default='v5.2')
        options = data.parse_args(rest)
        root = repository_root()
        verify_snapshot(root)
        print(json.dumps(verify_dataset(root, root/'training/data'/options.data_version,
                                        options.data_version), ensure_ascii=False, indent=2))
    else:
        if args.command == 'score':
            from latex_sft.evaluation import evaluate_latex as command
        else:
            from latex_sft.experiments import run_lora_inference as command
            if not wants_help and not any(a == '--eval-file' or a.startswith('--eval-file=') for a in rest):
                from latex_sft.paths import repository_root
                rest += ['--eval-file', str(repository_root()/'training/data/v5.2/latex_formula_eval_clean.jsonl')]
        original = sys.argv
        try:
            sys.argv = ['latex-sft '+args.command, *rest]
            command.main()
        finally:
            sys.argv = original


if __name__ == '__main__':
    main()
