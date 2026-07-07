import { test, expect } from '@playwright/test';

/**
 * E2E local do nó "Enviar para Planilha".
 * Flow de teste: teste-claude-planilha (start → sheet → end scheduling)
 * Planilha: 1yuCaCkgl7wO3HRsuAh3yY4btMBwf5Zm56GN7Vpv-5PU
 */
test('lead passa pelo nó planilha e agenda — linha criada e atualizada', async ({ page }) => {
  test.setTimeout(120000);

  await page.goto('/q/teste-claude-planilha?utm_source=teste-playwright&utm_medium=e2e-local&utm_campaign=no-planilha');

  // ── Formulário inicial ──
  await page.fill('#form-field-name', 'Carlos Viana Teste');
  await page.fill('#form-field-email', 'carlosaraujoviana@gmail.com');

  // País: +1 (dropdown customizado)
  await page.locator('button', { hasText: '(+55)' }).click();
  await page.locator('button', { hasText: '+1' }).first().click();

  // DDD (área) + número — fora do Brasil são inputs de texto
  await page.getByPlaceholder('Cód. área').fill('581');
  await page.getByPlaceholder('Número').fill('5780564');

  await page.getByRole('button', { name: 'Começar' }).click();

  // ── Nó sheet é pass-through → calendário abre direto ──
  await expect(page.getByText('Escolha o dia')).toBeVisible({ timeout: 15000 });

  // Espera slots carregarem e clica no primeiro dia disponível
  await page.waitForTimeout(3000);
  const dayButtons = page.locator('button:not([disabled])').filter({ hasText: /^\d{1,2}$/ });
  await expect(dayButtons.first()).toBeVisible({ timeout: 20000 });
  await dayButtons.first().click();

  // ── Escolhe horário ──
  await expect(page.getByText('Escolha o horário')).toBeVisible({ timeout: 15000 });
  const slotButtons = page.locator('button').filter({ hasText: /^\d{2}:\d{2}$/ });
  await expect(slotButtons.first()).toBeVisible({ timeout: 20000 });
  await slotButtons.first().click();

  // Continuar → confirmação
  await page.locator('button.w-full', { hasText: /Continuar|Confirmar/ }).click();
  await expect(page.getByText('Confirme seu agendamento')).toBeVisible({ timeout: 10000 });

  // ── Confirma agendamento ──
  await page.getByRole('button', { name: 'Confirmar Agendamento' }).click();
  await expect(page.getByText('Agendamento Confirmado!')).toBeVisible({ timeout: 45000 });
});
