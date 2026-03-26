// ══════════════════════════════════════════════════════════
// FlowQuote i18n — centralized translations
// Default language: French (fr)
// Supported: fr, pt, en, es
// ══════════════════════════════════════════════════════════

export type Lang = 'fr' | 'pt' | 'en' | 'es';

let currentLang: Lang = (typeof localStorage !== 'undefined' && localStorage.getItem('fq_lang') as Lang) || 'fr';

export function getLang(): Lang { return currentLang; }

export function setLang(lang: Lang) {
  currentLang = lang;
  if (typeof localStorage !== 'undefined') localStorage.setItem('fq_lang', lang);
}

// Shortcut translator
export function t(key: string): string {
  return translations[key]?.[currentLang] || translations[key]?.['fr'] || key;
}

// ── All translations ──────────────────────────────────────
export const translations: Record<string, Record<Lang, string>> = {

  // ═══ COMMON / SHARED ═══
  loading: { fr: 'Chargement...', pt: 'Carregando...', en: 'Loading...', es: 'Cargando...' },
  save: { fr: 'Enregistrer', pt: 'Salvar', en: 'Save', es: 'Guardar' },
  saving: { fr: 'Enregistrement...', pt: 'Salvando...', en: 'Saving...', es: 'Guardando...' },
  saved: { fr: 'Enregistré !', pt: 'Salvo!', en: 'Saved!', es: '¡Guardado!' },
  cancel: { fr: 'Annuler', pt: 'Cancelar', en: 'Cancel', es: 'Cancelar' },
  close: { fr: 'Fermer', pt: 'Fechar', en: 'Close', es: 'Cerrar' },
  edit: { fr: 'Éditer', pt: 'Editar', en: 'Edit', es: 'Editar' },
  delete: { fr: 'Supprimer', pt: 'Excluir', en: 'Delete', es: 'Eliminar' },
  back: { fr: 'Retour', pt: 'Voltar', en: 'Back', es: 'Volver' },
  next: { fr: 'Suivant', pt: 'Próximo', en: 'Next', es: 'Siguiente' },
  start: { fr: 'Commencer', pt: 'Começar', en: 'Start', es: 'Empezar' },
  preview: { fr: 'Aperçu', pt: 'Preview', en: 'Preview', es: 'Vista previa' },
  link: { fr: 'Lien', pt: 'Link', en: 'Link', es: 'Enlace' },
  error: { fr: 'Erreur', pt: 'Erro', en: 'Error', es: 'Error' },
  or: { fr: 'ou', pt: 'ou', en: 'or', es: 'o' },
  yes: { fr: 'Oui', pt: 'Sim', en: 'Yes', es: 'Sí' },
  no: { fr: 'Non', pt: 'Não', en: 'No', es: 'No' },
  continue: { fr: 'Continuer', pt: 'Continuar', en: 'Continue', es: 'Continuar' },
  confirm: { fr: 'Confirmer', pt: 'Confirmar', en: 'Confirm', es: 'Confirmar' },

  // ═══ HOME PAGE ═══
  homeSubtitle: { fr: 'Constructeur Visuel de Devis avec IA', pt: 'Construtor Visual de Orçamentos com IA', en: 'Visual Quote Builder with AI', es: 'Constructor Visual de Presupuestos con IA' },
  adminPanel: { fr: 'Panneau Admin', pt: 'Painel Admin', en: 'Admin Panel', es: 'Panel Admin' },
  viewDemo: { fr: 'Voir Questionnaire Démo', pt: 'Ver Questionário Demo', en: 'View Demo Questionnaire', es: 'Ver Cuestionario Demo' },
  schedulingMode: { fr: 'Mode Rendez-vous', pt: 'Modo Agendamento', en: 'Scheduling Mode', es: 'Modo Agendamiento' },
  creating: { fr: 'Création...', pt: 'Criando...', en: 'Creating...', es: 'Creando...' },

  // ═══ FLOWS DASHBOARD ═══
  myFlows: { fr: 'Mes Flux', pt: 'Meus Fluxos', en: 'My Flows', es: 'Mis Flujos' },
  training: { fr: 'Formation', pt: 'Treinamento', en: 'Training', es: 'Capacitación' },
  scheduling: { fr: 'Rendez-vous', pt: 'Agendamentos', en: 'Scheduling', es: 'Agendamientos' },
  aiSettings: { fr: 'IA', pt: 'IA', en: 'AI', es: 'IA' },
  submissions: { fr: 'Demandes', pt: 'Demandas', en: 'Submissions', es: 'Solicitudes' },
  newFlow: { fr: '+ Nouveau Flux', pt: '+ Novo Fluxo', en: '+ New Flow', es: '+ Nuevo Flujo' },
  noFlowsYet: { fr: 'Aucun flux créé', pt: 'Nenhum fluxo criado ainda', en: 'No flows created yet', es: 'Ningún flujo creado aún' },
  createFirst: { fr: 'Créer le premier flux', pt: 'Criar primeiro fluxo', en: 'Create first flow', es: 'Crear primer flujo' },
  nodes: { fr: 'nœuds', pt: 'nós', en: 'nodes', es: 'nodos' },
  confirmDeleteFlow: { fr: 'Supprimer le flux', pt: 'Apagar o fluxo', en: 'Delete the flow', es: 'Eliminar el flujo' },
  confirmDeleteSuffix: { fr: '? Cette action est irréversible.', pt: '? Esta ação não pode ser desfeita.', en: '? This action cannot be undone.', es: '? Esta acción no se puede deshacer.' },

  // Status labels
  draft: { fr: 'Brouillon', pt: 'Rascunho', en: 'Draft', es: 'Borrador' },
  published: { fr: 'Publié', pt: 'Publicado', en: 'Published', es: 'Publicado' },
  archived: { fr: 'Archivé', pt: 'Arquivado', en: 'Archived', es: 'Archivado' },

  // ═══ FLOW EDITOR ═══
  unsavedChanges: { fr: 'Modifications non enregistrées', pt: 'Alterações não salvas', en: 'Unsaved changes', es: 'Cambios sin guardar' },
  uploadCsv: { fr: 'Envoyer catalogue de prix (CSV)', pt: 'Enviar tabela de preços (CSV)', en: 'Upload price list (CSV)', es: 'Subir tabla de precios (CSV)' },
  csvLoaded: { fr: 'CSV chargé', pt: 'CSV carregado', en: 'CSV loaded', es: 'CSV cargado' },
  priceCsv: { fr: 'Prix (CSV)', pt: 'Preços (CSV)', en: 'Prices (CSV)', es: 'Precios (CSV)' },
  viewAgent: { fr: 'Voir la configuration de l\'agent IA', pt: 'Ver configuração do agente IA', en: 'View AI agent configuration', es: 'Ver configuración del agente IA' },
  agent: { fr: 'Agent', pt: 'Agente', en: 'Agent', es: 'Agente' },
  viewQuestionnaire: { fr: 'Visualiser le questionnaire', pt: 'Visualizar questionário', en: 'View questionnaire', es: 'Visualizar cuestionario' },

  // CSV Modal
  csvTitle: { fr: 'Catalogue de prix (CSV)', pt: 'Catálogo de preços (CSV)', en: 'Price Catalogue (CSV)', es: 'Catálogo de precios (CSV)' },
  csvDesc: { fr: 'Envoyez votre fichier CSV avec les produits et prix. L\'IA utilisera ce catalogue pour générer les devis.', pt: 'Envie seu arquivo CSV com produtos e preços. A IA usará este catálogo para gerar os orçamentos.', en: 'Upload your CSV file with products and prices. The AI will use this catalogue to generate quotes.', es: 'Suba su archivo CSV con productos y precios. La IA usará este catálogo para generar los presupuestos.' },
  csvDownloadTemplate: { fr: 'Télécharger le modèle', pt: 'Baixar modelo', en: 'Download template', es: 'Descargar plantilla' },
  csvDownloadHint: { fr: 'Téléchargez le modèle CSV pour voir le format attendu', pt: 'Baixe o modelo CSV para ver o formato esperado', en: 'Download the CSV template to see the expected format', es: 'Descargue la plantilla CSV para ver el formato esperado' },
  csvDragHere: { fr: 'Glissez votre fichier CSV ici', pt: 'Arraste seu arquivo CSV aqui', en: 'Drag your CSV file here', es: 'Arrastre su archivo CSV aquí' },
  csvChooseFile: { fr: 'Choisir un fichier', pt: 'Escolher arquivo', en: 'Choose a file', es: 'Elegir archivo' },
  csvFormat: { fr: 'Format: produit,prix,unité,catégorie', pt: 'Formato: produto,preço,unidade,categoria', en: 'Format: product,price,unit,category', es: 'Formato: producto,precio,unidad,categoría' },
  csvPreview: { fr: 'Aperçu du catalogue', pt: 'Pré-visualização do catálogo', en: 'Catalogue preview', es: 'Vista previa del catálogo' },
  csvProducts: { fr: 'produits', pt: 'produtos', en: 'products', es: 'productos' },
  csvAlreadyLoaded: { fr: 'CSV déjà chargé', pt: 'CSV já carregado', en: 'CSV already loaded', es: 'CSV ya cargado' },
  csvRemove: { fr: 'Supprimer CSV', pt: 'Remover CSV', en: 'Remove CSV', es: 'Eliminar CSV' },

  // Agent Modal
  agentTitle: { fr: 'Agent IA', pt: 'Agente IA', en: 'AI Agent', es: 'Agente IA' },
  agentReadonly: { fr: 'Configuration en lecture seule', pt: 'Configuração somente leitura', en: 'Read-only configuration', es: 'Configuración de solo lectura' },
  agentModel: { fr: 'Modèle', pt: 'Modelo', en: 'Model', es: 'Modelo' },
  agentPrompt: { fr: 'Prompt (Instructions système)', pt: 'Prompt (Instruções do sistema)', en: 'Prompt (System instructions)', es: 'Prompt (Instrucciones del sistema)' },
  agentSchema: { fr: 'Schéma de sortie (Output parsing)', pt: 'Schema de saída (Output parsing)', en: 'Output schema (Output parsing)', es: 'Esquema de salida (Output parsing)' },
  agentInfo: { fr: 'Ce sont les paramètres actuels de l\'agent IA. Pour modifier, changez dans la page Paramètres.', pt: 'Estes são os parâmetros atuais do agente IA. Para modificar, vá em Configurações.', en: 'These are the current AI agent settings. To modify, go to Settings.', es: 'Estos son los parámetros actuales del agente IA. Para modificar, vaya a Configuraciones.' },

  // ═══ PREVIEW PAGE ═══
  previewTitle: { fr: 'Aperçu :', pt: 'Preview:', en: 'Preview:', es: 'Vista previa:' },
  previewSubtitle: { fr: 'Simulation du questionnaire — comme le client le verra', pt: 'Simulação do questionário — como o cliente vai ver', en: 'Questionnaire simulation — how the client will see it', es: 'Simulación del cuestionario — como el cliente lo verá' },
  restart: { fr: 'Recommencer', pt: 'Recomeçar', en: 'Restart', es: 'Reiniciar' },
  editFlow: { fr: 'Éditer le flux', pt: 'Editar fluxo', en: 'Edit flow', es: 'Editar flujo' },
  publicLink: { fr: 'Lien public', pt: 'Link público', en: 'Public link', es: 'Enlace público' },
  collectedData: { fr: 'Données collectées', pt: 'Dados coletados', en: 'Collected data', es: 'Datos recopilados' },
  client: { fr: 'Client', pt: 'Cliente', en: 'Client', es: 'Cliente' },
  name: { fr: 'Nom', pt: 'Nome', en: 'Name', es: 'Nombre' },
  email: { fr: 'E-mail', pt: 'E-mail', en: 'E-mail', es: 'E-mail' },
  phone: { fr: 'Téléphone', pt: 'Telefone', en: 'Phone', es: 'Teléfono' },
  address: { fr: 'Adresse', pt: 'Endereço', en: 'Address', es: 'Dirección' },
  answers: { fr: 'Réponses', pt: 'Respostas', en: 'Answers', es: 'Respuestas' },
  noAnswersYet: { fr: 'Aucune réponse. Lancez la simulation.', pt: 'Nenhuma resposta ainda. Inicie a simulação.', en: 'No answers yet. Start the simulation.', es: 'Sin respuestas aún. Inicie la simulación.' },
  flowInfo: { fr: 'Info du flux', pt: 'Info do fluxo', en: 'Flow info', es: 'Info del flujo' },
  connections: { fr: 'Connexions', pt: 'Conexões', en: 'Connections', es: 'Conexiones' },
  status: { fr: 'Statut', pt: 'Status', en: 'Status', es: 'Estado' },
  version: { fr: 'Version', pt: 'Versão', en: 'Version', es: 'Versión' },

  // ═══ PUBLIC QUESTIONNAIRE ═══
  questionnaireNotFound: { fr: 'Questionnaire non trouvé', pt: 'Questionário não encontrado', en: 'Questionnaire not found', es: 'Cuestionario no encontrado' },
  getQuoteInMinutes: { fr: 'Obtenez votre devis en quelques minutes', pt: 'Receba seu orçamento em minutos', en: 'Get your quote in minutes', es: 'Reciba su presupuesto en minutos' },
  enterNumber: { fr: 'Entrez un nombre', pt: 'Digite um número', en: 'Enter a number', es: 'Ingrese un número' },
  yourAnswer: { fr: 'Votre réponse', pt: 'Sua resposta', en: 'Your answer', es: 'Su respuesta' },
  generatingQuote: { fr: 'Génération de votre devis...', pt: 'Gerando seu orçamento...', en: 'Generating your quote...', es: 'Generando su presupuesto...' },
  aiAnalyzing: { fr: 'Notre IA analyse vos besoins et calcule le meilleur prix', pt: 'Nossa IA analisa suas necessidades e calcula o melhor preço', en: 'Our AI analyzes your needs and calculates the best price', es: 'Nuestra IA analiza sus necesidades y calcula el mejor precio' },
  quoteReady: { fr: 'Votre devis est prêt !', pt: 'Seu orçamento está pronto!', en: 'Your quote is ready!', es: '¡Su presupuesto está listo!' },
  thankYou: { fr: 'Merci pour vos réponses !', pt: 'Obrigado pelas respostas!', en: 'Thank you for your answers!', es: '¡Gracias por sus respuestas!' },
  dataRecorded: { fr: 'Vos données ont été enregistrées. Nous vous contacterons sous 24h.', pt: 'Seus dados foram registrados. Entraremos em contato em 24h.', en: 'Your data has been recorded. We will contact you within 24h.', es: 'Sus datos fueron registrados. Le contactaremos en 24h.' },
  printPdf: { fr: 'Imprimer / PDF', pt: 'Imprimir / PDF', en: 'Print / PDF', es: 'Imprimir / PDF' },
  submissionError: { fr: 'Erreur lors de l\'envoi. Veuillez réessayer.', pt: 'Erro ao enviar. Tente novamente.', en: 'Error sending. Please try again.', es: 'Error al enviar. Intente de nuevo.' },
  requestRecorded: { fr: 'Votre demande a été enregistrée. Merci !', pt: 'Sua solicitação foi registrada. Obrigado!', en: 'Your request has been recorded. Thank you!', es: '¡Su solicitud fue registrada. ¡Gracias!' },
  requestFallback: { fr: 'Votre demande a été enregistrée. Un spécialiste vous contactera.', pt: 'Sua solicitação foi registrada. Um especialista entrará em contato.', en: 'Your request has been recorded. A specialist will contact you.', es: 'Su solicitud fue registrada. Un especialista le contactará.' },

  // Quote card
  quoteEstimate: { fr: 'Devis estimatif', pt: 'Orçamento estimado', en: 'Estimated quote', es: 'Presupuesto estimado' },
  productService: { fr: 'Produit / Service', pt: 'Produto / Serviço', en: 'Product / Service', es: 'Producto / Servicio' },
  qty: { fr: 'Qté', pt: 'Qtd', en: 'Qty', es: 'Cant' },
  price: { fr: 'Prix', pt: 'Preço', en: 'Price', es: 'Precio' },
  subtotal: { fr: 'Sous-total', pt: 'Subtotal', en: 'Subtotal', es: 'Subtotal' },
  total: { fr: 'Total', pt: 'Total', en: 'Total', es: 'Total' },
  toConsult: { fr: 'À consulter', pt: 'A consultar', en: 'To be quoted', es: 'A consultar' },
  recommendations: { fr: 'Recommandations', pt: 'Recomendações', en: 'Recommendations', es: 'Recomendaciones' },
  notes: { fr: 'Notes', pt: 'Notas', en: 'Notes', es: 'Notas' },
  validity: { fr: 'Validité: 30 jours', pt: 'Validade: 30 dias', en: 'Validity: 30 days', es: 'Validez: 30 días' },
  freeInspection: { fr: 'Inspection gratuite', pt: 'Inspeção gratuita', en: 'Free inspection', es: 'Inspección gratuita' },
  warranty: { fr: 'Garantie 2 ans', pt: 'Garantia 2 anos', en: '2-year warranty', es: 'Garantía 2 años' },
  permitsIncluded: { fr: 'Permis inclus', pt: 'Licenças incluídas', en: 'Permits included', es: 'Permisos incluidos' },

  // ═══ SCHEDULING (in questionnaire) ═══
  chooseDay: { fr: 'Choisissez le jour', pt: 'Escolha o dia', en: 'Choose the day', es: 'Elija el día' },
  selectAvailableDate: { fr: 'Sélectionnez une date disponible', pt: 'Selecione uma data disponível', en: 'Select an available date', es: 'Seleccione una fecha disponible' },
  chooseTime: { fr: 'Choisissez l\'heure', pt: 'Escolha o horário', en: 'Choose the time', es: 'Elija el horario' },
  morning: { fr: 'Matin', pt: 'Manhã', en: 'Morning', es: 'Mañana' },
  afternoon: { fr: 'Après-midi', pt: 'Tarde', en: 'Afternoon', es: 'Tarde' },
  noSlotsAvailable: { fr: 'Aucun horaire disponible', pt: 'Nenhum horário disponível', en: 'No time slots available', es: 'Ningún horario disponible' },
  confirmBooking: { fr: 'Confirmez votre rendez-vous', pt: 'Confirme seu agendamento', en: 'Confirm your booking', es: 'Confirme su agendamiento' },
  reviewData: { fr: 'Vérifiez les données avant de confirmer', pt: 'Verifique os dados antes de confirmar', en: 'Review the data before confirming', es: 'Verifique los datos antes de confirmar' },
  confirmScheduling: { fr: 'Confirmer le rendez-vous', pt: 'Confirmar agendamento', en: 'Confirm booking', es: 'Confirmar agendamiento' },
  bookingDone: { fr: 'Rendez-vous confirmé !', pt: 'Agendamento confirmado!', en: 'Booking confirmed!', es: '¡Agendamiento confirmado!' },
  backToCalendar: { fr: 'Retour au calendrier', pt: 'Voltar ao calendário', en: 'Back to calendar', es: 'Volver al calendario' },
  date: { fr: 'Date', pt: 'Data', en: 'Date', es: 'Fecha' },
  time: { fr: 'Heure', pt: 'Horário', en: 'Time', es: 'Horario' },
  scheduling2: { fr: 'Planification...', pt: 'Agendando...', en: 'Scheduling...', es: 'Agendando...' },

  // ═══ SETTINGS PAGE ═══
  settingsTitle: { fr: 'Paramètres IA', pt: 'Configurações de IA', en: 'AI Settings', es: 'Configuraciones de IA' },
  aiModel: { fr: 'Modèle IA', pt: 'Modelo de IA', en: 'AI Model', es: 'Modelo de IA' },
  aiModelDesc: { fr: 'Choisissez le fournisseur et le modèle utilisés pour générer les devis.', pt: 'Escolha o provedor e modelo usado para gerar os orçamentos.', en: 'Choose the provider and model used to generate quotes.', es: 'Elija el proveedor y modelo usado para generar presupuestos.' },
  provider: { fr: 'Fournisseur', pt: 'Provedor', en: 'Provider', es: 'Proveedor' },
  model: { fr: 'Modèle', pt: 'Modelo', en: 'Model', es: 'Modelo' },
  savedSettings: { fr: 'Enregistré ! Le prochain devis utilisera ce modèle.', pt: 'Salvo! O próximo orçamento usará este modelo.', en: 'Saved! The next quote will use this model.', es: '¡Guardado! El próximo presupuesto usará este modelo.' },

  // ═══ SUBMISSIONS PAGE ═══
  submissionsTitle: { fr: 'Demandes de devis', pt: 'Demandas de orçamento', en: 'Quote requests', es: 'Solicitudes de presupuesto' },
  submissionsCount: { fr: 'soumission(s) au total', pt: 'solicitação(ões) no total', en: 'submission(s) total', es: 'solicitud(es) en total' },
  noSubmissions: { fr: 'Aucune demande pour le moment.', pt: 'Nenhuma solicitação no momento.', en: 'No submissions yet.', es: 'Ninguna solicitud por el momento.' },
  noSubmissionsHint: { fr: 'Les soumissions apparaîtront ici quand les clients rempliront un questionnaire.', pt: 'As solicitações aparecerão aqui quando os clientes preencherem um questionário.', en: 'Submissions will appear here when clients fill out a questionnaire.', es: 'Las solicitudes aparecerán aquí cuando los clientes llenen un cuestionario.' },
  view: { fr: 'Voir', pt: 'Ver', en: 'View', es: 'Ver' },
  export: { fr: 'Exporter', pt: 'Exportar', en: 'Export', es: 'Exportar' },
  exportSave: { fr: 'Exporter & Sauvegarder', pt: 'Exportar e Salvar', en: 'Export & Save', es: 'Exportar y Guardar' },
  exportHint: { fr: 'Télécharger et sauvegarder localement', pt: 'Baixar e salvar localmente', en: 'Download and save locally', es: 'Descargar y guardar localmente' },
  quote: { fr: 'Devis', pt: 'Orçamento', en: 'Quote', es: 'Presupuesto' },
  specialist: { fr: 'Spécialiste', pt: 'Especialista', en: 'Specialist', es: 'Especialista' },
  thankYouType: { fr: 'Merci', pt: 'Obrigado', en: 'Thank you', es: 'Gracias' },
  actions: { fr: 'Actions', pt: 'Ações', en: 'Actions', es: 'Acciones' },
  flow: { fr: 'Flux', pt: 'Fluxo', en: 'Flow', es: 'Flujo' },
  type: { fr: 'Type', pt: 'Tipo', en: 'Type', es: 'Tipo' },
  generatedByAi: { fr: '✓IA', pt: '✓IA', en: '✓AI', es: '✓IA' },

  // Submission detail
  submissionDetail: { fr: 'Détail de la demande', pt: 'Detalhe da solicitação', en: 'Submission detail', es: 'Detalle de la solicitud' },
  generatedQuote: { fr: 'Devis généré par IA', pt: 'Orçamento gerado por IA', en: 'AI-generated quote', es: 'Presupuesto generado por IA' },
  result: { fr: 'Résultat', pt: 'Resultado', en: 'Result', es: 'Resultado' },
  generated: { fr: 'Généré', pt: 'Gerado', en: 'Generated', es: 'Generado' },
  noQuoteGenerated: { fr: 'Aucun devis généré pour cette demande.', pt: 'Nenhum orçamento gerado para esta solicitação.', en: 'No quote generated for this submission.', es: 'Ningún presupuesto generado para esta solicitud.' },

  // ═══ SCHEDULING DASHBOARD ═══
  schedulingTitle: { fr: 'Rendez-vous', pt: 'Agendamentos', en: 'Scheduling', es: 'Agendamientos' },
  schedulingSubtitle: { fr: 'Flux de rendez-vous et réservations', pt: 'Fluxos de agendamento e reservas', en: 'Scheduling flows and bookings', es: 'Flujos de agendamiento y reservas' },
  quotes: { fr: 'Devis', pt: 'Orçamentos', en: 'Quotes', es: 'Presupuestos' },
  newScheduling: { fr: '+ Nouveau rendez-vous', pt: '+ Novo Agendamento', en: '+ New Booking', es: '+ Nuevo Agendamiento' },
  flows: { fr: 'Flux', pt: 'Fluxos', en: 'Flows', es: 'Flujos' },
  bookings: { fr: 'Réservations', pt: 'Reservas', en: 'Bookings', es: 'Reservas' },
  totalFlows: { fr: 'Total de flux', pt: 'Total de fluxos', en: 'Total flows', es: 'Total de flujos' },
  totalBookings: { fr: 'Total réservations', pt: 'Total reservas', en: 'Total bookings', es: 'Total reservas' },
  noSchedulingFlows: { fr: 'Aucun flux de rendez-vous', pt: 'Nenhum fluxo de agendamento', en: 'No scheduling flows', es: 'Ningún flujo de agendamiento' },
  noBookingsYet: { fr: 'Aucune réservation', pt: 'Nenhuma reserva ainda', en: 'No bookings yet', es: 'Sin reservas aún' },
  lead: { fr: 'Lead', pt: 'Lead', en: 'Lead', es: 'Lead' },
  contact: { fr: 'Contact', pt: 'Contato', en: 'Contact', es: 'Contacto' },
  dateTime: { fr: 'Date / Heure', pt: 'Data / Hora', en: 'Date / Time', es: 'Fecha / Hora' },
  confirmed: { fr: 'Confirmé', pt: 'Confirmado', en: 'Confirmed', es: 'Confirmado' },
  cancelled: { fr: 'Annulé', pt: 'Cancelado', en: 'Cancelled', es: 'Cancelado' },

  // ═══ NODE BUILDER ═══
  startNode: { fr: 'Début', pt: 'Início', en: 'Start', es: 'Inicio' },
  collectsInfo: { fr: 'Collecte nom, email, téléphone', pt: 'Coleta nome, email, telefone', en: 'Collects name, email, phone', es: 'Recopila nombre, email, teléfono' },
  questionNode: { fr: 'Question', pt: 'Pergunta', en: 'Question', es: 'Pregunta' },
  messageNode: { fr: 'Message', pt: 'Mensagem', en: 'Message', es: 'Mensaje' },
  endNode: { fr: 'Fin', pt: 'Fim', en: 'End', es: 'Fin' },
  add: { fr: 'Ajouter :', pt: 'Adicionar:', en: 'Add:', es: 'Agregar:' },

  // End types
  endQuote: { fr: 'Génère un devis via IA', pt: 'Gera orçamento via IA', en: 'Generates quote via AI', es: 'Genera presupuesto via IA' },
  endSpecialist: { fr: 'Redirige vers un spécialiste', pt: 'Encaminha para contato', en: 'Redirects to specialist', es: 'Redirige a especialista' },
  endThankYou: { fr: 'Message de remerciement', pt: 'Mensagem de agradecimento', en: 'Thank you message', es: 'Mensaje de agradecimiento' },
  endScheduling: { fr: 'Rendez-vous (calendrier)', pt: 'Agendamento no calendário', en: 'Scheduling (calendar)', es: 'Agendamiento (calendario)' },

  // Question types
  singleChoice: { fr: 'Choix unique', pt: 'Escolha única', en: 'Single choice', es: 'Opción única' },
  yesNo: { fr: 'Oui / Non', pt: 'Sim / Não', en: 'Yes / No', es: 'Sí / No' },
  number: { fr: 'Nombre', pt: 'Número', en: 'Number', es: 'Número' },
  text: { fr: 'Texte libre', pt: 'Texto livre', en: 'Free text', es: 'Texto libre' },
  multipleChoice: { fr: 'Choix multiple', pt: 'Múltipla escolha', en: 'Multiple choice', es: 'Opción múltiple' },
  dateType: { fr: 'Date', pt: 'Data', en: 'Date', es: 'Fecha' },
  dropdown: { fr: 'Liste déroulante', pt: 'Lista suspensa', en: 'Dropdown', es: 'Lista desplegable' },
  photo: { fr: 'Photo', pt: 'Foto', en: 'Photo', es: 'Foto' },
  rating: { fr: 'Évaluation', pt: 'Avaliação', en: 'Rating', es: 'Evaluación' },

  // Node editor labels
  title: { fr: 'Titre', pt: 'Título', en: 'Title', es: 'Título' },
  questionType: { fr: 'Type de question', pt: 'Tipo de pergunta', en: 'Question type', es: 'Tipo de pregunta' },
  tooltip: { fr: 'Astuce (tooltip)', pt: 'Dica (tooltip)', en: 'Hint (tooltip)', es: 'Pista (tooltip)' },
  tooltipPlaceholder: { fr: 'Texte d\'aide pour le client', pt: 'Texto de ajuda para o cliente', en: 'Help text for the client', es: 'Texto de ayuda para el cliente' },
  required: { fr: 'Obligatoire', pt: 'Obrigatória', en: 'Required', es: 'Obligatoria' },
  options: { fr: 'Options', pt: 'Opções', en: 'Options', es: 'Opciones' },
  addOption: { fr: '+ Ajouter', pt: '+ Adicionar', en: '+ Add', es: '+ Agregar' },
  optionText: { fr: 'Texte de l\'option', pt: 'Texto da opção', en: 'Option text', es: 'Texto de la opción' },
  linkToCsv: { fr: 'Lier au produit du CSV...', pt: 'Vincular a produto do CSV...', en: 'Link to CSV product...', es: 'Vincular a producto del CSV...' },
  removeLink: { fr: 'Retirer le lien', pt: 'Remover vínculo', en: 'Remove link', es: 'Quitar vínculo' },
  uploadCsvHint: { fr: 'Chargez un CSV de prix pour lier chaque option à un produit du catalogue.', pt: 'Carregue um CSV de preços para vincular cada opção a um produto do catálogo.', en: 'Upload a price CSV to link each option to a catalogue product.', es: 'Cargue un CSV de precios para vincular cada opción a un producto del catálogo.' },
  eachOptionCreates: { fr: 'Chaque option crée une sortie — connectez au nœud suivant', pt: 'Cada opção cria uma saída — conecte ao próximo nó', en: 'Each option creates an output — connect to the next node', es: 'Cada opción crea una salida — conecte al siguiente nodo' },
  optionsNoCsv: { fr: 'option(s) sans produit lié au CSV. L\'IA peut halluciner.', pt: 'opção(ões) sem produto vinculado ao CSV. A IA pode alucinar.', en: 'option(s) without CSV product link. AI may hallucinate.', es: 'opción(es) sin producto vinculado al CSV. La IA puede alucinar.' },
  maxScale: { fr: 'Échelle maximale', pt: 'Escala máxima', en: 'Maximum scale', es: 'Escala máxima' },
  quantityProduct: { fr: 'Quantité de quel produit ?', pt: 'Quantidade de qual produto?', en: 'Quantity of which product?', es: '¿Cantidad de qué producto?' },
  quantityHint: { fr: 'La réponse numérique sera utilisée comme quantité de ce produit dans le devis.', pt: 'A resposta numérica será usada como quantidade deste produto no orçamento.', en: 'The numeric answer will be used as quantity of this product in the quote.', es: 'La respuesta numérica será usada como cantidad de este producto en el presupuesto.' },
  photoHint: { fr: 'Le client pourra envoyer une photo du lieu/équipement. L\'image sera sauvegardée avec les réponses.', pt: 'O cliente poderá enviar uma foto do local/equipamento. A imagem será salva com as respostas.', en: 'The client can send a photo of the site/equipment. The image will be saved with the answers.', es: 'El cliente podrá enviar una foto del lugar/equipo. La imagen se guardará con las respuestas.' },
  dateHint: { fr: 'Le client verra un sélecteur de date. Utile pour planifier des visites ou dates préférentielles.', pt: 'O cliente verá um seletor de data. Útil para agendamento de visitas ou datas preferenciais.', en: 'The client will see a date picker. Useful for scheduling visits or preferred dates.', es: 'El cliente verá un selector de fecha. Útil para agendar visitas o fechas preferenciales.' },
  endType: { fr: 'Type de finalisation', pt: 'Tipo de finalização', en: 'End type', es: 'Tipo de finalización' },
  endQuoteLabel: { fr: 'Générer devis (IA)', pt: 'Gerar orçamento (IA)', en: 'Generate quote (AI)', es: 'Generar presupuesto (IA)' },
  endSpecialistLabel: { fr: 'Contact spécialiste', pt: 'Contato especialista', en: 'Specialist contact', es: 'Contacto especialista' },
  endThankYouLabel: { fr: 'Remerciement', pt: 'Agradecimento', en: 'Thank you', es: 'Agradecimiento' },
  endSchedulingLabel: { fr: 'Rendez-vous (Calendrier)', pt: 'Agendamento (Calendário)', en: 'Scheduling (Calendar)', es: 'Agendamiento (Calendario)' },
  priceTable: { fr: 'Tableau de prix', pt: 'Tabela de preços', en: 'Price table', es: 'Tabla de precios' },
  priceTableHint: { fr: 'Listez tous les produits et prix. L\'IA utilise ce tableau pour calculer le devis.', pt: 'Liste todos os produtos e preços. A IA usa essa tabela para calcular o orçamento.', en: 'List all products and prices. AI uses this table to calculate the quote.', es: 'Liste todos los productos y precios. La IA usa esta tabla para calcular el presupuesto.' },
  businessRules: { fr: 'Règles métier', pt: 'Regras de negócio', en: 'Business rules', es: 'Reglas de negocio' },
  businessRulesHint: { fr: 'Dites quand appliquer chaque prix. Plus c\'est clair, meilleur est le devis.', pt: 'Diga quando aplicar cada preço. Quanto mais claro, melhor o orçamento.', en: 'Say when to apply each price. The clearer, the better the quote.', es: 'Diga cuándo aplicar cada precio. Cuanto más claro, mejor el presupuesto.' },
  clearRulesTitle: { fr: 'Règles claires = devis précis', pt: 'Regras claras = orçamentos precisos', en: 'Clear rules = precise quotes', es: 'Reglas claras = presupuestos precisos' },
  clearRulesP1: { fr: 'Sans règles, l\'IA peut oublier des articles ou se tromper dans les calculs. Décrivez les conditions de chaque prix.', pt: 'Sem regras, a IA pode esquecer itens ou calcular errado. Descreva as condições de cada preço.', en: 'Without rules, AI may forget items or miscalculate. Describe the conditions for each price.', es: 'Sin reglas, la IA puede olvidar ítems o calcular mal. Describa las condiciones de cada precio.' },
  clearRulesP2: { fr: 'Même ainsi, les IAs peuvent se tromper. Vérifiez toujours le devis avant de l\'envoyer au client.', pt: 'Mesmo assim, IAs podem cometer erros. Verifique sempre o orçamento antes de enviar ao cliente.', en: 'Even so, AIs can make mistakes. Always review the quote before sending to the client.', es: 'Aun así, las IAs pueden cometer errores. Siempre revise el presupuesto antes de enviar al cliente.' },
  clientMessage: { fr: 'Message au client', pt: 'Mensagem ao cliente', en: 'Client message', es: 'Mensaje al cliente' },
  clientMessagePlaceholder: { fr: 'Ex: Un spécialiste vous contactera sous 24h...', pt: 'Ex: Um especialista entrará em contato em 24h...', en: 'E.g.: A specialist will contact you within 24h...', es: 'Ej: Un especialista le contactará en 24h...' },
  schedulingInfo: { fr: 'Le client choisit date et heure sur le calendrier. Le rendez-vous est créé dans Google Calendar et envoyé via webhook (WhatsApp).', pt: 'O cliente escolhe data e horário no calendário. O agendamento é criado no Google Calendar e enviado via webhook (WhatsApp).', en: 'The client picks date and time on the calendar. The booking is created in Google Calendar and sent via webhook (WhatsApp).', es: 'El cliente elige fecha y hora en el calendario. El agendamiento se crea en Google Calendar y se envía via webhook (WhatsApp).' },
  schedulingModeLabel: { fr: 'Mode Rendez-vous', pt: 'Modo Agendamento', en: 'Scheduling Mode', es: 'Modo Agendamiento' },
  confirmMessage: { fr: 'Message de confirmation', pt: 'Mensagem de confirmação', en: 'Confirmation message', es: 'Mensaje de confirmación' },
  confirmMessagePlaceholder: { fr: 'Ex: Choisissez le meilleur jour et heure pour notre conversation...', pt: 'Ex: Escolha o melhor dia e horário para nossa conversa...', en: 'E.g.: Choose the best day and time for our conversation...', es: 'Ej: Elija el mejor día y hora para nuestra conversación...' },
  deleteNode: { fr: 'Supprimer le nœud', pt: 'Excluir nó', en: 'Delete node', es: 'Eliminar nodo' },
  startInfo: { fr: 'Point d\'entrée du flux. Collecte automatiquement : nom, email, téléphone et adresse du client.', pt: 'Ponto de entrada do fluxo. Coleta automaticamente: nome, email, telefone e endereço do cliente.', en: 'Flow entry point. Automatically collects: name, email, phone and address.', es: 'Punto de entrada del flujo. Recopila automáticamente: nombre, email, teléfono y dirección del cliente.' },
  forwardSpecialist: { fr: 'Rediriger vers un spécialiste', pt: 'Encaminhar para especialista', en: 'Forward to specialist', es: 'Redirigir a especialista' },
  forwardSpecialistHint: { fr: 'Le client sera informé qu\'un spécialiste le contactera. Les données seront enregistrées comme lead.', pt: 'O cliente será informado que um especialista entrará em contato. Os dados serão salvos como lead.', en: 'The client will be informed a specialist will contact them. Data will be saved as a lead.', es: 'El cliente será informado de que un especialista le contactará. Los datos se guardarán como lead.' },
  messageText: { fr: 'Texte du message', pt: 'Texto da mensagem', en: 'Message text', es: 'Texto del mensaje' },
  messageTextPlaceholder: { fr: 'Texte que le client verra...', pt: 'Texto que o cliente verá...', en: 'Text the client will see...', es: 'Texto que el cliente verá...' },
};
