import '../styles/main.css';
import { initAnimations } from './modules/animations.js';
import { initNavigation } from './modules/navigation.js';
import { initCarousel } from './modules/carousel.js';
import { initContact } from './modules/contact.js';
import { initFaq } from './modules/faq.js';

function bootstrap() {
  const lenis = initAnimations();
  initNavigation(lenis);
  initCarousel();
  initContact();
  initFaq();
}

if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', bootstrap);
else bootstrap();
