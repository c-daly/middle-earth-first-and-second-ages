"""Rebuild the two-column reading edition from the adjacent manuscript on Windows.

Run this file with Python, ReportLab and Pillow installed. The source art lives
in ../art. Pagination is measured once before the linked contents are printed.
"""
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr
import os, re, tempfile, sys
from PIL import Image as PILImage
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import FrameBreak, HRFlowable, Preformatted
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, NextPageTemplate, CondPageBreak, KeepTogether)
from reportlab.lib.utils import ImageReader
folder=Path(__file__).resolve().parent
root=folder.parent
stem='middle-earth-in-the-first-and-second-ages'
raw=(folder/(stem+'.md')).read_text('utf-8')
output_cache=tempfile.TemporaryDirectory(prefix='middle-earth-book-')
work=Path(output_cache.name)
W,H=612,792
PW,PH=W*2,H
M=38
gutter=19
width=(W-2*M-gutter)/2
ink='#191917'
dim='#444440'
accent='#302d29'
linkcolor='#343d40'
paper='#ffffff'
for name,file in [('Text','times.ttf'),('TextB','timesbd.ttf'),('TextI','timesi.ttf'),('TextBI','timesbi.ttf'),('UI','GARA.TTF'),('UIB','GARABD.TTF'),('Display','pala.ttf'),('Tree','cour.ttf')]:
    pdfmetrics.registerFont(TTFont(name,Path(os.environ['WINDIR'])/'Fonts'/file))
pdfmetrics.registerFontFamily('Text',normal='Text',bold='TextB',italic='TextI',boldItalic='TextBI')
def style(name,font='Text',size=11,lead=15,**kw):
    return ParagraphStyle(name,fontName=font,fontSize=size,leading=lead,textColor=kw.pop('textColor',HexColor(ink)),**kw)
body=style('Body',size=10.5,lead=12.85,spaceAfter=4.7,allowWidows=0,allowOrphans=0,alignment=TA_JUSTIFY)
part=style('Part','UIB',12,14,spaceBefore=10,spaceAfter=7,keepWithNext=1,alignment=TA_CENTER)
chapter=style('Chapter','Display',18,20.3,spaceBefore=10,spaceAfter=7,keepWithNext=1,alignment=TA_CENTER)
sub=style('Sub','UIB',13.1,14.4,spaceBefore=7,spaceAfter=4,keepWithNext=1,alignment=TA_CENTER)
cap=style('Cap','TextI',9.3,11,spaceBefore=4,spaceAfter=7)
brief=style('Brief','TextI',9.8,11.6,spaceAfter=4,keepWithNext=1,alignment=TA_CENTER)
cell=style('Cell','Text',9.6,11.3,spaceAfter=0)
th=style('Table header','UIB',9.9,11.6,textColor=HexColor('#ffffff'))
tocstyle=style('Contents entries','Text',10.2,12.7)
tocnum=style('Folio','TextB',10.0,12.7,alignment=TA_RIGHT)
tocpart=style('Contents divisions','UIB',12,14,spaceBefore=7,spaceAfter=2)
entry=style('Register entries','TextB',10.7,12.5,spaceBefore=5,spaceAfter=2,keepWithNext=1)
record=style('Register text','Text',10.3,12.3,spaceAfter=3.5,allowWidows=0,allowOrphans=0,alignment=TA_JUSTIFY)
def slug(t):
    return re.sub(r'[^\w -]','',t.lower()).replace(' ','-')
blocks=re.split(r'\n\s*\n',raw.strip())
headings=[b.lstrip('# ') for b in blocks if b.startswith('#')]
dest={slug(t):f'sec{n:03}' for n,t in enumerate(headings)}
name='Middle-earth in the First and Second Ages'
def inline(s):
    bits=[]
    for token in re.split(r'(\[[^\]]+\]\([^\s]*?\)(?=[\s.,);·!?]|$))',s):
        m=re.fullmatch(r'\[([^\]]+)\]\((.*)\)',token)
        if m:
            label,uri=m.groups()
            if uri.startswith('#'): uri='#'+dest[uri[1:]]
            bits.append('<link color="'+linkcolor+'" href='+quoteattr(uri)+'>'+emphasis(label)+'</link>')
        else:
            bits.append(emphasis(token))
    return ''.join(bits)
