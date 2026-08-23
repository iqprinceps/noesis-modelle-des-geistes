import json
from pathlib import Path

PROD = Path('06_PRODUCTION/EP03_PEAR')
TIMELINE = PROD / 'timeline' / 'EP03_V2_timeline.json'
VOICE_END = 609.8

# Load current timeline
timeline = json.loads(TIMELINE.read_text(encoding='utf-8'))

print(f'Original: {len(timeline)} Segmente')

# Create completely new timeline with no gaps or overlaps
# Each segment starts where the previous one ended
fixed = []
current_time = 0.0

for i, r in enumerate(timeline):
    entry = dict(r)
    
    # Start = end of previous segment
    entry['start'] = round(current_time, 3)
    
    # Keep original duration (but ensure minimum 2.0s)
    dur = max(2.0, r['duration'])
    
    # For last segment, extend to voice end
    if i == len(timeline) - 1:
        dur = VOICE_END - current_time
    
    entry['duration'] = round(dur, 3)
    entry['end'] = round(current_time + dur, 3)
    
    fixed.append(entry)
    current_time += dur

# Save
TIMELINE.write_text(json.dumps(fixed, ensure_ascii=False, indent=2) + "\n", encoding='utf-8')

# Verify
print(f'Gefixt: {len(fixed)} Segmente')
print(f'Letztes Ende: {fixed[-1]["end"]:.1f}s')
print(f'Voice: {VOICE_END:.1f}s')

# Check for gaps
gaps = 0
for i in range(len(fixed)-1):
    gap = fixed[i+1]['start'] - fixed[i]['end']
    if abs(gap) > 0.01:
        gaps += 1

print(f'Lücken/Überlappungen: {gaps}')

# Show segments
print(f'\nErste 3:')
for r in fixed[:3]:
    print(f'  {r["shot_id"]}: {r["start"]:.1f}s - {r["end"]:.1f}s ({r["duration"]:.1f}s)')

print(f'\nLetzte 3:')
for r in fixed[-3:]:
    print(f'  {r["shot_id"]}: {r["start"]:.1f}s - {r["end"]:.1f}s ({r["duration"]:.1f}s)')
