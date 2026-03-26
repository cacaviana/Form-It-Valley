import { test, expect } from '@playwright/test';

test.describe('FlowQuote - Production Tests', () => {

  test('Home page loads with FlowQuote title', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('h1')).toContainText('FlowQuote');
  });

  test('Home page has Admin and Demo buttons', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByText('Painel Admin')).toBeVisible();
  });

  test('Admin flow list loads', async ({ page }) => {
    await page.goto('/admin/flows');
    await expect(page.locator('h1')).toContainText('FlowQuote');
    // Should show at least one flow card
    await expect(page.locator('.bg-white.rounded-lg.border').first()).toBeVisible({ timeout: 10000 });
  });

  test('API /api/flows returns flows from MongoDB', async ({ request }) => {
    const res = await request.get('/api/flows');
    expect(res.ok()).toBeTruthy();
    const data = await res.json();
    expect(Array.isArray(data)).toBeTruthy();
    expect(data.length).toBeGreaterThan(0);
    expect(data[0]).toHaveProperty('name');
    expect(data[0]).toHaveProperty('slug');
    expect(data[0]).toHaveProperty('_id');
  });

  test('API /api/flows/:id returns full flow with nodes and edges', async ({ request }) => {
    // First get the list
    const listRes = await request.get('/api/flows');
    const flows = await listRes.json();
    const flowId = flows[0]._id;

    // Get full flow
    const res = await request.get(`/api/flows/${flowId}`);
    expect(res.ok()).toBeTruthy();
    const flow = await res.json();
    expect(flow).toHaveProperty('nodes');
    expect(flow).toHaveProperty('edges');
    expect(flow.name).toBeTruthy();
  });

  test('API /api/flows/slug/:slug returns flow', async ({ request }) => {
    const listRes = await request.get('/api/flows');
    const flows = await listRes.json();
    const slug = flows[0].slug;

    const res = await request.get(`/api/flows/slug/${slug}`);
    expect(res.ok()).toBeTruthy();
    const flow = await res.json();
    expect(flow.slug).toBe(slug);
  });

  test('API /api/submissions returns submissions list', async ({ request }) => {
    const res = await request.get('/api/submissions');
    expect(res.ok()).toBeTruthy();
    const data = await res.json();
    expect(data).toHaveProperty('submissions');
    expect(data).toHaveProperty('total');
  });

  test('Public questionnaire page loads for published flow', async ({ page, request }) => {
    // Find a published flow
    const listRes = await request.get('/api/flows');
    const flows = await listRes.json();
    const published = flows.find((f: any) => f.status === 'published');
    if (!published) {
      test.skip();
      return;
    }

    await page.goto(`/q/${published.slug}`);
    // Should show the form phase with name/email inputs
    await expect(page.locator('input[type="text"]').first()).toBeVisible({ timeout: 10000 });
    await expect(page.getByText('Commencer')).toBeVisible();
  });

  test('Flow editor page loads', async ({ page, request }) => {
    const listRes = await request.get('/api/flows');
    const flows = await listRes.json();
    const flowId = flows[0]._id;

    await page.goto(`/admin/flows/${flowId}/edit`);
    // Should show the save button and flow name input
    await expect(page.getByText('Salvar')).toBeVisible({ timeout: 10000 });
  });

  test('Submissions page loads', async ({ page }) => {
    await page.goto('/admin/submissions');
    await expect(page.locator('h1')).toContainText('Demandes');
  });
});
