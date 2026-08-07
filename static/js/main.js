// Главный JavaScript файл

document.addEventListener('DOMContentLoaded', function() {
    // Мобильное меню
    const menuToggle = document.getElementById('menuToggle');
    const navList = document.querySelector('.nav-list');

    if (menuToggle) {
        menuToggle.addEventListener('click', function() {
            navList.classList.toggle('open');
        });
    }

    // Анимация для карточек услуг
    const serviceCards = document.querySelectorAll('.service-card');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });

    serviceCards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });

    // Плавная прокрутка для якорных ссылок
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
});

// Функция для работы с формой обратной связи
function openContactForm() {
    window.location.href = '/contact-form';
}

function openAppointmentForm() {
    window.location.href = '/appointment/create';
}

function openLoginForm() {
    window.location.href = '/users/login';
}

// Имитация авторизации (для демонстрации)
const userRole = 'Manager'; // Может быть 'Manager', 'User' или null (не авторизован)

// Если пользователь авторизован, показываем соответствующие элементы
document.addEventListener('DOMContentLoaded', function() {
    if (userRole) {
        // Показываем элементы для авторизованного пользователя
        document.querySelectorAll('.auth-required').forEach(el => {
            el.style.display = 'block';
        });
        document.querySelectorAll('.guest-only').forEach(el => {
            el.style.display = 'none';
        });

        // Если роль Manager, показываем ссылку на админку
        if (userRole === 'Manager') {
            document.querySelector('.admin-link').style.display = 'block';
        }
    } else {
        // Показываем элементы для гостя
        document.querySelectorAll('.guest-only').forEach(el => {
            el.style.display = 'block';
        });
        document.querySelectorAll('.auth-required').forEach(el => {
            el.style.display = 'none';
        });
    }
});