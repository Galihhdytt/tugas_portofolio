const getAuthToken = () => localStorage.getItem('adminToken');

const api = async (url, options = {}) => {
  const headers = { ...(options.headers || {}) };
  const token = getAuthToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  if (options.body && !(options.body instanceof FormData) && !headers['Content-Type']) headers['Content-Type'] = 'application/json';
  const response = await fetch(url, { ...options, headers });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || 'Permintaan gagal');
  return data;
};

const renderMessage = (elementId, message) => {
  const el = document.getElementById(elementId);
  if (el) el.textContent = message;
};

const notifyPortfolioRefresh = () => {
  const stamp = String(Date.now());
  try {
    localStorage.setItem('portfolio:refresh', stamp);
  } catch (error) {
    console.warn('Gagal menulis refresh marker', error);
  }
  try {
    if (window.location.pathname.includes('/admin/')) {
      window.localStorage.setItem('portfolio:refresh:admin', stamp);
    }
  } catch (error) {
    console.warn('Gagal menulis refresh marker admin', error);
  }
  window.dispatchEvent(new Event('portfolio:refresh'));

  if (typeof BroadcastChannel !== 'undefined') {
    try {
      const channel = new BroadcastChannel('portfolio-refresh');
      channel.postMessage({ type: 'portfolio-refresh', stamp });
      channel.close();
    } catch (error) {
      console.warn('Gagal mengirim broadcast refresh', error);
    }
  }
};

const loadStats = async () => {
  const statsText = document.getElementById('statsText');
  const userText = document.getElementById('userText');
  if (!statsText || !userText) return;
  try {
    const res = await api('/api/dashboard/stats');
    statsText.textContent = `Pengalaman ${res.data.experiences_count} • Proyek ${res.data.projects_count} • Skill ${res.data.skills_count}`;
    userText.textContent = res.data.admin_name || 'Admin';
  } catch (error) {
    statsText.textContent = error.message;
  }
};

const loadProfile = async () => {
  const profileForm = document.getElementById('profileForm');
  if (!profileForm) return;
  try {
    const res = await api('/api/profiles');
    const profile = res.data || {};
    ['nama_lengkap','nama_panggilan','tempat_lahir','tanggal_lahir','email','telepon','universitas','fakultas','prodi','semester','alamat','foto_url'].forEach((field) => {
      const el = document.getElementById(field);
      if (el) el.value = profile[field] || '';
    });
    const preview = document.getElementById('profilePhotoPreview');
    if (preview && profile.foto_url) {
      preview.src = profile.foto_url;
      preview.style.display = 'block';
    }
  } catch (error) {
    renderMessage('profileMessage', error.message);
  }
};

const loadExperiences = async () => {
  const list = document.getElementById('experienceList');
  if (!list) return;
  try {
    const res = await api('/api/experiences');
    list.innerHTML = '';
    (res.data || []).forEach((item) => {
      const el = document.createElement('div');
      el.className = 'item';
      el.innerHTML = `<strong>${item.posisi || '-'}</strong> • ${item.perusahaan || '-'}<br><span class="muted">${item.durasi || ''}</span>`;
      const actions = document.createElement('div');
      actions.className = 'item-actions';
      actions.innerHTML = `<button data-action="edit" data-type="experience" data-id="${item.id}">Edit</button><button data-action="delete" data-type="experience" data-id="${item.id}">Hapus</button>`;
      el.appendChild(actions);
      list.appendChild(el);
    });
  } catch (error) {
    renderMessage('experienceMessage', error.message);
  }
};

const loadProjects = async () => {
  const list = document.getElementById('projectList');
  if (!list) return;
  try {
    const res = await api('/api/projects');
    list.innerHTML = '';
    (res.data || []).forEach((item) => {
      const el = document.createElement('div');
      el.className = 'item';
      el.innerHTML = `<strong>${item.judul || '-'}</strong><br><span class="muted">${(item.deskripsi || '').slice(0, 120)}</span>`;
      const actions = document.createElement('div');
      actions.className = 'item-actions';
      actions.innerHTML = `<button data-action="edit" data-type="project" data-id="${item.id}">Edit</button><button data-action="delete" data-type="project" data-id="${item.id}">Hapus</button>`;
      el.appendChild(actions);
      list.appendChild(el);
    });
  } catch (error) {
    renderMessage('projectMessage', error.message);
  }
};

const loadSkills = async () => {
  const list = document.getElementById('skillList');
  if (!list) return;
  try {
    const res = await api('/api/skills');
    list.innerHTML = '';
    (res.data || []).forEach((item) => {
      const el = document.createElement('div');
      el.className = 'item';
      el.innerHTML = `<strong>${item.nama_skill || '-'}</strong><br><span class="muted">${item.icon_class || '-'}</span>`;
      const actions = document.createElement('div');
      actions.className = 'item-actions';
      actions.innerHTML = `<button data-action="edit" data-type="skill" data-id="${item.id}">Edit</button><button data-action="delete" data-type="skill" data-id="${item.id}">Hapus</button>`;
      el.appendChild(actions);
      list.appendChild(el);
    });
  } catch (error) {
    renderMessage('skillMessage', error.message);
  }
};

