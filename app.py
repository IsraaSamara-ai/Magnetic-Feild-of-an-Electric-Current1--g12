import streamlit as st
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import wave
import io

st.set_page_config(
    page_title="قانون بيو-سافار | Biot-Savart Law",
    page_icon="🧲", layout="wide", initial_sidebar_state="expanded"
)

def generate_tone(frequency=440, duration=0.15, volume=0.3, sample_rate=22050):
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, False)
    wave_data = np.sin(2 * np.pi * frequency * t) * volume
    fade = min(n_samples, int(0.01 * sample_rate))
    wave_data[:fade] *= np.linspace(0, 1, fade)
    wave_data[-fade:] *= np.linspace(1, 0, fade)
    wave_data = (wave_data * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sample_rate)
        wf.writeframes(wave_data.tobytes())
    buf.seek(0)
    return buf

def play_sound(sound_type="click"):
    sounds = {"click": (800, 0.08, 0.2), "success": (523, 0.3, 0.25),
              "error": (200, 0.3, 0.25), "info": (660, 0.15, 0.2)}
    f, d, v = sounds.get(sound_type, sounds["click"])
    return generate_tone(f, d, v)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;800;900&display=swap');
*{font-family:'Cairo',sans-serif;direction:rtl;text-align:right}
.main-header{background:linear-gradient(135deg,#0d1b2a 0%,#1b2838 40%,#1a3a5c 100%);padding:35px;border-radius:20px;text-align:center;color:white;margin-bottom:30px;box-shadow:0 10px 40px rgba(0,0,0,0.4);border:1px solid rgba(100,180,255,0.2)}
.main-header h1{font-size:2.4em;font-weight:900;margin:0 0 8px 0;background:linear-gradient(90deg,#64b5f6,#fff,#64b5f6);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.main-header .en-title{font-size:1.1em;opacity:0.7;color:#90caf9}
.main-header .author{font-size:1em;opacity:0.85;margin-top:18px;padding-top:15px;border-top:1px solid rgba(100,180,255,0.25);color:#e3f2fd}
.section-card{background:white;border-radius:15px;padding:25px;margin-bottom:20px;box-shadow:0 4px 15px rgba(0,0,0,0.08);border-right:5px solid #1565c0}
.formula-box{background:linear-gradient(135deg,#e8eaf6,#c5cae9);border-radius:15px;padding:25px;margin:20px 0;text-align:center;border:2px solid #3f51b5;direction:ltr}
.formula-box .formula{font-size:1.8em;font-weight:700;color:#1a237e}
.info-box{background:linear-gradient(135deg,#e3f2fd,#bbdefb);border-radius:12px;padding:20px;margin:15px 0;border-right:4px solid #2196f3}
.warning-box{background:linear-gradient(135deg,#fff3e0,#ffe0b2);border-radius:12px;padding:20px;margin:15px 0;border-right:4px solid #ff9800}
.success-box{background:linear-gradient(135deg,#e8f5e9,#c8e6c9);border-radius:12px;padding:20px;margin:15px 0;border-right:4px solid #4caf50}
.life-example{background:linear-gradient(135deg,#fce4ec,#f8bbd0);border-radius:12px;padding:20px;margin:15px 0;border-right:4px solid #e91e63}
.derivation-step{background:#fafafa;border-radius:10px;padding:18px;margin:10px 0;border:1px solid #e0e0e0;direction:ltr;text-align:center}
.step-badge{display:inline-block;background:#1565c0;color:white;padding:4px 14px;border-radius:20px;font-size:0.85em;font-weight:700;margin-bottom:8px}
.stTabs [data-baseweb="tab-list"]{gap:5px;flex-wrap:wrap}
.stTabs [data-baseweb="tab"]{border-radius:10px 10px 0 0;padding:10px 18px;font-weight:600;font-size:0.9rem}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#1565c0,#1976d2)!important;color:white!important}
.result-box{background:linear-gradient(135deg,#e8f5e9,#a5d6a7);border:3px solid #2e7d32;border-radius:15px;padding:25px;text-align:center;margin:20px 0}
h2,h3{color:#0d47a1}
.quiz-option{padding:12px 20px;border:2px solid #e0e0e0;border-radius:10px;margin:8px 0}
.quiz-option.correct{border-color:#2e7d32;background:#c8e6c9}
.quiz-option.wrong{border-color:#c62828;background:#ffcdd2}
</style>
""", unsafe_allow_html=True)

MU_0 = 4 * np.pi * 1e-7
MATERIALS = {
    "الفراغ (Vacuum)": 1.0, "الهواء (Air)": 1.00000037,
    "النحاس (Copper)": 0.999994, "الألمنيوم (Aluminum)": 1.000022,
    "الماء (Water)": 0.999992, "الصلب (Steel)": 100,
    "الحديد الزهر (Cast Iron)": 200, "النيكل (Nickel)": 600,
    "المواد الفيريتية (Ferrite)": 5000, "الحديد النقي (Pure Iron)": 5000,
}

# ════════════════════════════════════════════════════════════════
def oersted_animation():
    return """
    <div style="text-align:center;direction:rtl">
    <canvas id="oerstedCanvas" width="600" height="350" style="border-radius:15px;background:#0a1628;max-width:100%"></canvas>
    <script>
    var c=document.getElementById('oerstedCanvas'),ctx=c.getContext('2d');
    var t=0,showCurrent=false;
    function draw(){
        ctx.clearRect(0,0,c.width,c.height);
        ctx.strokeStyle='#bdbdbd';ctx.lineWidth=6;
        ctx.beginPath();ctx.moveTo(50,175);ctx.lineTo(550,175);ctx.stroke();
        ctx.fillStyle='#ff9800';ctx.fillRect(20,155,30,40);
        ctx.fillStyle='#fff';ctx.font='bold 14px Cairo';ctx.fillText('+',28,170);ctx.fillText('-',28,195);
        if(showCurrent){
            ctx.strokeStyle='#f44336';ctx.lineWidth=3;
            var ax=100+((t*3)%400);
            ctx.beginPath();ctx.moveTo(ax,175);ctx.lineTo(ax+25,175);ctx.stroke();
            ctx.beginPath();ctx.moveTo(ax+25,175);ctx.lineTo(ax+18,168);ctx.stroke();
            ctx.beginPath();ctx.moveTo(ax+25,175);ctx.lineTo(ax+18,182);ctx.stroke();
            ctx.fillStyle='#f44336';ctx.font='bold 16px Cairo';ctx.fillText('I ->',ax+30,172);
        }
        var cx=300,cy=175,cr=35;
        ctx.beginPath();ctx.arc(cx,cy,cr,0,Math.PI*2);ctx.strokeStyle='#fff';ctx.lineWidth=2;ctx.stroke();
        ctx.fillStyle='rgba(255,255,255,0.1)';ctx.fill();
        var angle=showCurrent? Math.sin(t*0.05)*0.5 : 0;
        ctx.save();ctx.translate(cx,cy);ctx.rotate(angle);
        ctx.fillStyle='#f44336';ctx.beginPath();ctx.moveTo(0,-cr+8);ctx.lineTo(-5,0);ctx.lineTo(5,0);ctx.closePath();ctx.fill();
        ctx.fillStyle='#2196f3';ctx.beginPath();ctx.moveTo(0,cr-8);ctx.lineTo(-5,0);ctx.lineTo(5,0);ctx.closePath();ctx.fill();
        ctx.restore();
        ctx.fillStyle='#fff';ctx.font='bold 13px Cairo';
        if(showCurrent){
            ctx.fillText('انحراف الإبرة بسبب المجال المغناطيسي',cx-140,cy+60);
            for(var r=50;r<150;r+=25){
                ctx.strokeStyle='rgba(100,181,246,'+(0.6-r*0.003)+')';ctx.lineWidth=1.5;
                ctx.setLineDash([4,4]);ctx.beginPath();ctx.arc(cx,cy,r,0,Math.PI*2);ctx.stroke();ctx.setLineDash([]);
            }
        }else{ctx.fillText('إبرة البوصلة متوازية مع السلك (لا تيار)',cx-130,cy+60);}
        ctx.fillStyle='#90caf9';ctx.font='12px Cairo';ctx.fillText('سلك نحاسي',250,210);
        ctx.fillStyle='#ffd54f';ctx.font='bold 14px Cairo';
        ctx.fillText(showCurrent?'التيار يمر - اضغط لعكس':'اضغط لتشغيل التيار',150,30);
        t++;requestAnimationFrame(draw);
    }
    c.onclick=function(){showCurrent=!showCurrent;t=0;};
    draw();
    </script>
    </div>"""

# ════════════════════════════════════════════════════════════════
def straight_wire_animation(current_dir=1, current_val=5, distance=0.1, material_mu=1.0):
    dir_label = "للأعلى (خارج الصفحة) ⊙" if current_dir == 1 else "للأسفل (داخل الصفحة) ⊗"
    html = """
    <div style="text-align:center;direction:rtl">
    <canvas id="wireCanvas" width="650" height="500" style="border-radius:15px;background:#0a1628;max-width:100%"></canvas>
    <script>
    var c=document.getElementById('wireCanvas'),ctx=c.getContext('2d');
    var t=0;var dir=__DIR__;var I=__I__;var dist=__DIST__;var mu=__MU__;
    var cx=c.width/2,cy=c.height/2;
    var radii=[50,90,130,175,220];
    var colors=['#f44336','#ff9800','#ffeb3b','#4caf50','#2196f3'];
    function draw(){
        ctx.clearRect(0,0,c.width,c.height);
        ctx.beginPath();ctx.arc(cx,cy,18,0,Math.PI*2);ctx.fillStyle='#bdbdbd';ctx.fill();ctx.strokeStyle='#fff';ctx.lineWidth=2;ctx.stroke();
        if(dir===1){ctx.fillStyle='#f44336';ctx.beginPath();ctx.arc(cx,cy,6,0,Math.PI*2);ctx.fill();}
        else{ctx.strokeStyle='#f44336';ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(cx-8,cy-8);ctx.lineTo(cx+8,cy+8);ctx.stroke();ctx.beginPath();ctx.moveTo(cx+8,cy-8);ctx.lineTo(cx-8,cy+8);ctx.stroke();}
        for(var idx=0;idx<radii.length;idx++){
            var r=radii[idx];var col=colors[idx];
            ctx.strokeStyle=col;ctx.lineWidth=1.5;ctx.globalAlpha=0.4;ctx.beginPath();ctx.arc(cx,cy,r,0,Math.PI*2);ctx.stroke();ctx.globalAlpha=1;
            for(var p=0;p<6;p++){
                var baseAngle=(p/6)*Math.PI*2;
                var angle=baseAngle-dir*(t*0.02)*(1+0.5*(5-idx)/5);
                var px=cx+r*Math.cos(angle),py=cy+r*Math.sin(angle);
                var grd=ctx.createRadialGradient(px,py,0,px,py,8);grd.addColorStop(0,col);grd.addColorStop(1,'transparent');
                ctx.fillStyle=grd;ctx.beginPath();ctx.arc(px,py,8,0,Math.PI*2);ctx.fill();
                ctx.fillStyle='#fff';ctx.beginPath();ctx.arc(px,py,2.5,0,Math.PI*2);ctx.fill();
                var tang=angle-dir*Math.PI/2;
                ctx.strokeStyle=col;ctx.lineWidth=2;
                ctx.beginPath();ctx.moveTo(px,py);ctx.lineTo(px+12*Math.cos(tang),py+12*Math.sin(tang));ctx.stroke();
                var ah1=tang+2.5,ah2=tang-2.5;
                ctx.beginPath();ctx.moveTo(px+12*Math.cos(tang),py+12*Math.sin(tang));ctx.lineTo(px+6*Math.cos(ah1),py+6*Math.sin(ah1));ctx.stroke();
                ctx.beginPath();ctx.moveTo(px+12*Math.cos(tang),py+12*Math.sin(tang));ctx.lineTo(px+6*Math.cos(ah2),py+6*Math.sin(ah2));ctx.stroke();
            }
            var bVal=(4*Math.PI*1e-7*I*mu/(2*Math.PI*(r*0.001))).toExponential(2);
            ctx.fillStyle=col;ctx.font='11px Cairo';ctx.fillText('B='+bVal+' T',cx+r+10,cy-5);
        }
        ctx.fillStyle='#fff';ctx.font='bold 14px Cairo';ctx.fillText('التيار: '+I+' A  (__DIRLABEL__)',20,30);
        var fieldDirText = dir===1 ? 'المجال: عكس عقارب الساعة' : 'المجال: مع عقارب الساعة';
        ctx.fillStyle='#4caf50';ctx.font='bold 13px Cairo';ctx.fillText(fieldDirText,20,c.height-50);
        ctx.fillStyle='#90caf9';ctx.font='12px Cairo';ctx.fillText('نقطة = خارج الصفحة    علامة x = داخل الصفحة',20,c.height-20);
        ctx.fillStyle='#ffd54f';ctx.font='bold 13px Cairo';ctx.fillText('الجسيمات المتحركة تُظهر اتجاه المجال المغناطيسي',cx-150,cy+radii[4]+40);
        t++;requestAnimationFrame(draw);
    }draw();
    </script>
    </div>"""
    html = html.replace("__DIR__", str(current_dir))
    html = html.replace("__I__", str(current_val))
    html = html.replace("__DIST__", str(distance))
    html = html.replace("__MU__", str(material_mu))
    html = html.replace("__DIRLABEL__", dir_label)
    return html

# ════════════════════════════════════════════════════════════════
def circular_coil_animation(current_dir=1, current_val=5, N=5, R=0.1, material_mu=1.0):
    html = """
    <div style="text-align:center;direction:rtl">
    <canvas id="coilCanvas" width="650" height="500" style="border-radius:15px;background:#0a1628;max-width:100%"></canvas>
    <script>
    var c=document.getElementById('coilCanvas'),ctx=c.getContext('2d');
    var t=0;var dir=__DIR__;var I=__I__;var N=__N__;var R=__R__;var mu=__MU__;
    var cx=c.width/2,cy=c.height/2,coilR=120;
    function draw(){
        ctx.clearRect(0,0,c.width,c.height);
        var maxDraw=Math.min(N,8);
        for(var i=0;i<maxDraw;i++){var offset=i*4;ctx.strokeStyle='rgba(100,181,246,'+(0.3+0.1*i)+')';ctx.lineWidth=3;ctx.beginPath();ctx.ellipse(cx,cy+offset-15,coilR,coilR*0.3,0,0,Math.PI*2);ctx.stroke();}
        if(N>8){ctx.fillStyle='#90caf9';ctx.font='12px Cairo';ctx.fillText('+'+(N-8)+' لفات',cx+coilR+20,cy);}
        var nArrows=12;
        for(var i=0;i<nArrows;i++){
            var angle=(i/nArrows)*Math.PI*2-dir*t*0.015;
            var px=cx+coilR*Math.cos(angle);
            var py=cy+(coilR*0.3)*Math.sin(angle)-15;
            var tang=angle-dir*Math.PI/2;
            ctx.fillStyle='#f44336';ctx.beginPath();ctx.arc(px,py,5,0,Math.PI*2);ctx.fill();
            ctx.strokeStyle='#ff8a80';ctx.lineWidth=2;
            ctx.beginPath();ctx.moveTo(px,py);ctx.lineTo(px+10*Math.cos(tang),py+10*Math.sin(tang));ctx.stroke();
        }
        var bDir=dir,arrowLen=60;
        ctx.strokeStyle='#4caf50';ctx.lineWidth=5;
        ctx.beginPath();ctx.moveTo(cx,cy+bDir*arrowLen);ctx.lineTo(cx,cy-bDir*arrowLen);ctx.stroke();
        ctx.fillStyle='#4caf50';ctx.beginPath();
        ctx.moveTo(cx,cy-bDir*arrowLen);
        ctx.lineTo(cx-12,cy-bDir*arrowLen+bDir*20);
        ctx.lineTo(cx+12,cy-bDir*arrowLen+bDir*20);ctx.closePath();ctx.fill();
        ctx.fillStyle='#4caf50';ctx.font='bold 18px Cairo';ctx.direction='rtl';ctx.fillText('B',cx-30,cy-bDir*arrowLen+5);
        ctx.strokeStyle='rgba(76,175,80,0.3)';ctx.lineWidth=2;ctx.setLineDash([6,4]);
        ctx.beginPath();ctx.moveTo(cx,cy-bDir*200);ctx.lineTo(cx,cy+bDir*200);ctx.stroke();ctx.setLineDash([]);
        var bVal=(4*Math.PI*1e-7*I*N*mu/(2*R)).toExponential(2);
        ctx.fillStyle='#fff';ctx.font='bold 14px Cairo';ctx.fillText('B = '+bVal+' T',20,30);
        var bDirText = dir===1 ? 'المجال للأعلى - التيار عكس عقارب الساعة' : 'المجال للأسفل - التيار مع عقارب الساعة';
        ctx.fillStyle='#ffd54f';ctx.font='13px Cairo';ctx.fillText(bDirText,20,55);
        ctx.fillStyle='#90caf9';ctx.font='12px Cairo';ctx.fillText('الأسهم الحمراء = اتجاه التيار في الملف',20,c.height-40);
        ctx.fillText('السهم الأخضر = اتجاه المجال في المركز',20,c.height-20);
        t++;requestAnimationFrame(draw);
    }draw();
    </script>
    </div>"""
    html = html.replace("__DIR__", str(current_dir))
    html = html.replace("__I__", str(current_val))
    html = html.replace("__N__", str(N))
    html = html.replace("__R__", str(R))
    html = html.replace("__MU__", str(material_mu))
    return html

# ════════════════════════════════════════════════════════════════
def solenoid_animation(current_dir=1, current_val=5, n=1400, L=0.5, material_mu=1.0):
    html = """
    <div style="text-align:center;direction:rtl">
    <canvas id="solCanvas" width="700" height="480" style="border-radius:15px;background:#0a1628;max-width:100%"></canvas>
    <script>
    var c=document.getElementById('solCanvas'),ctx=c.getContext('2d');
    var t=0;var dir=__DIR__;var I=__I__;var n=__N__;var L=__L__;var mu=__MU__;
    var sx=100,sy=120,sw=500,sh=220,turns=20;
    function draw(){
        ctx.clearRect(0,0,c.width,c.height);
        ctx.fillStyle='rgba(30,60,90,0.5)';ctx.strokeStyle='#546e7a';ctx.lineWidth=2;
        ctx.beginPath();ctx.roundRect(sx,sy,sw,sh,15);ctx.fill();ctx.stroke();
        for(var i=0;i<turns;i++){var x=sx+20+i*(sw-40)/turns;ctx.strokeStyle='rgba(100,181,246,0.6)';ctx.lineWidth=2;ctx.beginPath();ctx.ellipse(x,sy+sh/2,8,sh/2-10,0,0,Math.PI*2);ctx.stroke();var aDir=-dir*(i%2===0?1:-1);ctx.fillStyle='#f44336';ctx.beginPath();ctx.arc(x,sy+5,4,0,Math.PI*2);ctx.fill();ctx.strokeStyle='#ff8a80';ctx.lineWidth=1.5;ctx.beginPath();ctx.moveTo(x,sy+5);ctx.lineTo(x+aDir*12,sy+5);ctx.stroke();}
        var fDir=dir,nLines=5;
        for(var i=0;i<nLines;i++){var y=sy+30+i*(sh-60)/(nLines-1);for(var p=0;p<8;p++){var px=sx+30+((p/8+t*0.008*fDir)%1)*(sw-60);if(px<sx+10||px>sx+sw-10)continue;var grd=ctx.createRadialGradient(px,y,0,px,y,6);grd.addColorStop(0,'#4caf50');grd.addColorStop(1,'transparent');ctx.fillStyle=grd;ctx.beginPath();ctx.arc(px,y,6,0,Math.PI*2);ctx.fill();ctx.fillStyle='#fff';ctx.beginPath();ctx.arc(px,y,2,0,Math.PI*2);ctx.fill();}ctx.strokeStyle='rgba(76,175,80,0.4)';ctx.lineWidth=1.5;ctx.setLineDash([4,3]);ctx.beginPath();ctx.moveTo(sx+15,y);ctx.lineTo(sx+sw-15,y);ctx.stroke();ctx.setLineDash([]);}
        var arrowY=sy+sh/2;ctx.strokeStyle='#66bb6a';ctx.lineWidth=6;ctx.beginPath();ctx.moveTo(sx+30,arrowY);ctx.lineTo(sx+sw-30,arrowY);ctx.stroke();
        var aX=fDir===1?sx+sw-30:sx+30,aD=fDir;ctx.fillStyle='#66bb6a';ctx.beginPath();ctx.moveTo(aX,arrowY);ctx.lineTo(aX-aD*20,arrowY-12);ctx.lineTo(aX-aD*20,arrowY+12);ctx.closePath();ctx.fill();
        ctx.fillStyle='#a5d6a7';ctx.font='bold 20px Cairo';ctx.fillText('B',sx+sw/2-10,arrowY-15);
        var nX=fDir===1?sx+sw+15:sx-35,sX=fDir===1?sx-35:sx+sw+15;
        ctx.fillStyle='#f44336';ctx.font='bold 28px Cairo';ctx.fillText('N',nX,arrowY+10);ctx.fillStyle='#2196f3';ctx.fillText('S',sX,arrowY+10);
        ctx.strokeStyle='rgba(76,175,80,0.2)';ctx.lineWidth=1.5;
        for(var i=0;i<3;i++){var offset=30+i*25;ctx.beginPath();ctx.moveTo(sx+sw/2,sy-offset);ctx.bezierCurveTo(sx+sw+80+offset,sy-40,sx+sw+80+offset,sy+sh+40,sx+sw/2,sy+sh+offset);ctx.stroke();ctx.beginPath();ctx.moveTo(sx+sw/2,sy-offset);ctx.bezierCurveTo(sx-80-offset,sy-40,sx-80-offset,sy+sh+40,sx+sw/2,sy+sh+offset);ctx.stroke();}
        var bVal=(4*Math.PI*1e-7*I*n*mu).toExponential(2);
        ctx.fillStyle='#fff';ctx.font='bold 14px Cairo';ctx.fillText('B = '+bVal+' T',20,30);
        ctx.fillStyle='#ffd54f';ctx.font='13px Cairo';ctx.fillText('n = '+n+' لفة/م، I = '+I+' A، L = '+L+' m',20,55);
        ctx.fillStyle='#90caf9';ctx.font='12px Cairo';ctx.fillText('الجسيمات الخضراء = اتجاه المجال داخل الملف',20,c.height-20);
        t++;requestAnimationFrame(draw);
    }draw();
    </script>
    </div>"""
    html = html.replace("__DIR__", str(current_dir))
    html = html.replace("__I__", str(current_val))
    html = html.replace("__N__", str(n))
    html = html.replace("__L__", str(L))
    html = html.replace("__MU__", str(material_mu))
    return html

# ════════════════════════════════════════════════════════════════
def right_hand_animation(case="wire", current_dir=1):
    case_names = {"wire": "موصل مستقيم", "coil": "ملف دائري", "solenoid": "ملف لولبي"}
    case_label = case_names.get(case, "موصل مستقيم")
    html = """
    <div style="text-align:center;direction:rtl">
    <canvas id="handCanvas" width="600" height="520" style="border-radius:15px;background:#0a1628;max-width:100%"></canvas>
    <script>
    var c=document.getElementById('handCanvas'),ctx=c.getContext('2d');
    var t=0;var caseType="__CASE__";var dir=__DIR__;var cx=300,cy=280;
    function drawHand(thumbAngle,fingerCurl,alpha){
        ctx.save();ctx.translate(cx,cy);ctx.globalAlpha=alpha||1;
        ctx.fillStyle='#ffccbc';ctx.strokeStyle='#e65100';ctx.lineWidth=2;ctx.beginPath();ctx.ellipse(0,0,55,70,0,0,Math.PI*2);ctx.fill();ctx.stroke();
        ctx.save();ctx.rotate(thumbAngle);ctx.fillStyle='#ffccbc';ctx.beginPath();ctx.moveTo(40,-15);ctx.lineTo(120,-25);ctx.lineTo(125,-10);ctx.lineTo(45,5);ctx.closePath();ctx.fill();ctx.stroke();ctx.fillStyle='#ffab91';ctx.beginPath();ctx.ellipse(115,-18,12,7,thumbAngle*0.1,0,Math.PI*2);ctx.fill();ctx.restore();
        for(var i=0;i<4;i++){var fAngle=fingerCurl+i*0.15;ctx.save();ctx.rotate(fAngle);ctx.fillStyle='#ffccbc';ctx.beginPath();ctx.ellipse(-30-i*5,-60+i*12,12,30,0.3,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.restore();}
        ctx.restore();
    }
    function draw(){
        ctx.clearRect(0,0,c.width,c.height);var thumbA,curlA;
        if(dir===1){thumbA=-Math.PI/2;curlA=0;}else{thumbA=Math.PI/2;curlA=Math.PI;}
        if(caseType==="wire"){ctx.strokeStyle='#546e7a';ctx.lineWidth=20;ctx.beginPath();ctx.moveTo(cx,cy-180);ctx.lineTo(cx,cy+180);ctx.stroke();ctx.fillStyle='#78909c';ctx.font='12px Cairo';ctx.fillText('موصل',cx+20,cy+200);for(var r=100;r<200;r+=30){ctx.strokeStyle='rgba(100,181,246,0.3)';ctx.lineWidth=1;ctx.setLineDash([3,3]);ctx.beginPath();ctx.arc(cx,cy,r,0,Math.PI*2);ctx.stroke();ctx.setLineDash([]);}}
        else if(caseType==="coil"){ctx.strokeStyle='#546e7a';ctx.lineWidth=4;ctx.beginPath();ctx.ellipse(cx,cy,150,50,0,0,Math.PI*2);ctx.stroke();ctx.fillStyle='#78909c';ctx.font='12px Cairo';ctx.fillText('ملف دائري',cx+130,cy+60);}
        else{ctx.fillStyle='rgba(30,60,90,0.5)';ctx.strokeStyle='#546e7a';ctx.lineWidth=2;ctx.beginPath();ctx.roundRect(cx-120,cy-80,240,160,15);ctx.fill();ctx.stroke();ctx.fillStyle='#78909c';ctx.font='12px Cairo';ctx.fillText('ملف لولبي',cx+100,cy+100);}
        drawHand(thumbA,curlA,0.85);
        var pulse=Math.sin(t*0.05)*0.3+0.7;ctx.fillStyle='rgba(244,67,54,'+pulse+')';ctx.font='bold 16px Cairo';
        if(caseType==="wire"){ctx.fillText('الابهام = اتجاه التيار',dir===1?cx+50:cx-230,cy-100);}
        else{ctx.fillText('الاصابع = اتجاه التيار',dir===1?cx+50:cx-230,cy-100);}
        ctx.fillStyle='rgba(33,150,243,'+pulse+')';ctx.font='bold 16px Cairo';
        if(caseType==="wire"){ctx.fillText('لف الاصابع = اتجاه المجال B',dir===1?cx+50:cx-260,cy+130);}
        else{ctx.fillText('الابهام = اتجاه المجال B',dir===1?cx+50:cx-230,cy+130);}
        ctx.fillStyle='#fff';ctx.font='bold 18px Cairo';ctx.fillText('قاعدة اليد اليمنى - __CASELABEL__',cx-120,35);
        ctx.fillStyle='#ffd54f';ctx.font='14px Cairo';
        if(caseType==="wire"){ctx.fillText('اشر بابهامك لاتجاه التيار ثم لف اصابعك حول الموصل',cx-210,c.height-30);ctx.fillText('اتجاه لف الاصابع = اتجاه المجال المغناطيسي',cx-190,c.height-10);}
        else{ctx.fillText('لف اصابعك باتجاه التيار في الملف',cx-160,c.height-30);ctx.fillText('ابهامك يشير لاتجاه المجال المغناطيسي',cx-170,c.height-10);}
        t++;requestAnimationFrame(draw);
    }draw();
    </script>
    </div>"""
    html = html.replace("__CASE__", case)
    html = html.replace("__DIR__", str(current_dir))
    html = html.replace("__CASELABEL__", case_label)
    return html

def plasma_animation():
    return """
    <div style="text-align:center;direction:rtl">
    <canvas id="plasmaCanvas" width="700" height="520" style="border-radius:15px;background:#050a15;max-width:100%"></canvas>
    <script>
    var c=document.getElementById('plasmaCanvas'),ctx=c.getContext('2d');
    var t=0;var cx=c.width/2,cy=c.height/2;
    var particles=[];
    for(var i=0;i<80;i++){var angle=Math.random()*Math.PI*2;var r=30+Math.random()*60;particles.push({x:cx+r*Math.cos(angle),y:cy+r*Math.sin(angle),vx:(Math.random()-0.5)*2,vy:(Math.random()-0.5)*2,type:Math.random()>0.5?'ion':'electron',trail:[]});}
    function draw(){
        ctx.fillStyle='rgba(5,10,21,0.15)';ctx.fillRect(0,0,c.width,c.height);
        ctx.strokeStyle='#37474f';ctx.lineWidth=4;ctx.beginPath();ctx.ellipse(cx,cy,250,180,0,0,Math.PI*2);ctx.stroke();ctx.fillStyle='rgba(55,71,79,0.1)';ctx.fill();
        ctx.strokeStyle='rgba(33,150,243,0.15)';ctx.lineWidth=1;for(var i=0;i<8;i++){var r=40+i*25;ctx.beginPath();ctx.ellipse(cx,cy,r,r*0.7,0,0,Math.PI*2);ctx.stroke();}
        for(var idx=0;idx<particles.length;idx++){
            var p=particles[idx];
            var dx=p.x-cx,dy=p.y-cy;var dist=Math.sqrt(dx*dx+dy*dy);var maxR=100;
            if(dist>maxR){var force=(dist-maxR)*0.05;p.vx-=(dx/dist)*force;p.vy-=(dy/dist)*force;}
            p.vx+=(Math.random()-0.5)*0.3;p.vy+=(Math.random()-0.5)*0.3;p.vx*=0.99;p.vy*=0.99;p.x+=p.vx;p.y+=p.vy;
            p.trail.push({x:p.x,y:p.y});if(p.trail.length>8)p.trail.shift();
            for(var ti=0;ti<p.trail.length;ti++){var alpha=ti/p.trail.length*0.5;ctx.fillStyle=p.type==='ion'?'rgba(244,67,54,'+alpha+')':'rgba(33,150,243,'+alpha+')';ctx.beginPath();ctx.arc(p.trail[ti].x,p.trail[ti].y,2,0,Math.PI*2);ctx.fill();}
            var grd=ctx.createRadialGradient(p.x,p.y,0,p.x,p.y,p.type==='ion'?6:4);
            if(p.type==='ion'){grd.addColorStop(0,'#ff5252');grd.addColorStop(1,'transparent');}else{grd.addColorStop(0,'#448aff');grd.addColorStop(1,'transparent');}
            ctx.fillStyle=grd;ctx.beginPath();ctx.arc(p.x,p.y,p.type==='ion'?6:4,0,Math.PI*2);ctx.fill();
            ctx.fillStyle='#fff';ctx.beginPath();ctx.arc(p.x,p.y,1.5,0,Math.PI*2);ctx.fill();
        }
        ctx.fillStyle='#fff';ctx.font='bold 16px Cairo';ctx.fillText('احتواء البلازما بالمجال المغناطيسي (توكاماك)',cx-180,30);
        ctx.fillStyle='#ff8a80';ctx.font='13px Cairo';ctx.fillText('ايونات موجبة',30,c.height-50);ctx.fillStyle='#82b1ff';ctx.fillText('الكترونات سالبة',30,c.height-30);
        ctx.fillStyle='#ffd54f';ctx.font='12px Cairo';ctx.fillText('المجال المغناطيسي يمنع الجسيمات من لمس جدران الوعاء',cx-200,c.height-10);
        var fAngle=t*0.02;for(var i=0;i<4;i++){var a=fAngle+i*Math.PI/2;var px=cx+110*Math.cos(a),py=cy+110*0.7*Math.sin(a);var fx=px-20*Math.cos(a),fy=py-20*0.7*Math.sin(a);ctx.strokeStyle='rgba(255,213,79,0.6)';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(px,py);ctx.lineTo(fx,fy);ctx.stroke();ctx.fillStyle='rgba(255,213,79,0.6)';ctx.beginPath();ctx.moveTo(fx,fy);ctx.lineTo(fx+8*Math.cos(a+0.5),fy+8*0.7*Math.sin(a+0.5));ctx.lineTo(fx+8*Math.cos(a-0.5),fy+8*0.7*Math.sin(a-0.5));ctx.closePath();ctx.fill();}
        t++;requestAnimationFrame(draw);
    }draw();
    </script>
    </div>"""

# ════════════════════════════════════════════════════════════════
def plot_straight_wire_field(I, r, material_mu):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), facecolor='#0a1628')
    for ax in [ax1, ax2]:
        ax.set_facecolor('#0a1628');ax.tick_params(colors='white')
        for s in ax.spines.values(): s.set_color('#37474f')
    distances = np.linspace(0.01, 0.5, 200)
    B_values = MU_0 * I * material_mu / (2 * np.pi * distances)
    ax1.plot(distances*100, B_values*1e6, color='#64b5f6', linewidth=2.5)
    ax1.axvline(x=r*100, color='#ff9800', linestyle='--', linewidth=2, label=f'r = {r*100:.1f} cm')
    B_at_r = MU_0 * I * material_mu / (2 * np.pi * r)
    ax1.plot(r*100, B_at_r*1e6, 'o', color='#ff9800', markersize=12, zorder=5)
    ax1.set_xlabel('r (cm)', color='white', fontsize=12);ax1.set_ylabel('B (uT)', color='white', fontsize=12)
    ax1.set_title('B vs r', color='white', fontsize=14, fontweight='bold')
    ax1.legend(facecolor='#1a237e', edgecolor='#37474f', labelcolor='white');ax1.grid(True, alpha=0.2, color='#546e7a')
    currents = np.linspace(0.1, 20, 200)
    B_vs_I = MU_0 * currents * material_mu / (2 * np.pi * r)
    ax2.plot(currents, B_vs_I*1e6, color='#ef5350', linewidth=2.5)
    ax2.axvline(x=I, color='#ffeb3b', linestyle='--', linewidth=2, label=f'I = {I:.1f} A')
    ax2.plot(I, B_at_r*1e6, 'o', color='#ffeb3b', markersize=12, zorder=5)
    ax2.set_xlabel('I (A)', color='white', fontsize=12);ax2.set_ylabel('B (uT)', color='white', fontsize=12)
    ax2.set_title('B vs I', color='white', fontsize=14, fontweight='bold')
    ax2.legend(facecolor='#1a237e', edgecolor='#37474f', labelcolor='white');ax2.grid(True, alpha=0.2, color='#546e7a')
    plt.tight_layout();return fig

def plot_coil_field(I, N, R, material_mu):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), facecolor='#0a1628')
    for ax in [ax1, ax2]:
        ax.set_facecolor('#0a1628');ax.tick_params(colors='white')
        for s in ax.spines.values(): s.set_color('#37474f')
    B_center = MU_0 * I * N * material_mu / (2 * R)
    turns = np.linspace(1, 50, 200);B_vs_N = MU_0*I*turns*material_mu/(2*R)
    ax1.plot(turns, B_vs_N*1e6, color='#66bb6a', linewidth=2.5)
    ax1.axvline(x=N, color='#ffeb3b', linestyle='--', linewidth=2, label=f'N={N:.0f}')
    ax1.plot(N, B_center*1e6, 'o', color='#ffeb3b', markersize=12, zorder=5)
    ax1.set_xlabel('N', color='white', fontsize=12);ax1.set_ylabel('B (uT)', color='white', fontsize=12)
    ax1.set_title('B vs N', color='white', fontsize=14, fontweight='bold')
    ax1.legend(facecolor='#1a237e', edgecolor='#37474f', labelcolor='white');ax1.grid(True, alpha=0.2, color='#546e7a')
    radii = np.linspace(0.01, 0.5, 200);B_vs_R = MU_0*I*N*material_mu/(2*radii)
    ax2.plot(radii*100, B_vs_R*1e6, color='#ab47bc', linewidth=2.5)
    ax2.axvline(x=R*100, color='#ffeb3b', linestyle='--', linewidth=2, label=f'R={R*100:.1f}cm')
    ax2.plot(R*100, B_center*1e6, 'o', color='#ffeb3b', markersize=12, zorder=5)
    ax2.set_xlabel('R (cm)', color='white', fontsize=12);ax2.set_ylabel('B (uT)', color='white', fontsize=12)
    ax2.set_title('B vs R', color='white', fontsize=14, fontweight='bold')
    ax2.legend(facecolor='#1a237e', edgecolor='#37474f', labelcolor='white');ax2.grid(True, alpha=0.2, color='#546e7a')
    plt.tight_layout();return fig

def plot_solenoid_field(I, n, material_mu):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), facecolor='#0a1628')
    for ax in [ax1, ax2]:
        ax.set_facecolor('#0a1628');ax.tick_params(colors='white')
        for s in ax.spines.values(): s.set_color('#37474f')
    B_sol = MU_0*I*n*material_mu
    densities = np.linspace(100, 5000, 200);B_vs_n = MU_0*I*densities*material_mu
    ax1.plot(densities, B_vs_n*1e3, color='#26c6da', linewidth=2.5)
    ax1.axvline(x=n, color='#ffeb3b', linestyle='--', linewidth=2, label=f'n={n:.0f}/m')
    ax1.plot(n, B_sol*1e3, 'o', color='#ffeb3b', markersize=12, zorder=5)
    ax1.set_xlabel('n (turns/m)', color='white', fontsize=12);ax1.set_ylabel('B (mT)', color='white', fontsize=12)
    ax1.set_title('B vs n', color='white', fontsize=14, fontweight='bold')
    ax1.legend(facecolor='#1a237e', edgecolor='#37474f', labelcolor='white');ax1.grid(True, alpha=0.2, color='#546e7a')
    currents = np.linspace(0.1, 20, 200);B_vs_I = MU_0*currents*n*material_mu
    ax2.plot(currents, B_vs_I*1e3, color='#ffa726', linewidth=2.5)
    ax2.axvline(x=I, color='#ffeb3b', linestyle='--', linewidth=2, label=f'I={I:.1f}A')
    ax2.plot(I, B_sol*1e3, 'o', color='#ffeb3b', markersize=12, zorder=5)
    ax2.set_xlabel('I (A)', color='white', fontsize=12);ax2.set_ylabel('B (mT)', color='white', fontsize=12)
    ax2.set_title('B vs I', color='white', fontsize=14, fontweight='bold')
    ax2.legend(facecolor='#1a237e', edgecolor='#37474f', labelcolor='white');ax2.grid(True, alpha=0.2, color='#546e7a')
    plt.tight_layout();return fig

# ════════════════════════════════════════════════════════════════
def main():
    st.markdown("""
    <div class="main-header">
        <h1>🧲 قانون بيو-سافار</h1>
        <div class="en-title">Biot-Savart Law | Magnetic Field of an Electric Current</div>
        <div class="author">✦ Israa Youssuf Samara ✦</div>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### 🎛️ لوحة التحكم")
        st.markdown("---")
        selected_material = st.selectbox("🔬 اختر الوسط المادي:", list(MATERIALS.keys()), index=0, key="mat_sel")
        material_mu = MATERIALS[selected_material]
        st.info(f"**النفاذية النسبية μr = {material_mu}**\n\nمادة ذات نفاذية أعلى = مجال أقوى!")
        st.markdown("---")
        st.markdown("### 📚 دليل الاستخدام")
        st.markdown("- أزرار لعكس التيار\n- شرائح لتغيير القيم\n- راقب التغيير بصرياً")

    tabs = st.tabs(["🏠 المقدمة", "📐 القانون والاشتقاق", "📏 موصل مستقيم", "🔄 ملف دائري", "🔧 ملف لولبي", "✋ قاعدة اليد اليمنى", "☢️ احتواء البلازما", "📝 التقييم"])

    # ═══ TAB 0 ═══
    with tabs[0]:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("## 🔬 تجربة أورستد - البداية المذهلة")
        st.markdown("""
        تخيّل أنك في مختبر عام **1820م**... العالم **أورستد** وضع بوصلة بالقرب من سلك يمر فيه تيار كهربائي...
        فلاحظ: **إبرة البوصلة انحرفت!** 🤯

        > **الشحنة المتحركة (التيار) تولّد مجالاً مغناطيسياً حولها**
        """)
        st.markdown("### 🎬 شاهد تجربة أورستد (اضغط الرسمة)")
        st.components.v1.html(oersted_animation(), height=380)
        st.audio(play_sound("info"), format="audio/wav", autoplay=False)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="life-example">', unsafe_allow_html=True)
        st.markdown("### 🌟 من حياتنا اليومية")
        st.markdown("""
        - **شاحن الهاتف**: تيار يولّد مجالاً مغناطيسياً ضعيفاً
        - **المحرك الكهربائي**: يعتمد على التيار والمجال المغناطيسي
        - **رافعة النفايات**: تيار قوي يجذب الحديد
        - **السماعات**: تيار متغير يولّد مجالاً يحرك الغشاء
        """)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("### 🤔 كيف نحسب المجال؟ العالمان **بيو** و **سافار** توصلا تجريبياً إلى علاقة رياضية! انتقل للتبويب التالي 👉")
        st.markdown('</div>', unsafe_allow_html=True)

    # ═══ TAB 1 ═══
    with tabs[1]:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("## 📐 قانون بيو-سافار")
        st.markdown("الموصل يتكوّن من أجزاء صغيرة. كل جزء يولّد مجالاً جزئياً. بجمعها (التكامل) نحصل على المجال الكلي!")
        st.markdown("""<div class="formula-box"><div class="formula">dB = (μ₀ / 4π) × (I · dL · sinθ) / r²</div></div>""", unsafe_allow_html=True)
        st.markdown("""
        | الرمز | المعنى | الوحدة |
        |-------|--------|--------|
        | **dB** | المجال الجزئي | T |
        | **μ₀** | نفاذية الفراغ = 4π×10⁻⁷ | T·m/A |
        | **I** | التيار | A |
        | **dL** | طول الجزء الصغير | m |
        | **θ** | الزاوية بين dL و r | درجة |
        | **r** | المسافة إلى النقطة | m |
        """)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("## 📝 الاشتقاق - موصل مستقيم لانهائي")
        st.markdown("""
        <div class="step-badge">الخطوة 1</div>
        <div class="derivation-step">dB = (μ₀ / 4π) × (I · dL · sinθ) / r²</div>
        <div class="step-badge">الخطوة 2</div>
        <div class="derivation-step">sinθ = R/r , r = R/sinθ , dL = R·dθ/sin²θ<br>بالتعويض: dB = (μ₀I / 4πR) × sinθ · dθ</div>
        <div class="step-badge">الخطوة 3</div>
        <div class="derivation-step">التكامل من 0 إلى π:<br>B = (μ₀I / 4πR) × [-cosθ]₀^π = (μ₀I / 4πR) × 2</div>
        <div class="step-badge">النتيجة ✅</div>
        <div class="formula-box"><div class="formula">B = μ₀I / (2πr)</div></div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("## 📝 اشتقاق ملف دائري")
        st.markdown("""<div class="derivation-step">θ = 90° → sinθ = 1<br>B = (μ₀I / 4πR²) × 2πR = μ₀I/(2R)<br><b>لـ N لفة:</b> B = μ₀IN / (2R)</div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("## 📝 اشتقاق ملف لولبي")
        st.markdown("""<div class="derivation-step">n = N/L (لفات/م)<br>بتجميع تأثير اللفات:<br><b>B = μ₀In = μ₀IN / L</b></div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="life-example">### 💡 تشبيه التكامل: عدّ الناس في طابور - تُحصي مجموعة صغيرة ثم تنتقل... التكامل = جمع كل المجموعات!</div>', unsafe_allow_html=True)

    # ═══ TAB 2: WIRE ═══
    with tabs[2]:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("## 📏 موصل مستقيم لانهائي")
        st.markdown("""<div class="formula-box"><div class="formula">B = μ₀ × μr × I / (2πr)</div></div>""", unsafe_allow_html=True)
        st.markdown('> **قاعدة اليد اليمنى:** الإبهام لاتجاه التيار → لف الأصابع = اتجاه المجال')
        st.markdown('- تيار ⊙ خارج الصفحة → المجال **عكس عقارب الساعة**\n- تيار ⊗ داخل الصفحة → المجال **مع عقارب الساعة**')

        col1, col2 = st.columns(2)
        with col1:
            current_wire = st.slider("التيار I (أمبير) - موصل:", 0.1, 20.0, 5.0, 0.1, key="sl_wire_I")
            current_dir_wire = st.radio("اتجاه التيار:", ["للأعلى (خارج الصفحة) ⊙", "للأسفل (داخل الصفحة) ⊗"], index=0, horizontal=True, key="rd_wire_dir")
            dir_wire = 1 if "للأعلى" in current_dir_wire else -1
            if st.button("🔄 عكس التيار", use_container_width=True, key="btn_wire"):
                dir_wire *= -1; st.rerun()
        with col2:
            distance_wire = st.slider("المسافة r (متر) - موصل:", 0.01, 1.0, 0.1, 0.01, key="sl_wire_r")
        st.markdown('</div>', unsafe_allow_html=True)

        B_wire = MU_0 * current_wire * material_mu / (2 * np.pi * distance_wire)
        st.markdown(f"""<div class="result-box">
            <div style="font-size:1.3em;font-weight:800;color:#1b5e20">B = {B_wire:.4e} T = {B_wire*1e6:.4f} μT</div>
            <div style="font-size:0.9em;color:#2e7d32;margin-top:8px">{selected_material} | μr={material_mu} | I={current_wire}A | r={distance_wire}m</div>
        </div>""", unsafe_allow_html=True)

        st.markdown(f'<div class="info-box">**ما يحدث:** التيار {current_wire}A → المجال = **{B_wire:.4e} T**. لو اخترت الحديد النقي (μr=5000) يصبح **{B_wire*5000/material_mu:.4e} T**!</div>', unsafe_allow_html=True)

        st.components.v1.html(straight_wire_animation(dir_wire, current_wire, distance_wire, material_mu), height=520)
        st.pyplot(plot_straight_wire_field(current_wire, distance_wire, material_mu))
        st.markdown('<div class="life-example">### 🌟 كابلات الطاقة تحمل تيارات كبيرة، مجالها يؤثر على البوصلة إذا اقتربت كثيراً!</div>', unsafe_allow_html=True)

    # ═══ TAB 3: COIL ═══
    with tabs[3]:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("## 🔄 ملف دائري")
        st.markdown("""<div class="formula-box"><div class="formula">B = μ₀ × μr × I × N / (2R)</div></div>""", unsafe_allow_html=True)
        st.markdown('> **قاعدة اليد اليمنى:** أصابعك لاتجاه التيار → الإبهام = اتجاه المجال B')
        st.markdown('- مجال **للأعلى** → التيار **عكس عقارب الساعة**\n- مجال **للأسفل** → التيار **مع عقارب الساعة**')

        col1, col2 = st.columns(2)
        with col1:
            current_coil = st.slider("التيار I (أمبير) - ملف دائري:", 0.1, 20.0, 5.0, 0.1, key="sl_coil_I")
            N_coil = st.slider("عدد اللفات N - ملف دائري:", 1, 50, 5, 1, key="sl_coil_N")
            current_dir_coil = st.radio("اتجاه المجال B:", ["للأعلى ↑", "للأسفل ↓"], index=0, horizontal=True, key="rd_coil_dir")
            dir_coil = 1 if "للأعلى" in current_dir_coil else -1
        with col2:
            R_coil = st.slider("نصف القطر R (متر) - ملف دائري:", 0.01, 1.0, 0.1, 0.01, key="sl_coil_R")
        st.markdown('</div>', unsafe_allow_html=True)

        B_coil = MU_0 * current_coil * material_mu * N_coil / (2 * R_coil)
        st.markdown(f"""<div class="result-box">
            <div style="font-size:1.3em;font-weight:800;color:#1b5e20">B = {B_coil:.4e} T = {B_coil*1e6:.4f} μT</div>
            <div style="font-size:0.9em;color:#2e7d32;margin-top:8px">N={N_coil} | I={current_coil}A | R={R_coil}m | μr={material_mu}</div>
        </div>""", unsafe_allow_html=True)

        b_dir_text = "عكس عقارب الساعة" if dir_coil == 1 else "مع عقارب الساعة"
        st.markdown(f'<div class="info-box">المجال {current_dir_coil} → التيار يسري **{b_dir_text}** في الملف. كل لفة من الـ {N_coil} تُساهم بمجال!</div>', unsafe_allow_html=True)

        st.components.v1.html(circular_coil_animation(dir_coil, current_coil, N_coil, R_coil, material_mu), height=520)
        st.pyplot(plot_coil_field(current_coil, N_coil, R_coil, material_mu))

    # ═══ TAB 4: SOLENOID ═══
    with tabs[4]:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("## 🔩 ملف لولبي")
        st.markdown("""<div class="formula-box"><div class="formula">B = μ₀ × μr × I × n = μ₀ × μr × I × N / L</div></div>""", unsafe_allow_html=True)
        st.markdown("سلك ملفوف أسطوانياً. المجال داخله **منتظم** عندما يكون طوله >> قطره!")

        col1, col2 = st.columns(2)
        with col1:
            current_sol = st.slider("التيار I (أمبير) - لولبي:", 0.1, 20.0, 5.0, 0.1, key="sl_sol_I")
            n_sol = st.slider("كثافة اللفات n (لفة/م) - لولبي:", 100, 5000, 1400, 50, key="sl_sol_n")
            current_dir_sol = st.radio("اتجاه المجال - لولبي:", ["الشمالي لليمين N→", "الشمالي لليسار ←N"], index=0, horizontal=True, key="rd_sol_dir")
            dir_sol = 1 if "لليمين" in current_dir_sol else -1
        with col2:
            L_sol = st.slider("طول الملف L (متر) - لولبي:", 0.1, 2.0, 0.5, 0.05, key="sl_sol_L")
            N_sol = int(n_sol * L_sol)
            st.info(f"**إجمالي اللفات N = {N_sol}**")
        st.markdown('</div>', unsafe_allow_html=True)

        B_sol = MU_0 * current_sol * material_mu * n_sol
        st.markdown(f"""<div class="result-box">
            <div style="font-size:1.3em;font-weight:800;color:#1b5e20">B = {B_sol:.4e} T = {B_sol*1e3:.4f} mT</div>
            <div style="font-size:0.9em;color:#2e7d32;margin-top:8px">n={n_sol}/m | I={current_sol}A | L={L_sol}m | N={N_sol}</div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="info-box">المجال منتظم داخل الملف. عكس اتجاه المجال → تبادل الأقطاب N و S!</div>', unsafe_allow_html=True)

        st.components.v1.html(solenoid_animation(dir_sol, current_sol, n_sol, L_sol, material_mu), height=500)
        st.pyplot(plot_solenoid_field(current_sol, n_sol, material_mu))
        st.markdown('<div class="life-example">### 🌟 جهاز الرنين المغناطيسي MRI يستخدم ملفاً لولبياً ضخماً (~1.5 تسلا)!</div>', unsafe_allow_html=True)

    # ═══ TAB 5: RIGHT HAND ═══
    with tabs[5]:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("## ✋ قاعدة اليد اليمنى")
        st.markdown("""
        **موصل مستقيم:** الإبهام = اتجاه التيار → لف الأصابع = اتجاه المجال B
        **ملف دائري/لولبي:** لف الأصابع = اتجاه التيار → الإبهام = اتجاه المجال B
        """)
        case_rh = st.radio("اختر الحالة:", ["موصل مستقيم", "ملف دائري", "ملف لولبي"], horizontal=True, key="rd_rh_case")
        case_key = {"موصل مستقيم": "wire", "ملف دائري": "coil", "ملف لولبي": "solenoid"}[case_rh]
        dir_rh = st.radio("اتجاه التيار - يد:", ["الأصلي", "العكس"], horizontal=True, index=0, key="rd_rh_dir")
        dir_rh_val = 1 if "الأصلي" in dir_rh else -1
        st.markdown('</div>', unsafe_allow_html=True)
        st.components.v1.html(right_hand_animation(case_key, dir_rh_val), height=540)
        st.markdown('<div class="warning-box">⚠️ استخدم اليد **اليمنى** فقط! اليسرى تعطي الاتجاه المعاكس!</div>', unsafe_allow_html=True)
        st.markdown('<div class="life-example">### 🌟 تشبيه: المسمار - تدور المفك (المجال) والإبهام (التيار) مرتبطان!</div>', unsafe_allow_html=True)

    # ═══ TAB 6: PLASMA ═══
    with tabs[6]:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("## ☢️ احتواء البلازما بالمجال المغناطيسي")
        st.markdown("""
        ### 🔥 البلازما = الحالة الرابعة للمادة
        غاز مسخّن لـ **ملايين الدرجات** → أيونات موجبة + إلكترونات سالبة

        ### ❓ لماذا الاحتواء؟
        البلازما **تُذيب أي وعاء مادي**! **الحل:** المجال المغناطيسي كـ "وعاء غير ملموس" 🔮

        ### 🧲 الآلية: F = qv × B
        الجسيمات المشحونة تدور حلزونياً حول خطوط المجال ولا تهرب!
        """)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 🎬 شاهد البلازما محتواة (الأحمر=أيونات، الأزرق=إلكترونات)")
        st.components.v1.html(plasma_animation(), height=540)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 🔬 التوكاماك")
        st.markdown("""
        جهاز حَلّي يُولّد مجالاً معقداً:
        1. **مجال حلقي (Toroidal):** يمنع الهروب الجانبي
        2. **مجال قطبي (Poloidal):** يمنع الهروب العمودي
        3. **المحصّل:** حلزوني يحبس البلازما!

        **والملفات اللولبية** التي درسناها تُستخدم هنا! 🎯

        | المعلمة | القيمة |
        |---------|--------|
        | حرارة البلازما | ~150,000,000 °C |
        | المجال المطلوب | ~5-13 تسلا |
        | أكبر مشروع (ITER) | فرنسا - قيد البناء |
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="success-box">### ✨ من قانون بسيط → طاقة نظيفة لا نهائية! **هذا جمال الفيزياء** 🌍</div>', unsafe_allow_html=True)

    # ═══ TAB 7: QUIZ ═══
    with tabs[7]:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("## 📝 التقييم التفاعلي النهائي")

        if "quiz_answers" not in st.session_state:
            st.session_state.quiz_answers = {}
        if "quiz_submitted" not in st.session_state:
            st.session_state.quiz_submitted = False
        if "quiz_score" not in st.session_state:
            st.session_state.quiz_score = 0

        questions = [
            {"q": "عند مضاعفة التيار I في قانون بيو-سافار، ماذا يحدث لـ dB?",
             "opts": ["يُضاعف", "يُربَع", "يبقى ثابتاً", "ينصف"], "c": 0, "exp": "dB ∝ I → مضاعفة I تُضاعف dB"},
            {"q": "شكل خطوط المجال حول موصل مستقيم لانهائي:",
             "opts": ["خطوط مستقيمة", "دوائر متحدة المركز", "خطوط متشعبة", "غير منتظمة"], "c": 1, "exp": "دوائر مركزها الموصل"},
            {"q": "سلك تيار 4A، مسافة 0.2m. المجال تقريباً:",
             "opts": ["2×10⁻⁶ T", "4×10⁻⁶ T", "8×10⁻⁶ T", "1×10⁻⁶ T"], "c": 1, "exp": "B=μ₀I/(2πr)=4×10⁻⁶ T"},
            {"q": "قاعدة اليد اليمنى على ملف دائري: الإبهام يشير لـ:",
             "opts": ["اتجاه التيار", "اتجاه المجال B في المركز", "اتجاه القوة", "المجال الكهربائي"], "c": 1, "exp": "الأصابع=التيار، الإبهام=B"},
            {"q": "ملف لولبي L=0.5m, N=1000, I=2A. المجال تقريباً:",
             "opts": ["1.6×10⁻³ T", "5.0×10⁻³ T", "2.5×10⁻³ T", "8.0×10⁻⁴ T"], "c": 1, "exp": "n=2000, B=μ₀In≈5.0×10⁻³ T"},
            {"q": "لماذا لا نحتوي البلازما بوعاء مادي?",
             "opts": ["خفيفة جداً", "ستُذيب الوعاء", "لا تتفاعل", "شفافة"], "c": 1, "exp": "حرارتها ملايين درجات!"},
            {"q": "مضاعفة N و L معاً في لولبي يُحدث:",
             "opts": ["يُضاعف B", "ثابت B", "يُربَع B", "ينقص B"], "c": 1, "exp": "B=μ₀I(N/L)، النسبة ثابتة!"},
            {"q": "المجال على امتداد موصل مستقيم يساوي:",
             "opts": ["أقصى قيمة", "صفراً", "نصف القصوى", "يعتمد على الطول"], "c": 1, "exp": "θ=0 أو 180° → sinθ=0 → B=0"},
        ]

        for i, q in enumerate(questions):
            st.markdown(f"### س{i+1}: {q['q']}")
            if not st.session_state.quiz_submitted:
                st.session_state.quiz_answers[i] = st.radio(
                    f"اختر - س{i}:", q["opts"], key=f"q_{i}", index=None, label_visibility="collapsed")
            else:
                sel = st.session_state.quiz_answers.get(i, -1)
                for j, opt in enumerate(q["opts"]):
                    cls = "correct" if j == q["c"] else ("wrong" if j == sel else "")
                    icon = "✅ " if j == q["c"] else ("❌ " if j == sel else "")
                    st.markdown(f'<div class="quiz-option {cls}">{icon}{opt}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="info-box">💡 {q["exp"]}</div>', unsafe_allow_html=True)
            st.markdown("---")

        if not st.session_state.quiz_submitted:
            if st.button("✅ تحقق من إجاباتي", type="primary", use_container_width=True, key="btn_quiz"):
                if len(st.session_state.quiz_answers) < len(questions):
                    st.warning("⚠️ أجب عن جميع الأسئلة!")
                else:
                    st.session_state.quiz_submitted = True
                    st.session_state.quiz_score = sum(
                        1 for i, q in enumerate(questions)
                        if st.session_state.quiz_answers.get(i) == q["c"])
                    st.rerun()
        else:
            sc = st.session_state.quiz_score; tot = len(questions); pct = sc/tot*100
            if pct >= 90: em, msg, cl = "🏆", "ممتاز!", "#1b5e20"
            elif pct >= 70: em, msg, cl = "👍", "جيد جداً!", "#e65100"
            elif pct >= 50: em, msg, cl = "📖", "مقبول، راجع الدروس.", "#c62828"
            else: em, msg, cl = "💪", "تحتاج مراجعة شاملة.", "#c62828"
            bg = "#e8f5e9" if pct >= 70 else "#ffebee"
            bg2 = "#a5d6a7" if pct >= 70 else "#ef9a9a"
            st.markdown(f"""<div class="result-box" style="border-color:{cl};background:linear-gradient(135deg,{bg},{bg2})">
                <div style="font-size:3em">{em}</div>
                <div style="font-size:1.8em;font-weight:900;color:{cl};margin:10px 0">{sc}/{tot} ({pct:.0f}%)</div>
                <div style="font-size:1.1em;color:{cl}">{msg}</div></div>""", unsafe_allow_html=True)
            if pct >= 70: st.audio(play_sound("success"), format="audio/wav")
            else: st.audio(play_sound("error"), format="audio/wav")
            if st.button("🔄 أعد المحاولة", use_container_width=True, key="btn_retry"):
                st.session_state.quiz_answers = {}; st.session_state.quiz_submitted = False; st.session_state.quiz_score = 0; st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;padding:25px;color:#78909c;font-size:0.9em;border-top:1px solid #263238;margin-top:30px">
        🧲 قانون بيو-سافار التفاعلي | Biot-Savart Law Interactive Explorer<br>
        ✦ Israa Youssuf Samara ✦<br>
        <span style="font-size:0.8em">فيزياء الصف الثاني عشر</span>
    </div>""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
