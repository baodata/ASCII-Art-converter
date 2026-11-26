// Interactive cursor glow following mouse movement
document.addEventListener('DOMContentLoaded', () => {
  const glow = document.querySelector('.mouse-glow');
  if (!glow) return;

  let mouseX = -1000;
  let mouseY = -1000;
  let currentX = -1000;
  let currentY = -1000;

  window.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
  });

  window.addEventListener('mouseout', () => {
    mouseX = -1000;
    mouseY = -1000;
  });

  function renderGlow() {
    currentX += (mouseX - currentX) * 0.15;
    currentY += (mouseY - currentY) * 0.15;
    glow.style.left = `${currentX}px`;
    glow.style.top = `${currentY}px`;
    requestAnimationFrame(renderGlow);
  }

  requestAnimationFrame(renderGlow);
});
