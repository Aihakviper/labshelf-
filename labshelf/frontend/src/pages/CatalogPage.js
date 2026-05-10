import { BookForm } from '../components/BookForm.js';
import { CatalogTable } from '../components/TableSections.js';
import { h } from '../ui.js';

export function CatalogPage({ data, onCreateBook }) {
  return h('div', { className: 'page-stack' },
    h(BookForm, { onSubmit: onCreateBook }),
    h(CatalogTable, { data }),
  );
}
