document.addEventListener("DOMContentLoaded",()=>{
 document.querySelectorAll("[data-current-year]").forEach(e=>e.textContent=new Date().getFullYear());
 const nav=document.querySelector(".main-nav"),toggle=document.querySelector(".nav-toggle");
 if(nav&&toggle){
  const links=[...nav.querySelectorAll(":scope > a")];
  const normalizedPath=value=>value.endsWith("/")?value+"index.html":value;
  const pathname=normalizedPath(location.pathname);
  links.forEach(link=>{try{const target=normalizedPath(new URL(link.href,location.href).pathname);if(target===pathname)link.classList.add("active")}catch{}});
  if(!nav.querySelector(".mobile-menu-cta")){
   const segments=location.pathname.split("/").filter(Boolean);
   const nested=segments.some(segment=>["destinations","routes","blog","countries","kenya","uganda","rwanda","south-sudan","drc","burundi"].includes(segment));
   const prefix=nested?"../":"./";
   const footer=document.createElement("div");footer.className="mobile-menu-footer";
   footer.innerHTML=`<a class="mobile-menu-cta" href="${prefix}booking.html">Book Seat</a><a class="mobile-menu-whatsapp" href="https://wa.me/254754932823" target="_blank" rel="noopener noreferrer">WhatsApp Support</a>`;
   nav.appendChild(footer);
  }
  const close=()=>{nav.classList.remove("open");toggle.classList.remove("is-open");toggle.textContent="\u2630";toggle.setAttribute("aria-expanded","false");toggle.setAttribute("aria-label","Open navigation");document.documentElement.classList.remove("menu-open")};
  const open=()=>{nav.classList.add("open");toggle.classList.add("is-open");toggle.textContent="\u00d7";toggle.setAttribute("aria-expanded","true");toggle.setAttribute("aria-label","Close navigation");document.documentElement.classList.add("menu-open");nav.querySelector("a")?.focus()};
  toggle.addEventListener("click",()=>nav.classList.contains("open")?close():open());
  nav.querySelectorAll("a").forEach(a=>a.addEventListener("click",close));
  addEventListener("keydown",e=>{if(e.key==="Escape")close()});
  addEventListener("resize",()=>{if(innerWidth>768)close()},{passive:true});
 }
 const progress=document.getElementById("scrollProgress");
 const onScroll=()=>{if(progress){const h=document.documentElement.scrollHeight-innerHeight;progress.style.width=(scrollY/(h||1)*100)+"%"}};
 addEventListener("scroll",onScroll,{passive:true});
 if("IntersectionObserver" in window){const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting)e.target.classList.add("visible")}),{threshold:.12});document.querySelectorAll("[data-reveal]").forEach(e=>io.observe(e))}
 const network=()=>{document.querySelector(".offline-banner")?.remove();if(!navigator.onLine){const b=document.createElement("div");b.className="offline-banner";b.textContent="You are offline. Saved pages remain available.";document.body.appendChild(b)}};addEventListener("online",network);addEventListener("offline",network);network();
 if("serviceWorker" in navigator)navigator.serviceWorker.register("/trinity-bus2/sw.js").catch(()=>{});
 document.querySelectorAll("[data-counter]").forEach(el=>{const end=+el.dataset.counter;let n=0;const tick=()=>{n+=Math.ceil(end/50);el.textContent=n>=end?end:n;if(n<end)requestAnimationFrame(tick)};tick()});
});
