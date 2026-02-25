// Progressive enhancement: make "Pick" buttons work via fetch for snappier UX
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.pick-form').forEach(form => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const btn = form.querySelector('button');
      try {
        const resp = await fetch(form.action, {
          method: 'POST',
          headers: { 'X-Requested-With': 'XMLHttpRequest' },
        });
        const data = await resp.json();
        if (data.ok) {
          btn.textContent = 'Picked';
          btn.classList.add('btn-picked');
          btn.disabled = true;
          // Update badge
          document.querySelectorAll('.badge').forEach(b => {
            b.textContent = data.count;
          });
          // If no badge yet, add one
          if (!document.querySelector('.badge') && data.count > 0) {
            document.querySelectorAll('.topbar-picks').forEach(el => {
              const badge = document.createElement('span');
              badge.className = 'badge';
              badge.textContent = data.count;
              el.appendChild(badge);
            });
          }
        }
      } catch {
        form.submit(); // fallback to normal form submission
      }
    });
  });
});
