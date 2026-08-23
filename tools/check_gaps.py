import json
from pathlib import Path

PROD = Path('06_PRODUCTION/EP03_PEAR')
TIMELINE = PROD / 'timeline' / 'EP03_V2_timeline.json'

timeline = json.loads(TIMELINE.read_text(encoding='utf-8'))

# Check the gaps between segments
total_gap = 0
for i in range(len(timeline)-1):
    gap = timeline[i+1]['start'] - timeline[i]['end']
    if gap > 0.1:
        total_gap += gap

last_end = timeline[-1]['end']
sum_dur = sum(r['duration'] for r in timeline)

print(f'Timeline Ende: {last_end:.1f}s ({last_end/60:.1f} Min)')
print(f'Summe Segmente: {sum_dur:.1f}s ({sum_dur/60:.1f} Min)')
print(f'Gesamtluecken: {total_gap:.1f}s ({total_gap/60:.1f} Min)')
print(f'Differenz: {last_end - sum_dur:.1f}s')
