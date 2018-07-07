import sys
import csv

sys.path.append('../../generic')
from sequence import schedule, pp


src_csv, dst_csv = sys.argv[1:]
print(src_csv, dst_csv)

ways = {}

# read in csv, stick in ways dict. key = way_id. (group by way id.)
with open(src_csv) as f:
    r = csv.reader(f)
    next(r, None)

    for row in r:
        k = row[0]
        v = ways.get(k, [])
        v.append(row)
        ways[k] = v
   
# write out new csv with extra order,depth columns
with open(dst_csv, 'w') as f:
    w = csv.writer(f)
    for way in ways.values():
        order, depth = schedule(way)
        for i, seq in enumerate(way):
             seq.append(order[i])
             seq.append(depth[i])
             w.writerow(seq)

