import json
from pathlib import Path

PROD = Path('06_PRODUCTION/EP03_PEAR')
TIMELINE = PROD / 'timeline' / 'EP03_V2_timeline.json'

timeline = json.loads(TIMELINE.read_text(encoding='utf-8'))

# Fix gaps: extend each segment to meet the next one
print('Fixe Lücken zwischen Segmenten...')

fixed = []
for i, r in enumerate(timeline):
    entry = dict(r)
    
    # If there's a gap to the next segment, extend this one
    if i < len(timeline) - 1:
        next_start = timeline[i+1]['start']
        if entry['end'] < next_start - 0.1:  # Gap > 0.1s
            # Extend to next segment start
            entry['end'] = next_start
            entry['duration'] = round(entry['end'] - entry['start'], 3)
    
    fixed.append(entry)

# Also extend last segment to voice end (609.8s)
if fixed:
    voice_end = 609.8
    last = fixed[-1]
    if last['end'] < voice_end:
        last['end'] = voice_end
        last['duration'] = round(last['end'] - last['start'], 3)

# Save fixed timeline
TIMELINE.write_text(json.dumps(fixed, ensure_ascii=False, indent=2) + "\n", encoding='utf-8')

# Report
print(f'Gefixte Segmente: {len(fixed)}')
print(f'Timeline Ende: {fixed[-1]["end"]:.1f}s')

# Check for remaining gaps
gaps = 0
for i in range(len(fixed)-1):
    gap = fixed[i+1]['start'] - fixed[i]['end']
    if gap > 0.1:
        gaps += 1
        print(f'  Lücke bei {fixed[i]["shot_id"]}: {gap:.1f}s')

if gaps == 0:
    print('Keine Lücken mehr!')
