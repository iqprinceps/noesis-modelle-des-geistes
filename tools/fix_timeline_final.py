import json
from pathlib import Path

PROD = Path('06_PRODUCTION/EP03_PEAR')
TIMELINE = PROD / 'timeline' / 'EP03_V2_timeline.json'
VOICE_END = 609.8  # Voice duration in seconds

# Load current timeline
timeline = json.loads(TIMELINE.read_text(encoding='utf-8'))

print(f'Original Timeline: {len(timeline)} Segmente')
print(f'Original Ende: {timeline[-1]["end"]:.1f}s')

# Fix: Each segment starts at its original start time
# and ends at the start of the next segment (or voice end for last)
fixed = []
for i, r in enumerate(timeline):
    entry = dict(r)
    
    # Keep original start time
    # End time = start of next segment
    if i < len(timeline) - 1:
        entry['end'] = timeline[i+1]['start']
    else:
        entry['end'] = VOICE_END
    
    # Calculate duration
    entry['duration'] = round(entry['end'] - entry['start'], 3)
    
    # Ensure minimum duration of 2.0 seconds
    if entry['duration'] < 2.0:
        entry['duration'] = 2.0
        entry['end'] = round(entry['start'] + 2.0, 3)
    
    fixed.append(entry)

# Verify no gaps
gaps = 0
for i in range(len(fixed)-1):
    gap = fixed[i+1]['start'] - fixed[i]['end']
    if abs(gap) > 0.01:
        gaps += 1
        print(f'  Lücke bei {fixed[i]["shot_id"]}: {gap:.3f}s')

# Save fixed timeline
TIMELINE.write_text(json.dumps(fixed, ensure_ascii=False, indent=2) + "\n", encoding='utf-8')

# Report
total_dur = sum(r['duration'] for r in fixed)
last_end = fixed[-1]['end']

print(f'\nGefixte Timeline:')
print(f'  Segmente: {len(fixed)}')
print(f'  Summe Dauern: {total_dur:.1f}s')
print(f'  Letztes Ende: {last_end:.1f}s')
print(f'  Voice Ende: {VOICE_END:.1f}s')
print(f'  Lücken: {gaps}')

# Show first and last segments
print(f'\nErste 3 Segmente:')
for r in fixed[:3]:
    print(f'  {r["shot_id"]}: {r["start"]:.1f}s - {r["end"]:.1f}s ({r["duration"]:.1f}s)')

print(f'\nLetzte 3 Segmente:')
for r in fixed[-3:]:
    print(f'  {r["shot_id"]}: {r["start"]:.1f}s - {r["end"]:.1f}s ({r["duration"]:.1f}s)')
