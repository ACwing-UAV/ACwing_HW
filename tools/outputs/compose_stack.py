from PIL import Image, ImageDraw, ImageFont
F='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def load(p, W, H):
    im=Image.open(p).convert('RGBA'); bg=Image.new('RGBA',im.size,'white'); bg.alpha_composite(im)
    a=im.split()[3].point(lambda v:255 if v>8 else 0); bb=a.getbbox(); m=20
    c=bg.crop((max(0,bb[0]-m),max(0,bb[1]-m),min(im.width,bb[2]+m),min(im.height,bb[3]+m))).convert('RGB'); c.thumbnail((W,H),Image.LANCZOS); return c
out=Image.new('RGB',(1800,820),'white'); d=ImageDraw.Draw(out)
d.text((24,18),'ACwing stack, rev A, 1.0 mm boards: ESC 1S + FC (grommets, 5 mm gap) + GPS (6 mm standoffs)',fill='black',font=ImageFont.truetype(F,26))
f=ImageFont.truetype(F,17)
for k,(n,cap) in enumerate((('stack_frontright.png','Front-right view: Qwiic FC J3 -> GPS J1 on the right edge, corner LEDs, both USB-C at the rear-right'),
                            ('stack_front.png','Front view: ESC A cable, FC J2 straight above ESC J1 (same edge distance, front-left)'))):
    im=load('/home/claude/stack/'+n,860,640); x=k*900+(900-im.width)//2; y=80+(650-im.height)//2; out.paste(im,(x,y))
    tw=d.textlength(cap,font=f); d.text((k*900+(900-tw)/2,770),cap,fill=(60,60,60),font=f)
out.save('/home/claude/acwing_hw/00 - Docs/04 - System_Docs/ACwing_stack_3D.png',optimize=True)
