#!/usr/bin/env python3
"""Produce the rebuilt, faster and more visual Gateway V2 master."""

from __future__ import annotations

import argparse, hashlib, json, math, re, subprocess, sys, uuid
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent.parent
PROD = ROOT / "06_PRODUCTION" / "EP02_GATEWAY_V2"
V1 = ROOT / "06_PRODUCTION" / "EP02_GATEWAY"
VOICE_TEXT = PROD / "04_VOICE_SCRIPT_CLEAN_V2.txt"
VOICE_MASTER = PROD / "voice" / "master" / "EP02_GATEWAY_V2_VO_MASTER.wav"
ALIGNMENT = PROD / "voice" / "alignment" / "EP02_GATEWAY_V2_alignment.json"
TIMELINE = PROD / "timeline" / "EP02_GATEWAY_V2_timeline.json"
SRT = PROD / "captions" / "EP02_GATEWAY_V2_de.srt"
AUDIO = PROD / "audio"; SEGMENTS = PROD / "render" / "segments"; FINAL = PROD / "render" / "final"
FPS = 30


def run(args: list[str], capture: bool = False) -> str:
    p = subprocess.run(args, text=True, capture_output=capture)
    if p.returncode: raise RuntimeError((p.stderr or p.stdout or "command failed")[-7000:])
    return (p.stdout or "") + (p.stderr or "")


def duration(path: Path) -> float:
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)], True).strip())


def sha256(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def loudness(path: Path, target=-14.0, peak=-1.0, lra=7.0) -> dict:
    out = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", f"loudnorm=I={target}:TP={peak}:LRA={lra}:print_format=json", "-f", "null", "-"], True)
    return json.loads(re.findall(r'\{\s*"input_i".*?\}', out, re.S)[-1])


def normalize_audio(source: Path, target: Path, integrated: float, peak: float, channels: int) -> dict:
    st = loudness(source, integrated, peak)
    f = (f"loudnorm=I={integrated}:TP={peak}:LRA=7:measured_I={st['input_i']}:measured_TP={st['input_tp']}:"
         f"measured_LRA={st['input_lra']}:measured_thresh={st['input_thresh']}:offset={st['target_offset']}:linear=true")
    target.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(source), "-af", f, "-ac", str(channels), "-ar", "48000", "-c:a", "pcm_s24le", str(target)])
    return loudness(target, integrated, peak)


def master_voice() -> None:
    stems = json.loads((PROD / "voice" / "stems.json").read_text(encoding="utf-8")); raw = PROD / "voice" / "raw_stems"
    mdir = PROD / "voice" / "master"; sdir = mdir / "stems"; sdir.mkdir(parents=True, exist_ok=True)
    lines=[]; report=[]
    pre = mdir / "pre.wav"; run(["ffmpeg","-y","-hide_banner","-loglevel","error","-f","lavfi","-i","anullsrc=r=48000:cl=mono:d=0.35","-c:a","pcm_s24le",str(pre)]); lines.append(f"file '{pre.as_posix()}'")
    for i, stem in enumerate(stems):
        src=raw/f"{stem['id']}.mp3"; dst=sdir/f"{stem['id']}.wav"; normalize_audio(src,dst,-18,-2,1)
        lines.append(f"file '{dst.as_posix()}'"); report.append({"id":stem["id"],"duration":round(duration(dst),3),"tts_speed":1.12,"file":str(dst.resolve())})
        if i < len(stems)-1:
            gap=mdir/f"gap_{i+1:02d}.wav"; run(["ffmpeg","-y","-hide_banner","-loglevel","error","-f","lavfi","-i","anullsrc=r=48000:cl=mono:d=0.65","-c:a","pcm_s24le",str(gap)]); lines.append(f"file '{gap.as_posix()}'")
    tail=mdir/"tail.wav"; run(["ffmpeg","-y","-hide_banner","-loglevel","error","-f","lavfi","-i","anullsrc=r=48000:cl=mono:d=2.2","-c:a","pcm_s24le",str(tail)]); lines.append(f"file '{tail.as_posix()}'")
    concat=mdir/"concat.txt"; concat.write_text("\n".join(lines)+"\n",encoding="utf-8")
    run(["ffmpeg","-y","-hide_banner","-loglevel","error","-f","concat","-safe","0","-i",str(concat),"-c:a","pcm_s24le",str(VOICE_MASTER)])
    payload={"duration":round(duration(VOICE_MASTER),3),"tts_speed":1.12,"stems":report}; (mdir/"stem_report.json").write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8"); print(json.dumps(payload,indent=2))


