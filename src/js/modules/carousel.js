import Swiper from 'swiper';
import { A11y, Keyboard, Navigation, Pagination } from 'swiper/modules';
import 'swiper/css'; import 'swiper/css/pagination';
export function initCarousel() { const root = document.querySelector('[data-office-carousel]'); if (!root) return; new Swiper(root, { modules: [A11y, Keyboard, Navigation, Pagination], slidesPerView: 1.08, spaceBetween: 16, keyboard: { enabled: true, onlyInViewport: true }, navigation: { prevEl: '[data-carousel-prev]', nextEl: '[data-carousel-next]' }, pagination: { el: '[data-carousel-pagination]', clickable: true }, breakpoints: { 700: { slidesPerView: 2.1, spaceBetween: 24 }, 1100: { slidesPerView: 2.55, spaceBetween: 30 } } }); }