def emphasis(s):
    s=escape(s)
    s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s)
    return re.sub(r'\*([^*]+?)\*',r'<i>\1</i>',s)
def jpg(src,maxsize):
    path=root/'art'/src
    f=work/(path.stem+str(maxsize)+'.jpg')
    if not f.exists() or f.stat().st_mtime<path.stat().st_mtime:
        with PILImage.open(path) as im:
            im.thumbnail((maxsize,maxsize),PILImage.Resampling.LANCZOS)
            im.convert('RGB').save(f,quality=93,optimize=True)
    return str(f)
coverjpg=jpg('the-chaining-of-melkor.png',2100)
platejpg=jpg('ancalagon-in-free-fall-3840x2160.png',2600)
def color(s):
    return HexColor(s)
def drawCover(c,d):
    c.setFillColor(color('#192021'));c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(color('#dfcbaa'));c.setFont('UIB',11)
    c.drawString(M,H-82,'A CAMPAIGN SOURCEBOOK')
    c.setFillColor(color('#fcf8ed'));c.setFont('Display',47)
    c.drawString(M,H-149,'Middle-earth in the');c.drawString(M,H-202,'First and Second Ages')
    cover_note=Paragraph(inline(blocks[1]),style('Cover note','Text',12,16,textColor=color('#e7daca')))
    _,note_height=cover_note.wrap(W-2*M,115)
    cover_note.drawOn(c,M,H-224-note_height)
    with PILImage.open(coverjpg) as im: iw,ih=im.size
    h=W*ih/iw
    c.drawImage(coverjpg,0,96,W,h)
    c.setFillColor(color('#d5c7b6'));c.setFont('TextI',11);c.drawString(M,61,'The chaining of Melkor')
    c.setFillColor(color('#b8b4aa'));c.setFont('UI',9);c.drawRightString(W-M,61,'MANUSCRIPT EDITION')
def paperPage(c,d):
    c.setFillColor(color(paper));c.rect(0,0,W,H,fill=1,stroke=0)
def footer(c,d):
    odd=d.page%2
    head=getattr(d,'running','Middle-earth in the First and Second Ages')
    c.setFillColor(color(ink));c.setStrokeColor(color(ink))
    c.setLineWidth(.8);c.line(M,H-30,W-M,H-30)
    c.setLineWidth(.35);c.line(M,H-32,W-M,H-32)
    c.setFont('UIB',9);c.drawString(M,H-23,'MIDDLE-EARTH')
    c.setFont('TextI',9);c.drawRightString(W-M,H-23,head)
    c.setLineWidth(.35);c.line(M,31,W-M,31)
    c.setFont('TextB',11)
    if odd:c.drawRightString(W-M,17,str(d.page))
    else:c.drawString(M,17,str(d.page))
    c.setFont('UI',8.4);c.drawCentredString(W/2,17,'FIRST AND SECOND AGES')
def drawPlate(c,d):
    c.setFillColor(color('#191c1e'));c.rect(0,0,PW,PH,stroke=0,fill=1)
    hh=PW*9/16
    c.drawImage(platejpg,0,PH-hh,PW,hh)
    c.setFillColor(color('#f4ead7'));c.setFont('Display',24);c.drawString(36,35,'The fall of Ancalagon')
    c.setFillColor(color('#e3ddd4'));c.setFont('Text',11)
    c.drawString(325,44,'The Silmaril shines on Eärendil’s brow. Beneath Vingilot, Ancalagon falls towards the three peaks of Thangorodrim.')
    c.drawString(325,26,'The War of Wrath, at the ending of the First Age.')
    c.setFillColor(color('#cec4b7'));c.setFont('UI',10);c.drawRightString(PW-28,27,str(d.page))
    c.linkURL('https://martijn.coppoolse.com/books/part/1231',(323,23,820,55),relative=0,thickness=0)
    target=dest['the-fall-of-ancalagon'];c.bookmarkPage(target)
    c.addOutlineEntry('The fall of Ancalagon',target,4);d.pages['The fall of Ancalagon']=d.page
