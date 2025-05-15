document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const errorElement = document.getElementById('error-message');

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            errorElement.textContent = '';

            try {
                const formData = new URLSearchParams();
                formData.append('username', loginForm.username.value);
                formData.append('password', loginForm.password.value);

                const response = await fetch("/api/token", {
                    method: "POST",
                    body: formData,
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    credentials: 'include'
                });

                if (response.redirected) {
                    window.location.href = response.url;
                    return;
                }

                const data = await response.json();
                if (data.access_token) {
                    window.location.href = "/api/dashboard";
                }
            } catch (error) {
                errorElement.textContent = 'Ошибка авторизации. Проверьте логин и пароль';
                console.error('Login error:', error);
            }
        });
    }
});