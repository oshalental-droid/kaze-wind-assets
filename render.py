from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
FONTS = [
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
    '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
    '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc',
]

def font(size):
    for p in FONTS:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    raise RuntimeError('Please install fonts-noto-cjk')

def wrap(draw, text, f, width):
    out = []
    for part in str(text).split('\n'):
        if not part:
            out.append('')
            continue
        cur=''
        for ch in part:
            if cur and draw.textbbox((0,0), cur+ch, font=f)[2]>width:
                out.append(cur)
                cur=ch
            else:
                cur+=ch
        if cur:
            out.append(cur)
    return out

def render_one(photo, scene, index, total, dest):
    w,h=1080,1350
    img=Image.new('RGB',(w,h),(255,255,255))
    d=ImageDraw.Draw(img)
    ink=(35,35,37)
    d.text((70,52),'風研究所',font=font(72),fill=ink)
    d.text((765,82),f'No.{index:03d} / {total:02d}',font=font(26),fill=(125,125,125))
    d.line([(70,170),(1010,170)],fill=(170,215,246),width=5)
    for idx,line in enumerate(wrap(d,scene.get('headline',''),font(53),920)[:3]):
        d.text((78,200+idx*72),line,font=font(53),fill=ink)
    sz=max(550,min(int(scene.get('avatar_size',810)),900))
    x=int(scene.get('avatar_center_x',540))-sz//2
    y=int(scene.get('avatar_top',340))
    img.paste(photo.resize((sz,sz),Image.Resampling.LANCZOS),(x,y))
    d=ImageDraw.Draw(img)
    d.line([(72,1150),(1008,1150)],fill=(228,230,232),width=2)
    for idx,line in enumerate(wrap(d,scene.get('body',''),font(40),920)[:3]):
        d.text((80,1180+idx*52),line,font=font(40),fill=ink)
    img.save(dest,format='PNG',optimize=True)

def main():
    path=ROOT/'assets'/'kazeo.png'
    if not path.exists():
        print('Mascot missing: upload assets/kazeo.png; skipping.')
        return
    photo=Image.open(path).convert('RGB')
    for fp in sorted((ROOT/'posts').glob('episode-*.json')):
        obj=json.loads(fp.read_text(encoding='utf-8'))
        panels=obj.get('panels',[])
        if not panels:
            continue
        out=ROOT/'outputs'/fp.stem
        out.mkdir(parents=True,exist_ok=True)
        for index,panel in enumerate(panels,1):
            render_one(photo,panel,index,len(panels),out/f'{index:02d}.png')
            print(f'Wrote {out}/{index:02d}.png')

if __name__=='__main__':
    main()
