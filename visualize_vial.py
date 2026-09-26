#!/usr/bin/env python3
"""Render Charybdis 4x6 Vial exports using the actual macOS Ortho keylayout. Stdlib only."""
import argparse
import html
import json
import re
from pathlib import Path
import xml.etree.ElementTree as ET

MAC = dict(zip('ASDFHGZXCVBQWERYT', [0,1,2,3,4,5,6,7,8,9,11,12,13,14,15,16,17]))
MAC.update({'O':31,'U':32,'I':34,'P':35,'L':37,'J':38,'K':40,'N':45,'M':46,
 '1':18,'2':19,'3':20,'4':21,'5':23,'6':22,'7':26,'8':28,'9':25,'0':29,
 'EQUAL':24,'MINUS':27,'RBRACKET':30,'LBRACKET':33,'QUOTE':39,'SCOLON':41,
 'BSLASH':42,'COMMA':43,'SLASH':44,'DOT':47,'GRAVE':50,'SPACE':49,
 'KP_DOT':65,'KP_ASTERISK':67,'KP_PLUS':69,'KP_SLASH':75,'KP_MINUS':78,'KP_EQUAL':81,
 'KP_0':82,'KP_1':83,'KP_2':84,'KP_3':85,'KP_4':86,'KP_5':87,'KP_6':88,'KP_7':89,'KP_8':91,'KP_9':92})
ALIASES={'ENT':'ENTER','ESC':'ESCAPE','BSPC':'BSPACE','SPC':'SPACE','SCLN':'SCOLON','QUOT':'QUOTE','COMM':'COMMA','SLSH':'SLASH','BSLS':'BSLASH','GRV':'GRAVE','LBRC':'LBRACKET','RBRC':'RBRACKET','MINS':'MINUS','EQL':'EQUAL','LSFT':'LSHIFT','RSFT':'RSHIFT','LCTL':'LCTRL','RCTL':'RCTRL','RGHT':'RIGHT','TRNS':'TRNS','CAPS':'CAPSLOCK'}
LABELS={'ENTER':'Enter','ESCAPE':'Esc','TAB':'Tab','BSPACE':'⌫','DELETE':'Del','SPACE':'Space','LSHIFT':'⇧','RSHIFT':'⇧','LCTRL':'⌃','RCTRL':'⌃','LALT':'⌥','RALT':'⌥','LGUI':'⌘','RGUI':'⌘','CAPSLOCK':'RU / EN','LEFT':'←','RIGHT':'→','UP':'↑','DOWN':'↓','HOME':'Home','END':'End','PGUP':'PgUp','PGDOWN':'PgDn','VOLU':'Vol +','VOLD':'Vol −','MUTE':'Mute','MPLY':'Play','MNXT':'Next','MPRV':'Prev'}
MODS={'LSFT':{'shift'},'RSFT':{'shift'},'LALT':{'option'},'RALT':{'option'},'LGUI':{'command'},'RGUI':{'command'},'LCTL':{'control'},'RCTL':{'control'},'LSA':{'shift','option'},'LCA':{'control','option'},'LCS':{'control','shift'},'LAG':{'option','command'},'SGUI':{'shift','command'}}
GLYPHS={'shift':'⇧','option':'⌥','command':'⌘','control':'⌃'}
NAMES=['BASE','NUM','NAV','SYM']

