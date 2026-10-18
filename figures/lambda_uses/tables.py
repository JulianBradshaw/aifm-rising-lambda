# Per-use AC shifts from attrib2_raw.json (all 2^5 on/off combinations of λ's use sites).
import json, itertools, math, csv
S = ['anchor', 'dynamics', 'history', 'eta', 'cap']
R = json.load(open('attrib2_raw.json')); D = {(r['mode'], r['target'], frozenset(r['subset'])): r for r in R}
rows = []
for mode in ['uplift-solved', 'time-horizon', 'revenue']:
    for t in [0.65, 0.8, 1.0]:
        v = lambda X: D[(mode, t, frozenset(X))]['ac']
        base, full = v([]), v(S); n = len(S)
        for s in S:
            o = [x for x in S if x != s]
            sh = sum(math.factorial(len(c))*math.factorial(n-len(c)-1)/math.factorial(n)*(v(list(c)+[s])-v(c))
                     for k in range(n) for c in itertools.combinations(o, k))
            rows.append(dict(anchor_mode=mode, lambda_from=0.5, lambda_to=t, use=s,
                ac_lambda05=round(base, 4), ac_lambda_to=round(full, 4), total_months=round(12*(full-base), 2),
                months_alone=round(12*(v([s])-base), 2), months_last=round(12*(full-v(o)), 2), months_shapley=round(12*sh, 2),
                f_now_lambda05=round(D[(mode,t,frozenset())]['f_now'], 3), f_now_use_alone=round(D[(mode,t,frozenset([s]))]['f_now'], 3)))
w = csv.DictWriter(open('lambda_uses_ac.csv', 'w', newline=''), fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(len(rows))
