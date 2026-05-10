import { h } from '../ui.js';

export function BookForm({ onSubmit }) {
  return h('form', {
    className: 'panel form-panel',
    onSubmit: (event) => {
      event.preventDefault();
      const form = event.currentTarget;
      onSubmit(Object.fromEntries(new FormData(form)));
      form.reset();
    },
  },
    h('div', { className: 'panel-head' }, h('h2', null, 'Add book')),
    h(Field, { label: 'Title', name: 'title', required: true }),
    h(Field, { label: 'Author', name: 'author', required: true }),
    h(Field, { label: 'ISBN', name: 'isbn' }),
    h(Field, { label: 'Category', name: 'category', defaultValue: 'General' }),
    h(Field, { label: 'Shelf', name: 'shelf_location' }),
    h(Field, { label: 'Copies', name: 'total_copies', type: 'number', min: '1', defaultValue: '1' }),
    h('button', { type: 'submit' }, 'Add to catalog'),
  );
}

function Field({ label, ...props }) {
  return h('label', null, label, h('input', props));
}