class Layout:
 def __init__(self,path):
  raw=Path(path).read_text()
  # Apple's XML 1.1 includes control references rejected by ElementTree XML 1.0.
  def safe(m):
   v=int(m[1][1:],16) if m[1].startswith('x') else int(m[1])
   return '\uFFFD' if v<32 else m[0]
  self.root=ET.fromstring(re.sub(r'&#(x[0-9a-fA-F]+|[0-9]+);',safe,raw))
  self.name=self.root.get('name')
  self.sets={s.get('id'):s for s in self.root.findall('keyMapSet')}
  first=self.root.find('layouts/layout'); self.mapset=first.get('mapSet')
  self.modmap=self.root.find(f"modifierMap[@id='{first.get('modifiers')}']")
 def table(self,s,i):
  e=self.sets[s].find(f"keyMap[@index='{i}']")
  if e is None: return {}
  d=self.table(e.get('baseMapSet'),e.get('baseIndex')) if e.get('baseMapSet') else {}
  for k in e:
   d[int(k.get('code'))]=k.get('output') # actions are deliberately not guessed
  return d
 def output(self,code,mods):
  normalize={'anyShift':'shift','shift':'shift','rightShift':'shift','anyOption':'option','option':'option','rightOption':'option','anyControl':'control','control':'control','rightControl':'control','caps':'caps','command':'command'}
  for sel in self.modmap:
   for item in sel:
    required=set(); allowed=set()
    for token in item.get('keys','').split():
     name=normalize.get(token.rstrip('?'),token.rstrip('?'))
     allowed.add(name)
     if not token.endswith('?'): required.add(name)
    if required<=mods<=allowed: return self.table(self.mapset,sel.get('mapIndex')).get(code)
  return self.table(self.mapset,self.modmap.get('defaultIndex','0')).get(code)

def describe(key,layout,ru=False,shift=False):
 raw=str(key); mods=({'caps'} if ru else set())|({'shift'} if shift else set()); hold=''
 lt=re.fullmatch(r'LT(\d+)\((.+)\)',raw)
 if lt: hold='Удержание: '+(NAMES[int(lt[1])] if int(lt[1])<4 else 'L'+lt[1]); raw=lt[2]
 mt=re.fullmatch(r'(LGUI|RGUI|LALT|RALT|LCTL|RCTL|LSFT|RSFT)_T\((.+)\)',raw)
 if mt:
  hold='Удержание: '+''.join(GLYPHS[x] for x in ['control','option','shift','command'] if x in MODS[mt[1]])
  raw=mt[2]
 while True:
  m=re.fullmatch(r'([A-Z]+)\((.+)\)',raw)
  if not m or m[1] not in MODS: break
  mods |= MODS[m[1]]; raw=m[2]
 layer=re.fullmatch(r'(MO|TG|TO|DF|OSL|TT)\((\d+)\)',raw)
 if layer:
  n=int(layer[2]); return {'text':NAMES[n] if n<4 else 'L'+str(n),'hold':'Слой · '+layer[1],'kind':'layer','raw':str(key)}
 k=raw.removeprefix('KC_'); k=ALIASES.get(k,k)
 result={'text':raw,'hold':hold,'kind':'unknown','raw':str(key)}
 if k=='NO': result.update(text='—',kind='empty')
 elif k in LABELS or re.fullmatch(r'F\d+',k): result.update(text=LABELS.get(k,k),kind='control')
 elif k in MAC:
  value=layout.output(MAC[k],mods)
  if value is not None:
   if 'command' in mods or 'control' in mods:
    prefix=''.join(GLYPHS[x] for x in ['control','option','shift','command'] if x in mods)
    result.update(text=prefix+k,kind='control')
   else: result.update(text=value if value else '∅',kind='symbol' if value and not value.isalpha() else 'letter')
 elif raw.startswith(('RM_','QK_')): result.update(text={'QK_BOOT':'Boot','QK_CLEAR_EEPROM':'Reset','RM_TOGG':'RGB','RM_PREV':'RGB −','RM_NEXT':'RGB +'}.get(raw,raw),kind='control')
 return result

