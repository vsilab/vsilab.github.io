# Regenerates assets/seal.svg. Needs: pip install fonttools brotli; npm i @fontsource/noto-serif-kr (run from the folder holding node_modules).
# Writes inseal-<weight>.svg; assets/seal.svg is the 700 version turned into a mask (name carved out of a solid square).
# 이응주 carved seal (음각). Traditional layout: 이 alone in the right column, 응 over 주 in the left, read right to left.
# Glyph outlines come from Noto Serif KR; 이 is rebuilt so its ㅇ keeps its true round form while only the shaft of ㅣ
# grows to the full column height (head and foot of the stroke are kept at their drawn size).
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.filterPen import FilterPen

W=sys.argv[1] if len(sys.argv)>1 else '700'
font=TTFont(f'node_modules/@fontsource/noto-serif-kr/files/noto-serif-kr-korean-{W}-normal.woff2')
gs=font.getGlyphSet(); cmap=font.getBestCmap()

def contours(ch):
    rp=RecordingPen(); gs[cmap[ord(ch)]].draw(rp)
    out=[];cur=[]
    for op,args in rp.value:
        cur.append((op,args))
        if op in('closePath','endPath'): out.append(cur);cur=[]
    return out
def bounds(cs):
    bp=BoundsPen(gs)
    for c in cs:
        for op,args in c: getattr(bp,op)(*args)
    return bp.bounds
class MapPen(FilterPen):
    def __init__(s,out,f): super().__init__(out); s.f=f
    def moveTo(s,p): s._outPen.moveTo(s.f(p))
    def lineTo(s,p): s._outPen.lineTo(s.f(p))
    def curveTo(s,*ps): s._outPen.curveTo(*[s.f(p) for p in ps])
    def qCurveTo(s,*ps): s._outPen.qCurveTo(*[None if p is None else s.f(p) for p in ps])
def path(cs,f):
    sp=SVGPathPen(gs); mp=MapPen(sp,f)
    for c in cs:
        for op,args in c: getattr(mp,op)(*args)
    return sp.getCommands()
def fit(cs,x0,y0,x1,y1,maxdist=1.10):
    bx0,by0,bx1,by1=bounds(cs); sx=(x1-x0)/(bx1-bx0); sy=(y1-y0)/(by1-by0)
    # allow a slight stretch to fill the cell, as carved seals do, but never distort the form
    if sx/sy>maxdist: sx=sy*maxdist
    if sy/sx>maxdist: sy=sx*maxdist
    cx=(x0+x1)/2; cy=(y0+y1)/2; mx=(bx0+bx1)/2; my=(by0+by1)/2
    return path(cs,lambda p:(cx+(p[0]-mx)*sx, cy-(p[1]-my)*sy))

S=100; m=6.5; g=4.6         # seal size, border, gutter
inner0,inner1=m+g,S-m-g
span=inner1-inner0-g
L0,L1=inner0,inner0+span*0.60; R0,R1=L1+g,inner1
cellh=(inner1-inner0-g)/2
d=[]
d.append(fit(contours('응'),L0,inner0,L1,inner0+cellh))
d.append(fit(contours('주'),L0,inner1-cellh,L1,inner1))
# 이: split the ㅇ (two contours) from the ㅣ stroke
cs=contours('이'); bb=[bounds([c]) for c in cs]
iv=max(range(len(cs)),key=lambda i:bb[i][3]-bb[i][1])
stem=[cs[iv]]; ring=[c for i,c in enumerate(cs) if i!=iv]
rb=bounds(ring); sb=bounds(stem)
jb=bounds(contours('주')); k=min((L1-L0)/(jb[2]-jb[0]),cellh/(jb[3]-jb[1]))*1.04
k=min(k,(R1-R0)/(sb[2]-rb[0]))
gw=(sb[2]-rb[0])*k; ox=R0+((R1-R0)-gw)/2
# ㅇ: true proportions, centred a little above the middle of the column
rh=(rb[3]-rb[1])*k; rcy=inner0+(inner1-inner0)*0.46
d.append(path(ring,lambda p:(ox+(p[0]-rb[0])*k, rcy-(p[1]-(rb[1]+rb[3])/2)*k)))
# ㅣ: head and foot at drawn size, only the shaft lengthened to the full column height
H0,H1=sb[1],sb[3]; head=H1-(H1-H0)*0.22; foot=H0+(H1-H0)*0.14
top_y,bot_y=inner0,inner1
def ymap(y):
    if y>=head: return top_y+(H1-y)*k
    if y<=foot: return bot_y-(y-H0)*k
    a=top_y+(H1-head)*k; b=bot_y-(foot-H0)*k
    return a+(head-y)/(head-foot)*(b-a)
d.append(path(stem,lambda p:(ox+(p[0]-rb[0])*k, ymap(p[1]))))
INK='#111418'; PAPER='#fcfcfb'
glyphs=' '.join(d)
svg=(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S} {S}"><rect width="{S}" height="{S}" fill="{INK}"/>'
     f'<path fill="{PAPER}" d="{glyphs}"/></svg>')
open(f'inseal-{W}.svg','w').write(svg)
# variant: hairline inner rule around the characters, as on fine carved seals
r=m*0.55
svg2=(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S} {S}"><rect width="{S}" height="{S}" fill="{INK}"/><path fill="{PAPER}" d="{glyphs}"/>'
      f'<rect x="{r}" y="{r}" width="{S-2*r}" height="{S-2*r}" fill="none" stroke="{PAPER}" stroke-width="0.7"/></svg>')
open(f'inseal-{W}-rule.svg','w').write(svg2)
print('ok')
