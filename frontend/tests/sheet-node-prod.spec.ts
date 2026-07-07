import { test, expect } from '@playwright/test';

/**
 * Teste REAL em producao do nó "Enviar para Planilha".
 * Flow: forms.itvalleyschool.com/q/teste-claude-planilha
 * Agenda de verdade: WhatsApp + email + Calendar reais pro Carlos.
 */
const BASE = 'https://forms.itvalleyschool.com';

test('PROD: lead real passa pelo nó planilha e agenda', async ({ page }) => {
  test.setTimeout(180000);

  await page.goto(`${BASE}/q/teste-claude-planilha?utm_source=teste-prod-claude&utm_medium=e2e&utm_campaign=validacao-no-planilha`);

  // ── Formulário inicial ──
  await page.fill('#form-field-name', 'Carlos Viana');
  await page.fill('#form-field-email', 'carlosaraujoviana@gmail.com');

  // País: +1 (dropdown customizado)
  await page.locator('button', { hasText: '(+55)' }).click();
  await page.locator('button', { hasText: '+1' }).first().click();

  await page.getByPlaceholder('Cód. área').fill('581');
  await page.getByPlaceholder('Número').fill('5780564');

  await page.getByRole('button', { name: 'Começar' }).click();

  // ── Nó sheet é pass-through → calendário abre direto ──
  await expect(page.getByText('Escolha o dia')).toBeVisible({ timeout: 20000 });

  // Primeiro dia disponível (nome acessível normalizado + não desabilitado)
  await page.waitForTimeout(4000);
  const dayButtons = page
    .getByRole('button', { name: /^\d{1,2}$/ })
    .and(page.locator('button:not([disabled])'));
  await expect(dayButtons.first()).toBeVisible({ timeout: 30000 });
  await dayButtons.first().click();

  // ── Primeiro horário ──
  await expect(page.getByText('Escolha o horário')).toBeVisible({ timeout: 20000 });
  const slotButtons = page
    .getByRole('button', { name: /^\d{2}:\d{2}$/ })
    .and(page.locator('button:not([disabled])'));
  await expect(slotButtons.first()).toBeVisible({ timeout: 30000 });
  await slotButtons.first().click();

  await page.locator('button.w-full', { hasText: /Continuar|Confirmar/ }).click();
  await expect(page.getByText('Confirme seu agendamento')).toBeVisible({ timeout: 15000 });

  // ── Confirma agendamento REAL ──
  await page.getByRole('button', { name: 'Confirmar Agendamento' }).click();
  await expect(page.getByRole('heading', { name: 'Agendamento Confirmado!' })).toBeVisible({ timeout: 60000 });
});
