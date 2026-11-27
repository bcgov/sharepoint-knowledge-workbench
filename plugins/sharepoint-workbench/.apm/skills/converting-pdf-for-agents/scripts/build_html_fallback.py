"""Fallback HTML generator for text-layer PDFs when scripts/convert_pdf.py is unreachable.
Writes a B.C. Design System styled site (index.html + one page per topic + images/ + style.css + a copy of the PDF)
and runs the mandatory link/heading check (check_links.py); exit code 2 and validation.json status FAIL if it fails.

Usage: python build_html_fallback.py <in.pdf> <out_folder> "<Document title>" [first_content_page=1]
         [--org "Branch or ministry"] [--doc-date "September 2026"] [--intro "Cover paragraph"]
         [--img-alt "Image from PDF page {page}"] [--footer-cut 750]
Heuristics tuned on one manual (bold 16pt = chapter, bold 14pt = section, 12pt body, footer top>750);
adjust cls()/thresholds for other PDFs and check the result. Needs pdfplumber + poppler (pdftoppm).
Needs ../assets/bc_tokens.css and bc_components.css (or copies beside this script) and check_links.py."""
import pdfplumber,re,os,html,subprocess,shutil,json,sys,argparse
from urllib.parse import quote
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,HERE)
import check_links
ap=argparse.ArgumentParser()
ap.add_argument('pdf'); ap.add_argument('out'); ap.add_argument('title'); ap.add_argument('first_page',nargs='?',type=int,default=1)
ap.add_argument('--org',default=''); ap.add_argument('--doc-date',default=''); ap.add_argument('--intro',default='')
ap.add_argument('--img-alt',default='Image from PDF page {page}'); ap.add_argument('--footer-cut',type=float,default=750)
A=ap.parse_args()
SRC=A.pdf; OUT=A.out.rstrip('/'); TITLE=A.title; START=A.first_page-1; FOOT=A.footer_cut
ORG=A.org; DATE=A.doc_date; INTRO=A.intro; IMGALT=A.img_alt
PDFNAME=re.sub(r'[#%*:<>?\\|"~&{}]','-',os.path.basename(SRC)); PDFREF=quote(PDFNAME)
shutil.rmtree(OUT,ignore_errors=True); os.makedirs(OUT+'/images')
shutil.copy(SRC,OUT+'/'+PDFNAME)
E=html.escape
def slug(s): return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')[:50] or 'topic'
def asset(name):
    for d in (os.path.join(HERE,'..','assets'),os.path.join(HERE,'assets'),HERE):
        p=os.path.join(d,name)
        if os.path.isfile(p): return open(p,encoding='utf-8').read()
    sys.exit('ERROR: '+name+' not found (looked in ../assets, ./assets, ./). Copy the skill assets/ folder with scripts/.')
topics=[]; cur=None; chapter=''; pending_ch=None
imgn=0
def cls(l):
    c=l['chars'][0]; b='Bold' in c['fontname']; s=round(c['size'])
    return b,s
def in_box(l,boxes):
    return any(b[0]-2<=l['x0'] and l['x1']<=b[2]+2 and b[1]-2<=l['top'] and l['bottom']<=b[3]+2 for b in boxes)
with pdfplumber.open(SRC) as pdf:
  NPAGES=len(pdf.pages)
  for pi in range(START,len(pdf.pages)):
    pg=pdf.pages[pi]; pn=pi+1
    items=[]
    tabs=pg.find_tables(); boxes=[t.bbox for t in tabs]
    for t in tabs:
        items.append((t.bbox[1],'table',t.extract()))
    for im in pg.images:
        if im['width']>=40 and im['height']>=40:
            items.append((im['top'],'img',im))
    for l in pg.extract_text_lines():
        if l['top']>FOOT or not l['text'].strip(): continue
        if in_box(l,boxes): continue
        items.append((l['top'],'line',l))
    items.sort(key=lambda x:x[0])
    for top,k,v in items:
        if k=='line':
            b,s=cls(v); t=v['text'].strip()
            if b and s>=14:
                if s>=16:
                    chapter=t; pending_ch=t
                    if cur is None or True:
                        cur=dict(title=t,chapter=t,pages=[pn],body=[]); topics.append(cur)
                    continue
                if cur and cur['title']==chapter and not cur['body'] and cur['pages'][-1]==pn:
                    cur['title']=t; cur['sub']=True; continue
                if t=='Overview' and cur: cur['body'].append(('line',pn,v,(True,12))); continue
                if cur and not cur['body'] and cur['title']!=chapter:
                    cur['title']+=' – '+re.sub(r'^\d+\s*[\.\)]?\s*','',t); continue
                cur=dict(title=t,chapter=chapter,pages=[pn],body=[]); topics.append(cur); continue
        if cur is None: continue
        if pn not in cur['pages']: cur['pages'].append(pn)
        if k=='line': cur['body'].append(('line',pn,v,cls(v)))
        elif k=='table': cur['body'].append(('table',pn,v,None))
        else:
            imgn+=1; fn=f'images/p{pn:02d}-{imgn:03d}.png'
            r=150/72
            subprocess.run(['pdftoppm','-png','-r','150','-f',str(pn),'-l',str(pn),'-singlefile','-x',str(int(v['x0']*r)),'-y',str(int(v['top']*r)),'-W',str(int(v['width']*r)),'-H',str(int(v['height']*r)),SRC,OUT+'/'+fn[:-4]],check=True)
            cur['body'].append(('img',pn,fn,v))
