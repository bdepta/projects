import sys
from PIL import Image, ImageDraw, ImageFont
BLUE=(10,110,209,255); ORANGE=(233,115,12,255); WHITE=(255,255,255,255); LINE=(216,222,229,255)
FONT="/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
def icon(variant,size=1024):
    S=size; im=Image.new("RGBA",(S,S),(0,0,0,0)); d=ImageDraw.Draw(im)
    m=int(S*0.04); r=int(S*0.2)
    if variant=="C":
        d.rounded_rectangle([m,m,S-m,S-m],r,fill=WHITE,outline=BLUE,width=int(S*0.05))
    else:
        d.rounded_rectangle([m,m,S-m,S-m],r,fill=WHITE,outline=LINE,width=int(S*0.012))
    f=ImageFont.truetype(FONT,int(S*0.40)); 
    # tight tracking
    txt="HSS"; gap=-int(S*0.012)
    ws=[d.textlength(c,font=f) for c in txt]; tot=sum(ws)+gap*2
    bb=f.getbbox("H"); capH=bb[3]-bb[1]
    x=(S-tot)/2; cy=S*0.47 if variant=="B" else S*0.5
    y=cy-capH/2-bb[1]
    for c,w in zip(txt,ws):
        d.text((x,y),c,font=f,fill=BLUE); x+=w+gap
    if variant=="B":
        bw=tot*0.62; by=cy+capH/2+S*0.07; bh=S*0.045
        d.rounded_rectangle([(S-bw)/2,by,(S+bw)/2,by+bh],bh/2,fill=ORANGE)
    return im
if __name__=="__main__":  # preview sheet: python make_icon.py <outdir>
    out=sys.argv[1]
    sheet=Image.new("RGBA",(3*360,400),(230,234,239,255))
    for i,v in enumerate("ABC"):
        sheet.alpha_composite(icon(v).resize((320,320),Image.LANCZOS),(i*360+20,40))
    sheet.save(out+"/proposals.png")
    for v in "ABC":
        icon(v).save(f"{out}/icon-{v}.png")
    # small-size check for B
    row=Image.new("RGBA",(300,70),(255,255,255,255)); x=6
    for s in (16,24,32,48):
        row.alpha_composite(icon("B").resize((s,s),Image.LANCZOS),(x,10)); x+=s+12
    row.save(out+"/small-B.png")
