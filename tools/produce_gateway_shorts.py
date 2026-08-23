#!/usr/bin/env python3
"""Align, mix and render two standalone Gateway Shorts in 9:16."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
import uuid
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import produce_ep02_gateway_v2 as common

ROOT=Path(__file__).resolve().parents[1]
PROD=ROOT/"06_PRODUCTION"/"EP02_GATEWAY_SHORTS_V1"
RAW=PROD/"voice_raw"
FPS=30; W=1080; H=1920

SPECS={
 "SHORT01_THREE_OBSERVERS":{
  "shots":[
   ("Drei Menschen", "S01_AI01_THREE_OBSERVERS_9x16.png", "RECONSTRUCTION"),
   ("Einer beobachtet", "S01_CARD01_THREE_OBSERVERS_9x16.png", "PRESENT"),
   ("Einer soll", "S01_DOC01_RECOMMENDATION_H_9x16.png", "PAST · IN THE REPORT"),
   ("Der dritte", "S01_AI02_TIME_OBSERVERS_9x16.png", "FUTURE"),
   ("Das klingt erfunden", "S01_DOC02_ARMY_HEADER_9x16.png", "U.S. ARMY REPORT · 1983"),
   ("genau dieser Vorschlag", "S01_DOC01_RECOMMENDATION_H_9x16.png", "RECOMMENDATION H"),
   ("Anschließend", "S01_CARD01_THREE_OBSERVERS_9x16.png", "COMPARE REPORTS"),
   ("Der entscheidende Punkt", "S01_DOC01_RECOMMENDATION_H_9x16.png", "A PROPOSED TEST"),
   ("Versuchsplan", "S01_AI01_THREE_OBSERVERS_9x16.png", "PLAN · NOT RESULT"),
   ("nicht, dass dieser Versuch", "S01_CARD01_THREE_OBSERVERS_9x16.png", "NO SUCCESS REPORTED"),
   ("Das Merkwürdige", "S01_AI02_TIME_OBSERVERS_9x16.png", "WHAT IS ACTUALLY STRANGE"),
   ("nicht, dass die Army", "S01_DOC02_ARMY_HEADER_9x16.png", "NO PROOF OF TIME TRAVEL"),
   ("Militäranalyst", "S01_AI01_THREE_OBSERVERS_9x16.png", "A MILITARY ANALYST"),
   ("konkreten Test", "S01_DOC01_RECOMMENDATION_H_9x16.png", "PAST · PRESENT · FUTURE"),
  ]},
 "SHORT02_TWO_TONES":{
  "shots":[
   ("Links vierhundert Hertz", "S02_AI01_LISTENER_9x16.png", "LEFT · 400 Hz"),
   ("Rechts vierhundertzehn", "S02_CARD01_BINAURAL_BEAT_9x16.png", "RIGHT · 410 Hz"),
   ("Bei der Verarbeitung", "S02_CARD01_BINAURAL_BEAT_9x16.png", "PERCEIVED PULSE · ≈10 Hz"),
   ("Dieser binaurale Beat", "S02_AI01_LISTENER_9x16.png", "REAL AUDITORY PHENOMENON"),
   ("Doch dann", "S02_DOC02_REPORT_MODEL_9x16.png", "THE GATEWAY REPORT'S CLAIM JUMP"),
   ("Aus Tönen", "S02_AI01_LISTENER_9x16.png", "TONES · RELAXATION · ATTENTION"),
   ("größeres Informationsfeld", "S02_AI02_EVIDENCE_GAP_9x16.png", "LARGER INFORMATION FIELD · CLAIM"),
   ("außerhalb normaler", "S02_AI02_EVIDENCE_GAP_9x16.png", "SPACE AND TIME · CLAIM"),
   ("Ein veränderter Zustand", "S02_CARD02_EVIDENCE_GAP_9x16.png", "EXPERIENCE ≠ INFORMATION"),
   ("Für Informationsübertragung", "S02_AI02_EVIDENCE_GAP_9x16.png", "WHAT EVIDENCE WOULD REQUIRE"),
   ("verborgenes Ziel", "S02_AI02_EVIDENCE_GAP_9x16.png", "PRESELECTED HIDDEN TARGET"),
   ("blind ausgewertet", "S02_CARD02_EVIDENCE_GAP_9x16.png", "BLIND · REPEATABLE"),
   ("Ein Effekt im Erleben", "S02_AI01_LISTENER_9x16.png", "A FINDING ABOUT PERCEPTION"),
   ("entferntes Ziel", "S02_AI02_EVIDENCE_GAP_9x16.png", "A FINDING ABOUT INFORMATION"),
   ("Genau zwischen beiden", "S02_CARD02_EVIDENCE_GAP_9x16.png", "THE GATEWAY EVIDENCE GAP"),
  ]},
}


def run(args,capture=False):
 p=subprocess.run(args,text=True,capture_output=capture)
 if p.returncode: raise RuntimeError((p.stderr or p.stdout or "command failed")[-7000:])
 return (p.stdout or "")+(p.stderr or "")


def duration(path): return float(run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",str(path)],True).strip())
def srt_time(v):
 ms=round(v*1000); h,r=divmod(ms,3600000); m,r=divmod(r,60000); s,ms=divmod(r,1000); return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
def ass_time(v):
 cs=round(v*100); h,r=divmod(cs,360000); m,r=divmod(r,6000); s,cs=divmod(r,100); return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def master(short):
 src=RAW/f"{short}.mp3"; base=PROD/short; voice=base/"voice"; voice.mkdir(parents=True,exist_ok=True)
 norm=voice/f"{short}_voice_-18LUFS.wav"; common.normalize_audio(src,norm,-18,-2,1)
 pre=voice/"pre.wav"; tail=voice/"tail.wav"
 run(["ffmpeg","-y","-hide_banner","-loglevel","error","-f","lavfi","-i","anullsrc=r=48000:cl=mono:d=0.20","-c:a","pcm_s24le",str(pre)])
 run(["ffmpeg","-y","-hide_banner","-loglevel","error","-f","lavfi","-i","anullsrc=r=48000:cl=mono:d=1.10","-c:a","pcm_s24le",str(tail)])
 concat=voice/"concat.txt"; concat.write_text("\n".join(f"file '{x.as_posix()}'" for x in (pre,norm,tail))+"\n",encoding="utf-8")
 out=voice/f"{short}_VOICE_MASTER.wav"; run(["ffmpeg","-y","-hide_banner","-loglevel","error","-f","concat","-safe","0","-i",str(concat),"-c:a","pcm_s24le",str(out)])
 (voice/"voice_report.json").write_text(json.dumps({"speed":1.12,"duration":duration(out),"source":str(src.resolve())},indent=2)+"\n",encoding="utf-8")
 return out


def multipart(audio,text):
 boundary="----GWSHORT"+uuid.uuid4().hex
 parts=[f"--{boundary}\r\n".encode(),b'Content-Disposition: form-data; name="text"\r\n\r\n',text.encode(),b"\r\n",f"--{boundary}\r\n".encode(),f'Content-Disposition: form-data; name="file"; filename="{audio.name}"\r\n'.encode(),b"Content-Type: audio/wav\r\n\r\n",audio.read_bytes(),b"\r\n",f"--{boundary}--\r\n".encode()]
 return b"".join(parts),boundary


def align(short,voice):
 sys.path.insert(0,r"C:\Users\iQPrinceps\Documents\Codex\NOESIS Channel\tools"); from elevenlabs_cli import _load_key
 text=(PROD/short/"voice"/f"{short}_TTS.txt").read_text(encoding="utf-8").strip(); body,b=multipart(voice,text)
 req=Request("https://api.elevenlabs.io/v1/forced-alignment",data=body,headers={"xi-api-key":_load_key(),"Content-Type":f"multipart/form-data; boundary={b}","Accept":"application/json"},method="POST")
 try:
  with urlopen(req,timeout=300) as res: data=json.loads(res.read().decode())
 except HTTPError as e: raise RuntimeError(f"Alignment HTTP {e.code}: {e.read().decode(errors='replace')}")
 data["source_text"]=text; path=PROD/short/"voice"/f"{short}_alignment.json"; path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); return path


def make_timeline(short,voice,alignment):
 base=PROD/short; data=json.loads(alignment.read_text(encoding="utf-8")); text=data["source_text"]; chars=data["characters"]
 rows=[]; cursor=0; starts=[]
 for i,(anchor,name,label) in enumerate(SPECS[short]["shots"]):
  pos=text.find(anchor,cursor)
  if pos<0: raise RuntimeError(f"{short}: missing anchor {anchor!r} after {cursor}")
  first=next(j for j in range(pos,pos+len(anchor)) if not text[j].isspace()); starts.append(0.0 if i==0 else float(chars[first]["start"])); cursor=pos+len(anchor)
 total=duration(voice)
 for i,((anchor,name,label),start) in enumerate(zip(SPECS[short]["shots"],starts),1):
  end=starts[i] if i<len(starts) else total; rows.append({"shot_id":f"{short}_SH{i:02d}","anchor":anchor,"visual":str((base/"assets"/name).resolve()),"label":label,"start":round(start,3),"end":round(end,3),"duration":round(end-start,3)})
 tdir=base/"timeline"; tdir.mkdir(exist_ok=True); path=tdir/f"{short}_timeline.json"; path.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 return rows


def sentence_spans(alignment):
 data=json.loads(alignment.read_text(encoding="utf-8")); text=data["source_text"]; chars=data["characters"]; spans=[]
 for m in re.finditer(r"[^.!?]+[.!?]+|[^.!?]+$",text,re.S):
  tx=re.sub(r"\s+"," ",m.group()).strip()
  if not tx: continue
  a=next(i for i in range(m.start(),m.end()) if not text[i].isspace()); z=next(i for i in range(m.end()-1,m.start()-1,-1) if not text[i].isspace())
  spans.append((float(chars[a]["start"]),float(chars[z]["end"]),tx))
 return spans


def captions(short,alignment):
 base=PROD/short; spans=sentence_spans(alignment); out=[]; ass=[]; n=0
 for st,en,tx in spans:
  words=tx.split(); chunks=[words] if len(words)<=9 else [words[:math.ceil(len(words)/2)],words[math.ceil(len(words)/2):]]; cur=st
  for i,ch in enumerate(chunks):
   ce=en if i==len(chunks)-1 else st+(en-st)*len(ch)/len(words); n+=1; caption=" ".join(ch); out += [str(n),f"{srt_time(cur)} --> {srt_time(ce)}",caption,""]; ass.append((cur,ce,caption)); cur=ce
 cdir=base/"captions"; cdir.mkdir(exist_ok=True); (cdir/f"{short}_de.srt").write_text("\n".join(out),encoding="utf-8-sig"); return ass


def camera(row,index):
 frames=max(1,math.ceil(row["duration"]*FPS)); x="iw/2-(iw/zoom/2)" if index%2==0 else f"(iw-iw/zoom)*on/{frames}"
 fade=f",fade=t=out:st={max(0,row['duration']-1):.3f}:d=1:color=#041114" if row.get("last") else ""
 return f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(zoom+.00016,1.065)':x='{x}':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30,eq=contrast=1.025:saturation=.94,unsharp=5:5:.2:5:5:0,format=yuv420p"+fade


def graphics(short,rows,caps):
 path=PROD/short/"render"/f"{short}.ass"; path.parent.mkdir(parents=True,exist_ok=True)
 head="""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Label,Arial,35,&H00FFFFFF,&H0,&H70000000,&HA0201B18,-1,0,0,0,100,100,1,0,3,1,0,8,55,55,85,1
