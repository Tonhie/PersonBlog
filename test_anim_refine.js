function animateBtnText(btn, newText) {
    if (!btn) return;
    const cleanText = newText.replace(/</g, "&lt;").replace(/>/g, "&gt;");
    if (btn.textContent.trim() === newText.trim()) return;
    
    let span = btn.querySelector('span.btn-text-inner');
    if (!span) {
        btn.innerHTML = `<span class="btn-text-inner" style="display:inline-block; transition: opacity 0.2s ease, transform 0.2s cubic-bezier(0.25, 1, 0.5, 1);">${btn.innerHTML}</span>`;
        span = btn.querySelector('span.btn-text-inner');
    }
    
    // Enable transition and animate out
    span.style.transition = 'opacity 0.15s ease, transform 0.15s cubic-bezier(0.25, 1, 0.5, 1)';
    span.style.opacity = '0';
    span.style.transform = 'translateY(-5px)';
    
    setTimeout(() => {
        // Disable transition to jump to bottom
        span.style.transition = 'none';
        span.innerHTML = cleanText;
        span.style.transform = 'translateY(5px)';
        
        // Force reflow
        void span.offsetHeight;
        
        // Re-enable transition and animate in
        span.style.transition = 'opacity 0.2s ease, transform 0.2s cubic-bezier(0.25, 1, 0.5, 1)';
        span.style.transform = 'translateY(0)';
        span.style.opacity = '1';
    }, 150);
}
