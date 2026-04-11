(function () {
    // Função para obter o valor de um parâmetro da URL
    function getParameterByName(name, url) {
        if (!url) url = window.location.href;
        name = name.replace(/[\[\]]/g, "\\$&");
        var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
            results = regex.exec(url);
        if (!results) return null;
        if (!results[2]) return '';
        return decodeURIComponent(results[2].replace(/\+/g, " "));
    }

    // Função para definir um cookie
    function setCookie(cookieName, cookieValue, expirationTime) {
        var cookiePath = "/";
        expirationTime = expirationTime * 1000;
        var date = new Date();
        var dateTimeNow = date.getTime();
        date.setTime(dateTimeNow + expirationTime);
        var expirationDate = date.toUTCString();
        document.cookie = cookieName + "=" + cookieValue + "; expires=" + expirationDate + "; path=" + cookiePath;
    }

    // Função para obter o valor de um cookie pelo nome
    function getCookieValue(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }

    const adParams = ['fbclid', 'gclid', 'gbraid', 'wbraid', 'li_fat_id'];
    const urlParams = new URLSearchParams(window.location.search);
    let isAdClick = false;
    adParams.forEach(param => {
        if (urlParams.has(param)) {
            isAdClick = true;
        }
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

    let parametros = ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term"];
    const urlParamsCapt = new URLSearchParams(window.location.search);
    const urlParamsCaptReferrer = new URLSearchParams(document.referrer.split('?')[1] || '');
    let utms = {};

    const cookieUtmSource = getCookieValue('cookieUtmSource');
    const cookieUtmMedium = getCookieValue('cookieUtmMedium');
    const cookieUtmCampaign = getCookieValue('cookieUtmCampaign');
    const cookieUtmContent = getCookieValue('cookieUtmContent');
    const cookieUtmTerm = getCookieValue('cookieUtmTerm');

    // Domínio raiz do seu site (sem www, sem subdomínio)
    const meuDominio = "itvalleyschool.com";

    // Verifica se o referrer é do próprio site (qualquer subdomínio conta como auto-referência)
    let referrerValido = false;
    let referrerHostname = "";
    if (document.referrer) {
        try {
            referrerHostname = new URL(document.referrer).hostname;
            referrerValido = !referrerHostname.endsWith(meuDominio);
        } catch (e) {
            referrerValido = false;
        }
    }

    parametros.forEach(el => {
        if (el === "utm_source") {
            utms[el] = urlParamsCapt.get(el) ?? (referrerValido ? (urlParamsCaptReferrer.get(el) ?? referrerHostname) : "direto");
        } else {
            utms[el] = urlParamsCapt.get(el) ?? (referrerValido ? (urlParamsCaptReferrer.get(el) ?? "") : "");
        }
    });

    let scks = Object.values(utms).filter(value => value !== "");

    let currentSckValues = [];
    if (urlParamsCapt.get('sck')) {
        currentSckValues = urlParamsCapt.get('sck').split('|');
    }
    scks = scks.filter(value => !currentSckValues.includes(value));

    let srcValues = [cookieUtmSource, cookieUtmMedium, cookieUtmCampaign, cookieUtmContent, cookieUtmTerm].filter(value => value !== null && value !== "");

    const updateLinks = (el, elURL) => {
        const elSearchParams = new URLSearchParams(elURL.search);
        let modified = false;

        urlParams.forEach((value, key) => {
            if (!elSearchParams.has(key)) {
                elSearchParams.append(key, value);
                modified = true;
            }
        });

        for (let key in utms) {
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
            return elURL.origin + elURL.pathname + "?" + elSearchParams.toString();
        }
        return el.href;
    };

    // >>> MUDANÇA: reescreve o href no momento do clique, não no load
    // Usa captura (true) + mousedown/touchstart/click para rodar antes de qualquer outro handler
    function handleInteraction(e) {
        const el = e.target.closest('a');
        if (!el || !el.href) return;
        try {
            const elURL = new URL(el.href, window.location.origin);
            if (!elURL.hash) {
                el.href = updateLinks(el, elURL);
            }
        } catch (err) {
            console.warn('Erro ao processar URL no link:', el.href);
        }
    }

    document.addEventListener('mousedown', handleInteraction, true);
    document.addEventListener('touchstart', handleInteraction, true);
    document.addEventListener('click', handleInteraction, true);

})();
