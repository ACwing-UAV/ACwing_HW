from PIL import Image, ImageDraw, ImageFont
import sys
F='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def load(p, size):
    im=Image.open(p).convert('RGBA')
    bg=Image.new('RGBA',im.size,(255,255,255,255)); bg.alpha_composite(im)
    a=im.split()[3].point(lambda v:255 if v>20 else 0); bb=a.getbbox()
    m=12; bb=(max(0,bb[0]-m),max(0,bb[1]-m),min(im.width,bb[2]+m),min(im.height,bb[3]+m))
    c=bg.crop(bb).convert('RGB'); c.thumbnail((size,size),Image.LANCZOS); return c
def panel(W,H,items,title=None,top=0):
    out=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(out)
    fnt=ImageFont.truetype(F,22); tf=ImageFont.truetype(F,26)
    if title: d.text((20,12),title,fill='black',font=tf)
    n=len(items); cw=W//n
    for k,(im,cap) in enumerate(items):
        x=k*cw+(cw-im.width)//2; y=top+(H-top-50-im.height)//2
        out.paste(im,(x,y)); tw=d.textlength(cap,font=fnt); d.text((k*cw+(cw-tw)/2,H-42),cap,fill=(60,60,60),font=fnt)
    return out
R='/tmp/rend/'
names={'ACwing_FC_A':('ACwing FC rev A','00 - FC_Docs'),'ACwing_ESC1S_A':('ACwing ESC 1S rev A','01 - ESC_1S_Docs'),
       'ACwing_GPS_A':('ACwing GPS rev A','02 - GPS_Docs'),'ACwing_Flow_A':('ACwing Flow rev A','03 - FLOW_Docs')}
for n,(t,d) in names.items():
    D='/home/claude/acwing_hw/00 - Docs/'+d+'/'
    panel(1900,1030,[(load(R+n+'_top.png',920),'Top'),(load(R+n+'_bot.png',920),'Bottom (seen from below)')],title=t,top=55).save(D+n+'_pcb.png',optimize=True)
    panel(1920,680,[(load(R+n+'_top.png',610),'Top'),(load(R+n+'_iso.png',610),'Isometric'),(load(R+n+'_bot.png',610),'Bottom')]).save(D+n+'_3D.png',optimize=True)
    print(n)
