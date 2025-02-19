const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const pool = require('./db'); // Импортируйте подключение к базе данных
const userRoutes = require('./routes/userRoutes'); // Импортируйте ваши маршруты

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(bodyParser.json());

// Использование маршрутов
app.use('/api/users', userRoutes);

// Простой маршрут
app.get('/', (req, res) => {
    res.send('API работает!');
});

app.listen(PORT, () => {
    console.log("Сервер запущен на http://localhost:3000");
});

