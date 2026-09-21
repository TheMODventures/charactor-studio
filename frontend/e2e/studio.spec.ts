import { test, expect } from '@playwright/test';

// These tests use the actual API, SQLite and FFmpeg worker. No network interception.
// The fixture is a synthetic solid image, not a model-quality test.
const image = Buffer.from(
  'iVBORw0KGgoAAAANSUhEUgAAAoAAAAFoCAIAAABIUN0GAAAFl0lEQVR4nO3XMRHAMBDEQDv8iQRBKBhWWLwK7xK4UnP7e88CAGY9w3sAgAADQMMDBoCAAANAQIABICDAABAQYAAICDAABAQYAAICDAABAQaAgAADQECAASAgwAAQEGAACAgwAAQEGAACAgwAAQEGgIAAA0BAgAEgIMAAEBBgAAgIMAAEBBgAAgIMAAEBBoCAAANAQIABICDAABAQYAAICDAABAQYAAICDAABAQaAgAADQECAASAgwAAQEGAACAgwAAQEGAACAgwAAQEGgIAAA0BAgAEgIMAAEBBgAAgIMAAEBBgAAgIMAAEBBoCAAANAQIABICDAABAQYAAICDAABAQYAAICDAABAQaAgAADQECAASAgwAAQEGAACAgwAAQEGAACAgwAAQEGgIAAA0BAgAEgIMAAEBBgAAgIMAAEBBgAAgIMAAEBBoCAAANAQIABICDAABAQYAAICDAABAQYAAICDAABAQaAgAADQECAASAgwAAQEGAACAgwAAQEGAACAgwAAQEGgIAAA0BAgAEgIMAAEBBgAAgIMAAEBBgAAgIMAAEBBoCAAANAQIABICDAABAQYAAICDAABAQYAAICDAABAQaAgAADQECAASAgwAAQEGAACAgwAAQEGAACAgwAAQEGgIAAA0BAgAEgIMAAEBBgAAgIMAAEBBgAAgIMAAEBBoCAAANAQIABICDAABAQYAAICDAABAQYAAICDAABAQaAgAADQECAASAgwAAQEGAACAgwAAQEGAACAgwAAQEGgIAAA0BAgAEgIMAAEBBgAAgIMAAEBBgAAgIMAAEBBoCAAANAQIABICDAABAQYAAICDAABAQYAAICDAABAQaAgAADQECAASAgwAAQEGAACAgwAAQEGAACAgwAAQEGgIAAA0BAgAEgIMAAEBBgAAgIMAAEBBgAAgIMAAEBBoCAAANAQIABICDAABAQYAAICDAABAQYAAICDAABAQaAgAADQECAASAgwAAQEGAACAgwAAQEGAACAgwAAQEGgIAAA0BAgAEgIMAAEBBgAAgIMAAEBBgAAgIMAAEBBoCAAANAQIABICDAABAQYAAICDAABAQYAAICDAABAQaAgAADQECAASAgwAAQEGAACAgwAAQEGAACAgwAAQEGgIAAA0BAgAEgIMAAEBBgAAgIMAAEBBgAAgIMAAEBBoCAAANAQIABICDAABAQYAAICDAABAQYAAICDAABAQaAgAADQECAASAgwAAQEGAACAgwAAQEGAACAgwAAQEGgIAAA0BAgAEgIMAAEBBgAAgIMAAEBBgAAgIMAAEBBoCAAANAQIABICDAABAQYAAICDAABAQYAAICDAABAQaAgAADQECAASAgwAAQEGAACAgwAAQEGAACAgwAAQEGgIAAA0BAgAEgIMAAEBBgAAgIMAAEBBgAAgIMAAEBBoCAAANAQIABICDAABAQYAAICDAABAQYAAICDAABAQaAgAADQECAASAgwAAQEGAACAgwAAQEGAACAgwAAQEGgIAAA0BAgAEgIMAAEBBgAAgIMAAEBBgABBgA7uABA0BAgAEgIMAAEBBgAAgIMAAEBBgAAgIMAAEBBoCAAANAQIABICDAABAQYAAICDAABAQYAAICDAABAQYAAQaAO3jAABAQYAAICDAABAQYAAICDAABAQaAgAADQECAASAgwAAQEGAACAgwAAQEGAACAgwAAQEGgIAAA0BAgAEgIMAAEBBgAAgIMAAEBBgAAgIMAAEBBoCAAANAQIABICDAABAQYAAICDAABAQYAAICDAABAQaAgAADQECAASAgwAAQEGAACAgwAAQEGAACAgwAAQEGgIAAA0BAgAEgIMAAEBBgAAgIMAAEBBgAAgIMAAEBBoCAAANAQIABICDAABAQYAAICDAABAQYANa8H4AjBPggNxbsAAAAAElFTkSuQmCC',
  'base64',
);

test('edit a character and persist its speech preferences', async ({ page }) => {
  await page.goto('/characters');
  await page.getByRole('button', { name: 'Edit R.Royale' }).click();
  await page.getByRole('button', { name: 'Speech style', exact: true }).click();
  await page.getByLabel('Regional influence').fill('Creator approved regional expression');
  await page.getByRole('button', { name: 'Save character', exact: true }).click();
  await expect(page.getByRole('dialog')).not.toBeVisible();
  await page.reload();
  await page.getByRole('button', { name: 'Edit R.Royale' }).click();
  await page.getByRole('button', { name: 'Speech style', exact: true }).click();
  await expect(page.getByLabel('Regional influence')).toHaveValue(
    'Creator approved regional expression',
  );
});

test('approve a scene and exact script, render a real storyboard and reload', async ({ page }) => {
  await page.goto('/');
  await page
    .getByLabel('Upload image')
    .setInputFiles({ name: 'e2e-fictional-scene.png', mimeType: 'image/png', buffer: image });
  await page
    .getByLabel('Ownership or authorization details')
    .fill('Original synthetic image for automated testing');
  await page.getByLabel('I have rights to use this fictional image.').check();
  await page.getByRole('button', { name: 'Upload asset', exact: true }).click();
  await expect(page.getByRole('img', { name: 'Shared scene preview' })).toBeVisible();
  await page.getByLabel('Both fictional characters are visible').check();
  await page
    .getByLabel('Dialogue line 1', { exact: true })
    .fill('A little perspective changes everything.');
  await page
    .getByLabel('Dialogue line 2', { exact: true })
    .fill('And a little sunshine helps, too.');
  await expect(page.getByRole('button', { name: 'Create storyboard' })).toBeDisabled();
  await page.getByLabel('I approve these exact words').check();
  await page.getByLabel('Duration', { exact: true }).selectOption('10');
  await page.getByRole('button', { name: 'Create storyboard' }).click();
  await expect(page).toHaveURL(/renders/);
  await expect(page.getByText('Storyboard ready — no voice or animation').first()).toBeVisible({
    timeout: 60000,
  });
  const download = page.getByRole('link', { name: 'Download MP4' }).first();
  const response = await page.request.get((await download.getAttribute('href'))!);
  expect(response.ok()).toBeTruthy();
  expect((await response.body()).subarray(0, 64).includes(Buffer.from('ftyp'))).toBeTruthy();
  await page.reload();
  await expect(download).toBeVisible();
});

test('mobile navigation and provider status are usable', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/settings');
  await expect(page.getByRole('heading', { name: 'Your studio, connected.' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Chatterbox', exact: true })).toBeVisible();
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth > window.innerWidth,
  );
  expect(overflow).toBe(false);
  await page.getByRole('link', { name: 'Characters', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Characters with character.' })).toBeVisible();
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
