import re, pathlib

t = pathlib.Path("DREHBUCH_V4.md").read_text(encoding="utf-8")
b = t.split("## Vollstaendiger Sprechertext")[1].split("## Endregel")[0]
k = re.sub(r"^#+.*$", "", b, flags=re.M)
w = k.split()

print(f"Woerter {len(w)} | Laufzeit {len(w)/140:.1f} min @140WPM / {len(w)/130:.1f} @130")
print(f"Zitate {k.count(chr(8222))} | Jahreszahlen {len(set(re.findall(r'1[5-9]\\d\\d|20\\d\\d', k)))}")

ges = 0
akte = re.findall(r"### (S\d)[^\n]*\n(.*?)(?=\n###|\Z)", b, re.S)
tot = sum(len(x[1].split()) for x in akte)

for name, txt in akte:
    n = len(txt.split())
    print(f"  {name} {n:>4} W  {ges/tot*100:>5.1f}%-{(ges+n)/tot*100:>5.1f}%")
    ges += n
