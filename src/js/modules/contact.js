import { SITE_CONFIG } from '../../config/site.js';
const whatsappUrl = (message = SITE_CONFIG.contact.whatsappMessage) => `https://wa.me/${SITE_CONFIG.contact.whatsapp}?text=${encodeURIComponent(message)}`;

export function initContact() {
  document.querySelectorAll('[data-contact="whatsapp"]').forEach((link) => { link.href = whatsappUrl(); link.target = '_blank'; link.rel = 'noopener noreferrer'; });
  document.querySelectorAll('[data-contact="whatsapp-label"]').forEach((el) => { el.textContent = SITE_CONFIG.contact.whatsappLabel; });
  document.querySelectorAll('[data-contact="instagram"]').forEach((link) => { link.href = SITE_CONFIG.contact.instagramUrl; link.target = '_blank'; link.rel = 'noopener noreferrer'; });
  document.querySelectorAll('[data-contact="instagram-label"]').forEach((el) => { el.textContent = `@${SITE_CONFIG.contact.instagram}`; });
  document.querySelectorAll('[data-contact="maps"]').forEach((link) => { link.href = SITE_CONFIG.contact.mapsUrl; link.target = '_blank'; link.rel = 'noopener noreferrer'; });
  document.querySelectorAll('[data-current-year]').forEach((el) => { el.textContent = String(new Date().getFullYear()); });
  const hero = document.querySelector('.hero'); const floating = document.querySelector('[data-whatsapp-float]');
  if (hero && floating) new IntersectionObserver(([entry]) => floating.classList.toggle('is-visible', !entry.isIntersecting), { threshold: 0.05 }).observe(hero);
  const form = document.querySelector('[data-contact-form]'); const status = form?.querySelector('[data-form-status]');
  if (!form || !status) return;
  form.addEventListener('submit', (event) => { event.preventDefault(); if (!form.reportValidity()) return; const data = new FormData(form); const name = String(data.get('nome') || '').trim().replace(/[\r\n]+/g, ' ').slice(0, 80); const allowed = new Set(['primeira consulta', 'retorno', 'informações']); const interest = allowed.has(data.get('interesse')) ? data.get('interesse') : 'informações'; const message = `Olá! Conheci o site do Dr. Fabiano Carvalho. Meu nome é ${name} e gostaria de ${interest}.`; status.textContent = 'O WhatsApp será aberto para você revisar e enviar a mensagem.'; status.dataset.state = 'success'; window.open(whatsappUrl(message), '_blank', 'noopener,noreferrer'); });
}