Style: Caption,Arial,55,&H00FFFFFF,&H0,&H00000000,&HC0000000,-1,0,0,0,100,100,0,0,3,3,0,2,70,70,185,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""; lines=[head]
 for row in rows: lines.append(f"Dialogue: 0,{ass_time(row['start']+.08)},{ass_time(row['end']-.08)},Label,,0,0,0,,{row['label']}\n")
 for st,en,tx in caps: lines.append(f"Dialogue: 1,{ass_time(st)},{ass_time(en)},Caption,,0,0,0,,{tx}\n")
 path.write_text("".join(lines),encoding="utf-8-sig"); return path


def audio_mix(short,voice):
 base=PROD/short; adir=base/"audio"; adir.mkdir(exist_ok=True); total=duration(voice)
 bed=adir/"ambient.wav"; premix=adir/"premix.wav"; final=adir/f"{short}_AUDIO_MASTER.wav"
 src=f"aevalsrc='0.025*sin(2*PI*52*t)+0.018*sin(2*PI*71*t+0.2*sin(2*PI*t/17))|0.025*sin(2*PI*58*t)+0.018*sin(2*PI*71*t+0.2*sin(2*PI*t/19))':s=48000:d={total}"
 run(["ffmpeg","-y","-hide_banner","-loglevel","error","-f","lavfi","-i",src,"-ac","2","-ar","48000","-c:a","pcm_s24le",str(bed)])
 fc="[0:a]pan=stereo|c0=c0|c1=c0,asplit=2[v][sc];[1:a][sc]sidechaincompress=threshold=.018:ratio=8:attack=20:release=450[d];[v][d]amix=inputs=2:weights='1 .18':normalize=0,alimiter=limit=.94[out]"
 run(["ffmpeg","-y","-hide_banner","-loglevel","error","-i",str(voice),"-i",str(bed),"-filter_complex",fc,"-map","[out]","-t",str(total),"-ac","2","-ar","48000","-c:a","pcm_s24le",str(premix)])
 common.normalize_audio(premix,final,-14,-1,2); return final