def frame(x=M,w=width,h=H,key='body'):
    return Frame(x,43,w,h-90,id=key,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
class Book(BaseDocTemplate):
    def __init__(self,path):
        super().__init__(path,pagesize=(W,H),title=name,author='Middle-earth campaign sourcebook',pageCompression=1,allowSplitting=1)
        self.addPageTemplates([PageTemplate('Cover',[frame()],onPage=drawCover,pagesize=(W,H)),PageTemplate('Body',[frame(key='left'),frame(M+width+gutter,key='right')],onPage=paperPage,onPageEnd=footer,pagesize=(W,H)),PageTemplate('Tables',[frame(M,W-2*M,key='reference')],onPage=paperPage,onPageEnd=footer,pagesize=(W,H)),PageTemplate('Plate',[frame(M,PW-2*M,PH)],onPage=drawPlate,pagesize=(PW,PH))])
        self.pages={}
    def afterFlowable(self,f):
        if not hasattr(f,'bookmark'):return
        t,level=f.bookmark;k=dest[slug(t)]
        y=self.frame._y+f.height
        self.canv.bookmarkHorizontalAbsolute(k,y+8,left=self.frame._x1)
        self.pages[t]=self.page
        if level is not None:self.canv.addOutlineEntry(t,k,level)
        if level in (0, 1) or re.match(r'^\d+\. ', t):
            self.running=re.sub(r'^\d+\. ','',t)
def heading(t,sty,level,shown=None):
    f=Paragraph(inline(shown or t),sty);f.bookmark=(t,level);return f
def rowtable(lines, available=width):
    rows=[[v.strip() for v in l.strip('|').split('|')] for l in lines if not re.fullmatch(r'[\s|:-]+',l)]
    cols=len(rows[0])
    assert all(len(r)==cols for r in rows),rows
    ratios=[.29,.71] if cols==2 else [.21,.40,.39]
    if rows[0][0]=='Work and surviving evidence':ratios=[.59,.41]
    if rows[0][0]=='People and period':ratios=[.19,.47,.34]
    if rows[0][0]=='Where':ratios=[.25,.75]
    if rows[0][0]=='At the table':ratios=[.37,.25,.38]
    if rows[0][0]=='Subject' and cols==2:ratios=[.78,.22]
    rows=[[Paragraph(inline(v),th if i==0 else cell) for v in r] for i,r in enumerate(rows)]
    table=Table(rows,colWidths=[available*x for x in ratios],repeatRows=1,hAlign='LEFT',spaceBefore=4,spaceAfter=9)
    table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),color('#333332')),('ROWBACKGROUNDS',(0,1),(-1,-1),[color(paper),color('#f3f3f1')]),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.55,color('#a8a59c')),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
    return table
