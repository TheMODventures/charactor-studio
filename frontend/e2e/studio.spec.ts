import { test, expect } from '@playwright/test';

// Actual API, SQLite and FFmpeg worker; inference is tested separately.
test('approve a scene and exact script, render a real storyboard and reload', async ({ page }) => {
  await page.goto('/');
  await page
    .getByLabel('Dialogue line 1', { exact: true })
    .fill('A little perspective changes everything.');
  await page
    .getByLabel('Dialogue line 2', { exact: true })
    .fill('And a little sunshine helps, too.');
  await expect(page.getByRole('button', { name: 'Create talking video' })).toBeDisabled();
  await page.getByText('Optional silent storyboard preview', { exact: true }).click();
  await expect(page.getByRole('button', { name: 'Create silent storyboard' })).toBeDisabled();
  await page.getByLabel('I approve these exact words').check();
  await expect(page.getByRole('button', { name: 'Create talking video' })).toBeDisabled();
  await page.getByRole('button', { name: 'Create silent storyboard' }).click();
  await expect(page.getByText('Storyboard ready — no voice or animation').first()).toBeVisible({
    timeout: 60000,
  });
  const download = page.getByRole('link', { name: 'Download MP4' }).first();
  const response = await page.request.get((await download.getAttribute('href'))!);
  expect(response.ok()).toBeTruthy();
  expect((await response.body()).subarray(0, 64).includes(Buffer.from('ftyp'))).toBeTruthy();
  const preview = page.locator('video');
  await expect
    .poll(() => preview.evaluate((element: HTMLVideoElement) => element.duration))
    .toBeLessThan(10);
  await page.goto('/renders');
  await page.reload();
  await expect(download).toBeVisible();
});

test('mobile navigation and provider status are usable', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/settings');
  await expect(page.getByRole('heading', { name: 'Settings', exact: true })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'kokoro', exact: true })).toBeVisible();
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth > window.innerWidth,
  );
  expect(overflow).toBe(false);
  await page.getByRole('link', { name: 'Characters', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Characters', exact: true })).toBeVisible();
});

test('missing GPU voices are surfaced instead of a fake completed render', async ({ request }) => {
  const conversations = await (await request.get('/api/v1/conversations')).json();
  const scenes = await (await request.get('/api/v1/scenes')).json();
  const result = await request.post('/api/v1/generations', {
    data: {
      conversation_id: conversations[0].id,
      scene_id: scenes[0].id,
      kind: 'animated',
      target_seconds: 60,
    },
  });
  expect([422, 503]).toContain(result.status());
});
