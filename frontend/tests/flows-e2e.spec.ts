import { test, expect } from '@playwright/test';

/**
 * E2E tests for all 3 flows:
 * 1. Cafe com Leite — simple product selection + quantity
 * 2. Devis Borne EV — full quote with catalogProduct + quantityProduct
 * 3. Consultoria Agendamento — specialist flow (no quote)
 */

test.describe('Cafe com Leite', () => {

  test('sim cafe x3, nao leite → only Cafe x3 in quote', async ({ page }) => {
    await page.goto('/q/cafe-com-leite');
    await page.waitForSelector('text=Commencer', { timeout: 15000 });

    // Fill client data
    await page.fill('input[type="text"]', 'Carlos Teste');
    await page.fill('input[type="email"]', 'carlos@teste.com');
    await page.click('button:has-text("Commencer")');

    // Q1: Voce gosta de cafe? → Sim
    await page.waitForSelector('text=Voce gosta de cafe');
    await page.click('button:has-text("Sim")');

    // Q2: E de leite? → Nao
    await page.waitForSelector('text=leite');
    await page.click('button:has-text("Nao")');

    // Q3: Quantos cafes? → 3
    await page.waitForSelector('text=Quantos cafes');
    await page.fill('input[type="number"]', '3');
    await page.click('button:has-text("Suivant")');

    // Wait for quote
    await page.waitForSelector('[data-testid="quote-items-table"]', { timeout: 90000 });

    const table = page.locator('[data-testid="quote-items-table"]');
    const tableText = (await table.textContent() ?? '').toLowerCase();

    // Cafe must appear
    expect(tableText).toContain('cafe');

    // Leite must NOT appear
    expect(tableText).not.toContain('leite');

    // Chocolate must NOT appear
    expect(tableText).not.toContain('chocolate');

    // Quantity should be 3
    expect(tableText).toContain('3');

    await page.screenshot({ path: 'test-results/cafe-sim-x3.png', fullPage: true });
    console.log('Table:', tableText.slice(0, 300));
  });

  test('nao tudo → zero items, total $0', async ({ page }) => {
    await page.goto('/q/cafe-com-leite');
    await page.waitForSelector('text=Commencer', { timeout: 15000 });

    await page.fill('input[type="text"]', 'Carlos Zero');
    await page.fill('input[type="email"]', 'zero@teste.com');
    await page.click('button:has-text("Commencer")');

    // Nao cafe
    await page.waitForSelector('text=Voce gosta de cafe');
    await page.click('button:has-text("Nao")');

    // Nao leite
    await page.waitForSelector('text=leite');
    await page.click('button:has-text("Nao")');

    // Quantity (doesn't matter, cafe not selected)
    await page.waitForSelector('text=Quantos cafes');
    await page.fill('input[type="number"]', '1');
    await page.click('button:has-text("Suivant")');

    // Wait for the page to finish processing (quote or end screen)
    await page.waitForTimeout(10000);

    // Check via API that the submission has zero items
    const pageText = (await page.textContent('body') ?? '').toLowerCase();

    // Should show total of 0 or empty quote
    const hasZeroTotal = pageText.includes('0,00') || pageText.includes('0.00');
    const hasNoProducts = !pageText.includes('cafe') || pageText.includes('0,00');

    // The table might show but with no product rows, OR the fallback message appears
    expect(hasZeroTotal || !pageText.includes('cafe')).toBeTruthy();

    await page.screenshot({ path: 'test-results/cafe-nao-tudo.png', fullPage: true });
    console.log('Has zero total:', hasZeroTotal);
  });
  test('admin error: quantityProduct points to wrong product → system follows config exactly', async ({ request }) => {
    const BACKEND = 'http://localhost:8001';

    // Get flow via backend API
    const flowRes = await request.get(`${BACKEND}/api/flows/slug/cafe-com-leite`);
    const flow = await flowRes.json();
    const flowId = flow._id;

    // Save original quantityProduct
    const qtyNode = flow.nodes.find((n: any) => n.id === 'q_qty_cafe');
    const originalProduct = qtyNode.data.quantityProduct;

    // Break it: point to Chocolate
    qtyNode.data.quantityProduct = 'Chocolate';
    await request.put(`${BACKEND}/api/flows/${flowId}`, { data: flow });

    // Submit with sim cafe, qty 5
    const subRes = await request.post(`${BACKEND}/api/submissions`, {
      data: {
        flow_id: flowId,
        flow_slug: 'cafe-com-leite',
        client_name: 'Teste Erro Admin',
        client_email: 'erro@teste.com',
        client_phone: '',
        client_address: '',
        end_node_id: 'end',
        answers: [
          { node_id: 'q_cafe', question: 'Cafe?', value: 'sim', label: 'Sim' },
          { node_id: 'q_leite', question: 'Leite?', value: 'nao', label: 'Nao' },
          { node_id: 'q_qty_cafe', question: 'Quantos?', value: '5', label: '5' },
        ],
      },
    });
    const sub = await subRes.json();
    const items = sub.quote_data?.items || [];

    console.log('Items:', items.map((i: any) => `${i.description} x${i.quantity} = $${i.subtotal}`));

    // System should follow the wrong config: Chocolate x5, NOT Cafe x5
    const chocolateItem = items.find((i: any) => i.description.toLowerCase().includes('chocolate'));
    expect(chocolateItem).toBeTruthy();
    expect(chocolateItem.quantity).toBe(5);
    expect(chocolateItem.subtotal).toBe(75); // 15 * 5

    // Cafe should still appear (from single_choice) but with qty 1
    const cafeItem = items.find((i: any) => i.description.toLowerCase().includes('cafe'));
    expect(cafeItem).toBeTruthy();
    expect(cafeItem.quantity).toBe(1);

    console.log('Admin error test PASSED: system followed wrong config exactly');

    // Restore correct config
    qtyNode.data.quantityProduct = originalProduct;
    await request.put(`${BACKEND}/api/flows/${flowId}`, { data: flow });
  });
});

