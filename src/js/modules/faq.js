export function initFaq() {
  document.querySelectorAll('.faq details').forEach((item) => {
    item.addEventListener('toggle', () => {
      if (!item.open) return;
      document.querySelectorAll('.faq details[open]').forEach((other) => {
        if (other !== item) other.open = false;
      });
    });
  });
}