def tocrow(title, pages, indent=0, label=None, font=None):
    target = dest[slug(title)]
    def linked(value, sty):
        return Paragraph('<link href="#'+target+'">'+escape(str(value))+'</link>',sty)
    row = [linked(label or title,font or tocstyle), linked(pages.get(title,'·'),tocnum)]
    return Table([row],colWidths=[width-22,22],style=[
        ('LEFTPADDING',(0,0),(-1,-1),0),('LEFTPADDING',(0,0),(0,0),indent),
        ('RIGHTPADDING',(0,0),(-1,-1),0),('VALIGN',(0,0),(-1,-1),'TOP'),
        ('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),1)])
def rules():
    rule=HRFlowable(width='100%',thickness=.5,color=color(ink),spaceBefore=4,spaceAfter=4)
    rule.keepWithNext=True
    return rule
def contents(pages):
    entries = [heading('Contents',chapter,0)]
    start = blocks.index('## Contents') + 1
    listing = blocks[start].splitlines()
    age_titles = {'Before the First Age','The First Age','The Second Age','The Third Age'}
    major = style('Contents parts','UIB',12,14)
    minor = style('Contents sections','UIB',11,13)
    detail = style('Contents detail','TextI',9.2,10.6)
    front = {'About this edition','Using this book'}
    part_two = False
    for line in listing:
        match = re.fullmatch(r'( *)- \[([^\]]+)\]\(#[^)]+\)',line)
        depth = len(match[1]) // 2
        title = match[2]
        if title == 'Powers and arts':
            entries.append(FrameBreak())
        if depth == 0 and title not in front:
            part_two = title.startswith('Part Two')
            entries.extend([Spacer(1,6),rules(),tocrow(title,pages,font=major)])
        elif depth == 1 or title in age_titles:
            entries.extend([Spacer(1,4),tocrow(title,pages,depth*5,font=minor)])
        elif title == 'The fall of Ancalagon':
            entries.append(tocrow(title,pages,depth*5,'Plate · '+title,detail))
        else:
            entries.append(tocrow(title,pages,depth*5,font=detail if part_two and depth>2 else tocstyle))
    return entries

def records(block):
    lines=block.splitlines();data=[[v.strip() for v in x.strip('|').split('|')] for x in lines]
    hdr=data[0]
    if hdr[0]=='Subject':
        compact=['| Subject | Ch. |','|---|---|']
        for a,b,c in data[2:]:
            compact.append('| '+a+'. '+c+' | '+b+' |')
        return [rowtable(compact)]
    a=[]
    for row in data[2:]:
        assert len(row)==len(hdr), (hdr,row)
        first=row[0].replace('**','')
        if hdr[0]=='Work':
            match=re.match(r'\*\*(.+?)\*\* (.*)',row[0])
            if match:first=match[1];row[1]=match[2]+' '+row[1]
        a.append(Paragraph(inline(first),entry))
        a.append(Paragraph(inline(row[1]),record))
        if len(row)>2:
            a.append(Paragraph('<i>'+escape(hdr[2].rstrip('.'))+'.</i> '+inline(row[2]),record))
    return a
def flow(pages):
    a=[Spacer(1,1),NextPageTemplate('Body'),PageBreak()]
    ix=blocks.index('## About this edition')
    while ix<len(blocks) and blocks[ix]!='## Contents':
        b=blocks[ix]
        ix+=1
        if b=='## Using this book':
            a.append(FrameBreak())
        a.append(heading(b[3:],chapter,0) if b.startswith('## ') else Paragraph(inline(b),body))
    a.append(PageBreak())
    a.extend(contents(pages))
    a.append(PageBreak())
    ix=next(j for j,b in enumerate(blocks) if b.startswith('## Part One'))
    current=0
    nsub=0
    section=''
    root_section=''
    while ix<len(blocks):
        b=blocks[ix]
        ix+=1
        hdr=re.fullmatch(r'(#{2,6}) (.+)',b)
        if hdr:
            depth=len(hdr[1])
            t=hdr[2]
            if t=='The fall of Ancalagon':
                a.extend([NextPageTemplate('Plate'),PageBreak(),Spacer(1,1),
                          NextPageTemplate('Body'),PageBreak()])
                ix+=2
            elif depth==2:
                root_section=t
                section=''
                current=0
                if t=='Reference guide':
                    a.extend([NextPageTemplate('Tables'),PageBreak()])
                elif t=='Register of campaign choices':
                    a.extend([NextPageTemplate('Body'),PageBreak()])
                elif t.startswith('Part Two'):
                    a.append(PageBreak())
                a.extend([rules(), heading(t,part if t.startswith('Part ') else chapter,0,t.upper())])
            elif re.match(r'^\d+\. ',t):
                number,title=t.split('. ',1)
                current=int(number)
                nsub=0
                if t=='28. Witnesses, danger, and consequence':
                    a.append(PageBreak())
                level=3 if section=='History' else 2
                a.extend([CondPageBreak(95),rules(),heading(t,chapter,level,number+'.0 '+title.upper())])
            elif depth==3:
                section=t
                current=0
                a.extend([CondPageBreak(112),heading(t,part,1,t.upper())])
            elif section=='History' and depth==4:
                a.extend([CondPageBreak(105),heading(t,sub,2)])
            elif root_section in ('Reference guide','Register of campaign choices'):
                a.append(heading(t,sub,2 if root_section=='Reference guide' else 1))
            elif section=='Adventure ideas' and depth==4:
                current=0
                a.extend([CondPageBreak(110),rules(),heading(t,chapter,2,t.upper())])
            else:
                nsub+=1
                label=f'{current}.{nsub}  {t}' if current else t
                level=3 if root_section.startswith('Part Two') or section=='Adventure ideas' or current in (15,18,21) else None
                if t in ('A place and its keepers','Ruling on a work of power'):
                    a.append(FrameBreak())
                a.append(heading(t,sub,level,label))
            continue
        if b.startswith('```text\n'):
            lines=b.splitlines()[1:-1]
            tree_style=style('Kindred tree','Tree',8.9,11.6,spaceBefore=4,spaceAfter=9)
            a.append(KeepTogether([Preformatted('\n'.join(lines),tree_style)]))
            continue
        if b.startswith('!['):
            filename=b.split('](')[1][:-1].split('/')[-1];f=jpg(filename,1550)
            with PILImage.open(f) as im: w,h=im.size
            drawW=min(width,130*w/h) if filename.startswith('sketch') else width
            pic=Image(f,width=drawW,height=drawW*h/w);pic.hAlign='CENTER'
            if 'ecthelion' in filename:a.append(KeepTogether([pic,Paragraph(inline(blocks[ix]),cap)]));ix+=1
            else:a.extend([pic,Spacer(1,5)])
            continue
        if b.startswith('|'):
            if root_section=='Reference guide':
                # A heading should keep the column labels and the first two rows
                # together. Keeping the whole table would waste the previous page.
                reservation=CondPageBreak(126)
                start=len(a)
                while start and getattr(a[start-1],'getKeepWithNext',lambda:False)():
                    start-=1
                if start<len(a):
                    a.insert(start,reservation)
                    a[-1].keepWithNext=False
                a.append(rowtable(b.splitlines(),W-2*M))
            else:
                a.extend(records(b))
            continue
        if b.startswith('- '):
            for l in b.splitlines():a.append(Paragraph(inline(l[2:]),body))
            continue
        if re.fullmatch(r'\*[^*]+\*',b):a.append(Paragraph(inline(b[1:-1]),brief));continue
        prose_style=record if root_section=='Register of campaign choices' else body
        a.append(Paragraph(inline(b),prose_style))
    return a
destfile=str(folder/(stem+'.pdf'))
first=Book(str(work/'pagination.pdf'));first.build(flow({}))
second=Book(str(work/'edition.pdf'));second.build(flow(first.pages))
assert first.pages==second.pages
from shutil import copyfile
staged=Path(destfile).with_suffix('.building.pdf')
copyfile(work/'edition.pdf',staged)
staged.replace(destfile)
output_cache.cleanup()
print('Pages:',second.page,'Plate:',second.pages['The fall of Ancalagon'],'Procedures:',second.pages['Guidance for the gamemaster'],'Register:',second.pages['Register of campaign choices'])
