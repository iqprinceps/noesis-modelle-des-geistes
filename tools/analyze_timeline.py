import json
from pathlib import Path

PROD = Path('06_PRODUCTION/EP03_PEAR')
TIMELINE = PROD / 'timeline' / 'EP03_V2_timeline.json'

timeline = json.loads(TIMELINE.read_text(encoding='utf-8'))

print('Timeline-Analyse:')
print('Gesamt-Shots:', len(timeline))
print()

# Find very short shots (< 1.5s)
short = [r for r in timeline if r['duration'] < 1.5]
print('Sehr kurze Shots (< 1.5s):', len(short))
for r in short[:10]:
    anchor = r['anchor'][:50]
    print(f'  {r["shot_id"]}: {r["duration"]:.2f}s - {anchor}')

print()

# Find very long shots (> 8s)
long = [r for r in timeline if r['duration'] > 8]
print('Sehr lange Shots (> 8s):', len(long))
for r in long[:10]:
    anchor = r['anchor'][:50]
    print(f'  {r["shot_id"]}: {r["duration"]:.2f}s - {anchor}')

print()

# Find rapid sequences (3+ shots in < 5s)
rapid_count = 0
for i in range(len(timeline)-2):
    total = timeline[i+2]['end'] - timeline[i]['start']
    if total < 5 and timeline[i]['duration'] < 2 and timeline[i+1]['duration'] < 2:
        rapid_count += 1
        if rapid_count <= 3:
            print(f'Rapid sequence at shot {i+1}:')
            for j in range(3):
                anchor = timeline[i+j]['anchor'][:40]
                print(f'  {timeline[i+j]["shot_id"]}: {timeline[i+j]["duration"]:.1f}s - {anchor}')
            print()

print('Rapid sequences total:', rapid_count)
