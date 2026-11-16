const TX=__TX__, LANGS=__LANGS__;
let LANG="zh";try{LANG=localStorage.getItem("ui-lang")||"zh";}catch(e){}
if(!TX.navHome[LANG])LANG="zh";
function tr(k,v){let s=(TX[k]||{})[LANG];if(s===undefined)s=(TX[k]||{}).zh||"";if(v)for(const x in v)s=String(s).split("{"+x+"}").join(v[x]);return s;}
function apply(){
  document.documentElement.lang=LANG==="zh"?"zh-CN":LANG;
  document.querySelectorAll("[data-i]").forEach(el=>{const v=el.dataset.v?JSON.parse(el.dataset.v):null;el.textContent=tr(el.dataset.i,v);});
  document.querySelectorAll("[data-tr]").forEach(el=>{el.textContent=LANG==="zh"?"":tr(el.dataset.tr);});
  document.querySelectorAll("select.lang").forEach(s=>s.value=LANG);
  progress();
}
function setLang(l){LANG=l;try{localStorage.setItem("ui-lang",l);}catch(e){}apply();}
// 进度：读取课后练习页保存在这台设备上的数据
function prog(id){let s=null;try{s=JSON.parse(localStorage.getItem("hsk-practice-"+id));}catch(e){}
  if(!s||!s.w)return{m:0,wr:0,stars:0,days:0};let m=0;for(const k in s.w)if(s.w[k].st>=3)m++;
  return{m:m,wr:Object.keys(s.written||{}).length,stars:s.stars||0,days:s.days||0};}
function last(){try{return JSON.parse(localStorage.getItem("last-lesson"));}catch(e){return null;}}
function progress(){
  const R=document.body.dataset.root||"";
  document.querySelectorAll("[data-prog]").forEach(el=>{const p=prog(el.dataset.prog),n=+el.dataset.n;
    el.className="chip "+(p.m>=n?"done":p.m>0?"doing":"");
    el.textContent=p.m>=n?tr("stDone",{a:p.m,b:n}):p.m>0?tr("stDoing",{a:p.m,b:n}):tr("stTodo");});
  document.querySelectorAll("[data-sum]").forEach(el=>{const ids=el.dataset.sum.split(","),tot=+el.dataset.n,kind=el.dataset.kind;
    let a=0;ids.forEach(id=>{const p=prog(id);a+=kind==="w"?p.wr:p.m;});
    el.querySelector("b").textContent=a+" / "+tot;
    const f=el.parentNode.querySelector("[data-fill='"+el.dataset.key+"']");if(f)f.style.width=Math.round(a/Math.max(tot,1)*100)+"%";});
  const c=document.getElementById("cont");
  if(c){const L=last();
    if(L&&L.id){const p=prog(L.id);
      c.querySelector("[data-c=tag]").textContent=L.level==="start"?tr("placementName"):tr("lessonInLevel",{lv:L.lv,n:L.no});
      c.querySelector("[data-c=title]").textContent=L.title;
      const n=+(c.dataset[String(L.id).toLowerCase()]||20);
      c.querySelector("[data-c=m]").textContent=p.m+" / "+n;
      c.querySelector("[data-c=fill]").style.width=Math.round(p.m/n*100)+"%";
      c.querySelector("[data-c=days]").textContent=p.days;c.querySelector("[data-c=stars]").textContent=p.stars;
      c.querySelector("[data-c=go]").href=R+L.practice;
      c.querySelector("[data-c=on]").style.display="flex";c.querySelector("[data-c=off]").style.display="none";}}
  const bp=document.getElementById("bnav-practice");if(bp){const L=last();if(L&&L.practice)bp.href=R+L.practice;}
}
let zh=null;function pv(){try{const v=speechSynthesis.getVoices();zh=v.find(x=>/^zh(-|_)?CN/i.test(x.lang))||v.find(x=>/^zh/i.test(x.lang))||null;}catch(e){}}
try{pv();speechSynthesis.onvoiceschanged=pv;}catch(e){}
function say(t){if(!zh){toast(tr("noVoice"));return;}try{speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(t);u.voice=zh;u.lang=zh.lang;u.rate=0.8;speechSynthesis.speak(u);}catch(e){}}
function toast(m){let d=document.getElementById("msg");if(!d){d=document.createElement("div");d.id="msg";d.setAttribute("role","status");d.style.cssText="position:fixed;left:50%;bottom:90px;transform:translateX(-50%);background:#14304A;color:#fff;padding:10px 16px;border-radius:12px;z-index:30";document.body.appendChild(d);}d.textContent=m;d.style.display="block";setTimeout(()=>d.style.display="none",2500);}
document.addEventListener("click",ev=>{
  const c=ev.target.closest(".vc");if(c){c.classList.toggle("open");say(c.dataset.w);return;}
  const n=ev.target.closest(".nw");if(n){n.classList.toggle("show");return;}
  const p=ev.target.closest("[data-say]");if(p){say(p.dataset.say);return;}
  const t=ev.target.closest("[data-toggle]");if(t){document.getElementById(t.dataset.box).classList.toggle(t.dataset.toggle);t.classList.toggle("on");}
});
document.addEventListener("DOMContentLoaded",()=>{
  const L=document.body.dataset.lesson;if(L){try{localStorage.setItem("last-lesson",L);}catch(e){}}
  apply();
});
