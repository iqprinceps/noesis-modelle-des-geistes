#!/usr/bin/env python3
"""NOESIS local render orchestrator.

Shared technical engine, episode-specific camera profiles. Voice alignment defines
beat boundaries; each cue can resolve to one or many local media files, so shot
counts stay episode-specific instead of following a template.
"""
from __future__ import annotations
import argparse, csv, json, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FPS, SUB = 30, 4
VIDEO_EXT={'.mp4','.mov','.mkv','.webm','.m4v','.avi'}
IMAGE_EXT={'.png','.jpg','.jpeg','.webp','.tif','.tiff'}
MEDIA_EXT=VIDEO_EXT|IMAGE_EXT
PROFILES={
'EP04A':dict(summary='EP04A_JUNG_KUNDALINI_V5',cue='VISUAL_CUE_SHEET_V5_FINAL.csv',voice='EP04A_JUNG_KUNDALINI_V5_VO_MASTER.wav',alignment='EP04A_JUNG_KUNDALINI_V5_alignment.json',out='EP04A_JUNG_KUNDALINI_V5',camera='vision',zoom=.052,hold_zoom=.022,fade=.18,bg='#0B0A0D'),
'EP04B':dict(summary='EP04B_CHAKRA_GENEALOGIE_V5',cue='VISUAL_CUE_SHEET_V5.csv',voice='EP04B_CHAKRA_GENEALOGIE_V5_VO_MASTER.wav',alignment='EP04B_CHAKRA_GENEALOGIE_V5_alignment.json',out='EP04B_CHAKRA_GENEALOGIE_V5',camera='archive',zoom=.042,hold_zoom=.015,fade=.12,bg='#11100E'),
'EP05':dict(summary='EP05_JUNG_PAULI_V4',cue='VISUAL_CUE_SHEET.csv',cue_fallback='03_EPISODEN/TYPE_B/EP05_JUNG_PAULI/VISUAL_CUE_SHEET.csv',voice='EP05_JUNG_PAULI_V4_VO_MASTER.wav',alignment='EP05_JUNG_PAULI_V4_alignment.json',out='EP05_JUNG_PAULI_V4',camera='precision',zoom=.044,hold_zoom=.018,fade=.14,bg='#0D1014'),
'EP06':dict(summary='EP06_SCHLAFPARALYSE_V4',cue='VISUAL_CUE_SHEET.csv',voice='EP06_SCHLAFPARALYSE_V4_VO_MASTER.wav',alignment='EP06_SCHLAFPARALYSE_V4_alignment.json',out='EP06_SCHLAFPARALYSE_V4',camera='intimate',zoom=.022,hold_zoom=.006,source_zoom=.008,fade=.16,bg='#090A0D'),
'EP07':dict(summary='EP07_SCHLAFPARALYSE_V4',cue='VISUAL_CUE_SHEET.csv',voice='EP07_SCHLAFPARALYSE_V4_VO_MASTER.wav',alignment='EP07_SCHLAFPARALYSE_V4_alignment.json',out='EP07_SCHLAFPARALYSE_V4',camera='archive',zoom=.015,hold_zoom=.004,source_zoom=.006,fade=.12,bg='#100D0B'),
'EP08':dict(summary='EP08_SCHLAFPARALYSE_V4',cue='VISUAL_CUE_SHEET.csv',voice='EP08_SCHLAFPARALYSE_V4_VO_MASTER.wav',alignment='EP08_SCHLAFPARALYSE_V4_alignment.json',out='EP08_SCHLAFPARALYSE_V4',camera='network',zoom=.024,hold_zoom=.007,source_zoom=.008,fade=.14,bg='#080B10')}

def run(a,capture=False):
 p=subprocess.run(a,text=True,capture_output=capture)
 if p.returncode: raise RuntimeError((p.stderr or p.stdout or 'command failed')[-8000:])
 return (p.stdout or '')+(p.stderr or '')
