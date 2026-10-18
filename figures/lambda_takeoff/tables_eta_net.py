# Shapley split of attrib_eta_net_raw.json into lambda_uses_eta_net.csv (same columns as lambda_uses_takeoff.csv).
import json, csv, itertools, math
P5 = ['anchor', 'benefit', 'history', 'etanet', 'cap']
out = json.load(open('attrib_eta_net_raw.json'))
rows = []
for meas in ['takeoff', 'asi', 'ac']:
    for mode in ['uplift-solved', 'time-horizon', 'revenue']:
        for lam in [0.65, 1.0]:
            v = {}
            for r in out:
                if r['mode'] == mode and r['lam'] == lam:
                    v[frozenset(r['subset'])] = {'takeoff': r['asi'] - r['ac'], 'asi': r['asi'], 'ac': r['ac']}[meas]
            full = frozenset(P5); n = len(P5)
            for u in P5:
                others = [x for x in P5 if x != u]; sh = 0.0
                for k in range(n):
                    for S in itertools.combinations(others, k):
                        S = frozenset(S); w = math.factorial(k) * math.factorial(n - k - 1) / math.factorial(n)
                        sh += w * (v[S | {u}] - v[S])
                rows.append(dict(measure=meas, anchor_mode=mode, asymptote='15', lambda_to=lam, use=u,
                    months_shapley=round(12 * sh, 3), months_alone=round(12 * (v[frozenset([u])] - v[frozenset()]), 3),
                    months_last=round(12 * (v[full] - v[full - {u}]), 3), value_lambda05=v[frozenset()], value_lambda_to=v[full],
                    total_months=round(12 * (v[full] - v[frozenset()]), 3)))
w = csv.DictWriter(open('lambda_uses_eta_net.csv', 'w', newline=''), fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
for r in rows:
    if r['measure'] in ('takeoff', 'asi'): print(r['measure'], r['anchor_mode'], r['lambda_to'], r['use'], r['months_shapley'], r['months_alone'], r['months_last'], r['total_months'])
