import { ReservationForm } from '../components/ReservationForm.js';
import { ReservationQueue } from '../components/TableSections.js';
import { h } from '../ui.js';

export function ReservationsPage({ data, onCreateReservation }) {
  return h('div', { className: 'page-stack' },
    h(ReservationForm, { books: data.books, members: data.members, onSubmit: onCreateReservation }),
    h(ReservationQueue, { data }),
  );
}
