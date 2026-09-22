import { SITE_CONFIG } from '../../config/site.js';

function whatsappUrl(message = SITE_CONFIG.contact.whatsappMessage) {
  return `https://wa.me/${SITE_CONFIG.contact.whatsapp}?text=${encodeURIComponent(message)}`;
}

export function initContact() {
  document.querySelectorAll('[data-contact="whatsapp"]').forEach((link) => {
    link.href = whatsappUrl();
  });
  document.querySelectorAll('[data-contact="whatsapp-label"]').forEach((element) => {
    element.textContent = SITE_CONFIG.contact.whatsappLabel;
  });
  document.querySelectorAll('[data-contact="email"]').forEach((link) => {
    link.href = `mailto:${SITE_CONFIG.contact.email}`;
  });
  document.querySelectorAll('[data-contact="email-label"]').forEach((element) => {
    element.textContent = SITE_CONFIG.contact.email;
  });
  document.querySelectorAll('[data-contact="instagram"]').forEach((link) => {
    link.href = SITE_CONFIG.contact.instagramUrl;
  });
  document.querySelectorAll('[data-contact="instagram-label"]').forEach((element) => {
    element.textContent = `@${SITE_CONFIG.contact.instagram}`;
  });
  document.querySelectorAll('[data-contact="maps"]').forEach((link) => {
    link.href = SITE_CONFIG.contact.mapsUrl;
  });

  const year = document.querySelector('[data-current-year]');
  if (year) year.textContent = String(new Date().getFullYear());

  const form = document.querySelector('[data-contact-form]');
  const status = document.querySelector('[data-form-status]');
  const submit = form?.querySelector('button[type="submit"]');
  if (!form || !status || !submit) return;

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!form.reportValidity()) return;

    const data = Object.fromEntries(new FormData(form).entries());
    if (data.botcheck) return;

    if (!SITE_CONFIG.form.accessKey) {
      const message = `Olá! Meu nome é ${data.nome}. Gostaria de conversar sobre ${data.interesse}. Telefone: ${data.telefone}.`;
      status.textContent = 'Abrindo o WhatsApp para concluir seu contato…';
      window.open(whatsappUrl(message), '_blank', 'noopener,noreferrer');
      return;
    }

    submit.disabled = true;
    status.textContent = 'Enviando…';
    try {
      const response = await fetch('https://api.web3forms.com/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({
          ...data,
          access_key: SITE_CONFIG.form.accessKey,
          subject: SITE_CONFIG.form.subject,
          from_name: SITE_CONFIG.brand.name
        })
      });
      const result = await response.json();
      if (!result.success) throw new Error(result.message || 'Falha no envio');
      form.reset();
      status.textContent = 'Mensagem recebida. Entraremos em contato em breve.';
      status.dataset.state = 'success';
    } catch {
      status.textContent = 'Não foi possível enviar agora. Use o WhatsApp ou tente novamente.';
      status.dataset.state = 'error';
    } finally {
      submit.disabled = false;
    }
  });
}
