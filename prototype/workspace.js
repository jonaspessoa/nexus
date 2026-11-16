const form = document.querySelector('form');
const title = document.querySelector('#title');
const investigate = document.querySelector('#investigate');
const feedback = document.querySelector('#feedback');
const tasks = document.querySelector('#task-list');

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
});