# render
def body_html(body):
    out=[];para=[];lst=None;lasttop=None
    def flush():
        nonlocal para
        if para: out.append('<p>'+E(' '.join(para))+'</p>'); para=[]
    def endlist():
        nonlocal lst
        if lst: out.append(('<ol>' if lst[0]=='o' else '<ul>')+''.join(f'<li>{E(x)}</li>' for x in lst[1])+('</ol>' if lst[0]=='o' else '</ul>')); lst=None
    prev=None;hs=[]
    for k,pn,v,c in body:
        if k=='table':
            flush();endlist()
            rows=[[E((x or '').replace('\n',' ')) for x in r] for r in v if any(r)]
            if rows:
                out.append('<div class="tw"><table><thead><tr>'+''.join(f'<th>{x}</th>' for x in rows[0])+'</tr></thead><tbody>'+''.join('<tr>'+''.join(f'<td>{x}</td>' for x in r)+'</tr>' for r in rows[1:])+'</tbody></table></div>')
            prev=None;continue
        if k=='img':
            flush();endlist()
            out.append(f'<figure><img src="{v}" alt="{E(IMGALT.format(page=pn))}" loading="lazy" width="{int(c["width"]*1.6)}"></figure>');prev=None;continue
        b,s=c; t=v['text'].strip()
        if (not b and s<=9 and re.match(r'(Image|Figure)\s*\d',t)) or re.match(r'^Image \d+ -',t):
            flush();endlist();out.append(f'<p class="cap">{E(t)}</p>');prev=v;continue
        if b and len(t)<80 and (prev is None or v['top']-prev['bottom']>6):
            flush();endlist();hs.append(t);out.append(f'<h2 id="s{len(hs)}">{E(t)}</h2>');prev=v;continue
        m=re.match(r'^(\d+[\.\)]|[a-z][\.\)])\s+(.*)',t); bu=re.match(r'^[•\u2022\uf0b7o\-–]\s+(.*)',t) or (len(t)>1 and t[0] in '\uf0b7\u2022')
        if m and (m.group(1)[0].isdigit() or len(m.group(1))==2):
            flush()
            if not lst or lst[0]!='o': endlist(); lst=['o',[]]
            lst[1].append(m.group(2))
        elif bu:
            flush()
            if not lst or lst[0]!='u': endlist(); lst=['u',[]]
            lst[1].append(re.sub(r'^[•\u2022\uf0b7o\-–]\s*','',t))
        elif lst and prev is not None and v['top']-prev['bottom']<4 and v['x0']>prev['x0']-1:
            lst[1][-1]+=' '+t
        else:
            endlist()
            if prev is not None and v['top']-prev['bottom']>5: flush()
            para.append(t)
        prev=v
    flush();endlist()
    return '\n'.join(out),hs

topics=[t for t in topics if t['body'] or t['title']]
for i,t in enumerate(topics):
    t['file']=f'{i+1:02d}-{slug(t["title"])}.html'
