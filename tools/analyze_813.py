import json
from pathlib import Path

PROD = Path('06_PRODUCTION/EP03_PEAR')
TIMELINE = PROD / 'timeline' / 'EP03_V2_timeline.json'

timeline = json.loads(TIMELINE.read_text(encoding='utf-8'))

# Check what happens around 8:13 (493 seconds)
print('Segmente um 8:13 (493s):')
for r in timeline:
    if 480 <= r['start'] <= 520:
        anchor = r['anchor'][:50]
        print(f'  {r["shot_id"]}: {r["start"]:.1f}s - {r["end"]:.1f}s ({r["duration"]:.1f}s) - {anchor}')

print()
print('Letzte 10 Segmente:')
for r in timeline[-10:]:
    anchor = r['anchor'][:50]
    print(f'  {r["shot_id"]}: {r["start"]:.1f}s - {r["end"]:.1f}s ({r["duration"]:.1f}s) - {anchor}')

print()
print(f'Timeline Ende: {timeline[-1]["end"]:.1f}s')
print(f'Voice Dauer: 609.8s')
print(f'Differenz: {609.8 - timeline[-1]["end"]:.1f}s')
