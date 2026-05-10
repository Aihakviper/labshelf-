import { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';

import './styles/app.css';
import { ApiClient } from './services/api.js';
import { Shell } from './components/Shell.js';
import { CatalogPage } from './pages/CatalogPage.js';
import { DashboardPage } from './pages/DashboardPage.js';
import { LoansPage } from './pages/LoansPage.js';
import { MembersPage } from './pages/MembersPage.js';
import { ReservationsPage } from './pages/ReservationsPage.js';
import { h } from './ui.js';

const pages = {
  dashboard: { title: 'Library operations', eyebrow: 'Overview' },
  catalog: { title: 'Catalog', eyebrow: 'Books and copies' },
  loans: { title: 'Loans', eyebrow: 'Borrowing activity' },
  reservations: { title: 'Reservations', eyebrow: 'Queue management' },
  members: { title: 'Members', eyebrow: 'Library users' },
};

function getPageFromHash() {
  const page = window.location.hash.replace('#', '');
  return pages[page] ? page : 'dashboard';
}

function App() {
  const api = useMemo(() => new ApiClient(), []);
  const [state, setState] = useState({ loading: true, payload: null, notice: null });
  const [activePage, setActivePage] = useState(getPageFromHash);

  useEffect(() => {
    api.dashboard().then((payload) => setState({ loading: false, payload, notice: null }));
  }, [api]);

  useEffect(() => {
    const handleHashChange = () => setActivePage(getPageFromHash());
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  const refreshFromAction = async (action, successFallback) => {
    try {
      const response = await action();
      setState({ loading: false, payload: { seeded: true, data: response.data }, notice: { type: 'success', text: response.message || successFallback } });
    } catch (error) {
      setState((current) => ({
        ...current,
        notice: { type: 'error', text: error.message },
      }));
    }
  };

  if (state.loading) {
    return h('main', { className: 'loading' }, 'Loading LabShelf+...');
  }

  if (state.payload.seeded === false) {
    return h('main', { className: 'empty-state' },
      h('h1', null, 'LabShelf+ is installed'),
      h('p', null, 'Run ', h('code', null, 'python manage.py seed_labshelf'), ' to load demo institutions and library activity.'),
    );
  }

  const data = state.payload.data || state.payload;
  const pageMeta = pages[activePage];

  const pageProps = {
    data,
    onCreateBook: (values) => refreshFromAction(() => api.createBook(values), 'Book added.'),
    onCreateMember: (values) => refreshFromAction(() => api.createMember(values), 'Member added.'),
    onCreateLoan: (values) => refreshFromAction(() => api.checkout(values), 'Loan created.'),
    onCreateReservation: (values) => refreshFromAction(() => api.reserve(values), 'Reservation added.'),
    onRenew: (loanId) => refreshFromAction(() => api.renewLoan(loanId), 'Loan renewed.'),
    onReturn: (loanId) => refreshFromAction(() => api.returnLoan(loanId), 'Book returned.'),
  };

  const pageContent = {
    dashboard: h(DashboardPage, pageProps),
    catalog: h(CatalogPage, pageProps),
    loans: h(LoansPage, pageProps),
    reservations: h(ReservationsPage, pageProps),
    members: h(MembersPage, pageProps),
  }[activePage];

  return h(Shell, {
    data,
    notice: state.notice,
    activePage,
    onPageChange: setActivePage,
    onTenantChange: (tenantId) => refreshFromAction(() => api.switchTenant(tenantId), 'Institution changed.'),
  },
    h('header', { className: 'page-header' },
      h('div', null,
        h('p', { className: 'eyebrow' }, `${pageMeta.eyebrow} - ${data.tenant.plan} plan`),
        h('h1', null, pageMeta.title),
      ),
      h('div', { className: 'policy-strip' },
        h('span', null, `${data.tenant.borrowingDays} day loans`),
        h('span', null, `${data.tenant.maxRenewals} renewals`),
        h('span', null, `NGN ${data.tenant.finePerDay}/day`),
      ),
    ),
    pageContent,
  );
}

createRoot(document.getElementById('root')).render(h(App));
