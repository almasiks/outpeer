
document.querySelectorAll('.top-btns button, .top-btns a').forEach(button => {
    button.addEventListener('click', function(e) {
        const targetId = this.innerText.toLowerCase().includes('обо мне') ? 'abtme' :
            this.innerText.toLowerCase().includes('навыки') ? 'my-skills' :
                this.innerText.toLowerCase().includes('образование') ? 'my-education' :
                    this.innerText.toLowerCase().includes('проекты') ? 'my-projects' :
                        this.innerText.toLowerCase().includes('контакты') ? 'my-registration' : null;

        if (targetId) {
            const element = document.getElementById(targetId);
            if (element) {
                element.scrollIntoView({ behavior: 'smooth' });
            }
        }
    });
});

//
const form = document.querySelector('.reg-form');
if (form) {
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        // Получаем данные
        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;

        if (name && email) {
            alert(`Спасибо, ${name}! Ваше сообщение успешно "отправлено". Я свяжусь с вами по адресу ${email}.`);
            form.reset();
        } else {
            alert('Пожалуйста, заполните основные поля!');
        }
    });
}

const skillItems = document.querySelectorAll('.skills-list li');
skillItems.forEach(item => {
    item.addEventListener('mouseenter', () => {
        item.style.transform = 'scale(1.05)';
        item.style.transition = '0.3s';
    });
    item.addEventListener('mouseleave', () => {
        item.style.transform = 'scale(1)';
    });
});