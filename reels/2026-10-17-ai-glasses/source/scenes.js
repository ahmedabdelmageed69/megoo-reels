/* ================= SCENES: AI glasses ================= */
const SC=[{d:3.6,f:g1},{d:4.4,f:g2},{d:3.4,f:g3},{d:10.0,f:g4},{d:4.6,f:g5},{d:6.0,f:g6},{d:4.8,f:g7},{d:5.6,f:g8}];
function glasses(x,y,sc,theme,o={},parent){
  const g=S('g',{transform:`translate(${x},${y}) scale(${sc})`},parent);
  const dk=theme==='dark';
  const st=dk?'#F4EEF8':C.ink, fill=dk?'rgba(255,255,255,.05)':'#FBF9F7', lens=dk?'rgba(190,170,255,.10)':'rgba(122,62,138,.06)';
  // temples
  S('path',{d:'M-300,-60 L-372,-44 L-380,-20',fill:'none',stroke:st,'stroke-width':12,'stroke-linecap':'round','stroke-linejoin':'round'},g);
  S('path',{d:'M300,-60 L372,-44 L380,-20',fill:'none',stroke:st,'stroke-width':12,'stroke-linecap':'round','stroke-linejoin':'round'},g);
  for(const sx of [-1,1]){
    S('rect',{x:sx<0?-300:40,y:-95,width:260,height:180,rx:70,fill:lens,stroke:st,'stroke-width':o.thin?8:18},g);
  }
  S('path',{d:'M-40,-30 Q0,-62 40,-30',fill:'none',stroke:st,'stroke-width':14},g);
  // camera + LED (left lens top corner from viewer = wearer's right)
  if(!o.thin){
    S('circle',{cx:262,cy:-78,r:15,fill:dk?'#17131C':C.ink,stroke:o.camHi?C.pur:st,'stroke-width':o.camHi?6:3},g);
    S('circle',{cx:262,cy:-78,r:5,fill:o.camHi?'#E5B8F0':'#888'},g);
    S('circle',{cx:-262,cy:-78,r:6,fill:o.led?'#FF4D6D':(dk?'#444':'#BBB')},g);
  }
  if(o.disp){ // answer shown inside right lens (viewer's right)
    const k=o.disp;
    S('rect',{x:-230,y:-40,width:120,height:72,rx:14,fill:dk?'rgba(140,255,200,.18)':'rgba(122,62,138,.15)',stroke:dk?'#8CFFC8':C.pur,'stroke-width':3,opacity:k},g);
    const tx=S('text',{x:-170,y:12,fill:dk?'#8CFFC8':C.pur,'font-size':48,'text-anchor':'middle',class:'mlbl',opacity:k},g);tx.textContent='C ✓';
    if(dk)S('rect',{x:-240,y:-50,width:140,height:92,rx:18,fill:'#8CFFC8',opacity:.18*k,filter:'url(#blur8)'},g);
  }
  return g;
}
function paper(x,y,sc,theme,o={},parent){
  const g=S('g',{transform:`translate(${x},${y}) scale(${sc}) rotate(${o.rot||0})`},parent);
  const dk=theme==='dark', st=dk?'#CFC6DA':C.ink;
  S('rect',{x:-210,y:-280,width:420,height:560,rx:10,fill:dk?'rgba(255,255,255,.06)':'#FFFFFF',stroke:st,'stroke-width':4},g);
  S('line',{x1:-170,y1:-220,x2:60,y2:-220,stroke:st,'stroke-width':10,'stroke-linecap':'round'},g);
  for(let i=0;i<3;i++)S('line',{x1:-170,y1:-160+i*40,x2:170-(i==2?120:0),y2:-160+i*40,stroke:st,'stroke-width':5,opacity:.5,'stroke-linecap':'round'},g);
  'ABCD'.split('').forEach((L,i)=>{const yy=0+i*62;
    S('circle',{cx:-150,cy:yy,r:20,fill:(o.mark&&L==='C')?C.pur:'none',stroke:st,'stroke-width':4},g);
    const t=S('text',{x:-150,y:yy+8,fill:(o.mark&&L==='C')?'#fff':st,'font-size':22,'text-anchor':'middle',class:'mlbl'},g);t.textContent=L;
    S('line',{x1:-110,y1:yy,x2:120-i*20,y2:yy,stroke:st,'stroke-width':5,opacity:.45,'stroke-linecap':'round'},g);});
  return g;
}
function phone(x,y,sc,parent){
  const g=S('g',{transform:`translate(${x},${y}) scale(${sc})`},parent);
  S('rect',{x:-75,y:-145,width:150,height:290,rx:26,fill:'#FBF9F7',stroke:C.ink,'stroke-width':5},g);
  S('line',{x1:-20,y1:-125,x2:20,y2:-125,stroke:C.ink,'stroke-width':5,'stroke-linecap':'round'},g);
  return g;
}
function aiBubble(x,y,sc,k,t,parent){
  const g=S('g',{transform:`translate(${x},${y}) scale(${sc*back(k)})`},parent);
  S('circle',{r:95,fill:C.pl,stroke:C.pur,'stroke-width':5},g);
  for(let i=0;i<6;i++){const a=i*Math.PI/3+t*.8;S('line',{x1:0,y1:0,x2:62*Math.cos(a),y2:62*Math.sin(a),stroke:C.pur,'stroke-width':3,opacity:.6},g);S('circle',{cx:62*Math.cos(a),cy:62*Math.sin(a),r:9,fill:C.pur},g)}
  S('circle',{r:30,fill:C.pur},g);
  const tx=S('text',{y:11,fill:'#fff','font-size':30,'text-anchor':'middle',class:'mlbl'},g);tx.textContent='AI';
  return g;
}
function darkRoom(t,g){
  // exam desk perspective + soft overhead light
  S('ellipse',{cx:540,cy:300,rx:520,ry:420,fill:'url(#beam)',opacity:.16,filter:'url(#blur20)'},g);
  S('path',{d:'M-100,1500 L330,1050 L750,1050 L1180,1500 Z',fill:'rgba(255,255,255,.03)',stroke:'#3A3442','stroke-width':3},g);
  for(let i=0;i<30;i++){const px=(i*137.5%1080), py=((i*251+t*20*(1+i%3))%1500)+120;S('circle',{cx:px,cy:py,r:1.5+(i%3),fill:'#fff',opacity:.08+(i%5)*.03},g)}
}
function g1(t){ // hook
  BG.setAttribute('fill',C.dark);
  const g=S('g',{transform:shake(t,t<.5?5*(1-t/.5):0)});
  darkRoom(t,g);
  paper(540,1180,.62,'dark',{rot:-4},g);
  const zoom=1.05+eo(t/3.6)*.12;
  glasses(540,640+Math.sin(t*2)*6,zoom,'dark',{disp:p(t,1.0,.3),led:Math.sin(t*10)>0},g).setAttribute('filter','url(#glow)');
  // scan beam down to paper
  const sb=p(t,.4,.4)*(1-p(t,1.0,.3));
  if(sb>0){S('path',{d:`M${540+262*zoom},${640-78*zoom} L300,1000 L780,1000 Z`,fill:'#B79CFF',opacity:.18*sb},g);
    const ly=1000+((t*900)%340);S('line',{x1:330,y1:ly,x2:750,y2:ly,stroke:'#D9C8FF','stroke-width':4,opacity:sb},g)}
  head('نظارة<br>بتغشّ.',.25,t,'#fff','top:1290px;font-size:150px');
  mono('SEOUL · OCT 2026 · ENTRANCE EXAM',1660,.7,t,'#fff');
  if(t<.25)S('rect',{x:0,y:0,width:W,height:H,fill:'#fff',opacity:1-t/.25});
}
function g2(t){ // looks normal? freeze
  BG.setAttribute('fill',C.dark);
  const g=S('g',{});
  darkRoom(t*.3,g);
  const frz=t>2.3; const z=1.0+eo(Math.min(t,2.3)/2.3)*.2;
  const gy=860;
  glasses(540,gy,z,'dark',{led:frz},g).setAttribute('filter','url(#glow)');
  if(frz){
    const k=p(t,2.3,.25);
    S('rect',{x:0,y:0,width:W,height:H,fill:'#fff',opacity:(1-k)*.6});
    const bx=540-420,by=gy-170,bw=840,bh=330;
    for(const [px,py,dx,dy] of [[bx,by,1,1],[bx+bw,by,-1,1],[bx,by+bh,1,-1],[bx+bw,by+bh,-1,-1]])
      S('path',{d:`M${px},${py+dy*50} L${px},${py} L${px+dx*50},${py}`,fill:'none',stroke:'#fff','stroke-width':5,opacity:k},g);
    // callouts
    const c1=p(t,2.6,.4);
    S('line',{x1:540+262*z,y1:gy-78*z,x2:960,y2:gy-200,stroke:'#F08AA8','stroke-width':3,opacity:c1},g);
    const l1=S('text',{x:960,y:gy-218,fill:'#F08AA8','font-size':30,class:'lbl','text-anchor':'middle',opacity:c1},g);l1.textContent='كاميرا';
    const c2=p(t,2.9,.4);
    S('line',{x1:540-170*z,y1:gy,x2:180,y2:gy+300,stroke:'#F08AA8','stroke-width':3,opacity:c2},g);
    const l2=S('text',{x:180,y:gy+345,fill:'#F08AA8','font-size':30,class:'lbl','text-anchor':'middle',opacity:c2},g);l2.textContent='شاشة جوه العدسة';
    mono('FREEZE · SMART GLASSES',1660,2.35,t,'#fff');
  }
  head('شكلها<br>عادي؟',.15,t,'#fff','top:240px');
  cap('في جامعة سيول، المراقب لاحظ نظارة <b>تخينة</b> زيادة عن اللزوم',.5,2.3,t,'#fff','#F08AA8');
  cap('طلعت نظارة <b>ذكاء اصطناعي</b>… والطالب اتمنع يقدّم 3 سنين',2.4,4.4,t,'#fff','#F08AA8');
}
function g3(t){ // how?
  BG.setAttribute('fill',C.dark);
  const g=S('g',{});
  const sl=(1-eo(t/.7))*260;
  const gg=S('g',{transform:`translate(${sl},0)`},g);
  glasses(540,860,.85,'dark',{},gg);
  const q=p(t,.8,.5);
  for(const [x,y,d] of [[220,1180,0],[540,1240,.2],[860,1180,.4]]){
    const k=p(t,.8+d,.5);
    S('line',{x1:540,y1:950,x2:x,y2:y-50,stroke:'#fff','stroke-width':3,'stroke-dasharray':'8 10',opacity:k},g);
    S('circle',{cx:x,cy:y,r:36,fill:'none',stroke:'#fff','stroke-width':4,opacity:k},g);
    const tq=S('text',{x,y:y+14,fill:'#fff','font-size':40,'text-anchor':'middle',class:'lbl',opacity:k},g);tq.textContent='?';
  }
  head('إزاي بتعرف<br>الإجابة؟',.2,t,'#fff','font-size:120px;top:250px');
  cap('مفيش حد بيلقّنه… والإجابة <b>جوه النظارة</b>',1.0,3.4,t,'#fff','#F08AA8');
}
function g4(t){ // 3 steps mechanism
  BG.setAttribute('fill',C.cream);
  const g=S('g',{});
  const ph=t<3.3?0:t<6.6?1:2;
  const GX=540,GY=700,GS=.7;
  // paper bottom-left, phone bottom-right
  paper(300,1060,.55,'cream',{mark:ph===2&&t>8.2},g);
  const pk=p(t,3.3,.5);
  if(pk>0){phone(800,1090,.9*back((t-3.3)/.5),g);}
  // step 1: scan beam
  if(ph===0){
    const k=p(t,.4,.4);
    S('path',{d:`M${GX+262*GS},${GY-78*GS} L170,920 L430,920 Z`,fill:C.pur,opacity:.12*k},g);
    const ly=910+((t*400)%300);S('line',{x1:190,y1:ly,x2:410,y2:ly,stroke:C.pur,'stroke-width':5,opacity:k},g);
  }
  // step 2: signal to phone then AI
  if(ph>=1){
    const k=p(t,3.5,.4);
    S('path',{d:`M${GX+200},${GY+60} Q900,820 820,960`,fill:'none',stroke:C.ink,'stroke-width':3,'stroke-dasharray':'10 10',opacity:k},g);
    const ak=p(t,4.4,.5);
    S('path',{d:`M860,960 Q980,860 900,${1090-330}`,fill:'none',stroke:C.ink,'stroke-width':3,'stroke-dasharray':'10 10',opacity:0},g);
    // pulses along path glasses->phone
    if(ph===1)for(let i=0;i<3;i++){const u=((t*1.2+i/3)%1);const x=(1-u)*(1-u)*(GX+200)+2*(1-u)*u*900+u*u*820, y=(1-u)*(1-u)*(GY+60)+2*(1-u)*u*820+u*u*960;S('circle',{cx:x,cy:y,r:9,fill:C.pur,opacity:k},g)}
    // AI bubble above-left of phone
    if(ak>0){
      S('line',{x1:770,y1:1000,x2:630,y2:1125,stroke:C.ink,'stroke-width':3,'stroke-dasharray':'10 10',opacity:ak},g);
      aiBubble(560,1185,.8,(t-4.4)/.5,t,g);
    }
  }
  // step 3: answer back into lens
  let disp=0;
  if(ph===2){
    const k=p(t,6.7,.4);
    for(let i=0;i<3;i++){const u=((t*1.2+i/3)%1);const x=(1-u)*820+u*(GX+200), y=(1-u)*960+u*(GY+60) - Math.sin(u*Math.PI)*140;S('circle',{cx:x,cy:y,r:9,fill:'#2E9E6B',opacity:k},g)}
    disp=p(t,7.4,.4);
  }
  glasses(GX,GY,GS,'cream',{camHi:ph===0,led:ph>0,disp},g);
  // lens zoom in phase 3
  if(disp>0){
    const zr=120*back((t-7.6)/.5);
    if(t>7.6){
      S('line',{x1:GX-170*GS,y1:GY,x2:230,y2:GY-140,stroke:C.ink,'stroke-width':2},g);
      S('circle',{cx:190,cy:GY-200,r:zr,fill:'#FBF9F7',stroke:C.ink,'stroke-width':4},g);
      const tx=S('text',{x:190,y:GY-178,fill:C.pur,'font-size':64*zr/120,'text-anchor':'middle',class:'mlbl'},g);tx.textContent='C ✓';
    }
  }
  // steps row
  const steps=[['01','تصوّر'],['02','تسأل'],['03','تجاوب']];
  steps.forEach(([n,s],i)=>{
    const x=880-i*300, y=1330; const k=p(t,.3+i*.15,.4); const on=i<=ph;
    S('line',{x1:x-240,y1:y+70,x2:x,y2:y+70,stroke:on?C.ink:'#BDB6C2','stroke-width':4,opacity:k},g);
    const tn=S('text',{x,y:y-6,fill:on?C.pur:'#BDB6C2','font-size':22,'text-anchor':'end',class:'mlbl',opacity:k},g);tn.textContent=n;
    const ts=S('text',{x,y:y+46,fill:on?C.ink:'#BDB6C2','font-size':44,'text-anchor':'end',class:'lbl',opacity:k},g);ts.textContent=s;
  });
  head('<span class="hl">3 خطوات.</span>',.15,t,C.ink,'top:200px;font-size:150px');
  cap('<b>الكاميرا</b> اللي في الإطار بتصوّر ورقة الأسئلة',.4,3.2,t,C.ink,C.pur);
  cap('الصورة تروح على الموبايل… و<b>الذكاء الاصطناعي</b> يحلها',3.3,6.5,t,C.ink,C.pur);
  cap('والإجابة تظهر على <b>شاشة صغيرة جوه العدسة</b>',6.6,10,t,C.ink,C.pur);
  if(t<.3)S('rect',{x:0,y:0,width:W,height:H*(1-eo(t/.3)),fill:C.dark});
}
function g5(t){ // 96/100 in 18 min
  BG.setAttribute('fill',C.cream);
  const g=S('g',{});
  const n=Math.round(96*eo((t-.3)/1.6));
  D('txt',`<span style="font-family:Mono;font-size:300px;color:${C.pur};direction:ltr;unicode-bidi:isolate">${n}</span><span style="font-family:Mono;font-size:110px;color:${C.ink};direction:ltr;unicode-bidi:isolate">/100</span>`,`top:560px;text-align:center;direction:ltr;opacity:${p(t,.1,.4)}`);
  // timer ring
  const rk=eo((t-.6)/2.0);
  const cx=540,cy=1160,r=110;
  S('circle',{cx,cy,r,fill:'none',stroke:'#DCD4E0','stroke-width':16},g);
  S('circle',{cx,cy,r,fill:'none',stroke:C.ink,'stroke-width':16,'stroke-dasharray':`${2*Math.PI*r*rk*.3} 9999`,transform:`rotate(-90 ${cx} ${cy})`,'stroke-linecap':'round'},g);
  const tm=S('text',{x:cx,y:cy+16,fill:C.ink,'font-size':48,'text-anchor':'middle',class:'mlbl'},g);tm.textContent=`${Math.round(18*rk)}:00`;
  const tl=S('text',{x:cx,y:cy+180,fill:'#8A8292','font-size':30,'text-anchor':'middle',class:'lbl',opacity:rk},g);tl.textContent='دقيقة بس';
  head('امتحان رياضة.',.1,t,C.ink,'font-size:110px;top:240px');
  mono('PRACTICE TEST · MATH · 30 QUESTIONS',470,.3,t,C.ink);
  cap('يوتيوبر كوري جربها: <b>96 من 100</b> في <b>18 دقيقة</b>… والإجابة بتظهر في أقل من 30 ثانية',.6,4.6,t,C.ink,C.pur);
}
function g6(t){ // Korea acts: inspect glasses
  BG.setAttribute('fill',C.cream);
  const g=S('g',{});
  // conveyor of glasses moving left, magnifier fixed at center
  const items=[{smart:false},{smart:true},{smart:false},{smart:false},{smart:false}];
  const sp=210, off=t*sp;
  items.forEach((it,i)=>{
    const x=1000 + i*420 - off; if(x<-300||x>1400)return;
    const near=Math.abs(x-540)<160;
    const gg=glasses(x,1000,.42,'cream',{thin:!it.smart,led:it.smart&&near},g);
    if(x<540-60){ // already inspected
      const ok=!it.smart;
      const bg=S('g',{transform:`translate(${x},${860})`},g);
      S('circle',{r:34,fill:ok?'#2E9E6B':'#C8364F'},bg);
      const tx=S('text',{y:13,fill:'#fff','font-size':38,'text-anchor':'middle',class:'lbl'},bg);tx.textContent=ok?'✓':'✕';
    }
  });
  // magnifier
  const mk=p(t,.2,.5);
  S('circle',{cx:540,cy:1000,r:170,fill:'rgba(122,62,138,.05)',stroke:C.ink,'stroke-width':10,opacity:mk},g);
  S('line',{x1:660,y1:1120,x2:780,y2:1240,stroke:C.ink,'stroke-width':26,'stroke-linecap':'round',opacity:mk},g);
  // date badge
  const bk=back((t-.6)/.5);
  if(t>.6){const b=S('g',{transform:`translate(540,650) scale(${bk})`},g);
    S('rect',{x:-230,y:-60,width:460,height:120,rx:24,fill:C.pur},b);
    const bt=S('text',{x:0,y:18,fill:'#fff','font-size':48,'text-anchor':'middle',class:'lbl'},b);bt.textContent='19 نوفمبر';bt.setAttribute('direction','rtl');}
  head('كوريا<br><span class="hl">اتحركت.</span>',.1,t,C.ink,'font-size:120px;top:200px');
  cap('امتحان القبول للجامعات في كوريا يوم <b>19 نوفمبر</b>',.5,2.9,t,C.ink,C.pur);
  cap('والمراقبين هيفتشوا <b>نظارة كل طالب</b> قبل كل امتحان',3.0,6.0,t,C.ink,C.pur);
}
function g7(t){ // same glasses, two uses
  BG.setAttribute('fill',C.cream);
  const g=S('g',{});
  const cards=[{x:560,t:'تساعد.',a:'تترجم وتشرح',b:'وإنت بتتعلم',ok:true},{x:80,t:'تغشّ.',a:'في الامتحان',b:'وتضيّع تعبك',ok:false}];
  cards.forEach((c,i)=>{
    if(t<.3+i*.25)return; const k=back((t-.3-i*.25)/.6);
    const hi=(t>2.2)?(i===(t<3.5?0:1)):true;
    const cg=S('g',{transform:`translate(${c.x+220},1030) scale(${k}) translate(-220,-330)`,opacity:hi?1:.45},g);
    S('rect',{x:0,y:0,width:440,height:660,rx:24,fill:'#FBF9F7',stroke:hi&&t>2.2?C.ink:'#CFC8D4','stroke-width':hi&&t>2.2?4:2},cg);
    const tt=S('text',{x:220,y:110,fill:C.ink,'font-size':64,'text-anchor':'middle',class:'lbl',direction:'rtl'},cg);tt.textContent=c.t;tt.setAttribute('font-weight','900');
    glasses(220,260,.55,'cream',{},cg);
    if(c.ok){const b=S('g',{transform:'translate(220,400)'},cg);S('rect',{x:-150,y:-40,width:300,height:80,rx:40,fill:C.pl},b);const tx=S('text',{y:12,fill:C.pur,'font-size':30,'text-anchor':'middle',class:'mlbl'},b);tx.textContent='Hello → أهلاً';}
    else{paper(220,410,.22,'cream',{mark:true},cg);const x=S('text',{x:300,y:440,fill:'#C8364F','font-size':70,'text-anchor':'middle',class:'lbl'},cg);x.textContent='✕';}
    const ta=S('text',{x:220,y:550,fill:C.pur,'font-size':40,'text-anchor':'middle',class:'lbl'},cg);ta.textContent=c.a;
    const tb=S('text',{x:220,y:605,fill:'#8A8292','font-size':28,'text-anchor':'middle',class:'lbl'},cg);tb.textContent=c.b;
  });
  head('<span class="hl">نفس النظارة.</span>',.1,t,C.ink,'font-size:120px');
  cap('<b>إنت</b> اللي بتقرر تستخدمها في إيه',.8,4.8,t,C.ink,C.pur);
}
function g8(t){ // outro
  BG.setAttribute('fill',C.cream);
  const a=1-p(t,2.6,.3);
  if(a>0) D('txt h','الذكاء الاصطناعي<br><span class="hl">أداة.</span>',`top:720px;text-align:center;color:${C.ink};font-size:120px;line-height:1.35;opacity:${p(t,.1,.5)*a};transform:translateY(${(1-p(t,.1,.5))*50}px)`);
  if(t>2.7){
    const k=p(t,2.75,.5);
    D('txt h','ابعتها لصاحبك<br><span class="hl">اللي في ثانوية عامة</span>',`top:640px;text-align:center;color:${C.ink};font-size:88px;line-height:1.5;opacity:${k};transform:translateY(${(1-k)*40}px)`);
    const k2=p(t,3.4,.5);
    D('txt','تابع <span style="font-family:Mono;direction:ltr;unicode-bidi:isolate;color:#7A3E8A">@_megoo.me</span> لأكتر',`top:1050px;text-align:center;font-size:48px;font-weight:700;color:${C.ink};opacity:${k2}`);
    S('line',{x1:500,y1:1180,x2:580,y2:1180,stroke:C.pur,'stroke-width':4,opacity:k2});
  }
  mono('TECH NOTES / 002',1250,.6,t,'#8A8292');
}