def multipart(audio: Path, text: str):
    b="----GWV2"+uuid.uuid4().hex; parts=[f"--{b}\r\n".encode(),b'Content-Disposition: form-data; name="text"\r\n\r\n',text.encode(),b"\r\n",f"--{b}\r\n".encode(),f'Content-Disposition: form-data; name="file"; filename="{audio.name}"\r\n'.encode(),b"Content-Type: audio/wav\r\n\r\n",audio.read_bytes(),b"\r\n",f"--{b}--\r\n".encode()]; return b"".join(parts),b


def align() -> None:
    sys.path.insert(0,r"C:\Users\iQPrinceps\Documents\Codex\NOESIS Channel\tools"); from elevenlabs_cli import _load_key  # type: ignore
    text=VOICE_TEXT.read_text(encoding="utf-8").strip(); body,b=multipart(VOICE_MASTER,text)
    req=Request("https://api.elevenlabs.io/v1/forced-alignment",data=body,headers={"xi-api-key":_load_key(),"Content-Type":f"multipart/form-data; boundary={b}","Accept":"application/json"},method="POST")
    try:
        with urlopen(req,timeout=300) as res: data=json.loads(res.read().decode())
    except HTTPError as e: raise RuntimeError(f"Alignment HTTP {e.code}: {e.read().decode(errors='replace')}")
    data.update({"source_text":text,"audio":str(VOICE_MASTER.resolve()),"audio_sha256":sha256(VOICE_MASTER)}); ALIGNMENT.parent.mkdir(parents=True,exist_ok=True); ALIGNMENT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print(ALIGNMENT)


