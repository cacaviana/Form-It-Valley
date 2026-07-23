/**
 * SSO Petra Suite — cookie `petra_sso` no dominio pai `.petrasuite.ai`.
 * O JSON do cookie tem o mesmo shape da sessao do portal (tokens + user +
 * tenant + products). Nao e HttpOnly de proposito (v1): os apps da suite
 * leem o cookie via JS para entrar logados sem novo login.
 */
const COOKIE_NAME = 'petra_sso';
const COOKIE_ATTRS = 'Domain=.petrasuite.ai; Path=/; Secure; SameSite=Lax';

function onPetraDomain(): boolean {
  return typeof location !== 'undefined' && location.hostname.endsWith('petrasuite.ai');
}

export function writeSsoCookie(sessionJson: string): void {
  if (!onPetraDomain()) return;
  document.cookie = `${COOKIE_NAME}=${encodeURIComponent(sessionJson)}; ${COOKIE_ATTRS}; Max-Age=28800`;
}

export function readSsoCookie(): string | null {
  if (typeof document === 'undefined') return null;
  const entry = document.cookie.split('; ').find((c) => c.startsWith(`${COOKIE_NAME}=`));
  if (!entry) return null;
  try {
    return decodeURIComponent(entry.slice(COOKIE_NAME.length + 1));
  } catch {
    return null;
  }
}

export function clearSsoCookie(): void {
  if (!onPetraDomain()) return;
  document.cookie = `${COOKIE_NAME}=; ${COOKIE_ATTRS}; Max-Age=0`;
}

/**
 * Tenta adotar a sessao do cookie petra_sso como sessao local do Calenda.
 * Retorna o access_token adotado, 'denied' se o plano nao inclui o Calenda,
 * ou null quando nao ha cookie utilizavel.
 */
export function tryAdoptSsoSession(): string | 'denied' | null {
  const raw = readSsoCookie();
  if (!raw) return null;
  try {
    const sso = JSON.parse(raw);
    if (!sso?.access_token) return null;
    const products: string[] = Array.isArray(sso.products) ? sso.products : [];
    const isMaster = sso.tenant?.is_master === true;
    if (!products.includes('calenda') && !isMaster) return 'denied';

    // Mesmo shape de sessao gravado pelo /login local.
    const sessionUser = {
      ...(sso.user ?? {}),
      tenant: sso.tenant ?? null,
      products,
      permissions: Array.isArray(sso.user?.permissions)
        ? sso.user.permissions
        : ['scheduling', 'flows', 'settings', 'users'],
      is_super_admin: isMaster || sso.user?.is_super_admin === true
    };
    localStorage.setItem('access_token', sso.access_token);
    if (sso.refresh_token) localStorage.setItem('refresh_token', sso.refresh_token);
    localStorage.setItem('user', JSON.stringify(sessionUser));
    return sso.access_token as string;
  } catch {
    return null;
  }
}
