const form = document.querySelector('form');
const title = document.querySelector('#title');
const investigate = document.querySelector('#investigate');
const feedback = document.querySelector('#feedback');
const tasks = document.querySelector('#task-list');
const recover = document.querySelector('#recover');
const serviceStatus = document.querySelector('#service-status');

recover.addEventListener('click', () => {
  const entry = document.createElement('li');
  entry.textContent = 'Hoje, 09:17 — Recuperado · HTTP 200';
  document.querySelector('#check-history').prepend(entry);
  serviceStatus.textContent = 'Disponível';
  serviceStatus.classList.add('available');
  feedback.textContent = 'Serviço recuperado. A tarefa continua na lista.';
  investigate.focus();
  recover.hidden = true;
});

investigate.addEventListener('click', () => {
  form.hidden = false;
  title.value = 'Investigar indisponibilidade do portfólio';
  title.setCustomValidity('');
  feedback.textContent = '';
  title.focus();
});

document.querySelector('#cancel').addEventListener('click', () => {
  form.hidden = true;
  investigate.focus();
});

title.addEventListener('input', () => title.setCustomValidity(''));

form.addEventListener('submit', (event) => {
  event.preventDefault();
  const taskTitle = title.value.trim();
  if (!taskTitle) {
    title.setCustomValidity('Digite um título para a tarefa.');
    title.reportValidity();
    return;
  }

  const item = document.createElement('li');
  item.textContent = taskTitle + ' — Portfólio · A fazer';
  tasks.append(item);
  document.querySelector('#empty').hidden = true;
  form.hidden = true;
  investigate.focus();
  feedback.textContent = 'Tarefa adicionada.';
  recover.hidden = serviceStatus.classList.contains('available');
});
