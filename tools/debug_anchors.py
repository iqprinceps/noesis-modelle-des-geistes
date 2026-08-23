import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\iQPrinceps\Documents\Codex\Youtube Modelle des Geistes\06_PRODUCTION\EP03_PEAR\07_VOICE_SCRIPT_CLEAN_V2.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Find similar text
searches = [
    'Tausend',
    'dafür sitzt',
    'Kiste ansehen',
    'angestrengt habe',
    'Polystyrolkugeln',
    'Nylonstiften',
    'übereinanderlegt',
    'Kommentare',
    'schreiben das später',
    'Zehnerpotenz',
    'größer die Studie',
    'Replikation selbst',
    'hat nicht funktioniert',
    'haben das auch veröffentlicht',
    'sie tun wollten',
]

for search in searches:
    idx = text.find(search)
    if idx >= 0:
        print(f'Found "{search}" at {idx}: {repr(text[max(0,idx-20):idx+50])}')
    else:
        print(f'NOT found: {search}')
