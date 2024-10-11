document.addEventListener('DOMContentLoaded', function () {
    const chatApp = document.getElementById('chat-app');
    const chatMessages = document.getElementById('chat-messages');
    const messageInput = document.getElementById('chat-message-input');
    const messageSubmit = document.getElementById('chat-message-submit');
    const autoScrollCheckbox = document.getElementById('auto-scroll-checkbox');
    const ordersList = document.getElementById('orders');
    const ordersContainer = document.getElementById('orders-list');
    const ordersLoading = document.getElementById('orders-loading');

    let ws = null;

    function setupWebSocket(userId) {
        if (ws) {
            ws.close(); // Закрыть существующее соединение перед открытием нового
        }
    }

    function openChat(roomId, userId, userName) {
        closeWebSocket(); // Закрываем предыдущее соединение


        const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
        const wsUrl = `${protocol}${window.location.host}/ws/chat/${userId}/`;
        ws = new WebSocket(wsUrl);

        ws.onopen = () => console.log(`WebSocket connection established for user ${userId}`);
        ws.onerror = error => console.error('WebSocket error:', error);
        ws.onmessage = event => displayMessage(JSON.parse(event.data));
        ws.onclose = () => console.log('WebSocket connection closed');
    }

    function openChat(userId) {
        if (!userId || userId === "null") {
            console.error('Invalid user ID:', userId);
            return;
        }

        // Очищаем старые сообщения и заказы
        chatMessages.innerHTML = '';
        ordersList.innerHTML = '';
        document.getElementById('chat-room-title').textContent = `Административный Чат ${roomId}`;
        chatApp.style.display = 'block';
        ordersContainer.style.display = 'block';

        // Загружаем сообщения чата и заказы
        loadMessages(roomId);
        loadOrders(userId);
    }

    function loadMessages(roomId) {
        console.log(`Loading messages for room ${roomId}`);
        const spinner = document.getElementById('loading-spinner');
        spinner.style.display = 'block';

        fetch(`/support/api/messages/${roomId}/`)
            .then(response => response.json())
            .then(data => {
                chatMessages.innerHTML = ''; // Очищаем перед загрузкой

                if (data.messages && Array.isArray(data.messages)) {
                    data.messages.forEach(message => {
                        displayMessage({
                            sender_id: message.sender,
                            sender_username: message.sender_phone,
                            message: message.message,
                            timestamp: message.timestamp
                        });
                    });
                } else {
                    console.error('Data does not contain expected "messages" array:', data);
                }
            })
            .catch(error => console.error('Error loading messages:', error))
            .finally(() => {
                spinner.style.display = 'none';
                // Всегда прокручиваем вниз после загрузки сообщений
                scrollToBottom(true);
            });

    }

    function displayMessage(data) {
        console.log(data,'new message')
        const messageElement = document.createElement('li');
        const userId = document.body.getAttribute('data-user-id');

        // Определяем стиль сообщения
        const messageClass = data.sender_id == userId ? 'user-message' : 'other-message';
        messageElement.classList.add('list-group-item', messageClass);

        // Форматируем сообщение для отображения
        messageElement.innerHTML = `<strong>${data.sender_username}:</strong> ${data.message} <br> <small>${new Date(data.timestamp).toLocaleString()}</small>`;

        // Добавляем сообщение в чат
        chatMessages.appendChild(messageElement);

        // Прокручиваем вниз, если включена автопрокрутка
        if (autoScrollCheckbox.checked) {
            scrollToBottom();
        }
    }

    function scrollToBottom(force = true) {
        // Прокручиваем вниз всегда при force=true (например, после загрузки сообщений)
        // Или если автопрокрутка включена
        if (force || autoScrollCheckbox.checked) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

    }
function loadOrders(userId) {
    console.log(`Загрузка заказов для пользователя с ID: ${userId}`); // Отладка

    ordersLoading.style.display = 'block'; // Показываем спиннер загрузки

    fetch(`/support/api/orders/${userId}/`)
        .then(response => response.json())
        .then(data => {
            console.log('Данные заказа:', data); // Отладка данных заказа

            ordersLoading.style.display = 'none'; // Скрываем спиннер

            // Проверяем, что заказы были получены внутри объекта data.orders
            if (data.orders && Array.isArray(data.orders)) {
                const accordionContainer = document.createElement('div');
                accordionContainer.classList.add('accordion', 'accordion-flush', 'overflow-y-scroll');
                accordionContainer.id = 'accordionFlushOrders';

                // Создаем аккордеон для каждого заказа
                data.orders.forEach((order, index) => {
                    console.log(`Создание аккордеона для заказа №${order.id}`); // Отладка

                    const orderItem = document.createElement('div');
                    orderItem.classList.add('accordion-item');

                    // Заголовок аккордеона
                    const header = document.createElement('h2');
                    header.classList.add('accordion-header');
                    const button = document.createElement('button');
                    button.classList.add('accordion-button', 'collapsed');
                    button.setAttribute('type', 'button');
                    button.setAttribute('data-bs-toggle', 'collapse');
                    button.setAttribute('data-bs-target', `#flush-collapse${order.id}`);
                    button.setAttribute('aria-expanded', 'false');
                    button.setAttribute('aria-controls', `flush-collapse${order.id}`);
                    button.textContent = `Заказ №${order.id}: ${getStatusText(order.order_status)}`;
                    button.style.color = getStatusColor(order.order_status);

                    header.appendChild(button);

                    // Тело аккордеона (содержимое заказа)
                    const collapse = document.createElement('div');
                    collapse.id = `flush-collapse${order.id}`;
                    collapse.classList.add('accordion-collapse', 'collapse');
                    collapse.setAttribute('data-bs-parent', '#accordionFlushOrders');

                    const body = document.createElement('div');
                    body.classList.add('accordion-body');


                    // Добавляем основную информацию о заказе
                    body.innerHTML = `
                        <strong>Дата заказа:</strong> ${new Date(order.order_time).toLocaleString()}<br>
                        <strong>Сумма:</strong> ${order.total_amount} KGS<br>
                        <strong>Метод оплаты:</strong> ${order.payment_method === 'card' ? 'Карта' : 'Наличные'}<br>
                        <strong>Промокод:</strong> ${order.promo_code || 'Отсутствует'}<br>
                        <strong>Тип получения:</strong> ${order.is_pickup ? 'Самовывоз' : 'Доставка'}<br>
                        <strong>Продукты:</strong>
                    `;


                    // Создаем список продуктов
                    if (order.order_items && Array.isArray(order.order_items)) {
                        const productList = document.createElement('ul');
                        productList.style.paddingLeft = '20px'; // Небольшой отступ для списка

                        order.order_items.forEach(item => {
                            const productItem = document.createElement('li');

                            // Добавляем основную информацию о продукте
                            productItem.innerHTML = `
                                <strong>${item.product.name}</strong> (${item.product.product_sizes.find(size => size.is_selected).size}) — ${item.quantity} шт.<br>
                                <em>Итого: ${item.total_amount} KGS</em><br>
                            `;

                            productList.appendChild(productItem);
                        });

                        // Добавляем список продуктов в тело аккордеона
                        body.appendChild(productList);
                    } else {
                        body.innerHTML += '<br><em>Продукты не найдены</em>';
                    }
                                        const openButton = document.createElement('a');
                    openButton.href = `/order/${order.id}/`; // Формируем URL для детального просмотра заказа
                    openButton.target = '_blank'; // Открытие в новой вкладке
                    openButton.classList.add('btn', 'btn-primary', 'btn-sm', 'mt-2', 'mx-auto'); // Стиль кнопки
                    openButton.textContent = 'Открыть заказ';

                    body.appendChild(openButton);

                    // Добавляем кнопку "Открыть" для детального просмотра заказа
// Добавляем кнопку к телу аккордеона
                    collapse.appendChild(body);

                    // Добавляем заголовок и содержимое в аккордеон
                    orderItem.appendChild(header);
                    orderItem.appendChild(collapse);
                    accordionContainer.appendChild(orderItem);
                });

                // Очищаем список и добавляем аккордеон
                ordersList.innerHTML = ''; // Очищаем предыдущие заказы
                ordersList.appendChild(accordionContainer); // Добавляем аккордеон
            } else {
                console.error('Неверный формат данных:', data); // Отладка ошибки
            }
        })
        .catch(error => {
            ordersLoading.style.display = 'none'; // Скрываем спиннер при ошибке
            console.error('Ошибка загрузки заказов:', error); // Отладка ошибки
        });
}// Функция для получения текста статуса
function getStatusText(status) {
    const statusMap = {
        'pending': 'В ожидании',
        'in_progress': 'В процессе',
        'delivery': 'Доставка',
        'completed': 'Завершено',
        'cancelled': 'Отменено'
    };
    return statusMap[status] || 'Неизвестно';
}

// Функция для получения цвета в зависимости от статуса
function getStatusColor(status) {
    const colorMap = {
        'pending': 'orange',      // В ожидании
        'in_progress': 'blue',    // В процессе
        'delivery': 'purple',     // Доставка
        'completed': 'green',     // Завершено
        'cancelled': 'red'        // Отменено
    };
    return colorMap[status] || 'black'; // По умолчанию черный цвет
}
// Функция для получения цвета в зависимости от статуса
  // Обработка кликов на список чатов
    document.querySelectorAll('.chat-link').forEach(link => {
        link.addEventListener('click', function (event) {
            event.preventDefault();
            const roomId = this.getAttribute('data-room-id');
            const userId = this.getAttribute('data-user-id');
            openChat(roomId, userId);
        });
    });

    // Отправка сообщения
    messageSubmit.addEventListener('click', function (event) {
        event.preventDefault();
        const message = messageInput.value.trim();
        if (message && ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                message: message,
                sender_id: document.body.getAttribute('data-user-id'),
                sender_username: document.body.getAttribute('data-user-username')
            }));
            messageInput.value = ''; // Очищаем поле ввода после отправки

        }
    });
});
