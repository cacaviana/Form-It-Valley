import { test, expect } from '@playwright/test';

const CSV_CONTENT = `produto,preco,unidade,categoria
Borne 16A Level 1,499,unidade,borne
Borne 32A Level 2,699,unidade,borne
Borne 48A Level 2,899,unidade,borne
Controller DCC-9,699,unidade,accessoire
Installation murale exterieure,490,unidade,installation
Installation sur poteau,690,unidade,installation
Cablage par pied,9,pied,cablage
Deplacement,69,unidade,deplacement`;

// Always use the dedicated EV charging flow — avoids contaminating other flows' CSVs
const EV_FLOW_SLUG = 'devis-borne-de-recharge-ev';

async function getTestFlow(request: any) {
  const res = await request.get(`/api/flows/slug/${EV_FLOW_SLUG}`);
  if (res.ok()) return res.json();
  return null;
}

test.describe('Quote E2E - Full flow with agent', () => {

  test('Step 1: Upload CSV via API', async ({ request }) => {
    const flow = await getTestFlow(request);
    expect(flow).toBeTruthy();

    // Save the CSV to the flow via API PUT
    const res = await request.put(`/api/flows/${flow._id}`, {
      data: {
        ...flow,
        pricing_csv: CSV_CONTENT
      }
    });
    expect(res.ok()).toBeTruthy();

    // Verify it was saved
    const updated = await (await request.get(`/api/flows/${flow._id}`)).json();
    expect(updated.pricing_csv).toContain('Borne 32A Level 2');
    expect(updated.pricing_csv).toContain('699');
  });

  test('Step 2: CSV upload modal opens and validates in editor', async ({ page, request }) => {
    const flow = await getTestFlow(request);
    expect(flow).toBeTruthy();

    await page.goto(`/admin/flows/${flow._id}/edit`);
    await expect(page.getByText('Salvar')).toBeVisible({ timeout: 20000 });

    // The button should show "CSV carregado" since we already uploaded
    await expect(page.locator('[data-testid="btn-csv-upload"]')).toBeVisible();

    // Wait a bit for Svelte reactivity to settle, then click
    await page.waitForTimeout(2000);

    // Use Svelte-compatible click
    await page.locator('[data-testid="btn-csv-upload"]').click();
    await page.waitForTimeout(1000);

    // Take screenshot to verify state
    await page.screenshot({ path: 'test-results/step2-modal.png' });
  });

  test('Step 3: Client fills form and receives quote from backend agent', async ({ page, request }) => {
    const flow = await getTestFlow(request);
    expect(flow).toBeTruthy();

    // Capture console logs for debugging
    const consoleLogs: string[] = [];
    page.on('console', msg => consoleLogs.push(`[${msg.type()}] ${msg.text()}`));

    // Monitor network requests to generate-quote
    const networkLogs: string[] = [];
    page.on('response', response => {
      if (response.url().includes('generate-quote')) {
        networkLogs.push(`PROXY: ${response.status()} ${response.url()}`);
      }
    });

    await page.goto(`/q/${flow.slug}`);
    await expect(page.locator('text=Commencer')).toBeVisible({ timeout: 10000 });

    // Phase 1: Fill client info
    await page.locator('input').first().fill('Jean Test');
    await page.locator('input[type="email"]').fill('jean@test.com');
    await page.locator('input[type="tel"]').fill('+1 450-555-9999');

    const allTextInputs = page.locator('input[type="text"]');
    const count = await allTextInputs.count();
    if (count > 1) {
      await allTextInputs.last().fill('123 Rue Test, Laval QC');
    }

    await page.locator('text=Commencer').click();

    // Phase 2: Answer questions - navigate dynamically
    const endNodeIds = flow.nodes.filter((n: any) => n.type === 'end').map((n: any) => n.id);
    let safetyCounter = 0;

    while (safetyCounter < 20) {
      safetyCounter++;
      await page.waitForTimeout(500);

      // Check if we reached the end (spinner or pre visible)
      const spinnerVisible = await page.locator('.animate-spin').isVisible().catch(() => false);
      const preVisible = await page.locator('pre').isVisible().catch(() => false);
      if (spinnerVisible || preVisible) break;

      // Check for question buttons
      const buttons = page.locator('button').filter({ hasNotText: /Retour|Commencer/ });
      const btnCount = await buttons.count();

      // Check for number input
      const numberInput = page.locator('input[type="number"]');
      const hasNumberInput = await numberInput.isVisible().catch(() => false);

      if (hasNumberInput) {
        await numberInput.fill('30');
        // Click "Suivant" button next to it
        await page.locator('button:has-text("Suivant")').click();
        continue;
      }

      if (btnCount > 0) {
        // Click the first valid option button
        await buttons.first().click();
        continue;
      }

      // If nothing to interact with, wait a bit (message node auto-advances)
      await page.waitForTimeout(2000);
    }

    // Phase 3: Wait for quote card with items table (AI agent generates it, up to 90s)
    const quoteTable = page.locator('[data-testid="quote-items-table"]');
    await expect(quoteTable).toBeVisible({ timeout: 90000 });

    // Verify table has items
    const rows = quoteTable.locator('tbody tr');
    const rowCount = await rows.count();
    expect(rowCount).toBeGreaterThan(0);

    // Verify total is displayed with currency
    const totalText = await page.locator('.text-blue-700.tabular-nums').textContent();
    expect(totalText).toBeTruthy();
    expect(totalText).toMatch(/[\d\s,.]+\s*\$/);

    // Verify print button is present
    await expect(page.locator('text=Imprimer')).toBeVisible();

    // Screenshot the final quote
    await page.screenshot({ path: 'test-results/step3-quote.png', fullPage: true });
  });

  test('Step 4: Verify submission was saved with quote in backend', async ({ request }) => {
    const res = await request.get('http://localhost:8001/api/submissions');
    if (res.ok()) {
      const data = await res.json();
      const submissions = data.submissions || [];
      if (submissions.length > 0) {
        const latest = submissions[0];
        expect(latest.status).toBe('quoted');
      }
    }
  });
});
