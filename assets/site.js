window.vsiFigError=function(img){if(img.dataset.fallback){img.src=img.dataset.fallback;img.dataset.fallback='';return;}var f=img.closest('figure');if(f)f.classList.add('is-empty');img.remove();};
(function(){
  var d=document; d.documentElement.classList.add('js');
  var btn=d.querySelector('.menu'), nav=d.getElementById('nav');
  if(btn&&nav){
    btn.addEventListener('click',function(){var o=btn.getAttribute('aria-expanded')!=='true';btn.setAttribute('aria-expanded',String(o));nav.classList.toggle('open',o);});
    nav.addEventListener('click',function(ev){if(ev.target.closest('a')){nav.classList.remove('open');btn.setAttribute('aria-expanded','false');}});
  }
  // publications: category chips + search
  function initPubs(root){
    var q=root.querySelector('#pub-q'); if(!q&&!root.querySelector('.chip')) return;
    var chips=[].slice.call(root.querySelectorAll('.chip')), groups=[].slice.call(root.querySelectorAll('.pub-group'));
    var empty=root.querySelector('#pub-empty');
    var cat='';
    function apply(){
      var s=q?q.value.trim().toLowerCase():'', n=0;
      groups.forEach(function(g){
        var inCat=!cat||g.id===cat, k=0;
        [].forEach.call(g.querySelectorAll('.pub'),function(it){var ok=inCat&&(!s||it.dataset.search.indexOf(s)>-1);it.hidden=!ok;if(ok)k++;});
        g.hidden=k===0; n+=k;
      });
      empty.hidden=n>0;
    }
    chips.forEach(function(c){c.addEventListener('click',function(){cat=c.dataset.cat;chips.forEach(function(x){x.setAttribute('aria-pressed',String(x===c));});apply();});});
    if(q) q.addEventListener('input',apply); apply();
  }
  initPubs(d);
  // single-file preview router
  if(window.VSI_PREVIEW){
    var views=[].slice.call(d.querySelectorAll('.view'));
    var ids={}; views.forEach(function(v){ids[v.dataset.view]=v;});
    function show(hash){
      var h=(hash||'').replace('#','')||'top', target=d.getElementById(h), view=null;
      if(ids[h]) view=ids[h]; else if(h==='top') view=ids.index; else if(target) view=target.closest('.view');
      if(!view) return false;
      views.forEach(function(v){v.hidden=v!==view;});
      var key=view.dataset.view;
      d.querySelectorAll('.nav a').forEach(function(a){if(a.dataset.nav===key)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');});
      if(target&&!ids[h]&&h!=='top') target.scrollIntoView(); else window.scrollTo(0,0);
      return true;
    }
    d.addEventListener('click',function(ev){var a=ev.target.closest('a[href^="#"]');if(!a)return;var h=a.getAttribute('href');if(h==='#main')return;
      if(show(h)){ev.preventDefault();try{history.replaceState(null,'',h);}catch(e){}}});
    show(location.hash);
  }
})();
// touch screens: portraits turn from black and white to color while they sit in the middle of the screen; a tap also toggles color
(function(){
  var d=document, mq=window.matchMedia&&window.matchMedia('(hover: none), (pointer: coarse)');
  if(!mq||!mq.matches) return;
  var ps=[].slice.call(d.querySelectorAll('.portrait'));
  if(!ps.length) return;
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(e){e.target.classList.toggle('on',e.isIntersecting);});},
      {rootMargin:'-30% 0px -30% 0px',threshold:0});
    ps.forEach(function(p){io.observe(p);});
  } else { ps.forEach(function(p){p.classList.add('on');}); }
  ps.forEach(function(p){p.addEventListener('click',function(){p.classList.toggle('on');});});
})();
