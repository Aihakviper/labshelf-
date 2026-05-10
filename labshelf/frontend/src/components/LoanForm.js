import { h } from '../ui.js';

export function LoanForm({ books, members, staff, onSubmit }) {
  return h('form', {
    className: 'panel form-panel',
    onSubmit: (event) => {
      event.preventDefault();
      onSubmit(Object.fromEntries(new FormData(event.currentTarget)));
    },
  },
    h('div', { className: 'panel-head' }, h('h2', null, 'Check out')),
    h(Select, { label: 'Book', name: 'book', options: books.map((book) => [book.id, `${book.title} (${book.availableCopies} available)`]) }),
    h(Select, { label: 'Member', name: 'member', options: members.map((member) => [member.id, member.name]) }),
    h(Select, { label: 'Processed by', name: 'checked_out_by', options: staff.map((user) => [user.id, user.name]) }),
    h('button', { type: 'submit' }, 'Create loan'),
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
