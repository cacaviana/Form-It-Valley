import type { Flow } from '$lib/dto/flows/types';

export const flowsMock: Flow[] = [
  {
    _id: 'flow_1',
    tenant_id: 'tenant_1',
    name: 'Devis Installation Borne',
    slug: 'total-electrique-borne',
    status: 'published',
    version: 1,
    nodes: [
      // ========== INÍCIO ==========
      {
        id: 'start',
        type: 'start',
        position: { x: 300, y: 0 },
        data: {
          title: 'Début du questionnaire',
          collectFields: ['name', 'email', 'phone', 'address']
        }
      },

      // ========== P1 — Região ==========
      {
        id: 'p1',
        type: 'question',
        position: { x: 300, y: 140 },
        data: {
          title: 'Quelle est votre région?',
          questionType: 'single_choice',
          options: [
            { id: 'p1_lana', label: 'Lanaudière', value: 'lanaudiere' },
            { id: 'p1_estm', label: 'Est de Montréal', value: 'est_montreal' },
            { id: 'p1_lava', label: 'Laval', value: 'laval' },
            { id: 'p1_autr', label: 'Autre', value: 'autre' }
          ],
          required: true,
          tooltip: 'Sélectionnez la région de votre résidence'
        }
      },

      // ========== FIM — Região não atendida ==========
      {
        id: 'end_region',
        type: 'end',
        position: { x: 650, y: 140 },
        data: {
          title: 'Région non desservie',
          endType: 'specialist',
          message: "Malheureusement, nous ne desservons pas votre région pour le moment. Un spécialiste vous contactera sous 24h pour évaluer les options disponibles."
        }
      },

      // ========== P2 — Marca do painel ==========
      {
        id: 'p2',
        type: 'question',
        position: { x: 300, y: 310 },
        data: {
          title: 'Quelle est la marque de votre panneau électrique?',
          questionType: 'single_choice',
          options: [
            { id: 'p2_sq', label: 'Square D', value: 'square_d' },
            { id: 'p2_si', label: 'Siemens', value: 'siemens' },
            { id: 'p2_ea', label: 'Eaton / Cutler-Hammer', value: 'eaton' },
            { id: 'p2_fe', label: 'Federal Pioneer', value: 'federal_pioneer' },
            { id: 'p2_ge', label: 'GE', value: 'ge' },
            { id: 'p2_st', label: 'Stab-Lok', value: 'stab_lok' },
            { id: 'p2_au', label: 'Autre / Je ne sais pas', value: 'autre' }
          ],
          required: true,
          tooltip: 'Regardez la porte intérieure de votre panneau électrique'
        }
      },

      // ========== P3 — Amperagem do painel ==========
      {
        id: 'p3',
        type: 'question',
        position: { x: 300, y: 500 },
        data: {
          title: "Quelle est la puissance (ampérage) de votre panneau?",
          questionType: 'single_choice',
          options: [
            { id: 'p3_60', label: '60A', value: '60' },
            { id: 'p3_100', label: '100A', value: '100' },
            { id: 'p3_150', label: '150A', value: '150' },
            { id: 'p3_200', label: '200A', value: '200' },
            { id: 'p3_320', label: '320A', value: '320' },
            { id: 'p3_400', label: '400A', value: '400' }
          ],
          required: true,
          tooltip: "Inscrit sur le disjoncteur principal en haut de votre panneau"
        }
      },

      // ========== P4 — Espaços livres ==========
      {
        id: 'p4',
        type: 'question',
        position: { x: 300, y: 700 },
        data: {
          title: 'Avez-vous des espaces libres dans votre panneau?',
          questionType: 'single_choice',
          options: [
            { id: 'p4_oui', label: 'Oui', value: 'oui' },
            { id: 'p4_dbl', label: 'Oui, double', value: 'double' },
            { id: 'p4_non', label: 'Non', value: 'non' }
          ],
          required: true,
          tooltip: "Des espaces vides où on peut ajouter un disjoncteur"
        }
      },

      // ========== FIM — Painel cheio ==========
      {
        id: 'end_panel',
        type: 'end',
        position: { x: 650, y: 700 },
        data: {
          title: 'Panneau plein',
          endType: 'specialist',
          message: "Votre panneau électrique n'a pas d'espace disponible. Un technicien doit évaluer les options (ajout de sous-panneau ou mise à jour). Nous vous contacterons sous 24h."
        }
      },

      // ========== P5 — Spa ==========
      {
        id: 'p5',
        type: 'question',
        position: { x: 300, y: 880 },
        data: {
          title: 'Avez-vous un spa (hot tub)?',
          questionType: 'yes_no',
          required: true,
          tooltip: "Un spa consomme beaucoup d'énergie et influence le choix de la borne"
        }
      },

      // ========== P6 — Já tem borne? ==========
      {
        id: 'p6',
        type: 'question',
        position: { x: 300, y: 1040 },
        data: {
          title: 'Avez-vous déjà une borne de recharge installée?',
          questionType: 'yes_no',
          required: true
        }
      },

      // ========== P6a — Tipo da borne (se Sim) ==========
      {
        id: 'p6a',
        type: 'question',
        position: { x: 100, y: 1200 },
        data: {
          title: 'Quel est le type de votre borne actuelle?',
          questionType: 'single_choice',
          options: [
            { id: 'p6a_plug', label: 'Plug-in (branchée)', value: 'plugin' },
            { id: 'p6a_hard', label: 'Hardwired (câblée)', value: 'hardwired' }
          ],
          required: true,
          tooltip: "Plug-in: se branche dans une prise. Hardwired: câblée directement au panneau."
        }
      },

      // ========== P6b — Amperagem da borne (se Sim) ==========
      {
        id: 'p6b',
        type: 'question',
        position: { x: 100, y: 1370 },
        data: {
          title: "Quel est l'ampérage de votre borne actuelle?",
          questionType: 'single_choice',
          options: [
            { id: 'p6b_16', label: '16A', value: '16' },
            { id: 'p6b_24', label: '24A', value: '24' },
            { id: 'p6b_32', label: '32A', value: '32' },
            { id: 'p6b_40', label: '40A', value: '40' },
            { id: 'p6b_48', label: '48A', value: '48' },
            { id: 'p6b_ns', label: 'Je ne sais pas', value: 'unknown' }
          ],
          required: true
        }
      },

      // ========== P7 — Local da instalação ==========
      {
        id: 'p7',
        type: 'question',
        position: { x: 300, y: 1540 },
        data: {
          title: "Où sera installée la borne de recharge?",
          questionType: 'single_choice',
          options: [
            { id: 'p7_mur', label: 'Mur extérieur (garage)', value: 'mur_exterieur' },
            { id: 'p7_pot', label: 'Poteau extérieur', value: 'poteau' },
            { id: 'p7_int', label: 'Intérieur', value: 'interieur' }
          ],
          required: true,
          tooltip: "L'installation intérieure nécessite une évaluation sur place"
        }
      },

      // ========== FIM — Instalação interior (especialista) ==========
      {
        id: 'end_interior',
        type: 'end',
        position: { x: 650, y: 1540 },
        data: {
          title: 'Installation intérieure',
          endType: 'specialist',
          message: "L'installation intérieure est plus complexe et nécessite une évaluation sur place. Un technicien vous contactera sous 24h pour planifier une visite."
        }
      },

      // ========== P8 — Distância ==========
      {
        id: 'p8',
        type: 'question',
        position: { x: 300, y: 1720 },
        data: {
          title: "Quelle est la distance entre votre panneau électrique et le lieu d'installation? (en pieds)",
          questionType: 'number',
          required: true,
          tooltip: "Mesurez approximativement la distance en pieds entre votre panneau et l'endroit où la borne sera installée"
        }
      },

      // ========== FIM — Orçamento ==========
      {
        id: 'end_quote',
        type: 'end',
        position: { x: 300, y: 1900 },
        data: {
          title: 'Générer le devis',
          endType: 'quote',
          businessContext: "Nous sommes Total Électrique, entreprise spécialisée dans l'installation de bornes de recharge pour véhicules électriques au Québec.\n\nPrix de base:\n- Borne 16A: 499$\n- Borne 32A: 699$\n- Borne 40A: 899$\n- Borne 48A: 1 099$\n- Controller de charge DCC-9: 699$\n- Installation mur extérieur: 490$\n- Installation poteau: 690$\n- Câblage: 9$/pied\n- Déplacement: 69$\n\nRecommandation de borne:\n- Panneau 60A → Borne 16A + Controller obligatoire\n- Panneau 100A sans spa → 16A direct ou 32A + Controller\n- Panneau 100A avec spa → 16A + Controller ou upgrade panneau\n- Panneau 150A sans spa → jusqu'à 40A direct\n- Panneau 150A avec spa → Controller obligatoire ou upgrade 200A\n- Panneau 200A sans spa → jusqu'à 60A direct\n- Panneau 200A avec spa → 32A direct ou 48A+ avec Controller\n- Panneau 320A/400A → jusqu'à 60-100A direct",
          aiInstruction: "Génère un devis professionnel en français canadien. Détaille chaque ligne (borne recommandée, installation, câblage, déplacement, controller si nécessaire). Affiche sous-totaux et total final en dollars canadiens. Inclus des recommandations techniques basées sur l'ampérage du panneau, la présence de spa, et la borne existante.",
          outputFormat: 'both'
        }
      }
    ],

    edges: [
      // Start → P1
      { id: 'e_start_p1', source: 'start', target: 'p1' },

      // P1 → P2 (regiões atendidas) ou → Especialista (Autre)
      { id: 'e_p1_p2_lana', source: 'p1', target: 'p2', sourceHandle: 'p1_lana', label: 'Lanaudière' },
      { id: 'e_p1_p2_estm', source: 'p1', target: 'p2', sourceHandle: 'p1_estm', label: 'Est Montréal' },
      { id: 'e_p1_p2_lava', source: 'p1', target: 'p2', sourceHandle: 'p1_lava', label: 'Laval' },
      { id: 'e_p1_end',     source: 'p1', target: 'end_region', sourceHandle: 'p1_autr', label: 'Autre → Spécialiste' },

      // P2 → P3 (todas as marcas seguem)
      { id: 'e_p2_p3', source: 'p2', target: 'p3' },

      // P3 → P4 (todas as amperagens seguem)
      { id: 'e_p3_p4', source: 'p3', target: 'p4' },

      // P4 → P5 (Oui/Double) ou → Especialista (Non)
      { id: 'e_p4_p5_oui', source: 'p4', target: 'p5', sourceHandle: 'p4_oui', label: 'Oui' },
      { id: 'e_p4_p5_dbl', source: 'p4', target: 'p5', sourceHandle: 'p4_dbl', label: 'Double' },
      { id: 'e_p4_end',    source: 'p4', target: 'end_panel', sourceHandle: 'p4_non', label: 'Non → Spécialiste' },

      // P5 → P6 (ambos seguem)
      { id: 'e_p5_p6_yes', source: 'p5', target: 'p6', sourceHandle: 'yes', label: 'Oui' },
      { id: 'e_p5_p6_no',  source: 'p5', target: 'p6', sourceHandle: 'no',  label: 'Non' },

      // P6 → P6a (Sim, tem borne) ou → P7 (Não, pula P6a/P6b)
      { id: 'e_p6_p6a',  source: 'p6', target: 'p6a', sourceHandle: 'yes', label: 'Oui → détails borne' },
      { id: 'e_p6_p7',   source: 'p6', target: 'p7',  sourceHandle: 'no',  label: 'Non → passer à P7' },

      // P6a → P6b
      { id: 'e_p6a_p6b', source: 'p6a', target: 'p6b' },

      // P6b → P7
      { id: 'e_p6b_p7', source: 'p6b', target: 'p7' },

      // P7 → P8 (Mur/Poteau) ou → Especialista (Intérieur)
      { id: 'e_p7_p8_mur', source: 'p7', target: 'p8', sourceHandle: 'p7_mur', label: 'Mur extérieur' },
      { id: 'e_p7_p8_pot', source: 'p7', target: 'p8', sourceHandle: 'p7_pot', label: 'Poteau' },
      { id: 'e_p7_end',    source: 'p7', target: 'end_interior', sourceHandle: 'p7_int', label: 'Intérieur → Spécialiste' },

      // P8 → Orçamento
      { id: 'e_p8_quote', source: 'p8', target: 'end_quote' }
    ],

    created_at: '2026-03-10T10:00:00Z',
    updated_at: '2026-03-10T14:30:00Z'
  }
];
