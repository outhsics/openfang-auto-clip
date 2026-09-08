"""Fixture-specific Tears of Steel checks; requires numpy and ffmpeg."""
import sys,json,subprocess,hashlib,struct,argparse
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from auto_clip import build_transcript_payload

def run(args): return subprocess.check_output(args)
def audio(p,start=0):
 return np.frombuffer(run(['ffmpeg','-v','error','-ss',str(start),'-i',str(p),'-t','45','-vn','-ac','1','-ar','16000','-f','f32le','-']),dtype='<f4')

def spans(mask):
 edges=np.flatnonzero(np.diff(np.r_[False,mask,False]))
 return [[round(a/24,6),round(b/24,6)] for a,b in zip(edges[::2],edges[1::2])]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('source',type=Path)
parser.add_argument('output_dirs',type=Path,nargs='+')
args=parser.parse_args()
for d in args.output_dirs:
 name=d.name;p=next(d.glob('*.mp4'))
 report=json.loads((d/'report.json').read_text());start=report['clips'][0]['start']
 probe=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
 assert probe['format']['duration'] == '45.000000', probe['format']
 assert (probe['streams'][0]['width'],probe['streams'][0]['height']) == (1080,1920)
 (d/'ffprobe.json').write_text(json.dumps(probe,indent=2))
 subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(p),'-f','null','-'],check=True)
 frames=np.frombuffer(run(['ffmpeg','-v','error','-i',str(p),'-vf','crop=1080:520:0:1400,scale=270:130,format=gray','-f','rawvideo','-']),dtype=np.uint8).reshape(-1,130,270)
 mask=(frames>80).sum(axis=(1,2))>5
 cues=build_transcript_payload(d/'clip_01.srt')['segments']
 per_cue=[]
 for i,c in enumerate(cues,1):
  sample=(c['start']+min(45,c['end']))/2
  per_cue.append(dict(index=i,start=c['start'],end=c['end'],sample=sample,visible=bool(mask[min(len(mask)-1,round(sample*24))])))
 # Compare decoded source and output audio at three positions; positive lag means output audio is later.
 a=audio(args.source,start); b=audio(p)
 checks=[]
 for t in [6,20,34]:
  n=t*16000; ref=a[n:n+32000]; chunk=b[n-1600:n+33600]
  corr=np.correlate(chunk,ref,mode='valid');lag=int(corr.argmax())-1600
  aligned=b[n+lag:n+lag+32000]
  checks.append(dict(time=t,lag_ms=lag/16,correlation=float(np.corrcoef(ref,aligned)[0,1])))
 atoms=[]
 with p.open('rb') as f:
  while f.tell()<p.stat().st_size:
   pos=f.tell();length,kind=struct.unpack('>I4s',f.read(8));
   if length==1:length=struct.unpack('>Q',f.read(8))[0]
   if length==0:length=p.stat().st_size-pos
   atoms.append(dict(type=kind.decode(),offset=pos,size=length));f.seek(pos+length)
 result=dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),frame_count=len(mask),caption_spans=spans(mask),cues=per_cue,audio_alignment=checks,mp4_atoms=atoms)
 (d/'audit.json').write_text(json.dumps(result,indent=2))
 print(name,json.dumps(result))
