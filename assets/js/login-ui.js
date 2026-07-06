document.getElementById('register-password')?.addEventListener('input', function () {
  const value = this.value;
  const fill = document.getElementById('strengthFill');
  let strength = 0;
  if (value.length >= 6) strength++;
  if (value.length >= 10) strength++;
  if (/[A-Z]/.test(value)) strength++;
  if (/[0-9]/.test(value)) strength++;
  if (/[^A-Za-z0-9]/.test(value)) strength++;

  const colors = ['', '#ef4444', '#f97316', '#eab308', '#22c55e', '#16a34a'];
  const widths = ['0%', '20%', '40%', '60%', '80%', '100%'];
  fill.style.width = widths[strength];
  fill.style.background = colors[strength] || '';
});

document.querySelectorAll('.auth-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.auth-tab').forEach(item => item.classList.remove('active'));
    document.querySelectorAll('.auth-form').forEach(form => {
      form.classList.remove('active');
      form.style.display = 'none';
    });
    tab.classList.add('active');
    const target = document.getElementById(tab.dataset.target);
    target.classList.add('active');
    target.style.display = 'flex';
    document.getElementById('login-message').textContent = '';
    document.getElementById('register-message').textContent = '';
  });
});

document.querySelectorAll('.toggle-password').forEach(btn => {
  btn.addEventListener('click', () => {
    const wrapper = btn.closest('.password-wrapper');
    const input = wrapper.querySelector('input');
    const mostrar = input.type === 'password';
    input.type = mostrar ? 'text' : 'password';
    btn.textContent = mostrar ? '👁' : '👁';
    btn.setAttribute('aria-label', mostrar ? 'Ocultar contraseña' : 'Mostrar contraseña');
    input.focus();
  });
});