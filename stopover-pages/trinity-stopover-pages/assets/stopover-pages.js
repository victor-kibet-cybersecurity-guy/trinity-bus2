const menuBtn=document.querySelector('.menu-btn');
const navLinks=document.querySelector('.nav-links');
if(menuBtn&&navLinks){menuBtn.addEventListener('click',()=>navLinks.classList.toggle('open'))}
document.querySelectorAll('.route-booking').forEach(form=>{
  form.addEventListener('submit',e=>{
    e.preventDefault();
    const d=new FormData(form);
    const message=[
      'Hello Trinity Bus Express,',
      `I want to travel from ${d.get('from')} to ${d.get('to')}.`,
      `Travel date: ${d.get('date')||'Not selected'}`,
      `Passengers: ${d.get('passengers')}`,
      'Please confirm the current fare, schedule, boarding point and seat availability.'
    ].join('\n');
    window.open(`https://wa.me/254754932823?text=${encodeURIComponent(message)}`,'_blank','noopener');
  })
})