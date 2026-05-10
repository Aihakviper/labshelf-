import React from 'react';

import { h } from '../ui.js';

const navItems = [
  ['dashboard', 'Dashboard'],
  ['catalog', 'Catalog'],
  ['loans', 'Loans'],
  ['reservations', 'Reservations'],
  ['members', 'Members'],
];

export function Shell({ data, notice, activePage, onPageChange, onTenantChange, children }) {
  return h(React.Fragment, null,
    h('aside', { className: 'sidebar' },
      h('div', { className: 'brand' },
        h('span', { className: 'brand-mark' }, 'L+'),
        h('div', null,
          h('strong', null, 'LabShelf+'),
          h('small', null, data.tenant.name),
        ),
      ),
      h('nav', { className: 'nav' },
        navItems.map(([page, label]) =>
          h('a', {
            key: page,
            className: activePage === page ? 'active' : '',
            href: `#${page}`,
            onClick: () => onPageChange(page),
          }, label),
        ),
      ),
      h('label', { className: 'tenant-select-label', htmlFor: 'tenant-select' }, 'Institution'),
      h('select', {
        id: 'tenant-select',
        value: data.tenant.id,
        onChange: (event) => onTenantChange(Number(event.target.value)),
      }, data.tenants.map((tenant) => h('option', { key: tenant.id, value: tenant.id }, tenant.name))),
    ),
    h('main', { className: 'main' },
      notice && h('div', { className: `message ${notice.type}` }, notice.text),
      children,
    ),
  );
}
