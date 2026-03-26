import { test, expect } from '@playwright/test';

test.describe('Formulario de qualificacao IT Valley', () => {

  test('lead qualificado (TI + diploma) → vai para calendario', async ({ page }) => {
    await page.goto('/q/form-pos-ia');
    await page.waitForSelector('input[type="text"]', { timeout: 10000 });

    // Etapa 1: Dados pessoais
    await page.locator('input[type="text"]').first().fill('Maria Teste');
    await page.fill('input[type="email"]', 'maria@itvalley.com');
    await page.fill('input[type="tel"]', '11999999999');
    await page.click('button:has-text("Comecar")');

    // Etapa 2: Area de atuacao → TI (qualificado)
    await page.waitForSelector('text=area de atuacao', { timeout: 10000 });
    await page.click('button:has-text("Tecnologia da Informacao")');

    // Etapa 3: Diploma → Sim (qualificado)
    await page.waitForSelector('text=diploma', { timeout: 5000 });
    await page.click('button:has-text("Sim")');

    // Etapa 4: Objetivo → qualquer opcao
    await page.waitForSelector('text=especializar', { timeout: 5000 });
    await page.click('button:has-text("Crescimento de carreira")');

    // Etapa 4: Investimento → Sim
    await page.waitForSelector('text=investimento', { timeout: 5000 });
    await page.click('button:has-text("Sim, consigo")');

    // Deve ir para o CALENDARIO, nao para devis
    await expect(page.locator('text=Escolha o dia')).toBeVisible({ timeout: 15000 });
    await expect(page.locator('text=Dom')).toBeVisible();
    await expect(page.locator('text=Seg')).toBeVisible();
  });

  test('lead desqualificado por area → mensagem de encerramento', async ({ page }) => {
    await page.goto('/q/form-pos-ia');
    await page.waitForSelector('input[type="text"]', { timeout: 10000 });

    // Dados pessoais
    await page.locator('input[type="text"]').first().fill('Joao Teste');
    await page.fill('input[type="email"]', 'joao@teste.com');
    await page.fill('input[type="tel"]', '11888888888');
    await page.click('button:has-text("Comecar")');

    // Area → Outra area (desqualificado)
    await page.waitForSelector('text=area de atuacao', { timeout: 10000 });
    await page.click('button:has-text("Outra area")');

    // Deve mostrar mensagem de encerramento
    await expect(page.locator('text=Obrigado pelo interesse')).toBeVisible({ timeout: 10000 });
    // Nao deve mostrar calendario
    await expect(page.locator('text=Escolha o dia')).toHaveCount(0);
  });

  test('lead desqualificado por diploma → mensagem de encerramento', async ({ page }) => {
    await page.goto('/q/form-pos-ia');
    await page.waitForSelector('input[type="text"]', { timeout: 10000 });

    // Dados pessoais
    await page.locator('input[type="text"]').first().fill('Ana Teste');
    await page.fill('input[type="email"]', 'ana@teste.com');
    await page.fill('input[type="tel"]', '11777777777');
    await page.click('button:has-text("Comecar")');

    // Area → TI (qualificado)
    await page.waitForSelector('text=area de atuacao', { timeout: 10000 });
    await page.click('button:has-text("Tecnologia da Informacao")');

    // Diploma → Nao possuo graduacao (desqualificado)
    await page.waitForSelector('text=diploma', { timeout: 5000 });
    await page.click('button:has-text("Nao possuo")');

    // Deve mostrar mensagem de exigencia de diploma
    await expect(page.locator('text=exige diploma')).toBeVisible({ timeout: 10000 });
    // Nao deve mostrar calendario
    await expect(page.locator('text=Escolha o dia')).toHaveCount(0);
  });

  test('lead cursando + sem condicoes financeiras → ainda vai para calendario', async ({ page }) => {
    await page.goto('/q/form-pos-ia');
    await page.waitForSelector('input[type="text"]', { timeout: 10000 });

    // Dados pessoais
    await page.locator('input[type="text"]').first().fill('Pedro Teste');
    await page.fill('input[type="email"]', 'pedro@teste.com');
    await page.fill('input[type="tel"]', '11666666666');
    await page.click('button:has-text("Comecar")');

    // Area → TI
    await page.waitForSelector('text=area de atuacao', { timeout: 10000 });
    await page.click('button:has-text("Tecnologia da Informacao")');

    // Diploma → Cursando (neutro, avanca)
    await page.waitForSelector('text=diploma', { timeout: 5000 });
    await page.click('button:has-text("Ainda estou cursando")');

    // Objetivo → qualquer
    await page.waitForSelector('text=especializar', { timeout: 5000 });
    await page.click('button:has-text("Transicao para a area")');

    // Investimento → Nao (avanca com ressalva, comercial avalia)
    await page.waitForSelector('text=investimento', { timeout: 5000 });
    await page.click('button:has-text("No momento nao")');

    // Mesmo com "nao", deve ir para calendario (comercial avalia depois)
    await expect(page.locator('text=Escolha o dia')).toBeVisible({ timeout: 15000 });
  });
});
