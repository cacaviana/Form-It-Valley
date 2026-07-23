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
