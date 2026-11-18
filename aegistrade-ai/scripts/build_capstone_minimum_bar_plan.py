"""Build the Word edition of the capstone minimum-bar action plan."""
from pathlib import Path
import re

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'docs'/'CAPSTONE_MINIMUM_BAR_ACTION_PLAN.md'
TARGET=ROOT/'docs'/'AegisTrade_Capstone_Minimum_Bar_Action_Plan.docx'


def shade(cell,fill):
    tc_pr=cell._tc.get_or_add_tcPr();element=OxmlElement('w:shd');element.set(qn('w:fill'),fill);tc_pr.append(element)


def borders(table,color='B7C9DF'):
    tbl_pr=table._tbl.tblPr
    node=OxmlElement('w:tblBorders')
    for edge in ('top','left','bottom','right','insideH','insideV'):
        child=OxmlElement('w:'+edge);child.set(qn('w:val'),'single');child.set(qn('w:sz'),'4');child.set(qn('w:color'),color);node.append(child)
    tbl_pr.append(node)


def inline(paragraph,text):
    parts=re.split(r'(\*\*.*?\*\*|`.*?`)',text)
    for part in parts:
        if not part:continue
        if part.startswith('**') and part.endswith('**'):
            run=paragraph.add_run(part[2:-2]);run.bold=True
        elif part.startswith('`') and part.endswith('`'):
            run=paragraph.add_run(part[1:-1]);run.font.name='Menlo';run.font.size=Pt(8.5);run.font.color.rgb=RGBColor(25,68,116)
        else:paragraph.add_run(part)


def add_table(doc,lines):
    rows=[]
    for line in lines:
        rows.append([x.strip() for x in line.strip().strip('|').split('|')])
    rows=[rows[0]]+rows[2:]
    table=doc.add_table(rows=1,cols=len(rows[0]));table.style='Light Shading Accent 1';table.autofit=True
    for i,value in enumerate(rows[0]):
        table.rows[0].cells[i].text=value;shade(table.rows[0].cells[i],'17365D')
        for run in table.rows[0].cells[i].paragraphs[0].runs:run.font.color.rgb=RGBColor(255,255,255);run.bold=True
    for row in rows[1:]:
        cells=table.add_row().cells
        for i,value in enumerate(row):
            cells[i].text=value
            if len(rows)>7 and i==0:shade(cells[i],'EAF1F8')
    borders(table);doc.add_paragraph()


def build():
    doc=Document();section=doc.sections[0]
    section.top_margin=Inches(.65);section.bottom_margin=Inches(.65);section.left_margin=Inches(.7);section.right_margin=Inches(.7)
    styles=doc.styles
    styles['Normal'].font.name='Aptos';styles['Normal'].font.size=Pt(9.5)
    styles['Normal'].paragraph_format.space_after=Pt(4)
    for name,size,color in [('Title',26,'17365D'),('Heading 1',17,'17365D'),('Heading 2',13,'245B8A'),('Heading 3',11,'2F6F92')]:
        styles[name].font.name='Aptos Display';styles[name].font.size=Pt(size);styles[name].font.color.rgb=RGBColor.from_string(color)
    header=section.header.paragraphs[0];header.text='AEGISTRADE AI  |  CAPSTONE MINIMUM-BAR ACTION PLAN';header.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    header.runs[0].font.size=Pt(8);header.runs[0].font.color.rgb=RGBColor(90,110,130)
    footer=section.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
    footer.add_run('Simulation-only research prototype  •  17 November 2026  •  ')
    fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');footer._p.append(fld)

    lines=SOURCE.read_text().splitlines();i=0;in_code=False;code=[]
    while i<len(lines):
        line=lines[i]
        if line.startswith('```'):
            if in_code:
                p=doc.add_paragraph();p.style='No Spacing';run=p.add_run('\n'.join(code));run.font.name='Menlo';run.font.size=Pt(8);run.font.color.rgb=RGBColor(25,68,116)
                p.paragraph_format.left_indent=Inches(.25);p.paragraph_format.space_after=Pt(7);code=[];in_code=False
            else:in_code=True
            i+=1;continue
        if in_code:code.append(line);i+=1;continue
        if line.startswith('|') and i+1<len(lines) and lines[i+1].startswith('|'):
            block=[]
            while i<len(lines) and lines[i].startswith('|'):block.append(lines[i]);i+=1
            add_table(doc,block);continue
        if line.startswith('# '):
            p=doc.add_paragraph(style='Title');inline(p,line[2:]);p.alignment=WD_ALIGN_PARAGRAPH.LEFT
        elif line.startswith('## '):
            doc.add_paragraph(line[3:],style='Heading 1')
        elif line.startswith('### '):doc.add_paragraph(line[4:],style='Heading 2')
        elif re.match(r'^\d+\. ',line):
            p=doc.add_paragraph(style='List Number');inline(p,re.sub(r'^\d+\. ','',line))
        elif line.startswith('- [ ] '):
            p=doc.add_paragraph(style='List Bullet');inline(p,'☐ '+line[6:])
        elif line.startswith('- [x] '):
            p=doc.add_paragraph(style='List Bullet');inline(p,'☑ '+line[6:])
        elif line.startswith('- '):
            p=doc.add_paragraph(style='List Bullet');inline(p,line[2:])
        elif not line.strip():doc.add_paragraph()
        else:
            p=doc.add_paragraph();inline(p,line.replace('  ',' '))
        i+=1

    core=doc.core_properties;core.title='AegisTrade Capstone Minimum-Bar Action Plan';core.subject='Tasks, steps, evidence and acceptance criteria for the capstone final review';core.author='AegisTrade AI team'
    doc.save(TARGET);return TARGET


if __name__=='__main__':print(build())
