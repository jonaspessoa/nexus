const form = document.querySelector('form');
const title = document.querySelector('#title');
const investigate = document.querySelector('#investigate');
const feedback = document.querySelector('#feedback');
const tasks = document.querySelector('#task-list');
const recover = document.querySelector('#recover');
const serviceStatus = document.querySelector('#service-status');
const storageKey = 'nexus-demo-v1';
let demo = { tasks: [], recovered: false };

try {
  const saved = JSON.parse(localStorage.getItem(storageKey));
  if (saved && Array.isArray(saved.tasks)) demo = saved;
} catch {
  // The demo still works in memory when browser storage is unavailable.
}

function saveDemo() {
  try {
    localStorage.setItem(storageKey, JSON.stringify(demo));
  } catch {
    // Storage may be disabled by the browser.
  }
}

function renderTask(taskTitle) {
  const item = document.createElement('li');
  item.textContent = taskTitle + ' — Portfólio · A fazer';
  tasks.append(item);
  document.querySelector('#empty').hidden = true;
}

demo.tasks.forEach(renderTask);
recover.hidden = !demo.tasks.length || demo.recovered;

function showRecovery() {
  const entry = document.createElement('li');
  entry.textContent = 'Hoje, 09:17 — Recuperado · HTTP 200';
  document.querySelector('#check-history').prepend(entry);
  serviceStatus.textContent = 'Disponível';
  serviceStatus.classList.add('available');
  recover.hidden = true;
}

if (demo.recovered) showRecovery();

recover.addEventListener('click', () => {
  demo.recovered = true;
  saveDemo();
  showRecovery();
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

  demo.tasks.push(taskTitle);
  saveDemo();
  renderTask(taskTitle);
  form.hidden = true;
  investigate.focus();
  feedback.textContent = 'Tarefa adicionada.';
  recover.hidden = serviceStatus.classList.contains('available');
});


document.querySelector('#reset-demo').addEventListener('click', () => {
  demo = { tasks: [], recovered: false };
  saveDemo();
  location.reload();
});
