<script lang="ts">
  import { goto } from '$app/navigation';
  import { FlowsService } from '$lib/services/flows.service';
  import type { Flow } from '$lib/dto/flows/types';
  import { onMount } from 'svelte';

  const service = new FlowsService();
  let flows = $state<Flow[]>([]);
  let loading = $state(true);
  let creatingScheduling = $state(false);

  onMount(async () => {
    try {
      flows = await service.list();
    } catch (e) {
      // silently fail — just show no demo button
    } finally {
      loading = false;
    }
  });

  const firstPublished = $derived(flows.find(f => f.status === 'published'));
  const firstFlow = $derived(flows[0]);
  const demoSlug = $derived(firstPublished?.slug || firstFlow?.slug);

  async function createSchedulingFlow() {
    creatingScheduling = true;
    try {
      // Create a pre-built scheduling flow with qualifying questions
      const res = await fetch('/api/flows', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: 'Pos-Graduacao IA & Machine Learning',
          slug: `qualificacao-ia-${Date.now()}`,
          status: 'draft',
          flow_type: 'scheduling',
          collect_fields: { name: true, email: true, phone: true, address: false },
          nodes: [
            { id: 'start-1', type: 'start', position: { x: 250, y: 0 }, data: { label: 'Inicio', collect_fields: { name: true, email: true, phone: true, address: false } } },
            { id: 'q-area', type: 'question', position: { x: 250, y: 150 }, data: { label: 'Area de atuacao', title: 'Qual e a sua area de atuacao atual?', questionType: 'single_choice', options: [{ id: 'ti', label: 'Tecnologia da Informacao (TI)', value: 'TI' }, { id: 'outra', label: 'Outra area (Administracao, Financas, Marketing, etc.)', value: 'Outra area' }, { id: 'saude', label: 'Saude / Ciencias da Vida', value: 'Saude' }, { id: 'estudante', label: 'Estudante sem experiencia profissional', value: 'Estudante' }], required: true } },
            { id: 'end-desqualificado-area', type: 'end', position: { x: 550, y: 300 }, data: { label: 'Desqualificado (area)', endType: 'message', message: 'Obrigado pelo seu interesse! No momento, a pos-graduacao em IA & Machine Learning e voltada para profissionais da area de TI. Fique atento as nossas proximas turmas!' } },
            { id: 'q-diploma', type: 'question', position: { x: 250, y: 350 }, data: { label: 'Diploma superior', title: 'Voce possui diploma de curso superior concluido?', questionType: 'single_choice', options: [{ id: 'sim', label: 'Sim', value: 'Sim' }, { id: 'cursando', label: 'Ainda estou cursando', value: 'Cursando' }, { id: 'nao', label: 'Nao possuo graduacao', value: 'Nao' }], required: true } },
            { id: 'end-desqualificado-diploma', type: 'end', position: { x: 550, y: 500 }, data: { label: 'Desqualificado (diploma)', endType: 'message', message: 'A matricula na pos-graduacao exige diploma de ensino superior concluido. Quando voce concluir sua graduacao, entre em contato conosco!' } },
            { id: 'q-objetivo', type: 'question', position: { x: 250, y: 550 }, data: { label: 'Objetivo', title: 'Por que voce quer se especializar em IA & Machine Learning?', questionType: 'single_choice', options: [{ id: 'carreira', label: 'Crescimento de carreira / promocao', value: 'Crescimento de carreira' }, { id: 'transicao', label: 'Transicao para a area de dados / IA', value: 'Transicao para dados/IA' }, { id: 'salario', label: 'Aumentar salario / empregabilidade', value: 'Aumentar salario' }, { id: 'empresa', label: 'Implementar IA na minha empresa', value: 'Implementar IA na empresa' }], required: true } },
            { id: 'q-investimento', type: 'question', position: { x: 250, y: 750 }, data: { label: 'Investimento', title: 'O investimento de 18x R$ 367,00 se encaixa no seu planejamento? (Total: R$ 6.606,00 sem juros)', questionType: 'single_choice', options: [{ id: 'sim', label: 'Sim, consigo realizar esse investimento', value: 'Sim' }, { id: 'talvez', label: 'Talvez — preciso entender melhor as condicoes', value: 'Talvez' }, { id: 'nao', label: 'No momento nao tenho condicoes financeiras', value: 'Nao' }], required: true } },
            { id: 'end-schedule', type: 'end', position: { x: 250, y: 950 }, data: { label: 'Agendar reuniao', endType: 'scheduling', message: 'Otimo! Escolha o melhor dia e horario para conversarmos sobre a pos-graduacao.' } },
          ],
          edges: [
            { id: 'e-start-area', source: 'start-1', target: 'q-area' },
            { id: 'e-area-ti', source: 'q-area', sourceHandle: 'ti', target: 'q-diploma' },
            { id: 'e-area-outra', source: 'q-area', sourceHandle: 'outra', target: 'end-desqualificado-area' },
            { id: 'e-area-saude', source: 'q-area', sourceHandle: 'saude', target: 'end-desqualificado-area' },
            { id: 'e-area-estudante', source: 'q-area', sourceHandle: 'estudante', target: 'end-desqualificado-area' },
            { id: 'e-diploma-sim', source: 'q-diploma', sourceHandle: 'sim', target: 'q-objetivo' },
            { id: 'e-diploma-cursando', source: 'q-diploma', sourceHandle: 'cursando', target: 'q-objetivo' },
            { id: 'e-diploma-nao', source: 'q-diploma', sourceHandle: 'nao', target: 'end-desqualificado-diploma' },
            { id: 'e-obj-inv', source: 'q-objetivo', target: 'q-investimento' },
            { id: 'e-inv-end', source: 'q-investimento', target: 'end-schedule' },
          ]
        })
      });

      if (res.ok) {
        const created = await res.json();
        goto(`/admin/scheduling`);
      }
    } catch (e) {
      console.error('Error creating scheduling flow:', e);
    } finally {
      creatingScheduling = false;
    }
  }
