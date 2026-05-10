import { h } from '../ui.js';

export function MemberList({ members }) {
  return h('section', { id: 'members', className: 'table-section' },
    h('div', { className: 'section-head' }, h('h2', null, 'Members')),
    members.map((member) => h('article', { className: 'member-row', key: member.id },
      h('div', null, h('strong', null, member.name), h('small', null, member.email)),
      h('span', null, member.studentId || 'Member'),
    )),
  );
}
