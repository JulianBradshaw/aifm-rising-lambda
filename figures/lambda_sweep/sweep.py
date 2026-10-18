import csv
from aifm import preset, run
p = preset('daniel-08-16-26'); PD = p['present_day']
rows = []
for setting, pd in [('native present day 2026.578', None), ('present day 2025.6', 2025.6)]:
    for k in range(15):
        lam = round(0.3 + 0.05*k, 2)
        q = dict(p, parallel_penalty=lam)
        if pd: q['present_day'] = pd
        ac, asi, err = run(q)
        rows.append(dict(preset='daniel-08-16-26', setting=setting, parallel_penalty=lam,
            ac_year=round(ac,4), asi_year=round(asi,4),
            months_aug2026_to_ac=round((ac-PD)*12,2), months_ac_to_asi=round((asi-ac)*12,2)))
        print(rows[-1], flush=True)
w = csv.DictWriter(open('lambda_sweep.csv','w',newline=''), fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
