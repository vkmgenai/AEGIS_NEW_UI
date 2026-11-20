"""Render executable AegisTrade LangGraph topologies locally as Mermaid and PNG."""
from pathlib import Path
import sys

from PIL import Image,ImageDraw,ImageFont
import math

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from aegistrade.agentic import c1_graph_mermaid,c2_graph_mermaid
from aegistrade.c2_portfolio import portfolio_graph_mermaid


OUTPUT=ROOT/'docs'/'diagrams'


def _font(size,bold=False):
    family='DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'
    try:return ImageFont.truetype(family,size)
    except OSError:return ImageFont.load_default()


def _local_png(path,title,source,nodes,edges):
    """Draw a presentation-ready image without sending graph source off-machine."""
    width=1500;max_level=max(node[4] for node in nodes);height=max(650,310+155*max_level)
    image=Image.new('RGB',(width,height),'white');draw=ImageDraw.Draw(image)
    draw.rounded_rectangle((28,24,width-28,height-24),radius=24,fill='#f7f9fc',outline='#234f9d',width=4)
    draw.text((60,48),title,font=_font(34,True),fill='#10233f')
    draw.text((60,98),'Rendered locally from the executable LangGraph topology',font=_font(20),fill='#52647c')
    center=width//2;box_w=360;box_h=82;top=155;gap=145
    positions={}
    for key,label,kind,column,level in nodes:
        x=center+column*440;y=top+level*gap;positions[key]=(x,y)
        fill='#dceaff' if kind=='normal' else '#ccefdc' if kind=='start' else '#ffe0b8'
        draw.rounded_rectangle((x-box_w//2,y,x+box_w//2,y+box_h),radius=34 if kind!='normal' else 16,
                               fill=fill,outline='#2457a7',width=3)
        bbox=draw.textbbox((0,0),label,font=_font(23,True));tw=bbox[2]-bbox[0];th=bbox[3]-bbox[1]
        draw.text((x-tw/2,y+(box_h-th)/2-3),label,font=_font(23,True),fill='#12243c')
    for source_key,target_key,label,dashed in edges:
        sx,sy=positions[source_key];tx,ty=positions[target_key]
        start=(sx,sy+box_h);end=(tx,ty)
        color='#6a3fb5' if dashed else '#234f9d';width_line=3
        if target_key in {'strategy','execute'} and source_key in {'replan','resume'}:
            bend=max(start[0],end[0])+box_w//2+75
            points=[start,(bend,start[1]),(bend,end[1]),end]
        else:points=[start,end]
        if dashed:
            for a,b in zip(points,points[1:]):
                length=max(abs(b[0]-a[0]),abs(b[1]-a[1]));steps=max(1,length//16)
                for n in range(0,steps,2):
                    p1=(a[0]+(b[0]-a[0])*n/steps,a[1]+(b[1]-a[1])*n/steps)
                    p2=(a[0]+(b[0]-a[0])*min(n+1,steps)/steps,a[1]+(b[1]-a[1])*min(n+1,steps)/steps)
                    draw.line((p1,p2),fill=color,width=width_line)
        else:draw.line(points,fill=color,width=width_line,joint='curve')
        previous=points[-2];angle=math.atan2(end[1]-previous[1],end[0]-previous[0]);size=16
        arrow=[end,(end[0]-size*math.cos(angle-.55),end[1]-size*math.sin(angle-.55)),
               (end[0]-size*math.cos(angle+.55),end[1]-size*math.sin(angle+.55))]
        draw.polygon(arrow,fill=color)
        if label:
            lx=(start[0]+end[0])//2+18;ly=(start[1]+end[1])//2-14
            draw.rounded_rectangle((lx-8,ly-5,lx+draw.textlength(label,font=_font(17))+8,ly+28),6,fill='white')
            draw.text((lx,ly),label,font=_font(17,True),fill=color)
    draw.text((60,height-64),'Source topology SHA is retained in the adjacent .mmd file.',font=_font(17),fill='#66758a')
    image.save(path)


def main():
    OUTPUT.mkdir(parents=True,exist_ok=True)
    diagrams={
        'C1_AI_EXPERIMENT_LANGGRAPH':('C1 AI Experiment - Single-Agent LangGraph',c1_graph_mermaid(),
            [('start','START','start',0,0),('plan','Plan','normal',0,1),('single_agent','Single agent','normal',0,2),('end','END','end',0,3)],
            [('start','plan','',False),('plan','single_agent','',False),('single_agent','end','',False)]),
        'C2_AI_EXPERIMENT_LANGGRAPH':('C2 AI Experiment - Supervisor and Specialists',c2_graph_mermaid(),
            [('start','START','start',0,0),('plan','Supervisor plan','normal',0,1),('market','Market specialist','normal',0,2),
             ('strategy','Strategy specialist','normal',0,3),('validate','Typed validation','normal',0,4),
             ('replan','Bounded replan','normal',1,4),('critic','Independent critic','normal',0,5),('end','END','end',0,6)],
            [('start','plan','',False),('plan','market','',False),('market','strategy','',False),
             ('strategy','validate','',False),('validate','replan','invalid',True),('replan','strategy','retry',True),
             ('validate','critic','valid',False),('critic','end','',False)]),
        'C2_PORTFOLIO_LANGGRAPH':('C2 Portfolio - Checkpointed LangGraph',portfolio_graph_mermaid(),
            [('start','START','start',0,0),('execute','Execute deterministic sessions','normal',0,1),
             ('human','Human interrupt','normal',-1,2),('done','Persist result','normal',1,2),
             ('resume','Apply Command(resume)','normal',-1,3),('end','END','end',1,3)],
            [('start','execute','',False),('execute','human','eligible evidence block',True),
             ('human','resume','review',False),('resume','execute','continue',True),
             ('execute','done','complete / safe pause',False),('done','end','',False)]),
    }
    for name,(title,source,nodes,edges) in diagrams.items():
        (OUTPUT/f'{name}.mmd').write_text(source,encoding='utf-8')
        _local_png(OUTPUT/f'{name}.png',title,source,nodes,edges)
        print(OUTPUT/f'{name}.png')


if __name__=='__main__':main()
