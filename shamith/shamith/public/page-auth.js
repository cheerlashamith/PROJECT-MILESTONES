import { getCurrentUserProfile, requireAuth } from './auth.js';

// Global Fetch Interceptor to catch Netlify 404 HTML errors on API routes
const originalFetch = window.fetch;
window.fetch = async function(...args) {
  const response = await originalFetch.apply(this, args);
  const url = typeof args[0] === 'string' ? args[0] : args[0]?.url || '';
  
  if (url.includes('/api/')) {
    const contentType = response.headers.get('content-type') || '';
    if (contentType.includes('text/html')) {
        const text = await response.clone().text();
        if (text.trim().startsWith('<') && text.includes('html>')) {
           return new Response(JSON.stringify({
               detail: "Backend API not reachable. If deployed on Netlify, the Python backend must be hosted separately.",
               message: "Backend API not reachable. If deployed on Netlify, the Python backend must be hosted separately."
           }), {
               status: 502,
               headers: { 'Content-Type': 'application/json' }
           });
        }
    }
  }
  return response;
};

// Internal pages include this module. Public landing and login pages do not.
requireAuth().catch(() => {
  window.location.replace('index.html');
});

function addNavigationItem(menu, href, icon, label, id = '') {
  if (menu.querySelector(`a[href="${href}"]`)) return;
  const link = document.createElement('a');
  link.href = href;
  link.className = 'menu-item';
  if (id) link.id = id;
  link.innerHTML = `<i class="fa-solid ${icon}"></i> ${label}`;
  menu.appendChild(link);
}

document.addEventListener('DOMContentLoaded', async () => {
  const menu = document.querySelector('.sidebar-menu');
  if (menu) {
    addNavigationItem(menu, 'theme-generator.html', 'fa-palette', 'Theme Visualizer');
    addNavigationItem(menu, 'compliance-agent.html', 'fa-clipboard-check', 'Compliance Agent');
    addNavigationItem(menu, 'insurance-agent.html', 'fa-shield-halved', 'Insurance Agent');
  }

  // Inject user profile into header if it doesn't exist
  const header = document.querySelector('header');
  if (header && !document.querySelector('.user-profile')) {
    header.style.display = 'flex';
    
    const spacer = document.createElement('div');
    spacer.style.flex = '1';
    header.appendChild(spacer);
    
    const profileContainer = document.createElement('div');
    profileContainer.className = 'user-profile';
    profileContainer.style.cssText = 'display: flex; align-items: center; gap: 10px; cursor: pointer; position: relative; margin-left: auto;';
    
    profileContainer.innerHTML = `
      <div style="text-align: right; display: flex; flex-direction: column;">
        <span id="globalUserEmail" style="font-size: 0.9rem; font-weight: 600; color: var(--text-main);">Loading...</span>
        <span style="font-size: 0.75rem; color: var(--text-muted);">User</span>
      </div>
      <div style="width: 40px; height: 40px; border-radius: 50%; background-color: var(--accent-primary); color: white; display: flex; align-items: center; justify-content: center; font-weight: 700;">
        <i class="fa-solid fa-user"></i>
      </div>
      <div id="globalProfileMenu" style="display: none; position: absolute; top: 55px; right: 0; background: white; border: 1px solid var(--border-color); border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: 150px; z-index: 1000; overflow: hidden;">
        <button id="globalLogoutBtn" style="width: 100%; padding: 12px; border: none; background: none; text-align: left; cursor: pointer; display: flex; align-items: center; gap: 10px; color: var(--text-main); transition: background 0.2s;" onmouseover="this.style.background='#f1f5f9'" onmouseout="this.style.background='none'"><i class="fa-solid fa-right-from-bracket" style="color: #ef4444;"></i> Sign Out</button>
      </div>
    `;
    
    header.appendChild(profileContainer);
    
    profileContainer.addEventListener('click', () => {
      const menu = document.getElementById('globalProfileMenu');
      menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
    });
    
    document.getElementById('globalLogoutBtn').addEventListener('click', async (e) => {
      e.stopPropagation(); // prevent toggling the menu
      const { supabase } = await import('./auth.js');
      await supabase.auth.signOut();
      window.location.href = 'index.html';
    });
  }

  try {
    const session = await requireAuth();
    if (session && session.user) {
      const emailEl = document.getElementById('globalUserEmail') || document.getElementById('userEmail');
      if (emailEl) {
        emailEl.innerText = session.user.email;
      }
    }
    const profile = await getCurrentUserProfile();
    if (profile?.is_admin && menu) {
      addNavigationItem(menu, 'admin-dashboard.html', 'fa-user-shield', 'Admin Dashboard');
    }
  } catch (_) {
    // Authentication redirection is handled above; optional admin navigation can fail closed.
  }
});