def render(short,rows,caps,audio):
 base=PROD/short; seg=base/"render"/"segments"; seg.mkdir(parents=True,exist_ok=True); rows[-1]["last"]=True
 for i,row in enumerate(rows):
  target=seg/f"{i+1:02d}_{row['shot_id']}.mp4"; print(f"{short}: {i+1:02d}/{len(rows):02d} {row['duration']:.2f}s · {row['anchor']}",flush=True)
  run(["ffmpeg","-y","-hide_banner","-loglevel","error","-loop","1","-framerate","30","-i",row["visual"],"-t",str(row["duration"]),"-vf",camera(row,i),"-an","-c:v","libx264","-preset","veryfast","-crf","16","-pix_fmt","yuv420p","-r","30",str(target)])
 concat=base/"render"/"concat.txt"; concat.write_text("\n".join(f"file '{(seg/f'{i+1:02d}_{r['shot_id']}.mp4').as_posix()}'" for i,r in enumerate(rows))+"\n",encoding="utf-8")
 picture=base/"render"/"picture.mp4"; run(["ffmpeg","-y","-hide_banner","-loglevel","error","-f","concat","-safe","0","-i",str(concat),"-c","copy",str(picture)])
 ass=graphics(short,rows,caps); assf="ass='"+str(ass).replace("\\","/").replace(":",r"\:")+"'"; final=base/"render"/"final"; final.mkdir(exist_ok=True); out=final/f"{short}_FINAL_1080x1920.mp4"
 run(["ffmpeg","-y","-hide_banner","-loglevel","error","-i",str(picture),"-i",str(audio),"-vf",assf,"-map","0:v:0","-map","1:a:0","-c:v","libx264","-preset","slow","-crf","18","-pix_fmt","yuv420p","-c:a","aac","-b:a","256k","-ar","48000","-movflags","+faststart","-shortest",str(out)])
 return out


