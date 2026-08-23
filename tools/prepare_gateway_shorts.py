#!/usr/bin/env python3
"""Create two standalone Gateway Shorts packages, dedicated 9:16 assets and TTS batch."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "06_PRODUCTION" / "EP02_GATEWAY_SHORTS_V1"
REF = ROOT / "06_PRODUCTION" / "EP02_GATEWAY" / "reference_package"
V2 = ROOT / "06_PRODUCTION" / "EP02_GATEWAY_V2"
GEN = Path("C:/Users/iQPrinceps/.codex/generated_images/01a01443-11f8-7e03-8285-8d53dc94c0bf")
W, H = 1080, 1920
BG = (4, 17, 20)
OFF = (239, 237, 226)
CYAN = (91, 210, 211)
GOLD = (228, 178, 68)
RED = (210, 84, 70)
FONT = Path("C:/Windows/Fonts/arial.ttf")
FONT_B = Path("C:/Windows/Fonts/arialbd.ttf")
SERIF = Path("C:/Windows/Fonts/georgia.ttf")

SHORTS = {
    "SHORT01_THREE_OBSERVERS": """Drei Menschen. Ein Ziel.

Einer beobachtet es jetzt. Einer soll dasselbe Ziel aus der unmittelbaren Vergangenheit sehen. Der dritte aus der unmittelbaren Zukunft.

Das klingt erfunden. Doch genau dieser Vorschlag steht in Empfehlung H des Gateway-Berichts der U.S. Army von 1983. Anschließend sollten alle drei Angaben verglichen werden.

Der entscheidende Punkt: Das Dokument beschreibt einen Versuchsplan. Es berichtet nicht, dass dieser Versuch erfolgreich durchgeführt wurde.

Das Merkwürdige ist also nicht, dass die Army Zeitreisen bewiesen hätte. Das Merkwürdige ist, dass ein Militäranalyst Vergangenheit und Zukunft überhaupt als mögliche Beobachtungspunkte in einen konkreten Test schrieb.""",
    "SHORT02_TWO_TONES": """Links vierhundert Hertz. Rechts vierhundertzehn.

Bei der Verarbeitung kann ein pulsierender Eindruck von ungefähr zehn Hertz entstehen. Dieser binaurale Beat ist ein reales Wahrnehmungsphänomen.

Doch dann macht der Gateway-Bericht einen gewaltigen Sprung. Aus Tönen, Entspannung und Aufmerksamkeit wird die Idee, Bewusstsein könne ein größeres Informationsfeld erreichen — sogar außerhalb normaler Raum- und Zeitgrenzen.

Ein veränderter Zustand beweist das nicht. Für Informationsübertragung müsste ein verborgenes Ziel vorher feststehen, blind ausgewertet und unabhängig wiederholt werden.

