import json
from pathlib import Path

PROD = Path('06_PRODUCTION/EP03_PEAR')
TIMELINE = PROD / 'timeline' / 'EP03_V2_timeline.json'

timeline = json.loads(TIMELINE.read_text(encoding='utf-8'))

# Fix last segment if negative duration
last = timeline[-1]
if last['duration'] < 0:
    last['duration'] = 2.0
    last['end'] = last['start'] + 2.0
    print('Fixed last segment: 2.0s')

# Save
TIMELINE.write_text(json.dumps(timeline, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('Timeline saved')
print('Last segment:', last['shot_id'], last['start'], last['end'], last['duration'])
