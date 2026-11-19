"""Build the source-reviewed Word handbook from Markdown and local diagrams.

Requires requirements-docs.txt and matplotlib. Does not call any LLM or cloud API.
"""
from __future__ import annotations
import os,re
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/aegis-mpl')
os.environ.setdefault('XDG_CACHE_HOME','/tmp/aegis-cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'
ASSETS=DOCS/'assets'


def diagram():
    ASSETS.mkdir(exist_ok=True)
    fig,ax=plt.subplots(figsize=(10,9));fig.patch.set_facecolor('white');ax.set(xlim=(0,10),ylim=(0,10));ax.axis('off')
    def box(x,y,w,h,title,detail,color='#eaf1f8'):
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.05,rounding_size=0.08',facecolor=color,edgecolor='#385b7b',linewidth=1.2))
        ax.text(x+w/2,y+h*.65,title,ha='center',va='center',fontsize=10,fontweight='bold',color='#173b5d')
        ax.text(x+w/2,y+h*.27,detail,ha='center',va='center',fontsize=8.5,color='#263b4d')
    def arrow(a,b):ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','color':'#61778c','lw':1.3})
    box(1,8.7,8,1,'Streamlit + FastAPI','NSE cache | rule-based stock ranking | consent | locked case')
    box(1,7.15,8,1,'C2: deterministic LangGraph supervisor','Plan | typed hand-offs | correction | shared eight-request ceiling')
    arrow((5,8.7),(5,8.15))
    for x,title,detail in [(0.15,'Market specialist','Market MCP | regime explanation'),(3.5,'Strategy specialist','Policy + strategy MCP | cited choice'),(6.85,'Compliance critic','Policy + strategy MCP | accept/reject')]:
        box(x,5.35,3,1.15,title,detail)
        arrow((5,7.15),(x+1.5,6.5))
    arrow((3.15,5.9),(3.5,5.9));arrow((6.5,5.9),(6.85,5.9))
    box(1,3.55,8,1.1,'Final code guard -> saved research result','Route agreement | observed citation IDs | critic verdict | trace + usage')
    for x in [1.65,5,8.35]:arrow((x,5.35),(5,4.65))
    box(1,1.8,8,1.1,'Required completed C2 -> code-sized proposal','Recheck exact case + entry | risk | persisted human approve / edit / reject',color='#fff1df')
    arrow((5,3.55),(5,2.9))
    box(1,.15,8,1.1,'Simulator and audit only','Fresh quote | exact hash | kill switch | idempotency | reconciliation',color='#e9f2e8')
    arrow((5,1.8),(5,1.25))
    path=ASSETS/'capstone_architecture.png';fig.savefig(path,dpi=180,bbox_inches='tight');plt.close(fig)
    return path


def add_inline(paragraph,text):
    # Strip link syntax while retaining the destination for a self-contained document.
    text=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',r'\1 (\2)',text)
    parts=re.split(r'(\*\*.*?\*\*|`[^`]+`)',text)
    for part in parts:
        run=paragraph.add_run(part[2:-2] if part.startswith('**') else part[1:-1] if part.startswith('`') else part)
        if part.startswith('**'):run.bold=True
        if part.startswith('`'):run.font.name='Consolas';run.font.size=Pt(9)


def shade(cell,color):
    pr=cell._tc.get_or_add_tcPr();el=OxmlElement('w:shd');el.set(qn('w:fill'),color);pr.append(el)


def table(doc,rows):
    t=doc.add_table(rows=1,cols=len(rows[0]));t.style='Table Grid'
    header=t.rows[0]
    repeat=OxmlElement('w:tblHeader');header._tr.get_or_add_trPr().append(repeat)
    for i,label in enumerate(rows[0]):
        shade(header.cells[i],'173B5D');p=header.cells[i].paragraphs[0];add_inline(p,label)
        for r in p.runs:r.font.color.rgb=RGBColor(255,255,255);r.bold=True;r.font.size=Pt(9)
    for index,values in enumerate(rows[1:]):
        cells=t.add_row().cells
        row_fill=None
        status=values[0] if values else ''
        for marker,color in {
            '🟩':'E2F0D9',  # Current UI demo/runtime path.
            '🟦':'DDEBF7',  # Capstone evaluation/supporting path.
            '🟨':'FFF2CC',  # Retained compatibility or alternative, not the demo path.
            '⬜':'E7E6E6',  # Generated state/artifact, not source code.
        }.items():
            if status.startswith(marker):row_fill=color;break
        for i,value in enumerate(values):
            add_inline(cells[i].paragraphs[0],value)
            if row_fill:shade(cells[i],row_fill)
            elif index%2==0:shade(cells[i],'F0F4F8')
            for p in cells[i].paragraphs:
                p.paragraph_format.space_after=Pt(4)
                for r in p.runs:r.font.size=Pt(9)
        # Keep individual rows together, but allow the table to span pages.
        trpr=cells[0]._tc.getparent().get_or_add_trPr();tag=OxmlElement('w:cantSplit');trpr.append(tag)
    doc.add_paragraph()


def append_markdown(doc,text,figure=None,page_breaks=True):
    if 'Code' not in doc.styles:
        from docx.enum.style import WD_STYLE_TYPE
        style=doc.styles.add_style('Code',WD_STYLE_TYPE.PARAGRAPH)
        style.font.name='Consolas';style.font.size=Pt(8)
    lines=text.splitlines();i=0;code=False;subtitle_done=False
    while i<len(lines):
        line=lines[i]
        if line.startswith('```'):
            code=not code;i+=1;continue
        if code:
            p=doc.add_paragraph(style='Code');p.add_run(line);i+=1;continue
        if not line.strip():i+=1;continue
        if line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].startswith('|'):
                vals=[c.strip() for c in lines[i].strip('|').split('|')]
                if not all(set(c)<=set('-: ') for c in vals):rows.append(vals)
                i+=1
            table(doc,rows);continue
        if line.startswith('#'):
            n=len(line)-len(line.lstrip('#'));title=line[n:].strip()
            if n==1:doc.add_paragraph(title,'Title')
            elif title=='Capstone review, complete project guide and viva handbook':doc.add_paragraph(title,'Subtitle')
            else:
                p=doc.add_heading(title,level=min(3,n-1))
                if n==2 and page_breaks:p.paragraph_format.page_break_before=True
                if title.startswith('4. Architecture') and figure:
                    doc.add_picture(str(figure),width=Inches(6.25))
                    doc.add_paragraph('Figure 1. Implemented C2 research path and separate approval-controlled simulator path.','Caption')
            i+=1;continue
        if line.startswith('> '):
            p=doc.add_paragraph(style='Quote');add_inline(p,line[2:])
        elif line.startswith('- '):
            p=doc.add_paragraph(style='List Bullet');add_inline(p,line[2:])
        else:
            p=doc.add_paragraph();add_inline(p,line)
        i+=1


