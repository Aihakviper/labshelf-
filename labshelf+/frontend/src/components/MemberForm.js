import { h } from '../ui.js';

export function MemberForm({ onSubmit }) {
  return h('form', {
    className: 'panel form-panel',
    onSubmit: (event) => {
      event.preventDefault();
      const form = event.currentTarget;
      onSubmit(Object.fromEntries(new FormData(form)));
      form.reset();
    },
  },
    h('div', { className: 'panel-head' }, h('h2', null, 'Add member')),
    h(Field, { label: 'Name', name: 'name', required: true }),
    h(Field, { label: 'Email', name: 'email', type: 'email', required: true }),
    h(Field, { label: 'Student ID', name: 'student_id' }),
    h('button', { type: 'submit' }, 'Add member'),
  );
}

function Field({ label, ...props }) {
  return h('label', null, label, h('input', props));
}
