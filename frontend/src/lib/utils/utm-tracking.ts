export function trackUtms(): void {
  if (typeof window === 'undefined' || typeof document === 'undefined') return;

  function getParameterByName(name: string, url?: string): string | null {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, '\\$&');
    const regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)');
    const results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, ' '));
  }

  function setCookie(cookieName: string, cookieValue: string, expirationTime: number): void {
    const cookiePath = '/';
    const ms = expirationTime * 1000;
    const date = new Date();
    date.setTime(date.getTime() + ms);
    const expirationDate = date.toUTCString();
    document.cookie = `${cookieName}=${cookieValue}; expires=${expirationDate}; path=${cookiePath}`;
  }

  function getCookieValue(name: string): string | null {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop()!.split(';').shift() ?? null;
    return null;
  }

  const adParams = ['fbclid', 'gclid', 'gbraid', 'wbraid', 'li_fat_id'];

  const urlParams = new URLSearchParams(window.location.search);
  let isAdClick = false;
  adParams.forEach((param) => {
    if (urlParams.has(param)) isAdClick = true;
  });

  if (isAdClick) {
    const utmSource = getParameterByName('utm_source');
    const utmMedium = getParameterByName('utm_medium');
    const utmCampaign = getParameterByName('utm_campaign');
    const utmContent = getParameterByName('utm_content');
    const utmTerm = getParameterByName('utm_term');

    if (utmSource) setCookie('cookieUtmSource', utmSource, 63072000);
    if (utmMedium) setCookie('cookieUtmMedium', utmMedium, 63072000);
    if (utmCampaign) setCookie('cookieUtmCampaign', utmCampaign, 63072000);
    if (utmContent) setCookie('cookieUtmContent', utmContent, 63072000);
    if (utmTerm) setCookie('cookieUtmTerm', utmTerm, 63072000);
  }

  const parametros = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'];
  const urlParamsCapt = new URLSearchParams(window.location.search);
  const urlParamsCaptReferrer = new URLSearchParams(document.referrer.split('?')[1] || '');
  const utms: Record<string, string> = {};

  const cookieUtmSource = getCookieValue('cookieUtmSource');
  const cookieUtmMedium = getCookieValue('cookieUtmMedium');
  const cookieUtmCampaign = getCookieValue('cookieUtmCampaign');
  const cookieUtmContent = getCookieValue('cookieUtmContent');
  const cookieUtmTerm = getCookieValue('cookieUtmTerm');

  parametros.forEach((el) => {
    if (el === 'utm_source') {
      utms[el] =
        urlParamsCapt.get(el) ??
        (document.referrer
          ? urlParamsCaptReferrer.get(el) ?? new URL(document.referrer).hostname
          : 'direto');
    } else {
      utms[el] = urlParamsCapt.get(el) ?? urlParamsCaptReferrer.get(el) ?? '';
    }
  });

  let scks = Object.values(utms).filter((value) => value !== '');

  let currentSckValues: string[] = [];
  if (urlParamsCapt.get('sck')) {
    currentSckValues = urlParamsCapt.get('sck')!.split('|');
  }
  scks = scks.filter((value) => !currentSckValues.includes(value));

  const srcValues = [
    cookieUtmSource,
    cookieUtmMedium,
    cookieUtmCampaign,
    cookieUtmContent,
    cookieUtmTerm,
  ].filter((value): value is string => value !== null && value !== '');

  const updateLinks = (el: HTMLAnchorElement, elURL: URL): string => {
    const elSearchParams = new URLSearchParams(elURL.search);
    let modified = false;

    urlParams.forEach((value, key) => {
      if (!elSearchParams.has(key)) {
        elSearchParams.append(key, value);
        modified = true;
      }
    });

    for (const key in utms) {
      if (!elSearchParams.has(key)) {
        elSearchParams.append(key, utms[key]);
        modified = true;
      }
    }

    if (cookieUtmSource) elSearchParams.append('cookieUtmSource', cookieUtmSource);
    if (cookieUtmMedium) elSearchParams.append('cookieUtmMedium', cookieUtmMedium);
    if (cookieUtmCampaign) elSearchParams.append('cookieUtmCampaign', cookieUtmCampaign);
    if (cookieUtmContent) elSearchParams.append('cookieUtmContent', cookieUtmContent);
    if (cookieUtmTerm) elSearchParams.append('cookieUtmTerm', cookieUtmTerm);

    if (!elSearchParams.has('sck') && scks.length > 0) {
      elSearchParams.append('sck', scks.join('|'));
      modified = true;
    }

    if (!elSearchParams.has('src') && srcValues.length > 0) {
      elSearchParams.append('src', srcValues.join('|'));
      modified = true;
    }

    if (modified) {
      return elURL.origin + elURL.pathname + '?' + elSearchParams.toString();
    }
    return el.href;
  };

  document.querySelectorAll('a').forEach((el) => {
    try {
      const anchor = el as HTMLAnchorElement;
      const elURL = new URL(anchor.href, window.location.origin);
      if (!elURL.hash) {
        anchor.href = updateLinks(anchor, elURL);
      }
    } catch {
      console.warn('Erro ao processar URL no link:', (el as HTMLAnchorElement).href);
    }
  });
}
