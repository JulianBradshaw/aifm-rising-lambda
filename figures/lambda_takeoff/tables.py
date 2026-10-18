# Per-use shifts in takeoff (AC -> ASI), ASI date and AC date from attrib_raw.json:
# Shapley value over all 2^5 on/off combinations, plus switched-first and switched-last.
import json, itertools, math, csv
S = ['anchor', 'dynamics', 'history', 'eta', 'cap']
R = json.load(open('attrib_raw.json'))
D = {(r['asymptote'], r['mode'], r['target'], frozenset(r['subset'])): r for r in R}
MEAS = {'takeoff': lambda r: r['asi'] - r['ac'], 'asi': lambda r: r['asi'], 'ac': lambda r: r['ac']}
rows = []
for cap in ['15', '100', '1e8']:
    for mode in ['uplift-solved', 'time-horizon', 'revenue']:
        for t in [0.65, 1.0]:
            for meas, f in MEAS.items():
                v = lambda X: f(D[(cap, mode, t, frozenset(X))])
                base, full = v([]), v(S); n = len(S)
                for s in S:
                    o = [x for x in S if x != s]
                    sh = sum(math.factorial(len(c)) * math.factorial(n - len(c) - 1) / math.factorial(n) * (v(list(c) + [s]) - v(c))
                             for k in range(n) for c in itertools.combinations(o, k))
                    rows.append(dict(asymptote=cap, anchor_mode=mode, lambda_from=0.5, lambda_to=t, measure=meas, use=s,
                        value_lambda05=round(base, 4), value_lambda_to=round(full, 4), total_months=round(12 * (full - base), 2),
                        months_alone=round(12 * (v([s]) - base), 2), months_last=round(12 * (full - v(o)), 2),
                        months_shapley=round(12 * sh, 2)))
w = csv.DictWriter(open('lambda_uses_takeoff.csv', 'w', newline=''), fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
for r in rows:
    if r['lambda_to'] == 1.0 and r['measure'] != 'ac':
        print(r['asymptote'], r['anchor_mode'], r['measure'], r['use'], r['months_shapley'], (r['months_alone'], r['months_last']), 'net', r['total_months'])
