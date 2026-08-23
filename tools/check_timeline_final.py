import json
from pathlib import Path

PROD = Path('06_PRODUCTION/EP03_PEAR')
TIMELINE = PROD / 'timeline' / 'EP03_V2_timeline.json'

timeline = json.loads(TIMELINE.read_text(encoding='utf-8'))

# Check total duration
total = sum(r['duration'] for r in timeline)
last_end = timeline[-1]['end']

print(f'Summe Segmente: {total:.1f}s')
print(f'Letztes Ende: {last_end:.1f}s')
print(f'Voice: 609.8s')

# Check for gaps
gaps = []
for i in range(len(timeline)-1):
    gap = timeline[i+1]['start'] - timeline[i]['end']
    if gap > 0.1:
        gaps.append((i, gap))

print(f'Lücken: {len(gaps)}')
for i, gap in gaps[:5]:
    shot_id = timeline[i]['shot_id']
    print(f'  Nach {shot_id}: {gap:.1f}s')

# Check segment durations
print(f'\nErste 5 Segmente:')
for r in timeline[:5]:
    print(f'  {r["shot_id"]}: {r["start"]:.1f}s - {r["end"]:.1f}s ({r["duration"]:.1f}s)')

print(f'\nLetzte 5 Segmente:')
for r in timeline[-5:]:
    print(f'  {r["shot_id"]}: {r["start"]:.1f}s - {r["end"]:.1f}s ({r["duration"]:.1f}s)')
