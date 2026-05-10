import { h } from '../ui.js';

export function ReservationForm({ books, members, onSubmit }) {
  return h('form', {
    className: 'panel form-panel',
    onSubmit: (event) => {
      event.preventDefault();
      onSubmit(Object.fromEntries(new FormData(event.currentTarget)));
    },
  },
    h('div', { className: 'panel-head' }, h('h2', null, 'Reserve')),
    h(Select, { label: 'Book', name: 'book', options: books.map((book) => [book.id, book.title]) }),
    h(Select, { label: 'Member', name: 'user', options: members.map((member) => [member.id, member.name]) }),
    h('button', { type: 'submit' }, 'Join queue'),
  );
}

function Select({ label, name, options }) {
  return h('label', null, label,
    h('select', { name, required: true },
      h('option', { value: '' }, 'Select'),
      options.map(([value, text]) => h('option', { key: value, value }, text)),
    ),
  );
}