Ein Effekt im Erleben ist ein Befund über Wahrnehmung. Ein korrekt beschriebenes entferntes Ziel wäre ein Befund über Information. Genau zwischen beiden liegt die Gateway-Beweislücke.""",
}

AI_SOURCES = {
    "SHORT01_THREE_OBSERVERS": [
        (GEN / "exec-9596b734-6e4d-4c22-9fa4-0a41b820f25a.png", "S01_AI01_THREE_OBSERVERS_9x16.png"),
        (GEN / "exec-fc369e0e-b546-4e41-a275-48a073dc69e7.png", "S01_AI02_TIME_OBSERVERS_9x16.png"),
    ],
    "SHORT02_TWO_TONES": [
        (GEN / "exec-7ebf0100-7996-493f-891d-e7489b8632e2.png", "S02_AI01_LISTENER_9x16.png"),
        (GEN / "exec-8b357f84-b60d-4e1d-bd3d-b524afcee4fb.png", "S02_AI02_EVIDENCE_GAP_9x16.png"),
    ],
}


def ft(path, size): return ImageFont.truetype(str(path), size)


def cover(im: Image.Image) -> Image.Image:
    scale = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.Resampling.LANCZOS)
    return im.crop(((im.width-W)//2, (im.height-H)//2, (im.width-W)//2+W, (im.height-H)//2+H))


def canvas(title, kicker="GATEWAY · U.S. ARMY REPORT · 1983"):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    d.rounded_rectangle((34, 34, W-34, H-34), 20, outline=(35, 90, 92), width=3)
    d.text((58, 65), kicker, font=ft(FONT_B, 25), fill=CYAN)
    d.multiline_text((58, 122), title, font=ft(SERIF, 57), fill=OFF, spacing=10)
    return im, d


def doc_card(source_name, crop_box, filename, title, highlights):
    page = Image.open(REF / source_name).convert("RGB"); crop = page.crop(crop_box)
    scale = min(960/crop.width, 1280/crop.height); crop = crop.resize((round(crop.width*scale), round(crop.height*scale)), Image.Resampling.LANCZOS)
    im, d = canvas(title); x=(W-crop.width)//2; y=420+(1200-crop.height)//2; im.paste(crop,(x,y))
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
    for x1,y1,x2,y2 in highlights:
        od.rounded_rectangle((x+round((x1-crop_box[0])*scale),y+round((y1-crop_box[1])*scale),x+round((x2-crop_box[0])*scale),y+round((y2-crop_box[1])*scale)),6,fill=(*GOLD,55),outline=(*GOLD,245),width=3)
    Image.alpha_composite(im.convert("RGBA"),ov).convert("RGB").save(filename,quality=96)


def observer_card(path):
    im,d=canvas("THREE OBSERVERS.\nONE TARGET.","RECOMMENDATION H")
    ys=[570,930,1290]; labels=[("PAST","FOCUS 15"),("PRESENT","NORMAL SPACE-TIME"),("FUTURE","FOCUS 21")]
    for y,(name,sub) in zip(ys,labels):
        d.ellipse((132,y-55,242,y+55),outline=CYAN,width=5); d.line((187,y+55,187,y+180),fill=CYAN,width=5)
        d.line((187,y+105,120,y+165),fill=CYAN,width=5); d.line((187,y+105,254,y+165),fill=CYAN,width=5)
        d.text((310,y-20),name,font=ft(FONT_B,46),fill=OFF); d.text((312,y+47),sub,font=ft(FONT_B,25),fill=GOLD)
        d.line((650,y+40,930,960),fill=(55,135,138),width=4)
    d.rounded_rectangle((570,865,980,1055),30,fill=GOLD); d.text((775,960),"COMPARE\nREPORTS",anchor="mm",align="center",font=ft(FONT_B,35),fill=BG)
    d.text((540,1770),"PROPOSED PROCEDURE · NO RESULT REPORTED",anchor="mm",font=ft(FONT_B,22),fill=(125,190,190))
    im.save(path,quality=96)


def beat_card(path):
    im,d=canvas("TWO TONES.\nONE PERCEIVED BEAT.","AUDITORY PHENOMENON")
    d.text((150,520),"LEFT",font=ft(FONT_B,30),fill=CYAN); d.text((150,575),"400 Hz",font=ft(FONT_B,64),fill=OFF)
    d.text((690,520),"RIGHT",font=ft(FONT_B,30),fill=CYAN); d.text((690,575),"410 Hz",font=ft(FONT_B,64),fill=OFF)
    for base,freq,color in [(830,8,CYAN),(1010,10,GOLD)]:
        pts=[]
        import math
        for x in range(80,1001,4): pts.append((x,base+75*math.sin((x-80)/920*math.pi*freq)))
        d.line(pts,fill=color,width=5)
    d.line((540,690,540,1180),fill=(80,145,145),width=4)
    d.polygon([(540,1200),(523,1165),(557,1165)],fill=GOLD)
    d.rounded_rectangle((160,1270,920,1510),28,fill=(11,34,37),outline=GOLD,width=4)
    d.text((540,1360),"≈ 10 Hz",anchor="mm",font=ft(FONT_B,78),fill=GOLD)
    d.text((540,1445),"PERCEIVED PULSE",anchor="mm",font=ft(FONT_B,28),fill=OFF)
    d.text((540,1750),"REAL PHENOMENON · LIMITED CONCLUSION",anchor="mm",font=ft(FONT_B,23),fill=CYAN)
    im.save(path,quality=96)


def evidence_card(path):
    im,d=canvas("WHERE EVIDENCE\nSTOPS", "THE CLAIM GAP")
    boxes=[(100,540,980,810,CYAN,"MEASURABLE","PERCEPTION · ATTENTION"),(100,1260,980,1530,RED,"NOT ESTABLISHED","REMOTE INFORMATION")]
    for x1,y1,x2,y2,c,h,s in boxes:
        d.rounded_rectangle((x1,y1,x2,y2),24,fill=(11,32,35),outline=c,width=4); d.text((150,y1+70),h,font=ft(FONT_B,39),fill=c); d.text((150,y1+145),s,font=ft(FONT_B,34),fill=OFF)
    d.line((540,840,540,990),fill=CYAN,width=6); d.line((540,1090,540,1230),fill=RED,width=6)
    d.line((460,995,620,1075),fill=GOLD,width=13); d.line((620,995,460,1075),fill=GOLD,width=13)
    d.text((540,1160),"NO DEMONSTRATED BRIDGE",anchor="mm",font=ft(FONT_B,25),fill=GOLD)
    d.text((540,1740),"EXPERIENCE ≠ INFORMATION TRANSFER",anchor="mm",font=ft(FONT_B,24),fill=CYAN)
    im.save(path,quality=96)


def main():
    for short, text in SHORTS.items():
        base=OUT/short; assets=base/"assets"; voice=base/"voice"; assets.mkdir(parents=True,exist_ok=True); voice.mkdir(parents=True,exist_ok=True)
        (base/"01_SCRIPT.md").write_text(f"# {short}\n\n## Voiceover\n\n{text}\n",encoding="utf-8")
        (base/"02_VOICE_SCRIPT_CLEAN.txt").write_text(text+"\n",encoding="utf-8")
        for src,name in AI_SOURCES[short]:
            if not src.is_file(): raise FileNotFoundError(src)
            cover(Image.open(src).convert("RGB")).save(assets/name,quality=96)
    s1=OUT/"SHORT01_THREE_OBSERVERS"/"assets"; s2=OUT/"SHORT02_TWO_TONES"/"assets"
    observer_card(s1/"S01_CARD01_THREE_OBSERVERS_9x16.png")
    doc_card("GW_REPORT_PDF28_RECOMMENDATIONS_H_L.png",(85,210,1440,550),s1/"S01_DOC01_RECOMMENDATION_H_9x16.png","THE ORIGINAL\nRECOMMENDATION H",[(105,240,1400,520)])
    doc_card("GW_REPORT_PDF01_HEADER.png",(70,45,1450,430),s1/"S01_DOC02_ARMY_HEADER_9x16.png","NOT A FORUM POST.\nAN ARMY REPORT.",[(300,110,1010,240),(1110,260,1385,320)])
    beat_card(s2/"S02_CARD01_BINAURAL_BEAT_9x16.png"); evidence_card(s2/"S02_CARD02_EVIDENCE_GAP_9x16.png")
    report=Image.open(ROOT/"04_ASSETS"/"02_CURATED"/"EP02_GATEWAY"/"APPROVED"/"GW_010_Exhibit_5.png").convert("RGB")
    ri, rd=canvas("THE REPORT'S\nWORLD MODEL", "ORIGINAL GATEWAY EXHIBIT"); report.thumbnail((950,1300),Image.Resampling.LANCZOS); ri.paste(report,((W-report.width)//2,420+(1300-report.height)//2)); ri.save(s2/"S02_DOC02_REPORT_MODEL_9x16.png",quality=96)
    patent=Image.open(REF/"GW_PATENT_PDF02.png").convert("RGB")
    pi, pd=canvas("A TECHNICAL DRAWING\nIS NOT A PROOF", "MONROE PATENT · 1993"); patent.thumbnail((930,1250),Image.Resampling.LANCZOS); pi.paste(patent,((W-patent.width)//2,430+(1250-patent.height)//2)); pi.save(s2/"S02_DOC01_PATENT_CONTEXT_9x16.png",quality=96)
    # One two-stem batch; both are standalone scripts and files.
    raw=OUT/"voice_raw"; raw.mkdir(parents=True,exist_ok=True); stems=[]
    for idx,(short,text) in enumerate(SHORTS.items(),1):
        tf=OUT/short/"voice"/f"{short}_TTS.txt"; spoken=text.replace("U.S. Army","U S Army").replace("1983","neunzehnhundertdreiundachtzig")
        tf.write_text(spoken+"\n",encoding="utf-8"); stems.append({"id":short,"text_file":str(tf.resolve())})
    batch={"voice":"TUKJhQmz3RPYBNAgC5A1","model":"eleven_multilingual_v2","settings":{"stability":.56,"similarity_boost":.80,"style":.04,"speed":1.12,"use_speaker_boost":True},"seed":2608,"output_format":"mp3_44100_128","output_dir":str(raw.resolve()),"stems":stems}
    (OUT/"voice_batch.json").write_text(json.dumps(batch,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Prepared 2 Shorts / {sum(len(re.findall(r'\b[\w-]+\b',t)) for t in SHORTS.values())} words / 4 AI assets / speed 1.12")


if __name__=="__main__": main()
