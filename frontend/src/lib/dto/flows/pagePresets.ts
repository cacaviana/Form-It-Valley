import type { PageTemplate, PageContent } from './types';

export const PAGE_TEMPLATE_OPTIONS: { value: PageTemplate; label: string }[] = [
  { value: 'centered', label: 'Centralizada (fundo preto)' },
  { value: 'pos_ia', label: 'Pós IA' },
  { value: 'pos_dados', label: 'Pós Dados' }
];

export const PAGE_BACKGROUND_URL: Record<PageTemplate, string | null> = {
  centered: null,
  pos_ia: '/fundo_posIA.webp',
  pos_dados: '/fundo_posDADOS.webp'
};

const COMMON_BULLETS = [
  'Estágio Internacional Remoto',
  'Método PÓS 3X: A cada 3 disciplinas um novo certificado',
  'Comunidade de alunos com CEO da pós',
  'Disciplinas de acordo com o que o mercado exige'
];

const COMMON_HEADLINE = 'UM ECOSSISTEMA COMPLETO PARA FORMAR PROFISSIONAIS VALORIZADOS.';
const COMMON_HEADLINE_HIGHLIGHT = 'ECOSSISTEMA COMPLETO';
const COMMON_TOP_BANNER = 'PREENCHA O FORMULÁRIO E DESCUBRA MAIS INFORMAÇÕES LOGO ABAIXO.';
const COMMON_DISCIPLINES_TITLE = 'CONHEÇA NOSSAS DISCIPLINAS:';

export const PAGE_PRESETS: Record<PageTemplate, PageContent> = {
  centered: {},
  pos_ia: {
    topBannerText: COMMON_TOP_BANNER,
    headline: COMMON_HEADLINE,
    headlineHighlight: COMMON_HEADLINE_HIGHLIGHT,
    bullets: [...COMMON_BULLETS],
    disciplinesTitle: COMMON_DISCIPLINES_TITLE,
    disciplines: [
      'Programação aplicada a Ciência de Dados',
      'Extração, Transformação e Carregamento de Dados (ETL)',
      'Fundamentos de Aprendizado de Máquina',
      'Análise e modelagem preditiva',
      'Deep Learning',
      'Processamento de Linguagem Natural (NLP)',
      'IA generativa',
      'Cloud Computing para Machine Learning',
      'Modelos de Machine Learning em Produção'
    ]
  },
  pos_dados: {
    topBannerText: COMMON_TOP_BANNER,
    headline: COMMON_HEADLINE,
    headlineHighlight: COMMON_HEADLINE_HIGHLIGHT,
    bullets: [...COMMON_BULLETS],
    disciplinesTitle: COMMON_DISCIPLINES_TITLE,
    disciplines: [
      'Engenharia de dados em cloud',
      'Extração, Transformação e Carregamento de Dados (ETL)',
      'Programação para engenheiros e cientistas de dados',
      'Arquitetura e Infraestrutura em nuvem',
      'Bancos NoSQL',
      'IA generativa para engenheiros de dados',
      'DataOps',
      'Deep Learning',
      'Cloud Computing para Machine Learning'
    ]
  }
};

export function resolvePageContent(template: PageTemplate, custom?: PageContent | null): Required<PageContent> {
  const preset = PAGE_PRESETS[template] || {};
  const c = custom || {};
  return {
    topBannerText: c.topBannerText ?? preset.topBannerText ?? '',
    headline: c.headline ?? preset.headline ?? '',
    headlineHighlight: c.headlineHighlight ?? preset.headlineHighlight ?? '',
    bullets: c.bullets ?? preset.bullets ?? [],
    disciplinesTitle: c.disciplinesTitle ?? preset.disciplinesTitle ?? '',
    disciplines: c.disciplines ?? preset.disciplines ?? []
  };
}
