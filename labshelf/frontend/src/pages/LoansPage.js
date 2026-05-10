import { LoanForm } from '../components/LoanForm.js';
import { LoanList } from '../components/TableSections.js';
import { h } from '../ui.js';

export function LoansPage({ data, onCreateLoan, onRenew, onReturn }) {
  return h('div', { className: 'page-stack' },
    h(LoanForm, { books: data.books, members: data.members, staff: data.staff, onSubmit: onCreateLoan }),
    h(LoanList, { data, onRenew, onReturn }),
  );
}