test.describe('Devis Borne EV', () => {

  test('Borne 32A + mur ext + 25 pieds → correct items and cablage quantity', async ({ page }) => {
    await page.goto('/q/devis-borne-de-recharge-ev');
    await page.waitForSelector('text=Commencer', { timeout: 15000 });

    // Client data
    await page.fill('input[type="text"]', 'Carlos Viana');
    await page.fill('input[type="email"]', 'carlos@teste.com');
    const telInput = page.locator('input[type="tel"]');
    if (await telInput.isVisible().catch(() => false)) {
      await telInput.fill('5815780564');
    }
    const textInputs = page.locator('input[type="text"]');
    if (await textInputs.count() > 1) {
      await textInputs.last().fill('12110 Rue Conrad-Bernier');
    }
    await page.click('button:has-text("Commencer")');

    // Region → Est de Montreal
    await page.waitForSelector('text=region');
    await page.click('button:has-text("Est de Montreal")');

    // Panneau → 200A
    await page.waitForSelector('text=amperage');
    await page.click('button:has-text("200A")');

    // Espaces libres → Oui
    await page.waitForSelector('text=espaces libres');
    await page.click('button:has-text("Oui")');

    // Type borne → 32A
    await page.waitForSelector('text=type de borne');
    await page.click('button:has-text("32A")');

    // Installation → Mur exterieur
    await page.waitForSelector('text=installee');
    await page.click('button:has-text("Mur exterieur")');

    // Distance → 25 pieds
    await page.waitForSelector('text=distance');
    await page.fill('input[type="number"]', '25');
    await page.click('button:has-text("Suivant")');

    // Wait for quote
    await page.waitForSelector('[data-testid="quote-items-table"]', { timeout: 90000 });

    const table = page.locator('[data-testid="quote-items-table"]');
    const tableText = (await table.textContent() ?? '').toLowerCase();

    // Borne 32A must appear
    expect(tableText).toContain('borne 32a');

    // Installation murale must appear
    expect(tableText).toContain('installation');

    // Cablage must appear with 25 pieds
    expect(tableText).toContain('cablage');
    expect(tableText).toContain('25');

    // Context items must NOT appear as line items
    expect(tableText).not.toContain('est de montreal');
    expect(tableText).not.toContain('200a');

    // AI must NOT add products on its own
    expect(tableText).not.toContain('deplacement');
    expect(tableText).not.toContain('controller');

    await page.screenshot({ path: 'test-results/borne-32a-happy.png', fullPage: true });
    console.log('Table:', tableText.slice(0, 500));
  });
});

test.describe('Consultoria Agendamento', () => {

  test('specialist flow → no quote, thank you message', async ({ page }) => {
    await page.goto('/q/consultoria-agendamento');
    await page.waitForSelector('text=Commencer', { timeout: 15000 });

    // Client data
    await page.fill('input[type="text"]', 'Carlos Consulta');
    await page.fill('input[type="email"]', 'consult@teste.com');
    const telInput = page.locator('input[type="tel"]');
    if (await telInput.isVisible().catch(() => false)) {
      await telInput.fill('5815780564');
    }
    await page.click('button:has-text("Commencer")');

    // Tipo → Consultation technique
    await page.waitForSelector('text=consultation');
    await page.click('button:has-text("technique")');

    // Urgent → Oui (goes to end)
    await page.waitForSelector('text=urgent');
    await page.click('button:has-text("Oui")');

    // Should see end message (specialist type, no quote)
    await page.waitForTimeout(3000);

    // No quote table should exist
    const hasQuoteTable = await page.locator('[data-testid="quote-items-table"]').isVisible().catch(() => false);
    expect(hasQuoteTable).toBeFalsy();

    // Should see thank you / specialist message
    const pageText = (await page.textContent('body') ?? '').toLowerCase();
    const hasEndMessage = pageText.includes('merci') || pageText.includes('specialiste') || pageText.includes('contactera');
    expect(hasEndMessage).toBeTruthy();

    await page.screenshot({ path: 'test-results/consultoria-specialist.png', fullPage: true });
    console.log('Page contains end message:', hasEndMessage);
  });
});
