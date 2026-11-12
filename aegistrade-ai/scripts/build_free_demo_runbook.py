"""Build the free-account UI practice runbook; no API requests or config changes."""
from pathlib import Path
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from scripts.build_viva_guide import append_markdown


def main():
    root=Path(__file__).resolve().parents[1]
    stem='AegisTrade_Free_OpenRouter_UI_Demo_Runbook'
    doc=Document();sec=doc.sections[0]
    sec.page_width=Inches(8.27);sec.page_height=Inches(11.69)
    sec.top_margin=Inches(.7);sec.bottom_margin=Inches(.65)
    sec.left_margin=Inches(.75);sec.right_margin=Inches(.75)
    style=doc.styles['Normal'];style.font.name='Calibri';style.font.size=Pt(10.5)
    style.paragraph_format.space_after=Pt(6);style.paragraph_format.line_spacing=1.07
    for name in ['Title','Heading 1','Heading 2','Heading 3']:
        doc.styles[name].font.name='Calibri';doc.styles[name].font.color.rgb=RGBColor.from_string('173B5D')
    doc.styles['Title'].font.size=Pt(30);doc.styles['Heading 1'].font.size=Pt(18);doc.styles['Heading 2'].font.size=Pt(13)
    header=sec.header.paragraphs[0];header.text='AEGISTRADE AI  |  FREE-ACCOUNT UI PRACTICE'
    header.runs[0].font.size=Pt(8)
    footer=sec.footer.paragraphs[0];footer.alignment=2
    footer.add_run('Checked 10 November 2026  •  Source 0.15.1  •  Page ').font.size=Pt(8)
    field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)
    doc.core_properties.title='AegisTrade AI — Free OpenRouter UI Demo Runbook'
    doc.core_properties.author='AegisTrade AI project team'
    doc.core_properties.subject='UI practice with free-model limits, zero-generation fallback and exam preparation'
    append_markdown(doc,(root/'docs'/f'{stem}.md').read_text(),page_breaks=False)
    target=root/'docs'/f'{stem}.docx';doc.save(target);print(target)

if __name__=='__main__':main()
