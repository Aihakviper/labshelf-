import { h } from '../ui.js';

export function CatalogTable({ data }) {
  return h('section', { id: 'catalog', className: 'table-section' },
    h('div', { className: 'section-head' },
      h('h2', null, 'Catalog'),
      h('span', null, `${data.stats.copies} copies tracked`),
    ),
    h('div', { className: 'table-wrap' },
      h('table', null,
        h('thead', null, h('tr', null, ['Title', 'Author', 'Category', 'Available', 'Queue', 'Shelf'].map((heading) => h('th', { key: heading }, heading)))),
        h('tbody', null, data.books.map((book) => h('tr', { key: book.id },
          h('td', null, h('strong', null, book.title), h('small', null, book.isbn || 'No ISBN')),
          h('td', null, book.author),
          h('td', null, book.category),
          h('td', null, `${book.availableCopies}/${book.totalCopies}`),
          h('td', null, book.queueSize),
          h('td', null, book.shelfLocation || '-'),
        ))),
      ),
    ),
  );
}

export function LoanList({ data, onRenew, onReturn }) {
  return h('section', { id: 'loans', className: 'table-section' },
    h('div', { className: 'section-head' },
      h('h2', null, 'Open loans'),
      h('span', null, `${data.stats.overdue} overdue`),
    ),
    h('div', { className: 'loan-list' },
      data.loans.length
        ? data.loans.map((loan) => h('article', { className: 'loan-row', key: loan.id },
            h('div', null, h('strong', null, loan.book.title), h('span', null, `${loan.member.name} - Due ${loan.dueDate} - ${loan.status}`)),
            h('div', { className: 'row-actions' },
              h('button', { className: 'ghost', onClick: () => onRenew(loan.id) }, 'Renew'),
              h('button', { onClick: () => onReturn(loan.id) }, 'Return'),
            ),
          ))
        : h('p', { className: 'empty' }, 'No open loans.'),
    ),
  );
}

export function ReservationQueue({ data }) {
  return h('section', { id: 'reservations', className: 'table-section' },
    h('div', { className: 'section-head' }, h('h2', null, 'Reservation queue')),
    data.reservations.length
      ? data.reservations.map((reservation) => h('article', { className: 'queue-item', key: reservation.id },
          h('span', { className: 'queue-pos' }, reservation.queuePosition),
          h('div', null, h('strong', null, reservation.book.title), h('small', null, `${reservation.user.name} - ${reservation.status}`)),
        ))
      : h('p', { className: 'empty' }, 'No reservations.'),
  );
}

export function TableSections({ data, onRenew, onReturn }) {
  return h('div', null,
    h(CatalogTable, { data }),
    h(LoanList, { data, onRenew, onReturn }),
    h(ReservationQueue, { data }),
  );
}