def qa(short,out,rows):
 probe=json.loads(run(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(out)],True)); vs=next(s for s in probe["streams"] if s["codec_type"]=="video"); au=next(s for s in probe["streams"] if s["codec_type"]=="audio"); loud=common.loudness(out); d=float(probe["format"]["duration"])
 checks={"portrait_1080x1920":vs.get("width")==1080 and vs.get("height")==1920,"h264":vs.get("codec_name")=="h264","aac_48k_stereo":au.get("codec_name")=="aac" and au.get("sample_rate")=="48000" and au.get("channels")==2,"duration_under_60":d<60.5,"loudness":abs(float(loud["input_i"])+14)<=.5,"peak":float(loud["input_tp"])<=-.8,"speed_112":json.loads((PROD/short/"voice"/"voice_report.json").read_text())["speed"]==1.12,"semantic_timing":all(r.get("anchor") for r in rows)}
 rep={"file":str(out.resolve()),"sha256":hashlib.sha256(out.read_bytes()).hexdigest(),"duration":d,"shots":len(rows),"avg_shot":round(d/len(rows),2),"loudness":loud,"checks":checks}; q=out.parent/f"{short}_QA.json"; q.write_text(json.dumps(rep,indent=2)+"\n",encoding="utf-8")
 run(["ffmpeg","-y","-hide_banner","-loglevel","error","-i",str(out),"-vf","fps=1/8,scale=216:384,tile=4x2","-frames:v","1","-q:v","2",str(out.parent/f"{short}_CONTACT.jpg")]); print(json.dumps(rep,indent=2))
 if not all(checks.values()): raise RuntimeError(f"{short} QA failed")


def produce(short):
 voice=master(short); alignment=align(short,voice); rows=make_timeline(short,voice,alignment); caps=captions(short,alignment); audio=audio_mix(short,voice); out=render(short,rows,caps,audio); qa(short,out,rows)


def main():
 ap=argparse.ArgumentParser(); ap.add_argument("short",choices=["all",*SPECS]); args=ap.parse_args()
 for short in SPECS:
  if args.short in ("all",short): produce(short)


if __name__=="__main__": main()
