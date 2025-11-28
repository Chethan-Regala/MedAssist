(function(){
  const $ = (id) => document.getElementById(id);
  const out = (el, data) => el.textContent = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
  const storageKey = 'medassist.baseUrl';
  const defaultBase = 'http://127.0.0.1:8000';

  const baseUrlInput = $('baseUrl');
  baseUrlInput.value = localStorage.getItem(storageKey) || baseUrlInput.value || defaultBase;
  $('saveBase').onclick = () => localStorage.setItem(storageKey, baseUrlInput.value);

  const api = (path) => `${baseUrlInput.value.replace(/\/$/, '')}${path}`;

  $('doTriage').onclick = async () => {
    const payload = {
      user_id: $('triageUser').value.trim() || 'demo-user',
      symptoms: $('symptoms').value.trim(),
      context: $('context').value.trim() || null
    };
    out($('triageOut'), 'Running...');
    try {
      const res = await fetch(api('/triage'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      out($('triageOut'), data);
    } catch (e) {
      out($('triageOut'), String(e));
    }
  };

  $('checkMeds').onclick = async () => {
    const meds = $('meds').value.split(',').map(s => s.trim()).filter(Boolean);
    const payload = { user_id: $('medUser').value.trim() || 'demo-user', medications: meds };
    out($('medOut'), 'Checking...');
    try {
      const res = await fetch(api('/medications/check'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      out($('medOut'), data);
    } catch (e) {
      out($('medOut'), String(e));
    }
  };

  $('pause').onclick = () => simplePost('/reminders/pause', $('remStatus'));
  $('resume').onclick = () => simplePost('/reminders/resume', $('remStatus'));
  $('status').onclick = () => simpleGet('/reminders/status', $('remStatus'));

  async function simplePost(path, dest) {
    out(dest, 'Sending...');
    try {
      const res = await fetch(api(path), { method: 'POST' });
      out(dest, await res.json());
    } catch (e) { out(dest, String(e)); }
  }
  async function simpleGet(path, dest) {
    out(dest, 'Fetching...');
    try {
      const res = await fetch(api(path));
      out(dest, await res.json());
    } catch (e) { out(dest, String(e)); }
  }
})();
