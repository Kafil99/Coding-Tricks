const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => document.querySelectorAll(selector);

const hourEl = $('.hour');
const dotEl = $('.dot');
const minEl = $('.min');
const secEl = $('.sec');
const meridianEl = $('.meridian');
const weekEls = $$('.week div');

let showDot = true;

const updateClock = () => {
    const now = new Date();

    const utcTime = now.getTime() + now.getTimezoneOffset() * 60000; 
    const pstTime = new Date(utcTime + 5 * 60 * 60000); 

    let hours = pstTime.getHours();
    const minutes = String(pstTime.getMinutes()).padStart(2, '0');
    const seconds = String(pstTime.getSeconds()).padStart(2, '0');
    const dayIndex = pstTime.getDay(); 

    const meridian = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12 || 12;

    hourEl.textContent = String(hours).padStart(2, '0');
    minEl.textContent = minutes;
    secEl.textContent = seconds;
    meridianEl.textContent = meridian;

    showDot = !showDot;
    dotEl.style.opacity = showDot ? '1' : '0';

    weekEls.forEach((el, index) => {
        el.classList.toggle('active', index === dayIndex);
        el.setAttribute('aria-current', index === dayIndex ? 'true' : 'false');
    });
};

const syncClock = () => {
    const now = new Date();
    const msUntilNextSecond = 1000 - now.getMilliseconds();
    setTimeout(() => {
        updateClock();
        setInterval(updateClock, 1000);
    }, msUntilNextSecond);
};

syncClock();
