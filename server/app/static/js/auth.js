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
                if (data.redirect_url) {
                    window.location.href = data.redirect_url;
                }
            } catch (error) {
                errorElement.textContent = 'Ошибка соединения с сервером';
                console.error('Login error:', error);
            }
        });
        // Обработчик выхода
        document.getElementById('logout-btn').addEventListener('click', async () => {
            try {
                const response = await fetch('/api/logout', {
                    method: 'POST',
                    credentials: 'include',
                });

                if (response.ok) {
                    localStorage.removeItem('access_token');
                    window.location.href = '/login';
                }
            } catch (error) {
                console.error('Ошибка при выходе:', error);
            }
        });
        document.getElementById('session-form').addEventListener('submit', async (e) => {
            e.preventDefault();

            const date_time = document.getElementById('date_time').value;
            const duration = parseInt(durationSelect.value);
            const price = parseFloat(priceInput.value);

            const now = new Date();
            const selectedDate = new Date(date_time);
            if (selectedDate <= now) {
                alert("Нельзя выбрать дату и время в прошлом");
                return;
            }

            try {
                const response = await fetch('/api/sessions/', {
                    method: 'POST',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ date_time, duration, price, status: "scheduled" })
                });

                if (response.ok) {
                    const newSession = await response.json();
                    alert('Сессия успешно добавлена');

                    // Добавляем новую сессию в список без перезагрузки
                    const sessionsList = document.querySelector('.list-group');
                    if (sessionsList) {
                        const li = document.createElement('li');
                        li.className = 'list-group-item';
                        li.textContent = `${new Date(newSession.date_time).toLocaleString()} — ${newSession.status} — ${newSession.price} ₽`;
                        sessionsList.appendChild(li);
                    }

                    // Очистить форму
                    document.getElementById('session-form').reset();
                    // Инициализировать цену по умолчанию
                    priceInput.value = priceByDuration[durationSelect.value] || '';
                } else {
                    const data = await response.json();
                    alert('Ошибка при добавлении сессии: ' + data.detail);
                }
            } catch (error) {
                console.error('Ошибка запроса:', error);
                alert('Ошибка сети');
            }
        });
    }
});