export class ApiClient {
  async dashboard() {
    return this.request('/api/dashboard/');
  }

  async switchTenant(tenantId) {
    return this.request('/api/tenant/', { tenant_id: tenantId });
  }

  async createBook(values) {
    return this.request('/api/books/', values);
  }

  async createMember(values) {
    return this.request('/api/members/', values);
  }

  async checkout(values) {
    return this.request('/api/loans/', values);
  }

  async reserve(values) {
    return this.request('/api/reservations/', values);
  }

  async renewLoan(loanId) {
    return this.request(`/api/loans/${loanId}/renew/`, {});
  }

  async returnLoan(loanId) {
    return this.request(`/api/loans/${loanId}/return/`, {});
  }

  async request(url, body = null) {
    const options = body
      ? {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
          },
          credentials: 'same-origin',
          body: JSON.stringify(body),
        }
      : { credentials: 'same-origin' };

    const response = await fetch(url, options);
    const payload = await parseResponse(response);
    if (!response.ok) {
      throw new Error(payload.error || 'Request failed.');
    }
    return payload;
  }
}

async function parseResponse(response) {
  const contentType = response.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    return response.json();
  }

  const text = await response.text();
  if (!response.ok) {
    return { error: text.includes('CSRF') ? 'Request blocked by CSRF protection. Refresh the page and try again.' : 'Server returned a non-JSON error response.' };
  }
  throw new Error('Server returned an invalid response.');
}

function getCookie(name) {
  return document.cookie
    .split(';')
    .map((cookie) => cookie.trim())
    .find((cookie) => cookie.startsWith(`${name}=`))
    ?.split('=')[1] || '';
}
