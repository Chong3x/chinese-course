
let zh=null;function pv(){try{const v=speechSynthesis.getVoices();zh=v.find(x=>/^zh(-|_)?CN/i.test(x.lang))||v.find(x=>/^zh/i.test(x.lang))||null;}catch(e){}}
try{pv();speechSynthesis.onvoiceschanged=pv;}catch(e){}
function say(t){if(!zh){alertBox('这台设备没有中文语音。');return;}try{speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(t);u.voice=zh;u.lang=zh.lang;u.rate=0.8;speechSynthesis.speak(u);}catch(e){}}
function alertBox(m){let d=document.getElementById('msg');if(!d){d=document.createElement('div');d.id='msg';d.style.cssText='position:fixed;left:50%;bottom:20px;transform:translateX(-50%);background:#14304A;color:#fff;padding:10px 16px;border-radius:12px;z-index:9';document.body.appendChild(d);}d.textContent=m;d.style.display='block';setTimeout(()=>d.style.display='none',2500);}
document.addEventListener('click',ev=>{
  const c=ev.target.closest('.vc');if(c){c.classList.toggle('open');say(c.dataset.w);return;}
  const n=ev.target.closest('.nw');if(n){n.classList.toggle('show');return;}
  const p=ev.target.closest('[data-say]');if(p){say(p.dataset.say);return;}
  const t=ev.target.closest('[data-toggle]');if(t){const cls=t.dataset.toggle;const box=document.getElementById(t.dataset.box);box.classList.toggle(cls);t.classList.toggle('on');}
});