def dur(p): return float(run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(p)],True).strip())

def paths(ep):
 c=PROFILES[ep]; s=ROOT/'PRODUCTION_SUMMARY'/c['summary']; prod=ROOT/'06_PRODUCTION'/c['out']
 cues=[s/c['cue']]+([ROOT/c['cue_fallback']] if c.get('cue_fallback') else [])
 cue=next((x for x in cues if x.is_file()),cues[0])
 voices=[s/'voice'/'master'/c['voice'],prod/'voice'/'master'/c['voice'],prod/'audio'/c['voice']]
 aligns=[s/'voice'/'alignment'/c['alignment'],prod/'voice'/'alignment'/c['alignment']]
 voice=next((x for x in voices if x.is_file()),voices[0]); align=next((x for x in aligns if x.is_file()),aligns[0])
 return dict(summary=s,prod=prod,cue=cue,voice=voice,alignment=align,
  timeline=prod/'timeline'/f"{c['out']}_timeline.json",segments=prod/'render'/'segments',
  picture=prod/'render'/'picture.mp4',final=prod/'render'/'final'/f"{c['out']}_FINAL.mp4",
  manifest=prod/'render_manifest.json')

def read_cues(p):
 with p.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
 if not rows: raise SystemExit(f'Empty cue sheet: {p}')
 return rows
def cue_id(r,i): return r.get('cue_id') or r.get('id') or r.get('act') or f'CUE{i+1:03d}'
def cue_anchor(r): return r.get('voice_anchor') or r.get('anchor') or r.get('anchor_text') or ''
def cue_scene(r): return r.get('section') or r.get('scene') or r.get('act') or ''

def media_kind(q):
 if not q:return 'MISSING'
 if q.suffix.lower() in VIDEO_EXT:return 'VIDEO'
 s=q.as_posix().upper(); stem=q.stem.upper()
 if stem.startswith('CARD') or '/CARDS/' in s:return 'CARD'
 documentary=('MAP','DOCUMENT','SCAN','PDF','TESTIMONY','DEPOSITION','EXAMINATION','RECORD','PSG','EEG','POLYSOMNOGRAPH','SOURCE_TABLE','MANIFEST','NEWSPAPER','LETTER','FILE_1947','DIAGRAM')
 if any(token in stem for token in documentary):return 'SOURCE_STATIC'
 if '/01_ORIGINAL_GREEN/' in s or '/02_REVIEW_YELLOW/' in s:return 'SOURCE'
 return 'STILL'

def alignment_chars(d):
 for x in [d]+[d[k] for k in ('alignment','normalized_alignment') if isinstance(d.get(k),dict)]:
  ch=x.get('characters') or x.get('chars'); st=x.get('character_start_times_seconds') or x.get('starts'); en=x.get('character_end_times_seconds') or x.get('ends')
  if isinstance(ch,list) and isinstance(st,list) and isinstance(en,list): return ''.join(ch),[float(v) for v in st],[float(v) for v in en]
 words=d.get('words')
 if isinstance(words,list) and words:
  text=''; starts=[]; ends=[]
  for w in words:
   t=str(w.get('text') or w.get('word') or '')
   if text and t and t[0] not in '.,;:!?': t=' '+t
   s=float(w.get('start',0)); e=float(w.get('end',s)); text+=t; starts += [s]*len(t); ends += [e]*len(t)
  return text,starts,ends
 raise SystemExit('Unsupported forced-alignment JSON schema')
def anchor_time(anchor,text,starts,default):
 for q in [x.strip() for x in re.split(r'\s*/\s*|\s*\.\.\.\s*',anchor) if len(x.strip())>=3] or [anchor]:
  m=re.search(re.escape(q),text,re.I)
  if m: return starts[min(m.start(),len(starts)-1)]
 return default

