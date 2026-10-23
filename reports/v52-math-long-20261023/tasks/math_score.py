from answer_audit import reliable_last_boxed_content, looks_truncated
from lm_eval.tasks.hendrycks_math.utils import is_equiv, process_results as old_score


def process_results(doc, results):
    answer = reliable_last_boxed_content(results[0])
    return {
        'exact_match': int(answer is not None and is_equiv(answer, str(doc['answer']))),
        'legacy_exact_match': old_score(doc, results)['exact_match'],
        'unverified': int(answer is None),
        'suspected_truncation': int(looks_truncated(results[0])),
    }