const profileForm = document.getElementById('profileForm');
if (profileForm) {
  profileForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const formData = new FormData(profileForm);
    try {
      await api('/api/profiles', { method: 'POST', body: formData });
      renderMessage('profileMessage', 'Profil berhasil disimpan');
      notifyPortfolioRefresh();
      loadProfile();
    } catch (error) {
      renderMessage('profileMessage', error.message);
    }
  });
}

const experienceForm = document.getElementById('experienceForm');
if (experienceForm) {
  experienceForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const id = document.getElementById('experienceId').value;
    const payload = {
      posisi: document.getElementById('experiencePosisi').value,
      perusahaan: document.getElementById('experiencePerusahaan').value,
      durasi: document.getElementById('experienceDurasi').value,
      deskripsi: document.getElementById('experienceDeskripsi').value
    };
    try {
      if (id) await api(`/api/experiences/${id}`, { method: 'PUT', body: JSON.stringify(payload) });
      else await api('/api/experiences', { method: 'POST', body: JSON.stringify(payload) });
      experienceForm.reset();
      renderMessage('experienceMessage', 'Pengalaman berhasil disimpan');
      notifyPortfolioRefresh();
      loadExperiences();
    } catch (error) {
      renderMessage('experienceMessage', error.message);
    }
  });
}

const projectForm = document.getElementById('projectForm');
if (projectForm) {
  projectForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const formData = new FormData(projectForm);
    const id = document.getElementById('projectId').value;
    try {
      if (id) await api(`/api/projects/${id}`, { method: 'PUT', body: formData });
      else await api('/api/projects', { method: 'POST', body: formData });
      projectForm.reset();
      renderMessage('projectMessage', 'Proyek berhasil disimpan');
      notifyPortfolioRefresh();
      loadProjects();
    } catch (error) {
      renderMessage('projectMessage', error.message);
    }
  });
}

const skillForm = document.getElementById('skillForm');
if (skillForm) {
  skillForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const id = document.getElementById('skillId').value;
    const payload = {
      nama_skill: document.getElementById('skillNama').value,
      icon_class: document.getElementById('skillIcon').value
    };
    try {
      if (id) await api(`/api/skills/${id}`, { method: 'PUT', body: JSON.stringify(payload) });
      else await api('/api/skills', { method: 'POST', body: JSON.stringify(payload) });
      skillForm.reset();
      renderMessage('skillMessage', 'Skill berhasil disimpan');
      notifyPortfolioRefresh();
      loadSkills();
    } catch (error) {
      renderMessage('skillMessage', error.message);
    }
  });
}

document.addEventListener('click', async (event) => {
  const button = event.target.closest('button[data-action]');
  if (!button) return;
  const { action, type, id } = button.dataset;
  if (action === 'delete') {
    try {
      if (type === 'experience') await api(`/api/experiences/${id}`, { method: 'DELETE' });
      if (type === 'project') await api(`/api/projects/${id}`, { method: 'DELETE' });
      if (type === 'skill') await api(`/api/skills/${id}`, { method: 'DELETE' });
      notifyPortfolioRefresh();
      if (type === 'experience') loadExperiences();
      if (type === 'project') loadProjects();
      if (type === 'skill') loadSkills();
    } catch (error) {
      if (type === 'experience') renderMessage('experienceMessage', error.message);
      if (type === 'project') renderMessage('projectMessage', error.message);
      if (type === 'skill') renderMessage('skillMessage', error.message);
    }
    return;
  }
  if (action === 'edit') {
    if (type === 'experience') {
      const item = (await api('/api/experiences')).data.find((entry) => entry.id == id);
      if (item) {
        document.getElementById('experienceId').value = item.id;
        document.getElementById('experiencePosisi').value = item.posisi || '';
        document.getElementById('experiencePerusahaan').value = item.perusahaan || '';
        document.getElementById('experienceDurasi').value = item.durasi || '';
        document.getElementById('experienceDeskripsi').value = item.deskripsi || '';
      }
    }
    if (type === 'project') {
      const item = (await api('/api/projects')).data.find((entry) => entry.id == id);
      if (item) {
        document.getElementById('projectId').value = item.id;
        document.getElementById('projectJudul').value = item.judul || '';
        document.getElementById('projectDeskripsi').value = item.deskripsi || '';
        document.getElementById('projectLink').value = item.link_project || '';
      }
    }
    if (type === 'skill') {
      const item = (await api('/api/skills')).data.find((entry) => entry.id == id);
      if (item) {
        document.getElementById('skillId').value = item.id;
        document.getElementById('skillNama').value = item.nama_skill || '';
        document.getElementById('skillIcon').value = item.icon_class || '';
      }
    }
  }
});

document.querySelectorAll('.tab-btn').forEach((button) => {
  button.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach((btn) => btn.classList.toggle('active', btn === button));
    document.querySelectorAll('.panel').forEach((panel) => {
      panel.classList.toggle('active', panel.id === button.dataset.target);
    });
  });
});

const logoutBtn = document.getElementById('logoutBtn');
if (logoutBtn) {
  logoutBtn.addEventListener('click', async () => {
    try { await fetch('/api/logout', { method: 'POST' }); } catch (error) { console.error(error); }
    localStorage.removeItem('adminToken');
    window.location.href = '/admin/login.html';
  });
}

(async function init() {
  try {
    await api('/api/auth/check');
  } catch (error) {
    window.location.href = '/admin/login.html';
    return;
  }
  loadStats();
  loadProfile();
  loadExperiences();
  loadProjects();
  loadSkills();
})();