def srt_time(v: float) -> str:
    ms=round(v*1000); h,r=divmod(ms,3600000); m,r=divmod(r,60000); s,ms=divmod(r,1000); return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def build_srt() -> None:
    d=json.loads(ALIGNMENT.read_text(encoding="utf-8")); text=d["source_text"]; chars=d["characters"]
    protected=text.replace("U.S.","U§S§"); protected=re.sub(r"(?<=\b[A-Z])\.(?=\s+[A-ZÄÖÜ])","§",protected); protected=re.sub(r"\b(\d{1,2})\.(?=\s+(?:Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember))",r"\1§",protected)
    spans=[]
    for mt in re.finditer(r"[^.!?]+[.!?]+|[^.!?]+$",protected,re.S):
        original=text[mt.start():mt.end()]; sent=re.sub(r"\s+"," ",original).strip()
        if not sent: continue
        a=next(i for i in range(mt.start(),mt.end()) if not text[i].isspace()); z=next(i for i in range(mt.end()-1,mt.start()-1,-1) if not text[i].isspace()); st,en=float(chars[a]["start"]),float(chars[z]["end"]); words=sent.split(); chunks=[words] if len(words)<=12 else [words[:len(words)//2],words[len(words)//2:]]; cur=st
        for j,ch in enumerate(chunks): ce=en if j==len(chunks)-1 else st+(en-st)*len(ch)/len(words); spans.append((cur,ce," ".join(ch))); cur=ce
    lines=[]
    for i,(st,en,tx) in enumerate(spans,1): lines += [str(i),f"{srt_time(st)} --> {srt_time(en)}",tx,""]
    SRT.parent.mkdir(parents=True,exist_ok=True); SRT.write_text("\n".join(lines),encoding="utf-8-sig"); print(f"Captions {len(spans)}")


def asset(*parts: str) -> str: return str(ROOT.joinpath(*parts).resolve())
def prod(*parts: str) -> str: return str(PROD.joinpath(*parts).resolve())
def v1(*parts: str) -> str: return str(V1.joinpath(*parts).resolve())


def shot(path: str, kind="STILL", label="", title="") -> dict: return {"visual":path,"kind":kind,"evidence_label":label,"on_screen_text":title}


def visual_sequences() -> list[list[dict]]:
    ai=lambda n: asset("05_GENERATED","EP02_GATEWAY_V2","AI_FINAL",n)
    doc=lambda n: prod("visuals","document_crops",n)
    card=lambda n: prod("visuals","cards",n)
    ex=lambda n: asset("04_ASSETS","02_CURATED","EP02_GATEWAY","APPROVED",n)
    patent=lambda n: prod("visuals","patents",n)
    oldai=lambda *p: asset("05_GENERATED","EP02_GATEWAY",*p)
    rp=lambda n: v1("reference_package",n)
    luna=lambda n: asset("04_ASSETS","02_CURATED","EP02_GATEWAY","V2_RESEARCH_LUNA",n)
    return [
      [shot(ai("GWV2_IMG01_THREE_OBSERVERS_16x9.png"),label="RECONSTRUCTION"),shot(card("V2_CARD01_THREE_OBSERVERS.png"),label="PROPOSED"),shot(doc("V2_DOC09_RECOMMENDATION_H.png"),label="IN THE REPORT"),shot(doc("V2_DOC01_ARMY_HEADER_DATE.png"),label="DOCUMENTED"),shot(doc("V2_DOC03_MCDONNELL_SIGNATURE.png"),label="DOCUMENTED"),shot(luna("GWV2_IMG_001_Fort_Meade_entrance_2009_PD.jpg"),label="FORT MEADE · 2009"),shot(doc("V2_DOC01_ARMY_HEADER_DATE.png"),label="ARMY REPORT"),shot(ai("GWV2_IMG01_THREE_OBSERVERS_16x9.png"),label="RECONSTRUCTION"),shot(doc("V2_DOC09_RECOMMENDATION_H.png"),label="PROPOSED"),shot(card("V2_CARD01_THREE_OBSERVERS.png"),label="NO RESULT REPORTED"),shot(ai("GWV2_IMG02_ROBERT_MONROE_PORTRAIT_RECON_16x9.png"),label="PORTRAIT RECONSTRUCTION"),shot(ai("GWV2_IMG04_BINAURAL_LISTENING_CLOSEUP_16x9.png"),label="RECONSTRUCTION")],
      [shot(ai("GWV2_IMG02_ROBERT_MONROE_PORTRAIT_RECON_16x9.png"),label="PORTRAIT RECONSTRUCTION",title="ROBERT MONROE"),shot(ai("GWV2_IMG04_BINAURAL_LISTENING_CLOSEUP_16x9.png"),label="RECONSTRUCTION"),shot(luna("GWV2_VID_001_Computer_Meditation_CC_BY_SA_3.0.ogv"),kind="VIDEO",label="CONTEXT · NOT GATEWAY FOOTAGE"),shot(rp("GW_PATENT_PDF01.png"),label="1993 PATENT"),shot(rp("GW_PATENT_PDF02.png"),label="PATENT DRAWING"),shot(doc("V2_DOC02_TASK_BENTOV.png"),label="IN THE REPORT"),shot(doc("V2_DOC03_MCDONNELL_SIGNATURE.png"),label="DOCUMENTED",title="WAYNE M. McDONNELL"),shot(ai("GWV2_IMG03_BENTOV_EDITORIAL_RECON_16x9.png"),label="DRAMATIZED RECONSTRUCTION",title="ITZHAK BENTOV · NOT A PHOTOGRAPH"),shot(patent("BENTOV_1971-01.png"),label="U.S. PATENT · 1971"),shot(patent("BENTOV_1969-1.png"),label="U.S. PATENT · 1969"),shot(patent("BENTOV_1971-02.png"),label="PATENT DRAWING"),shot(card("V2_CARD02_PEOPLE_CHAIN.png"),label="MODEL PROVENANCE"),shot(doc("V2_DOC02_TASK_BENTOV.png"),label="IN THE REPORT"),shot(doc("V2_DOC03_MCDONNELL_SIGNATURE.png"),label="NO VERIFIED PORTRAIT"),shot(luna("GWV2_IMG_001_Fort_Meade_entrance_2009_PD.jpg"),label="FORT MEADE · 2009")],
      [shot(ai("GWV2_IMG04_BINAURAL_LISTENING_CLOSEUP_16x9.png"),label="RECONSTRUCTION"),shot(v1("qa_renders","CARD02_BINAURAL_BEAT.png"),label="AUDITORY PHENOMENON"),shot(v1("qa_renders","CARD02_BINAURAL_BEAT.png"),label="400 Hz · 410 Hz"),shot(v1("qa_renders","CARD02_BINAURAL_BEAT.png"),label="BINAURAL BEAT"),shot(asset("06_PRODUCTION","Gateway_Production","Assets_Research_Luna","GW_IMG_002_PMC7082494_Figure1_Binaural_vs_Monaural.jpg"),label="RESEARCH FIGURE"),shot(luna("GWV2_VID_001_Computer_Meditation_CC_BY_SA_3.0.ogv"),kind="VIDEO",label="CONTEXT · NOT GATEWAY FOOTAGE"),shot(rp("GW_PATENT_PDF01.png"),label="US 5,213,562"),shot(rp("GW_PATENT_PDF02.png"),label="PATENT DRAWING"),shot(rp("GW_PATENT_PDF03.png"),label="PATENT DRAWING"),shot(rp("GW_PATENT_PDF04.png"),label="PATENT DRAWING"),shot(ai("GWV2_IMG02_ROBERT_MONROE_PORTRAIT_RECON_16x9.png"),label="PORTRAIT RECONSTRUCTION"),shot(ex("GW_002_Exhibit_1A.png"),label="IN THE REPORT"),shot(ex("GW_003_Exhibit_1B.png"),label="IN THE REPORT"),shot(card("V2_CARD03_MECHANISM_LADDER.png"),label="CLAIM GAP")],
      [shot(ai("GWV2_IMG06_CONSCIOUSNESS_FIELD_MODEL_16x9.png"),label="MODEL VISUALIZATION"),shot(ex("GW_002_Exhibit_1A.png"),label="ORIGINAL DIAGRAM"),shot(ex("GW_003_Exhibit_1B.png"),label="ORIGINAL DIAGRAM"),shot(ex("GW_004_Exhibit_1C.png"),label="ORIGINAL DIAGRAM"),shot(ex("GW_005_Exhibit_2.png"),label="ORIGINAL DIAGRAM"),shot(ex("GW_006_Exhibit_3.png"),label="ORIGINAL DIAGRAM"),shot(ex("GW_007_Exhibit_4A.png"),label="ORIGINAL DIAGRAM"),shot(ex("GW_008_Exhibit_4B.png"),label="ORIGINAL DIAGRAM"),shot(ex("GW_009_Exhibit_4C.png"),label="ORIGINAL DIAGRAM"),shot(ex("GW_010_Exhibit_5.png"),label="ORIGINAL DIAGRAM"),shot(ai("GWV2_IMG06_CONSCIOUSNESS_FIELD_MODEL_16x9.png"),label="MODEL VISUALIZATION"),shot(card("V2_CARD03_MECHANISM_LADDER.png"),label="CLAIM GAP"),shot(ai("GWV2_IMG03_BENTOV_EDITORIAL_RECON_16x9.png"),label="DRAMATIZED RECONSTRUCTION",title="NOT A PHOTOGRAPH"),shot(patent("BENTOV_1971-01.png"),label="INVENTOR CONTEXT")],
      [shot(v1("qa_renders","CARD03_FOCUS_LEVELS.png"),label="IN THE REPORT"),shot(doc("V2_DOC04_FOCUS15_HEADING.png"),label="IN THE REPORT"),shot(ai("GWV2_IMG05_FOCUS15_TIME_WHEEL_16x9.png"),label="MODEL VISUALIZATION"),shot(doc("V2_DOC05_LESS_THAN_FIVE_PERCENT.png"),label="IN THE REPORT"),shot(ai("GWV2_IMG05_FOCUS15_TIME_WHEEL_16x9.png"),label="FOCUS 15 · VISUALIZATION"),shot(doc("V2_DOC06_FOCUS21_FUTURE.png"),label="IN THE REPORT"),shot(oldai("STYLE_REFERENCES","IMG02_GW_STYLE_CONCEPTUAL_16x9.png"),label="MODEL VISUALIZATION"),shot(doc("V2_DOC07_OBE_NO_GUARANTEE.png"),label="IN THE REPORT"),shot(oldai("AI_RECONSTRUCTIONS","IMG06_GW_OUT_OF_BODY_CONCEPT_16x9.png"),label="RECONSTRUCTION"),shot(luna("GWV2_VID_001_Computer_Meditation_CC_BY_SA_3.0.ogv"),kind="VIDEO",label="CONTEXT · NOT GATEWAY FOOTAGE"),shot(doc("V2_DOC07_OBE_NO_GUARANTEE.png"),label="NO GUARANTEE"),shot(oldai("AI_RECONSTRUCTIONS","IMG06_GW_OUT_OF_BODY_CONCEPT_16x9.png"),label="RECONSTRUCTION"),shot(v1("qa_renders","CARD05_CLAIM_GAP.png"),label="NOT ESTABLISHED"),shot(card("V2_CARD05_EVIDENCE_SCALE.png"),label="EVIDENCE GAP"),shot(doc("V2_DOC06_FOCUS21_FUTURE.png"),label="CLAIM IN REPORT")],
      [shot(doc("V2_DOC08_INFORMATION_COLLECTION.png"),label="IN THE REPORT"),shot(ai("GWV2_IMG01_THREE_OBSERVERS_16x9.png"),label="RECONSTRUCTION"),shot(card("V2_CARD01_THREE_OBSERVERS.png"),label="PROPOSED"),shot(doc("V2_DOC08_INFORMATION_COLLECTION.png"),label="NO PERFECT RESULT"),shot(doc("V2_DOC09_RECOMMENDATION_H.png"),label="IN THE REPORT"),shot(card("V2_CARD01_THREE_OBSERVERS.png"),label="PAST · PRESENT · FUTURE"),shot(ai("GWV2_IMG01_THREE_OBSERVERS_16x9.png"),label="RECONSTRUCTION"),shot(doc("V2_DOC09_RECOMMENDATION_H.png"),label="PROPOSED PROCEDURE"),shot(card("V2_CARD04_TEST_PROTOCOL.png"),label="MISSING EVIDENCE CHAIN"),shot(doc("V2_DOC10_NONCORPOREAL_FORMS.png"),label="IN THE REPORT"),shot(ai("GWV2_IMG07_NONCORPOREAL_BARRIER_CLAIM_16x9.png"),label="CLAIM VISUALIZATION"),shot(doc("V2_DOC11_HOLOGRAPHIC_BARRIER.png"),label="IN THE REPORT"),shot(ai("GWV2_IMG07_NONCORPOREAL_BARRIER_CLAIM_16x9.png"),label="CLAIM VISUALIZATION"),shot(doc("V2_DOC12_IF_EXPERIMENTS_CARRIED_THROUGH.png"),label="CONDITIONAL"),shot(card("V2_CARD03_MECHANISM_LADDER.png"),label="ONTOLOGY OF THE REPORT"),shot(doc("V2_DOC09_RECOMMENDATION_H.png"),label="NO RESULT REPORTED")],
      [shot(ai("GWV2_IMG04_BINAURAL_LISTENING_CLOSEUP_16x9.png"),label="MEASURABLE PHENOMENON"),shot(rp("GW_PLOS_PDF01_ABSTRACT.png"),label="META-ANALYSIS · 2019"),shot(asset("06_PRODUCTION","Gateway_Production","Assets_Research_Luna","GW_IMG_002_PMC7082494_Figure1_Binaural_vs_Monaural.jpg"),label="RESEARCH FIGURE"),shot(rp("GW_PLOS_PDF07_PRISMA.png"),label="SYSTEMATIC REVIEW · 2023"),shot(v1("qa_renders","CARD05_CLAIM_GAP.png"),label="5 SUPPORT · 8 CONTRADICT · 1 MIXED"),shot(card("V2_CARD05_EVIDENCE_SCALE.png"),label="EVIDENCE SCALE"),shot(ai("GWV2_IMG06_CONSCIOUSNESS_FIELD_MODEL_16x9.png"),label="MODEL VISUALIZATION"),shot(card("V2_CARD04_TEST_PROTOCOL.png"),label="TEST STANDARD"),shot(card("V2_CARD04_TEST_PROTOCOL.png"),label="BLIND · LOCK · REPEAT"),shot(ai("GWV2_IMG01_THREE_OBSERVERS_16x9.png"),label="RECONSTRUCTION"),shot(v1("qa_renders","CARD05_CLAIM_GAP.png"),label="NOT ESTABLISHED"),shot(card("V2_CARD05_EVIDENCE_SCALE.png"),label="CLAIM GAP"),shot(rp("GW_PLOS_PDF01_ABSTRACT.png"),label="LIMITED EVIDENCE"),shot(rp("GW_PLOS_PDF07_PRISMA.png"),label="HETEROGENEOUS METHODS"),shot(card("V2_CARD04_TEST_PROTOCOL.png"),label="WHAT WOULD COUNT")],
      [shot(doc("V2_DOC01_ARMY_HEADER_DATE.png"),label="DOCUMENTED"),shot(doc("V2_DOC03_MCDONNELL_SIGNATURE.png"),label="DOCUMENTED"),shot(v1("qa_renders","CARD06_EVIDENCE_RESIDUE.png"),label="EVIDENCE RESIDUE"),shot(doc("V2_DOC04_FOCUS15_HEADING.png"),label="IN THE REPORT"),shot(doc("V2_DOC06_FOCUS21_FUTURE.png"),label="IN THE REPORT"),shot(doc("V2_DOC09_RECOMMENDATION_H.png"),label="PROPOSED"),shot(doc("V2_DOC10_NONCORPOREAL_FORMS.png"),label="IN THE REPORT"),shot(doc("V2_DOC11_HOLOGRAPHIC_BARRIER.png"),label="IN THE REPORT"),shot(ai("GWV2_IMG01_THREE_OBSERVERS_16x9.png"),label="RECONSTRUCTION"),shot(card("V2_CARD01_THREE_OBSERVERS.png"),label="PROPOSED · NOT PROVEN"),shot(doc("V2_DOC12_IF_EXPERIMENTS_CARRIED_THROUGH.png"),label="THE CONDITIONAL ENDING"),shot(doc("V2_DOC09_RECOMMENDATION_H.png"),label="THE IMPOSSIBLE · PLANNED ON PAPER")]
    ]


def build_timeline() -> None:
    d=json.loads(ALIGNMENT.read_text(encoding="utf-8")); text=d["source_text"]; chars=d["characters"]; stems=json.loads((PROD/"voice"/"stems.json").read_text(encoding="utf-8")); seqs=visual_sequences(); total=duration(VOICE_MASTER)
    starts=[]; cursor=0
    for stem in stems:
        clean=stem["clean_text"]; pos=text.find(clean,cursor)
        if pos<0: raise RuntimeError(stem["id"])
        first=next(i for i in range(pos,pos+len(clean)) if not text[i].isspace()); starts.append(float(chars[first]["start"])); cursor=pos+len(clean)
    starts[0]=0.0; bounds=starts+[total]; rows=[]; count=0
    for si,(a,b,seq) in enumerate(zip(bounds,bounds[1:],seqs),1):
        span=b-a
        if si==1:
            early=[3.0,3.0,4.0,4.0]; remain=span-sum(early); durations=early+[remain/(len(seq)-len(early))]*(len(seq)-len(early))
        else: durations=[span/len(seq)]*len(seq)
        t=a
        for item,dur in zip(seq,durations):
            count+=1; path=Path(item["visual"])
            if not path.is_file(): raise FileNotFoundError(path)
            rows.append({**item,"shot_id":f"GWV2_{count:03d}","scene":f"S{si}","start":round(t,3),"end":round(t+dur,3),"duration":round(dur,3)}); t+=dur
    rows[-1]["end"]=round(total,3); rows[-1]["duration"]=round(rows[-1]["end"]-rows[-1]["start"],3)
    TIMELINE.parent.mkdir(parents=True,exist_ok=True); TIMELINE.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print(f"Timeline {len(rows)} shots / {total:.3f}s / avg {total/len(rows):.2f}s")


def build_audio() -> None:
    AUDIO.mkdir(parents=True,exist_ok=True); total=duration(VOICE_MASTER); voice=AUDIO/"EP02V2_voice_-18LUFS.wav"; vs=normalize_audio(VOICE_MASTER,voice,-18,-2,1)
    drone=f"aevalsrc='0.040*sin(2*PI*48*t)+0.025*sin(2*PI*64*t+0.2*sin(2*PI*t/41))|0.040*sin(2*PI*56*t)+0.025*sin(2*PI*64*t+0.2*sin(2*PI*t/47))':s=48000:d={total}"
    noise=f"anoisesrc=color=pink:amplitude=.026:r=48000:d={total}"; raw=AUDIO/"EP02V2_ambient_raw.wav"; bed=AUDIO/"EP02V2_ambient_-33LUFS.wav"
    fc="[0:a]lowpass=f=620,aecho=.8:.45:900|2100:.05|.02[t];[1:a]highpass=f=260,lowpass=f=3600,volume=.11[n];[t][n]amix=inputs=2:weights='1 .18':normalize=0[out]"
    run(["ffmpeg","-y","-hide_banner","-loglevel","error","-f","lavfi","-i",drone,"-f","lavfi","-i",noise,"-filter_complex",fc,"-map","[out]","-ac","2","-ar","48000","-c:a","pcm_s24le",str(raw)]); bs=normalize_audio(raw,bed,-33,-4,2)
    pre=AUDIO/"EP02V2_premix.wav"; final=AUDIO/"EP02V2_final_mix.wav"; fade=max(0,total-1.7)
    mix=f"[0:a]pan=stereo|c0=c0|c1=c0,asplit=2[v][sc];[1:a][sc]sidechaincompress=threshold=.020:ratio=7:attack=25:release=550[d];[v][d]amix=inputs=2:weights='1 1':normalize=0,afade=t=out:st={fade}:d=1.7,alimiter=limit=.94[out]"
    run(["ffmpeg","-y","-hide_banner","-loglevel","error","-i",str(voice),"-i",str(bed),"-filter_complex",mix,"-map","[out]","-t",str(total),"-ac","2","-ar","48000","-c:a","pcm_s24le",str(pre)]); fs=normalize_audio(pre,final,-14,-1,2)
    (AUDIO/"audio_mix_report.json").write_text(json.dumps({"duration":total,"tts_speed":1.12,"voice":vs,"bed":bs,"final":fs,"rights":"Original procedural synthesis; no samples."},indent=2)+"\n",encoding="utf-8"); print(fs)


def camera_filter(index: int,row: dict) -> str:
    frames=max(1,math.ceil(row["duration"]*FPS)); inc=.00011 if row["kind"]!="VIDEO" else 0; x="iw/2-(iw/zoom/2)" if index%2==0 else f"(iw-iw/zoom)*on/{frames}"; y="ih/2-(ih/zoom/2)"
    base="scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080"
    # The public-domain/context clip is 4:3. Preserve the full frame instead of
    # cutting away the subject's hands and equipment with a centre crop.
    if row["kind"]=="VIDEO":
        return "scale=1440:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=#041114,eq=contrast=1.03:saturation=.90,format=yuv420p"
    # Bentov's portrait patent pages contain relevant drawings from top to
    # bottom. Fit the complete page into a dark 16:9 field before the subtle
    # camera move; all report quotation images are already editorial crops.
    if "visuals\\patents" in row["visual"] or "visuals/patents" in row["visual"]:
        base="scale=1720:970:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=#041114"
    fade=f",fade=t=out:st={max(0,row['duration']-2):.3f}:d=2:color=#041114" if row["shot_id"]=="GWV2_113" else ""
    return base+f",zoompan=z='min(zoom+{inc},1.07)':x='{x}':y='{y}':d=1:s=1920x1080:fps={FPS},eq=contrast=1.025:saturation=.94,unsharp=5:5:.22:5:5:0,format=yuv420p"+fade


def at(v: float) -> str:
    cs=round(v*100); h,r=divmod(cs,360000); m,r=divmod(r,6000); s,cs=divmod(r,100); return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def esc(s: str) -> str: return s.replace("\\",r"\\").replace("{",r"\{").replace("}",r"\}")


def graphics(rows: list[dict]) -> Path:
    p=PROD/"render"/"EP02_GATEWAY_V2_graphics.ass"; p.parent.mkdir(parents=True,exist_ok=True)
    head="""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Title,Arial,37,&H00F2EFE5,&H0,&H90000000,&H78000000,-1,0,0,0,100,100,1,0,3,1,0,7,82,82,60,1
Style: Evidence,Arial,22,&H00FFFFFF,&H0,&H70000000,&H9823211E,-1,0,0,0,100,100,1,0,3,1,0,9,70,70,58,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""; lines=[head]
    for r in rows:
        st,en=at(r["start"]+.15),at(max(r["start"]+.3,r["end"]-.15))
        if r["on_screen_text"]: lines.append(f"Dialogue: 0,{st},{en},Title,,0,0,0,,{esc(r['on_screen_text'])}\n")
        if r["evidence_label"]: lines.append(f"Dialogue: 0,{st},{en},Evidence,,0,0,0,,{esc(r['evidence_label'])}\n")
    p.write_text("".join(lines),encoding="utf-8-sig"); return p


def render(force=False,limit: int|None=None) -> None:
    rows=json.loads(TIMELINE.read_text(encoding="utf-8")); todo=rows[:limit] if limit else rows; SEGMENTS.mkdir(parents=True,exist_ok=True)
    for i,row in enumerate(todo):
        target=SEGMENTS/f"{i+1:03d}_{row['shot_id']}.mp4"
        if target.exists() and not force: continue
        print(f"Render {i+1:03d}/{len(todo):03d} {row['shot_id']} {row['duration']:.2f}s",flush=True); isvid=row["kind"]=="VIDEO"; inputs=["-stream_loop","-1","-i",row["visual"]] if isvid else ["-loop","1","-framerate",str(FPS),"-i",row["visual"]]
        run(["ffmpeg","-y","-hide_banner","-loglevel","error",*inputs,"-t",str(row["duration"]),"-vf",camera_filter(i,row),"-an","-c:v","libx264","-preset","veryfast","-crf","16","-pix_fmt","yuv420p","-r",str(FPS),str(target)])
    if limit: return
    concat=PROD/"render"/"concat.txt"; paths=[SEGMENTS/f"{i+1:03d}_{r['shot_id']}.mp4" for i,r in enumerate(rows)]; concat.write_text("\n".join(f"file '{p.as_posix()}'" for p in paths)+"\n",encoding="utf-8")
    silent=PROD/"render"/"EP02_GATEWAY_V2_picture_lock.mp4"; run(["ffmpeg","-y","-hide_banner","-loglevel","error","-f","concat","-safe","0","-i",str(concat),"-c","copy",str(silent)])
    ass=graphics(rows); assf="ass='"+str(ass).replace("\\","/").replace(":",r"\:")+"'"; mix=AUDIO/"EP02V2_final_mix.wav"; FINAL.mkdir(parents=True,exist_ok=True); out=FINAL/"EP02_GATEWAY_V2_FINAL_1080p.mp4"
    run(["ffmpeg","-y","-hide_banner","-loglevel","error","-i",str(silent),"-i",str(mix),"-vf",assf,"-map","0:v:0","-map","1:a:0","-c:v","libx264","-preset","slow","-crf","18","-pix_fmt","yuv420p","-c:a","aac","-b:a","320k","-ar","48000","-movflags","+faststart","-shortest",str(out)]); print(out)


def qa() -> None:
    video=FINAL/"EP02_GATEWAY_V2_FINAL_1080p.mp4"; probe=json.loads(run(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(video)],True)); vs=next(s for s in probe["streams"] if s["codec_type"]=="video"); au=next(s for s in probe["streams"] if s["codec_type"]=="audio"); l=loudness(video); rows=json.loads(TIMELINE.read_text(encoding="utf-8")); dur=float(probe["format"]["duration"])
    checks={"1080p":vs.get("width")==1920 and vs.get("height")==1080,"h264_yuv420p":vs.get("codec_name")=="h264" and vs.get("pix_fmt")=="yuv420p","aac_48k_stereo":au.get("codec_name")=="aac" and au.get("sample_rate")=="48000" and au.get("channels")==2,"duration_match":abs(dur-duration(VOICE_MASTER))<.3,"shot_density":len(rows)>=105 and dur/len(rows)<=5.8,"loudness":abs(float(l["input_i"])+14)<=.5,"peak":float(l["input_tp"])<=-.8,"speed_112":json.loads((PROD/"voice"/"master"/"stem_report.json").read_text())["tts_speed"]==1.12}
    rep={"file":str(video.resolve()),"sha256":sha256(video),"bytes":video.stat().st_size,"duration":dur,"shots":len(rows),"average_shot_seconds":round(dur/len(rows),2),"video":{k:vs.get(k) for k in ("codec_name","width","height","pix_fmt","r_frame_rate")},"audio":{k:au.get(k) for k in ("codec_name","sample_rate","channels","bit_rate")},"loudness":l,"checks":checks}; (FINAL/"EP02_GATEWAY_V2_QA.json").write_text(json.dumps(rep,indent=2)+"\n",encoding="utf-8")
    run(["ffmpeg","-y","-hide_banner","-loglevel","error","-i",str(video),"-vf","fps=1/40,scale=480:270,tile=4x4","-frames:v","1","-q:v","2",str(FINAL/"EP02_GATEWAY_V2_CONTACT_SHEET.jpg")]); print(json.dumps(rep,indent=2));
    if not all(checks.values()): raise RuntimeError("QA failed")


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("command",choices=["master","align","srt","timeline","audio","render","qa","all"]); ap.add_argument("--force",action="store_true"); ap.add_argument("--limit",type=int); a=ap.parse_args()
    if a.command in ("master","all"): master_voice()
    if a.command in ("align","all"): align()
    if a.command in ("srt","all"): build_srt()
    if a.command in ("timeline","all"): build_timeline()
    if a.command in ("audio","all"): build_audio()
    if a.command in ("render","all"): render(a.force,a.limit)
    if a.command in ("qa","all") and not a.limit: qa()


if __name__=="__main__": main()
