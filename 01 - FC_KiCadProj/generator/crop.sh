cd /tmp/claude-0 && pdftoppm -r 260 -png sch.pdf big && python3 -c "
from PIL import Image
im=Image.open('big-1.png'); W,H=im.size
def crop(n,x0,y0,x1,y1):
    s=W/420.0; im.crop((int(x0*s),int(y0*s),int(x1*s),int(y1*s))).save(n)
crop('A.png',10,10,180,120); crop('B.png',10,120,180,190); crop('C.png',180,8,285,216); crop('D.png',284,8,412,152); crop('E.png',8,190,285,290); crop('F.png',284,150,412,252)
"