def main():
    doc=Document();section=doc.sections[0]
    section.page_width=Inches(8.27);section.page_height=Inches(11.69)
    section.top_margin=Inches(.72);section.bottom_margin=Inches(.7)
    section.left_margin=Inches(.85);section.right_margin=Inches(.85)
    normal=doc.styles['Normal'];normal.font.name='Calibri';normal.font.size=Pt(10.5)
    normal.paragraph_format.space_after=Pt(7);normal.paragraph_format.line_spacing=1.12
    for name in ('Title','Subtitle','Heading 1','Heading 2','Heading 3'):
        doc.styles[name].font.name='Calibri';doc.styles[name].font.color.rgb=RGBColor.from_string('173B5D')
    doc.styles['Title'].font.size=Pt(34)
    doc.styles['Heading 1'].font.size=Pt(19);doc.styles['Heading 2'].font.size=Pt(14)
    if 'Code' not in doc.styles:
        from docx.enum.style import WD_STYLE_TYPE
        code=doc.styles.add_style('Code',WD_STYLE_TYPE.PARAGRAPH)
        code.font.name='Consolas';code.font.size=Pt(8)
        code.paragraph_format.space_after=Pt(2)
    header=section.header.paragraphs[0];header.text='AEGISTRADE AI  |  CAPSTONE & VIVA HANDBOOK'
    header.runs[0].font.size=Pt(8);header.runs[0].font.color.rgb=RGBColor.from_string('61778C')
    footer=section.footer.paragraphs[0];footer.alignment=2
    footer.add_run('9 November 2026  •  Page ').font.size=Pt(8)
    field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)
    figure=diagram()
    append_markdown(doc,(DOCS/'AegisTrade_Capstone_Review_and_Viva_Guide.md').read_text(),figure)
    doc.add_page_break();doc.add_heading('Appendix C. Detailed source-to-code gap register',level=1)
    append_markdown(doc,(DOCS/'CAPSTONE_GAP_REVIEW.md').read_text(),page_breaks=False)
    output=DOCS/'AegisTrade_Capstone_Review_and_Viva_Guide.docx'
    doc.core_properties.title='AegisTrade AI — Capstone Review and Viva Guide'
    doc.core_properties.subject='Guideline/proposal/slides/source review, actual implementation and viva preparation'
    doc.core_properties.author='AegisTrade team: Veneet, Karthika, Mathangi'
    doc.save(output)
    check=Document(output)
    print(f'Created {output.name}: {len(check.paragraphs)} paragraphs, {len(check.tables)} tables, {len(check.inline_shapes)} diagram.')
    assert any('27. Which parts' in p.text for p in check.paragraphs)
    assert any('Appendix C' in p.text for p in check.paragraphs)
    assert len(check.tables)>=7

if __name__=='__main__':main()
