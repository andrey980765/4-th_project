// contacts/static/contacts/js/contacts.js
document.addEventListener('DOMContentLoaded', function(){
  const searchInput = document.getElementById('searchInput');
  if (searchInput){
    let timeout = null;
    searchInput.addEventListener('input', function(){
      clearTimeout(timeout);
      timeout = setTimeout(()=> doSearch(searchInput.value), 300);
    });
  }

  // delete
  document.addEventListener('click', function(e){
    if (e.target.matches('.btn-delete')){
      const id = e.target.dataset.id;
      if (!confirm('Удалить запись?')) return;
      fetch(AJAX_DELETE_URL_TEMPLATE.replace('__ID__', id), {
        method: 'POST',
        headers: {'X-CSRFToken': getCookie('csrftoken')},
      }).then(r => r.json()).then(data => {
        if (data.ok){
          const row = document.querySelector(`tr[data-id="${id}"]`);
          if (row) row.remove();
        }
      });
    }
    if (e.target.matches('.btn-edit')){
      const id = e.target.dataset.id;
      openEditModal(id);
    }
  });

  // helpers
  function doSearch(q){
    fetch(AJAX_SEARCH_URL + '?q=' + encodeURIComponent(q))
      .then(r => r.json())
      .then(data => {
        const tbody = document.getElementById('contactsTableBody');
        tbody.innerHTML = '';
        data.results.forEach(c => {
          const tr = document.createElement('tr');
          tr.dataset.id = c.id;
          tr.innerHTML = `<td class="name">${escapeHtml(c.name)}</td>
            <td class="email">${escapeHtml(c.email)}</td>
            <td class="phone">${escapeHtml(c.phone)}</td>
            <td class="notes">${escapeHtml(c.notes).substring(0,80)}</td>
            <td>
              <button class="btn btn-sm btn-outline-secondary btn-edit" data-id="${c.id}">Редакт.</button>
              <button class="btn btn-sm btn-outline-danger btn-delete" data-id="${c.id}">Удалить</button>
            </td>`;
          tbody.appendChild(tr);
        });
      });
  }

  function openEditModal(id){
    // извлечь текущие данные из строки
    const row = document.querySelector(`tr[data-id="${id}"]`);
    const name = row.querySelector('.name').textContent.trim();
    const email = row.querySelector('.email').textContent.trim();
    const phone = row.querySelector('.phone').textContent.trim();
    const notes = row.querySelector('.notes').textContent.trim();

    const modalHtml = `
<div class="modal fade" id="editModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content">
      <form id="editForm">
        <div class="modal-header">
          <h5 class="modal-title">Редактировать</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <div id="editErrors" class="mb-2"></div>
          <div class="mb-2">
            <label>Имя</label>
            <input name="name" class="form-control" value="${escapeHtml(name)}" required>
          </div>
          <div class="mb-2">
            <label>Email</label>
            <input name="email" class="form-control" value="${escapeHtml(email)}" required>
          </div>
          <div class="mb-2">
            <label>Телефон</label>
            <input name="phone" class="form-control" value="${escapeHtml(phone)}">
          </div>
          <div class="mb-2">
            <label>Примечание</label>
            <textarea name="notes" class="form-control">${escapeHtml(notes)}</textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" data-bs-dismiss="modal" type="button">Отменить</button>
          <button class="btn btn-primary" type="submit">Сохранить</button>
        </div>
      </form>
    </div>
  </div>
</div>`;
    document.getElementById('editModalContainer').innerHTML = modalHtml;
    const modalEl = document.getElementById('editModal');
    const bsModal = new bootstrap.Modal(modalEl);
    bsModal.show();

    document.getElementById('editForm').addEventListener('submit', function(ev){
      ev.preventDefault();
      const formData = new FormData(this);
      fetch(AJAX_UPDATE_URL_TEMPLATE.replace('__ID__', id), {
        method: 'POST',
        headers: {'X-CSRFToken': getCookie('csrftoken')},
        body: formData
      }).then(async res => {
        if (!res.ok){
          const j = await res.json().catch(()=>({errors:{'__all__':'Ошибка сервера'}}));
          showErrors(j.errors || {'__all__':'Ошибка'});
        } else {
          const j = await res.json();
          if (j.ok){
            // обновить строку
            const r = document.querySelector(`tr[data-id="${id}"]`);
            r.querySelector('.name').textContent = j.contact.name;
            r.querySelector('.email').textContent = j.contact.email;
            r.querySelector('.phone').textContent = j.contact.phone;
            r.querySelector('.notes').textContent = j.contact.notes.substring(0,80);
            bsModal.hide();
          }
        }
      }).catch(err => showErrors({'__all__': String(err)}));
    });

    function showErrors(errors){
      const cont = document.getElementById('editErrors');
      cont.innerHTML = '';
      for (const k in errors){
        const div = document.createElement('div');
        div.className = 'alert alert-danger py-1';
        div.textContent = errors[k];
        cont.appendChild(div);
      }
    }
  }

  // small util
  function getCookie(name) {
    const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return v ? v.pop() : '';
  }
  function escapeHtml(text) {
    return text.replace(/[&<>"']/g, function(m){ return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[m]; });
  }
});
