const menuBtn = document.querySelector('.menu-btn');
const navLinks = document.querySelector('.nav-links');
if (menuBtn && navLinks) {
  menuBtn.addEventListener('click', () => navLinks.classList.toggle('open'));
}
document.querySelectorAll('.route-booking').forEach(form => {
  form.addEventListener('submit', event => {
    event.preventDefault();
    const data = new FormData(form);
    const from = data.get('from');
    const to = data.get('to');
    const date = data.get('date') || 'Not selected';
    const passengers = data.get('passengers');
    const message = [
      'Hello Trinity Bus Express,',
      `I want to book a bus from ${from} to ${to}.`,
      `Travel date: ${date}`,
      `Passengers: ${passengers}`,
      'Please confirm the latest fare, departure time, boarding point and seat availability.'
    ].join('\n');
    const phone = form.dataset.whatsapp || '254754932823';
    window.open(`https://wa.me/${phone}?text=${encodeURIComponent(message)}`, '_blank', 'noopener');
  });
});