def media_index(p):
 roots=[p['prod']/'visuals',p['prod']/'motion',p['prod']/'motion_clips',ROOT/'05_GENERATED',ROOT/'04_ASSETS']; out=[]
 for root in roots:
  if root.exists(): out += [x for x in root.rglob('*') if x.is_file() and x.suffix.lower() in MEDIA_EXT]
 return out
def tokens(raw):
 bad={'archive','edit','motion','generated','archive+motion','archive/reconstruction/motion mix'}
 return [x.strip() for x in re.split(r'\s*\+\s*|\s+or\s+|\s*->\s*|\s*,\s*',raw or '',flags=re.I) if x.strip() and x.strip().casefold() not in bad]
def score(tok,p):
 t=re.sub('[^a-z0-9]+','',tok.casefold()); n=re.sub('[^a-z0-9]+','',p.stem.casefold())
 if len(t)<3:return -1
 if t==n:return 100
 if t in n:return 70
 return sum(10 for c in re.split('[^A-Za-z0-9]+',tok) if len(c)>=3 and re.sub('[^a-z0-9]+','',c.casefold()) in n)

def raw_manifest(p):
 if not p['manifest'].is_file(): return {}
 d=json.loads(p['manifest'].read_text(encoding='utf-8')); return d.get('assets',d)
def to_path(x):
 q=Path(str(x)); return q if q.is_absolute() else ROOT/q
def manifest_paths(v):
 if isinstance(v,str): v=[v] if v else []
 if not isinstance(v,list): return []
 return [to_path(x) for x in v if x and to_path(x).is_file()]

def auto_visuals(row,idx):
 found=[]; spec=row.get('source_or_generated') or row.get('asset') or row.get('visual') or ''
 for tok in tokens(spec):
  ranked=sorted(((score(tok,q),q) for q in idx),reverse=True,key=lambda z:z[0])
  if ranked and ranked[0][0]>=20 and ranked[0][1] not in found: found.append(ranked[0][1])
 if found:return found
 words=[w for w in re.findall('[A-Za-z0-9]{4,}',row.get('primary_visual') or row.get('beat') or '') if w.casefold() not in {'real','archive','historical','generic','motion','source'}]
 ranked=sorted(((sum(w.casefold() in q.stem.casefold() for w in words),q) for q in idx),reverse=True,key=lambda z:z[0])
 return [ranked[0][1]] if ranked and ranked[0][0]>0 else []
def resolve_visuals(row,i,idx,man):
 cid=cue_id(row,i); explicit=manifest_paths(man.get(cid))
 return explicit if explicit else auto_visuals(row,idx)