open(OUT+'/style.css','w',encoding='utf-8').write(asset('bc_tokens.css').rstrip()+'\n'+asset('bc_components.css'))
def navhtml(cur):
    groups={}
    for t in topics: groups.setdefault(t['chapter'],[]).append(t)
    s=''
    for ch,ts in groups.items():
        op=' open' if cur and cur['chapter']==ch else ''
        s+=f'<details{op}><summary>{E(ch)}</summary>'+''.join(f'<a href="{t["file"]}"'+(' aria-current="page"' if t is cur else '')+f'>{E(t["title"])}</a>' for t in ts)+'</details>'
    return '<nav class="toc" aria-label="Contents"><a href="index.html"'+(' aria-current="page"' if cur is None else '')+f'>Home</a>{s}</nav>'
def page(title,inner,cur=None):
    org=f'<span class="org">{E(ORG)}</span>' if ORG else ''
    when=f' ({E(DATE)})' if DATE else ''
    forg=f'{E(ORG)}. ' if ORG else ''
    return f"""<!DOCTYPE html>
<html lang="en-CA"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(title)} - {E(TITLE)}</title><link rel="stylesheet" href="style.css"></head><body>
<a class="skip" href="#main">Skip to main content</a>
<header class="bc"><div class="in"><a href="index.html">{E(TITLE)}</a>{org}</div></header>
<div class="subheader"><div class="in"><a href="index.html">Home</a><a href="{PDFREF}">Original PDF</a></div></div>
<div class="layout">{navhtml(cur)}<main id="main">{inner}</main></div>
<footer class="bc"><div class="in">{forg}HTML version of {E(TITLE)}{when}. The PDF is the source of record.</div></footer></body></html>
"""
for i,t in enumerate(topics):
    pr=topics[i-1] if i else None; nx=topics[i+1] if i<len(topics)-1 else None
    rng=f'{t["pages"][0]}\u2013{t["pages"][-1]}' if len(t['pages'])>1 else str(t['pages'][0])
    bh,hs=body_html(t['body'])
    crumbs=f'<nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="index.html">Home</a></li><li>{E(t["chapter"])}</li><li aria-current="page">{E(t["title"])}</li></ol></nav>'
    onp=('<nav class="onpage" aria-label="On this page"><strong>On this page</strong><ul>'+''.join(f'<li><a href="#s{j+1}">{E(h)}</a></li>' for j,h in enumerate(hs))+'</ul></nav>') if len(hs)>1 else ''
    inner=crumbs+f'<h1>{E(t["title"])}</h1><p class="meta">Source: PDF page {rng}. <a href="{PDFREF}#page={t["pages"][0]}">Open in the PDF</a></p>'+onp+bh
    inner+='<nav class="pn" aria-label="Previous and next topic"><span>'+(f'<a class="btn sec" href="{pr["file"]}">\u2190 {E(pr["title"])}</a>' if pr else '')+'</span><span>'+(f'<a class="btn" href="{nx["file"]}">{E(nx["title"])} \u2192</a>' if nx else '')+'</span></nav>'
    open(OUT+'/'+t['file'],'w',encoding='utf-8').write(page(t['title'],inner,t))
cards='';last=None
for t in topics:
    if t['chapter']!=last:
        if last is not None: cards+='</div>'
        cards+=f'<h2>{E(t["chapter"])}</h2><div class="grid">';last=t['chapter']
    cards+=f'<div class="card"><a href="{t["file"]}">{E(t["title"])}</a><p class="meta">PDF pages {t["pages"][0]}\u2013{t["pages"][-1]}</p></div>'
if topics: cards+='</div>'
intro=f'<p>{E(INTRO)}</p>' if INTRO else ''
start=f'<a class="btn" href="{topics[0]["file"]}">Start reading</a> ' if topics else ''
open(OUT+'/index.html','w',encoding='utf-8').write(page('Home',f'<h1>{E(TITLE)}</h1>{intro}<p class="meta">{len(topics)} topics \u00b7 {NPAGES} PDF pages</p><p>{start}<a class="btn sec" href="{PDFREF}">Open the original PDF</a></p>'+cards))
lc=check_links.check_output(OUT,pdf_copied=True,pdf_pages=NPAGES)
status='PASS' if lc['ok'] and topics else 'FAIL'
rep={'status':status,'pages':NPAGES,'topics':len(topics),'images':imgn,'link_check':{'status':'PASS' if lc['ok'] else 'FAIL','pages':lc['files'],'links':lc['links'],'broken':lc['broken'],'heading_problems':lc['heading_problems']}}
json.dump(rep,open(OUT+'/validation.json','w'),indent=2)
print(json.dumps(rep,indent=2))
sys.exit(0 if status=='PASS' else 2)
