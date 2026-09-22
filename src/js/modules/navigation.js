export function initNavigation(lenis) {
  const header = document.querySelector('[data-header]');
  const button = document.querySelector('[data-menu-button]');
  const menu = document.querySelector('[data-menu]');

  const close = () => {
    menu?.removeAttribute('data-open');
    button?.setAttribute('aria-expanded', 'false');
  };

  const updateHeader = () => header?.classList.toggle('is-scrolled', window.scrollY > 16);
  window.addEventListener('scroll', updateHeader, { passive: true });
  updateHeader();

  button?.addEventListener('click', () => {
    const opening = menu?.getAttribute('data-open') !== 'true';
    menu?.toggleAttribute('data-open', opening);
    button.setAttribute('aria-expanded', String(opening));
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') close();
  });

  document.querySelectorAll('a[href^="#"]').forEach((link) => {
    link.addEventListener('click', (event) => {
      const target = document.querySelector(link.getAttribute('href'));
      if (!target) return;
      event.preventDefault();
      close();
      if (lenis) lenis.scrollTo(target, { offset: -72, duration: 1 });
      else target.scrollIntoView({ behavior: 'smooth' });
    });
  });
}