def build(data,layout):
 layers=data.get('layout',[])
 if not layers or any(len(l)!=10 or any(len(r)!=6 for r in l) for l in layers): raise ValueError('Ожидается матрица Charybdis 4×6: 10 строк × 6 столбцов на слой.')
 views={}
 for ru in [False,True]:
  for shift in [False,True]:
   result=[]
   for i,layer in enumerate(layers):
    cells=[]
    for r,row in enumerate(layer):
     for c,key in enumerate(row):
      if key==-1: continue
      source=i
      while key=='KC_TRNS' and source>0:
       source=0; key=layers[0][r][c]
      cell=describe(key,layout,ru,shift)
      cell.update(r=r,c=c,inherited=source!=i,source=source)
      cells.append(cell)
    result.append(cells)
   views[f'{int(ru)}{int(shift)}']=result
 combos=[]
 for combo in data.get('combo',[]):
  if len(combo)>=5 and combo[4]!='KC_NO': combos.append({'keys':[k.removeprefix('KC_') for k in combo[:4] if k!='KC_NO'],'result':describe(combo[4],layout)['text']})
 return {'views':views,'combos':combos,'layout':layout.name,'layers':len(layers)}

def static_board(cells):
 def key(cell):
  text=html.escape(cell['text']); hold=html.escape(cell['hold'])
  raw=html.escape(cell['raw'],quote=True)
  short_hold=html.escape(cell['hold'].removeprefix('Удержание: '))
  return f'<div class="key {cell["kind"]}" title="{raw}"><span class="position">{cell["r"]},{cell["c"]}</span><span class="value">{text}</span><span class="hold">{short_hold}</span></div>'
 lookup={(c['r'],c['c']):c for c in cells}
 halves=[]
 for side in range(2):
  keys=[]
  for r in range(4):
   for c in range(6):
    cell=lookup.get((r+5*side,5-c if side else c))
    if cell: keys.append(key(cell))
  positions=[(1,1,1),(3,2,1),(5,2,2)] if side else [(3,4,1),(4,5,1),(1,6,1),(5,5,2),(2,6,2)]
  thumbs=[]
  for c,x,y in positions:
   cell=lookup.get((9 if side else 4,c))
   if cell: thumbs.append(key(cell).replace('<div class=',f'<div style="grid-column:{x};grid-row:{y}" class=',1))
  keys.append('<div class="thumbs">'+''.join(thumbs)+'</div>')
  halves.append('<div class="half">'+''.join(keys)+'</div>')
 return ''.join(halves)

def static_fallback(data):
 sections=['<p>Все слои: EN и RU. В интерактивном режиме используй переключатели выше.</p>']
 for mode,label in [('00','EN'),('10','RU')]:
  for i,cells in enumerate(data['views'][mode]):
   title=f'{NAMES[i] if i<4 else i} / {label}'
   sections.append('<section class="layer-sheet"><h3>'+title+'</h3><div class="stage"><div class="board">'+static_board(cells)+'</div></div></section>')
 return ''.join(sections)

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('vil',type=Path)
 p.add_argument('--keylayout',type=Path,default=Path.home()/'Library/Keyboard Layouts/Universal.bundle/Contents/Resources/Universal Layout Ortho.keylayout')
 p.add_argument('-o','--output',type=Path,default=Path('keymap.html'))
 args=p.parse_args()
 try:
  data=build(json.loads(args.vil.read_text()),Layout(args.keylayout)); data['file']=args.vil.name
  template=Path(__file__).with_name('keymap_template.html').read_text()
  payload=json.dumps(data,ensure_ascii=False).replace('<','\\u003c').replace('&','\\u0026')
  args.output.parent.mkdir(parents=True,exist_ok=True)
  page=template.replace('__DATA__',payload).replace('__STATIC_BOARD__',static_board(data['views']['00'][0])).replace('__FALLBACK__',static_fallback(data))
  chips=''.join('<span class="chip">'+html.escape(' + '.join(c['keys'])+' → '+c['result'])+'</span>' for c in data['combos'])
  page=page.replace('__COMBOS__',chips).replace('__SUBTITLE__',html.escape(data['file']+' · '+data['layout']))
  args.output.write_text(page)
 except (OSError,ValueError,ET.ParseError) as e: p.exit(1,f'Ошибка: {e}\n')
 print(args.output.resolve())
if __name__=='__main__': main()