</script>

<div class="min-h-screen flex items-center justify-center" style="background: linear-gradient(135deg, #0D2033 0%, #173650 100%);">
  <div class="text-center max-w-lg px-6">
    <!-- Logo -->
    <p class="text-xs font-medium tracking-[0.45em] uppercase text-petra-light mb-5 opacity-80">IT Valley — Escola de Tecnologia</p>
    <h1 class="text-6xl font-light tracking-tight text-white mb-4">
      Form<span class="font-semibold bg-gradient-to-r from-petra-steel to-petra-light bg-clip-text text-transparent">IT Valley</span>
    </h1>
    <p class="text-lg font-light text-petra-pale/70 mb-12">Qualificacao e Agendamento Inteligente</p>

    <div class="flex flex-col items-center gap-4">
      <div class="flex gap-3 justify-center">
        <!-- Quote button hidden — IT Valley uses scheduling only -->
        <!-- <button onclick={() => goto('/admin/flows')}>Panneau Admin</button> -->
        <!-- <button>Questionnaire Démo</button> -->
      </div>

      <!-- Scheduling Mode -->
      <button
        onclick={createSchedulingFlow}
        disabled={creatingScheduling}
        class="px-8 py-3.5 rounded-full text-base font-normal tracking-wide cursor-pointer transition-all hover:-translate-y-0.5 disabled:opacity-40 flex items-center gap-2.5"
        style="background: var(--color-surface-teal, #C8DDD7); color: #173650; border: 1px solid rgba(40,120,100,0.2); box-shadow: 0 4px 20px rgba(40,120,100,0.15);"
      >
        {#if creatingScheduling}
          <span class="w-5 h-5 border-2 border-petra-dark border-t-transparent rounded-full animate-spin"></span>
          Criando...
        {:else}
          <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5" />
          </svg>
          Modo Agendamento
        {/if}
      </button>

      <!-- Admin Panel for scheduling -->
      <button
        onclick={() => goto('/admin/scheduling')}
        class="px-8 py-3.5 rounded-full text-base font-normal tracking-wide text-petra-pale cursor-pointer transition-all hover:-translate-y-0.5 hover:bg-white/5"
        style="border: 1px solid rgba(165,200,228,0.32);"
      >
        Painel Admin
      </button>
    </div>

    <p class="mt-12 text-[10px] font-light tracking-[0.12em] text-petra-light/40">PETRA IA &middot; Design System v2</p>
  </div>
</div>
