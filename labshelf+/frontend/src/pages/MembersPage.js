import { MemberForm } from '../components/MemberForm.js';
import { MemberList } from '../components/MemberList.js';
import { h } from '../ui.js';

export function MembersPage({ data, onCreateMember }) {
  return h('div', { className: 'page-stack' },
    h(MemberForm, { onSubmit: onCreateMember }),
    h(MemberList, { members: data.members }),
  );
}
