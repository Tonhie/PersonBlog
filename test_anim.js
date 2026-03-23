function animateBtnText(btn, newText) {
    if (!btn || btn.textContent.includes(newText)) return;
    let span = btn.querySelector('span.btn-text-inner');
    if (!span) {
        btn.innerHTML = `<span class="btn-text-inner" style="display:inline-block; transition: all 0.2s cubic-bezier(0.25, 1, 0.5, 1);">${btn.textContent}</span>`;
        span = btn.querySelector('span.btn-text-inner');
    }
    span.style.opacity = '0';
    span.style.transform = 'translateY(-5px)';
    setTimeout(() => {
        span.textContent = newText;
        span.style.transform = 'translateY(5px)';
        requestAnimationFrame(() => {
            span.style.transform = 'translateY(0)';
            span.style.opacity = '1';
        });
    }, 200);
}
