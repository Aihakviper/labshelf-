import { BookForm } from '../components/BookForm.js';
import { LoanForm } from '../components/LoanForm.js';
import { ReservationForm } from '../components/ReservationForm.js';
import { StatGrid } from '../components/StatGrid.js';
import { h } from '../ui.js';

export function DashboardPage({ data, onCreateBook, onCreateLoan, onCreateReservation }) {
  return h('div', null,
    h(StatGrid, { stats: data.stats, tenant: data.tenant }),
    h('section', { className: 'workbench' },
      h(BookForm, { onSubmit: onCreateBook }),
      h(LoanForm, { books: data.books, members: data.members, staff: data.staff, onSubmit: onCreateLoan }),
      h(ReservationForm, { books: data.books, members: data.members, onSubmit: onCreateReservation }),
    ),
  );
}
