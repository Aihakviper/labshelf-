import { h } from '../ui.js';

export function StatGrid({ stats, tenant }) {
  const items = [
    ['Books', stats.books, `${stats.copies} total copies`],
    ['Active loans', stats.active_loans, `${stats.overdue} overdue`],
    ['Reservations', stats.reservations, `Queue limit ${tenant.reservationLimit}`],
    ['Unpaid fines', `NGN ${stats.unpaid_fines}`, 'Linked to loan records'],
  ];

  return h('section', { className: 'stats-grid' },
    items.map(([label, value, helper]) =>
      h('article', { key: label },
        h('span', null, label),
        h('strong', null, value),
        h('small', null, helper),
      ),
    ),
  );
}
