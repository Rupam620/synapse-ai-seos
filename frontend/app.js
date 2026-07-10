(() => {
  'use strict';

  const els = {
    baseUrl: document.getElementById('base-url'),
    token: document.getElementById('jwt-token'),
    authPill: document.getElementById('auth-state-pill'),
    statusPill: document.getElementById('status-pill'),
    output: document.getElementById('response-output'),
    metaMethod: document.getElementById('meta-method'),
    metaPath: document.getElementById('meta-path'),
    metaStatus: document.getElementById('meta-status'),
    metaTime: document.getElementById('meta-time'),
    checkWwwAuth: document.getElementById('check-www-auth'),
    checkErrCode: document.getElementById('check-error-code'),
    checkLatency: document.getElementById('check-latency'),
    btnUseSample: document.getElementById('btn-use-sample'),
    btnClearToken: document.getElementById('btn-clear-token'),
    btnCopyToken: document.getElementById('btn-copy-token'),
    btnGenerateToken: document.getElementById('btn-generate-token'),
    btnHealth: document.getElementById('btn-health'),
    btnBacklog: document.getElementById('btn-backlog'),
    btnMe: document.getElementById('btn-me'),
    btnClearConsole: document.getElementById('btn-clear-console'),
    toastRegion: document.getElementById('toast-region'),
    claimSub: document.getElementById('claim-sub'),
    claimEmail: document.getElementById('claim-email'),
    claimName: document.getElementById('claim-name'),
    claimRoles: document.getElementById('claim-roles')
  };

  const state = {
    token: '',
    baseUrl: els.baseUrl.value.trim(),
    lastRequest: null
  };

  const ui = {
    setAuthState(isAuth) {
      els.authPill.className = `pill ${isAuth ? 'pill-ok' : 'pill-neutral'}`;
      els.authPill.textContent = isAuth ? 'Token Present' : 'Not Authenticated';
    },
    setStatus(kind, label) {
      const map = {
        idle: 'pill-neutral',
        ok: 'pill-ok',
        warn: 'pill-warn',
        err: 'pill-err'
      };
      els.statusPill.className = `pill ${map[kind] || map.idle}`;
      els.statusPill.textContent = label;
    },
    setMeta({ method = '-', path = '-', status = '-', time = '-' } = {}) {
      els.metaMethod.textContent = method;
      els.metaPath.textContent = path;
      els.metaStatus.textContent = status;
      els.metaTime.textContent = time;
    },
    setChecks({ wwwAuth = '-', errorCode = '-', latency = '-' } = {}) {
      els.checkWwwAuth.textContent = wwwAuth;
      els.checkErrCode.textContent = errorCode;
      els.checkLatency.textContent = latency;
    },
    writeOutput(data) {
      els.output.textContent = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
    },
    toast(message) {
      const item = document.createElement('div');
      item.className = 'toast';
      item.textContent = message;
      els.toastRegion.appendChild(item);
      setTimeout(() => item.remove(), 2200);
    }
  };

  const apiClient = {
    async request(method, path) {
      const start = performance.now();
      const baseUrl = state.baseUrl.replace(/\/$/, '');
      const url = `${baseUrl}${path}`;
      const headers = { 'Accept': 'application/json' };
      if (state.token.trim()) headers.Authorization = `Bearer ${state.token.trim()}`;

      const res = await fetch(url, { method, headers });
      const duration = `${Math.round(performance.now() - start)}ms`;
      let body;
      try {
        body = await res.json();
      } catch {
        body = await res.text();
      }

      return {
        ok: res.ok,
        status: res.status,
        headers: res.headers,
        body,
        duration,
        method,
        path
      };
    }
  };

  function base64UrlEncode(obj) {
    const raw = btoa(unescape(encodeURIComponent(JSON.stringify(obj))));
    return raw.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  }

  function makeMockJwt(payload) {
    const header = { alg: 'none', typ: 'JWT' };
    return `${base64UrlEncode(header)}.${base64UrlEncode(payload)}.`;
  }

  function updateTokenFromInput() {
    state.token = els.token.value.trim();
    ui.setAuthState(Boolean(state.token));
  }

  async function runRequest(method, path) {
    ui.setStatus('warn', 'Loading...');
    ui.setMeta({ method, path, status: '...', time: '...' });
    ui.setChecks({});

    try {
      const result = await apiClient.request(method, path);
      const wwwAuth = result.headers.get('www-authenticate') || '-';
      const errorCode = result.body && typeof result.body === 'object'
        ? (result.body.code || result.body.detail?.code || '-')
        : '-';

      ui.setMeta({
        method: result.method,
        path: result.path,
        status: String(result.status),
        time: result.duration
      });
      ui.setChecks({
        wwwAuth,
        errorCode,
        latency: result.duration
      });
      ui.writeOutput(result.body);

      if (result.ok) {
        ui.setStatus('ok', 'Success');
      } else if (result.status === 401) {
        ui.setStatus('warn', 'Unauthorized');
      } else {
        ui.setStatus('err', `HTTP ${result.status}`);
      }

      ui.toast(`Request completed: ${method} ${path} (${result.status})`);
    } catch (err) {
      ui.setStatus('err', 'Network Error');
      ui.setMeta({ method, path, status: 'ERR', time: '-' });
      ui.writeOutput({ error: String(err?.message || err) });
      ui.toast('Network request failed');
    }
  }

  function attachEvents() {
    els.baseUrl.addEventListener('change', () => {
      state.baseUrl = els.baseUrl.value.trim();
      ui.toast('Base URL updated');
    });

    els.token.addEventListener('input', updateTokenFromInput);

    els.btnUseSample.addEventListener('click', () => {
      const now = Math.floor(Date.now() / 1000);
      const token = makeMockJwt({
        sub: 'sample-user',
        email: 'sample@synapse.ai',
        name: 'Sample User',
        roles: ['viewer'],
        exp: now + 3600
      });
      els.token.value = token;
      updateTokenFromInput();
      ui.toast('Sample token applied');
    });

    els.btnGenerateToken.addEventListener('click', () => {
      const now = Math.floor(Date.now() / 1000);
      const roles = els.claimRoles.value.split(',').map(x => x.trim()).filter(Boolean);
      const payload = {
        sub: els.claimSub.value.trim() || 'user-123',
        email: els.claimEmail.value.trim() || undefined,
        name: els.claimName.value.trim() || undefined,
        roles,
        exp: now + 3600
      };
      const token = makeMockJwt(payload);
      els.token.value = token;
      updateTokenFromInput();
      ui.writeOutput({ info: 'Mock unsigned JWT generated in browser.', payload });
      ui.toast('Mock JWT generated');
    });

    els.btnClearToken.addEventListener('click', () => {
      els.token.value = '';
      updateTokenFromInput();
      ui.toast('Token cleared');
    });

    els.btnCopyToken.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(els.token.value || '');
        ui.toast('Token copied');
      } catch {
        ui.toast('Clipboard unavailable');
      }
    });

    els.btnHealth.addEventListener('click', () => runRequest('GET', '/health'));
    els.btnBacklog.addEventListener('click', () => runRequest('GET', '/backlog'));
    els.btnMe.addEventListener('click', () => runRequest('GET', '/users/me'));

    els.btnClearConsole.addEventListener('click', () => {
      ui.writeOutput('Ready.');
      ui.setMeta();
      ui.setChecks();
      ui.setStatus('idle', 'Idle');
    });
  }

  function init() {
    updateTokenFromInput();
    ui.setStatus('idle', 'Idle');
    ui.setMeta();
    ui.setChecks();
    ui.writeOutput({
      tips: [
        'Set API Base URL if different from localhost:8000.',
        'Use GET /health for public endpoint validation.',
        'Use GET /backlog and GET /users/me to verify JWT protection.'
      ]
    });
    attachEvents();
  }

  init();
})();
