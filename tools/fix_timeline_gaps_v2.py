import json
from pathlib import Path

PROD = Path('06_PRODUCTION/EP03_PEAR')
TIMELINE = PROD / 'timeline' / 'EP03_V2_timeline.json'

timeline = json.loads(TIMELINE.read_text(encoding='utf-8'))

print('Fixe Timeline-Lücken...')

# Create new timeline with no gaps
fixed = []
for i, r in enumerate(timeline):
    entry = dict(r)
    
    # Start time stays the same
    # End time = start of next segment (or voice end for last)
    if i < len(timeline) - 1:
        entry['end'] = timeline[i+1]['start']
    else:
        entry['end'] = 609.8  # Voice end
    
    entry['duration'] = round(entry['end'] - entry['start'], 3)
    fixed.append(entry)

# Save
TIMELINE.write_text(json.dumps(fixed, ensure_ascii=False, indent=2) + "\n", encoding='utf-8')

# Verify
total = sum(r['duration'] for r in fixed)
last_end = fixed[-1]['end']

print(f'Gefixte Segmente: {len(fixed)}')
print(f'Summe Dauern: {total:.1f}s')
print(f'Letztes Ende: {last_end:.1f}s')

# Check for remaining gaps
gaps = 0
for i in range(len(fixed)-1):
    gap = fixed[i+1]['start'] - fixed[i]['end']
    if abs(gap) > 0.01:
        gaps += 1

print(f'Verbleibende Lücken: {gaps}')
