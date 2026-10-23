from math_score import process_results
from answer_audit import reliable_last_boxed_content

def score(text):
    return process_results({'answer':'42','solution':r'\boxed{42}'}, [text])
assert score(r'Reasoning. \boxed{42}')['exact_match'] == 1
assert score(r'\boxed{43}')['exact_match'] == 0
assert score(r'\boxed{42')['unverified'] == 1
assert score(r'\boxed{42} but the answer is 43')['unverified'] == 1
assert reliable_last_boxed_content(r'\boxed{\frac{1}{2}}') == r'\frac{1}{2}'
print('Answer extraction: 5 checks passed')
