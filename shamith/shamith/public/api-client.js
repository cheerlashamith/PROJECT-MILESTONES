(function () {
  const DEFAULT_TIMEOUT_MS = 30_000;

  async function parseResponse(response) {
    const contentType = response.headers.get('content-type') || '';
    let body;
    if (contentType.includes('application/json')) {
      body = await response.json();
    } else {
      const text = await response.text();
      // If it looks like HTML (e.g. Netlify 404), don't dump the whole HTML
      if (text.trim().startsWith('<') && text.includes('html>')) {
        body = { detail: "Backend API not reachable (Received HTML error page). If deployed on Netlify, the Python backend must be hosted separately." };
      } else {
        body = { detail: text };
      }
    }
    
    if (!response.ok) {
      const message = body.detail || body.message || `Request failed (${response.status})`;
      throw new Error(message);
    }
    return body;
  }

  async function request(url, options = {}, timeoutMs = DEFAULT_TIMEOUT_MS) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), timeoutMs);
    try {
      return await parseResponse(await fetch(url, { ...options, signal: controller.signal }));
    } catch (error) {
      if (error.name === 'AbortError') throw new Error('The backend request timed out.');
      throw error;
    } finally {
      clearTimeout(timeout);
    }
  }

  async function json(url, body, options = {}) {
    return request(url, {
      ...options,
      method: options.method || 'POST',
      headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
      body: JSON.stringify(body),
    });
  }

  async function waitForTask(taskId, options = {}) {
    const intervalMs = options.intervalMs || 1_000;
    const timeoutMs = options.timeoutMs || 10 * 60_000;
    const startedAt = Date.now();
    while (Date.now() - startedAt < timeoutMs) {
      const task = await request(`/api/tasks/${encodeURIComponent(taskId)}`);
      if (task.status === 'completed') return task.result !== undefined ? task.result : task.response;
      if (task.status === 'error') throw new Error(task.error || 'The AI task failed.');
      await new Promise(resolve => setTimeout(resolve, intervalMs));
    }
    throw new Error('The AI task did not finish before the timeout.');
  }

  async function submitTask(url, body, options = {}) {
    const task = await json(url, body, options);
    return waitForTask(task.task_id, options);
  }

  window.CIHApi = { request, json, waitForTask, submitTask };
})();