def write_manifest(ep,p,cues,idx):
 old=raw_manifest(p); assets=dict(old); unresolved=[]
 for i,row in enumerate(cues):
  cid=cue_id(row,i)
  if cid in assets: continue
  qs=auto_visuals(row,idx)
  vals=[]
  for q in qs:
   try: vals.append(str(q.relative_to(ROOT)))
   except ValueError: vals.append(str(q))
  assets[cid]=vals[0] if len(vals)==1 else vals
  if not vals: unresolved.append(cid)
 p['manifest'].parent.mkdir(parents=True,exist_ok=True)
 p['manifest'].write_text(json.dumps({'episode':ep,'note':'A cue may map to one path or a list of paths. Lists expand into individual shots inside the cue/act window. Empty entries must be filled locally; the renderer never invents footage.','assets':assets},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('Manifest:',p['manifest']);
 if unresolved: print('Unresolved:',len(unresolved),'->',', '.join(unresolved[:20]))

def build_timeline(ep,p,cues,idx):
 text,starts,_=alignment_chars(json.loads(p['alignment'].read_text(encoding='utf-8'))); total=dur(p['voice']); man=raw_manifest(p); beats=[]; cursor=0.0
 for i,row in enumerate(cues):
  t=max(cursor,min(anchor_time(cue_anchor(row),text,starts,cursor),total-.05)); beats.append((row,t)); cursor=t
 shots=[]
 for i,(row,start) in enumerate(beats):
  end=beats[i+1][1] if i+1<len(beats) else total
  if end<=start:end=min(total,start+.35)
  visuals=resolve_visuals(row,i,idx,man); n=max(1,len(visuals)); span=end-start
  for j in range(n):
   s=start+span*j/n; e=start+span*(j+1)/n; q=visuals[j] if visuals else None; base=cue_id(row,i)
   shots.append(dict(shot_id=base if n==1 else f'{base}_{j+1:02d}',cue_id=base,scene=cue_scene(row),anchor=cue_anchor(row),
    pace=(row.get('pace') or 'normal').casefold(),function=row.get('edit_function') or row.get('edit_rule') or '',notes=row.get('notes') or '',
    visual=str(q) if q else '',kind=media_kind(q),start=round(s,3),end=round(e,3),duration=round(e-s,3)))
 for i,r in enumerate(shots):
  r['scene_first']=i==0 or shots[i-1]['scene']!=r['scene']; r['scene_last']=i==len(shots)-1 or shots[i+1]['scene']!=r['scene']; r['motion_policy']=motion_policy(ep,i,r)
 p['timeline'].parent.mkdir(parents=True,exist_ok=True); p['timeline'].write_text(json.dumps({'episode':ep,'duration':total,'voice':str(p['voice']),'shots':shots},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 miss=[r for r in shots if not r['visual']]; print(f'Timeline: {len(shots)} shots / {total:.2f}s / unresolved {len(miss)}')
 long=[r for r in shots if r['duration']>12]
 if long: print('QA note: long holds remain because this episode currently has sparse selected coverage:',', '.join(r['shot_id'] for r in long[:12]))
 if miss: print('Missing:',', '.join(r['shot_id'] for r in miss[:30]))
 return shots

def contain_needed(p):
 if p.suffix.lower() in VIDEO_EXT:return False
 try:
  from PIL import Image
  with Image.open(p) as im: ar=im.width/max(1,im.height)
  return not 1.62<=ar<=1.95
 except Exception:return False
def motion_policy(ep,i,r):
 kind=r.get('kind','STILL')
 if kind=='VIDEO':return 'NATIVE_CLIP_NO_EXTERNAL_CAMERA'
 if kind=='CARD':return 'STATIC_CARD'
 if kind=='SOURCE_STATIC':return 'STATIC_SOURCE'
 if kind=='SOURCE':return 'SUBTLE_SOURCE' if i%3==0 and r.get('pace') not in {'hold','reset'} else 'STATIC_SOURCE'
 # Only about half of ordinary stills move; the rest are deliberately calm.
 return 'SUBTLE_STILL' if i%2==0 and r.get('duration',0)>1.5 else 'STATIC_STILL'

def base_filter(r,scale='1920:1080'):
 # Die Hintergrundunschaerfe wird mit der Arbeitsaufloesung skaliert, sonst
 # wirkt der Grund bei hoeher aufgeloester Kameravorlage schaerfer als geplant.
 sigma=round(28*int(scale.split(':')[0])/1920,1)
 if contain_needed(Path(r['visual'])):return f'split=2[fg][bg];[bg]scale={scale}:force_original_aspect_ratio=increase,crop={scale},gblur=sigma={sigma},eq=brightness=-0.24[back];[fg]scale={scale}:force_original_aspect_ratio=decrease[front];[back][front]overlay=(W-w)/2:(H-h)/2'
 return f'scale={scale}:force_original_aspect_ratio=increase,crop={scale}'

def camera_filter(ep,i,r):
 c=PROFILES[ep]; policy=r.get('motion_policy') or motion_policy(ep,i,r); frames=max(2,round(r['duration']*FPS*SUB))
 fade=float(c['fade']); fi=f",fade=t=in:st=0:d={fade:.3f}:color={c['bg']}" if r['scene_first'] else ''; fo=f",fade=t=out:st={max(0,r['duration']-fade):.3f}:d={fade:.3f}:color={c['bg']}" if r['scene_last'] else ''
 if policy.startswith('STATIC_') or policy=='NATIVE_CLIP_NO_EXTERNAL_CAMERA':
  return base_filter(r)+f',fps={FPS},format=yuv420p'+fi+fo
 amount=c.get('source_zoom',.008) if policy=='SUBTLE_SOURCE' else (c['hold_zoom'] if r.get('pace') in {'hold','reset'} else c['zoom'])
 fam={'vision':['in','diag','out','up','in','left','out','right'],'archive':['left','right','in','down','right','out','up','left'],'precision':['in','right','out','left','down','in','up','right'],'intimate':['in','in','left','out','right','in','up','out'],'network':['diag','right','in','left','out','down','diag','up']}
 mode='in' if policy=='SUBTLE_SOURCE' else fam[c['camera']][i%8]; z0,z1=(1,1+amount) if mode!='out' else (1+amount,1); p=f'on/{frames}'; q=f'(({p})*({p})*(3-2*({p})))'; z=f'({z0:.5f}+({z1-z0:.5f})*{q})'
 x=f'(iw-iw/zoom)*(0.70*(1-{q}))' if mode=='left' else f'(iw-iw/zoom)*(0.70*{q})' if mode=='right' else f'(iw-iw/zoom)*(0.15+0.55*{q})' if mode=='diag' else '(iw-iw/zoom)/2'
 y=f'(ih-ih/zoom)*(0.70*(1-{q}))' if mode=='up' else f'(ih-ih/zoom)*(0.70*{q})' if mode=='down' else f'(ih-ih/zoom)*(0.70-0.50*{q})' if mode=='diag' else '(ih-ih/zoom)/2'
 # Produktionsstandard, "Die Fahrt muss glatt laufen": zoompan rechnet
 # ganzzahlig. Sieht es die Vorlage in Ausgabegroesse, ist ein Schritt ein
 # voller Ausgabepixel und die Fahrt laeuft in Stufen. Die Vorlage geht daher
 # auf 7680x4320, und zoompan gibt in 3840x2160 aus; der anschliessende
 # Lanczos-Downscale auf 1920 macht aus dem Ganzzahlschritt einen
 # Viertelpixelschritt.
 #
 # zoompan direkt auf 1920 ausgeben zu lassen genuegt nicht - sein interner
 # Scaler rastet dann wieder auf ganze Ausgabepixel (gemessen 0,41 statt 0,16).
 #
 # Zusaetzlich vier Zwischenschritte je Ausgabebild, gemittelt mit tmix: die
 # vier Positionen runden unterschiedlich, ihr Mittel bewegt sich in Vierteln.
 # tblend mittelte nur je zwei von vier Subframes und warf den Rest weg.
 base=base_filter(r,'7680:4320')
 weights=' '.join(['1']*SUB)
 return base+f",zoompan=z='{z}':x='{x}':y='{y}':d=1:s=3840x2160:fps={FPS*SUB},tmix=frames={SUB}:weights='{weights}',framestep={SUB},scale=1920:1080:flags=lanczos,fps={FPS},format=yuv420p"+fi+fo

def render(ep,p,shots):
 miss=[r for r in shots if not r['visual'] or not Path(r['visual']).is_file()]
 if miss: raise SystemExit('Unresolved/missing visuals: '+', '.join(r['shot_id'] for r in miss[:30]))
 p['segments'].mkdir(parents=True,exist_ok=True)
 for i,r in enumerate(shots):
  out=p['segments']/f"{i+1:03d}_{r['shot_id']}.mp4"
  if out.is_file() and dur(out)>=max(.1,r['duration']-.08):continue
  inp=['-stream_loop','-1','-i',r['visual']] if r['kind']=='VIDEO' else ['-loop','1','-i',r['visual']]
  run(['ffmpeg','-y','-hide_banner','-loglevel','error',*inp,'-t',f"{r['duration']:.3f}",'-vf',camera_filter(ep,i,r),'-an','-c:v','libx264','-preset','veryfast','-crf','16','-pix_fmt','yuv420p','-r',str(FPS),str(out)]); print(f"render {i+1:03d}/{len(shots)} {r['shot_id']}")
def picture(p,shots):
 lst=p['segments'].parent/'concat.txt'; lst.write_text('\n'.join("file '"+(p['segments']/f"{i+1:03d}_{r['shot_id']}.mp4").as_posix()+"'" for i,r in enumerate(shots))+'\n',encoding='utf-8'); run(['ffmpeg','-y','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(lst),'-c','copy',str(p['picture'])]); return p['picture']
def audio_choice(p):
 cs=[]
 for d in (p['prod']/'audio',p['summary']/'audio',p['summary']/'audio_stems'):
  if d.exists(): cs += [q for q in d.glob('*.wav') if 'MASTER' in q.name.upper() or 'MIX' in q.name.upper()]
 return cs[0] if cs else p['voice']
def final(p,shots):
 pic=picture(p,shots); a=audio_choice(p); p['final'].parent.mkdir(parents=True,exist_ok=True); run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(pic),'-i',str(a),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','320k','-shortest','-movflags','+faststart',str(p['final'])]); print('Final:',p['final'])
def doctor(p):
 checks=[('summary',p['summary'].is_dir(),p['summary']),('cue',p['cue'].is_file(),p['cue']),('voice',p['voice'].is_file(),p['voice']),('alignment',p['alignment'].is_file(),p['alignment'])]
 for n,ok,x in checks:print(f"{'OK' if ok else 'MISS':4} {n:10} {x}")
 for b in ('ffmpeg','ffprobe'):print(f"{'OK' if shutil.which(b) else 'MISS':4} binary     {b}")
 return 0 if all(ok for _,ok,_ in checks) and all(shutil.which(b) for b in ('ffmpeg','ffprobe')) else 1
def qa(p,shots):
 bad=[]
 for i,r in enumerate(shots):
  s=p['segments']/f"{i+1:03d}_{r['shot_id']}.mp4"
  if not s.is_file():bad.append((r['shot_id'],'missing'));continue
  d=dur(s)
  if abs(d-r['duration'])>.15:bad.append((r['shot_id'],f"duration {d:.2f}/{r['duration']:.2f}"))
 print(f'QA segments: {len(shots)-len(bad)}/{len(shots)} OK')
 if bad:return 1
 jitter=ROOT/'tools'/'spg_zappelpruefung.py'
 if jitter.is_file():
  try:run([sys.executable,str(jitter),str(p['timeline']),'--segmente',str(p['segments'])])
  except Exception as e:print('Camera QA warning:',e)
 return 0

def main():
 a=argparse.ArgumentParser();a.add_argument('episode',choices=PROFILES);a.add_argument('command',nargs='?',default='all',choices=['doctor','manifest','plan','render','final','qa','all']);x=a.parse_args(); ep=x.episode;p=paths(ep)
 if x.command=='doctor':return doctor(p)
 if doctor(p):raise SystemExit('Production inputs incomplete. Build voice master/alignment first.')
 cues=read_cues(p['cue']);idx=media_index(p)
 if x.command in {'manifest','all'}:write_manifest(ep,p,cues,idx)
 shots=build_timeline(ep,p,cues,idx)
 if x.command=='plan':return 0
 if x.command in {'render','all'}:render(ep,p,shots)
 if x.command in {'final','all'}:final(p,shots)
 if x.command in {'qa','all'}:return qa(p,shots)
 return 0
if __name__=='__main__':raise SystemExit(main())
