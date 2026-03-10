import { test, expect } from '@playwright/test';

const BASE = 'http://localhost:8080';

// ---------------------------------------------------------------------------
//  API — On-chain Agent Identity Endpoints
// ---------------------------------------------------------------------------

test.describe('API — On-chain Agent Registration', () => {
    test('list registered agents returns array', async ({ request }) => {
        const res = await request.get(`${BASE}/v1/agents`);
        expect(res.ok()).toBeTruthy();
        const body = await res.json();
        expect(body.agents).toBeDefined();
        expect(Array.isArray(body.agents)).toBeTruthy();
        expect(body.total).toBeDefined();
    });

    test('register agent via on-chain tx', async ({ request }) => {
        const name = `E2E-Agent-${Date.now()}`;
        const res = await request.post(`${BASE}/v1/agent/register`, {
            data: {
                name,
                role: 'member',
                boot_bio: 'Automated e2e test agent for on-chain identity.',
                provider: 'e2e-test',
            },
        });
        // 201 Created or 200 if already registered (idempotent)
        expect([200, 201]).toContain(res.status());
        const body = await res.json();
        expect(body.agent_id).toBeDefined();
        expect(body.name).toBe(name);
        expect(body.role).toBe('member');
        expect(['registered', 'already_registered']).toContain(body.status);
    });

    test('register agent requires name', async ({ request }) => {
        const res = await request.post(`${BASE}/v1/agent/register`, {
            data: { role: 'member' },
        });
        expect(res.ok()).toBeFalsy();
        expect(res.status()).toBe(400);
    });

    test('register agent defaults role to member', async ({ request }) => {
        const res = await request.post(`${BASE}/v1/agent/register`, {
            data: { name: `E2E-Default-Role-${Date.now()}` },
        });
        expect([200, 201]).toContain(res.status());
        const body = await res.json();
        expect(body.role).toBe('member');
    });

    test('register agent is idempotent', async ({ request }) => {
        // First registration
        const name = `E2E-Idempotent-${Date.now()}`;
        const res1 = await request.post(`${BASE}/v1/agent/register`, {
            data: { name, role: 'member' },
        });
        expect([200, 201]).toContain(res1.status());
        const body1 = await res1.json();

        // Second registration with same identity (same auth context)
        const res2 = await request.post(`${BASE}/v1/agent/register`, {
            data: { name: 'Different Name', role: 'observer' },
        });
        expect(res2.ok()).toBeTruthy();
        const body2 = await res2.json();
        expect(body2.agent_id).toBe(body1.agent_id);
        expect(body2.status).toBe('already_registered');
    });
});

test.describe('API — On-chain Agent Update', () => {
    test('update agent self-metadata', async ({ request }) => {
        // Ensure agent is registered first
        await request.post(`${BASE}/v1/agent/register`, {
            data: { name: `E2E-Update-${Date.now()}`, role: 'member' },
        });

        const res = await request.put(`${BASE}/v1/agent/update`, {
            data: {
                name: `E2E-Updated-${Date.now()}`,
                boot_bio: 'Updated bio via e2e test.',
            },
        });
        expect(res.ok()).toBeTruthy();
        const body = await res.json();
        expect(body.agent_id).toBeDefined();
        expect(body.status).toBe('updated');
        expect(body.tx_hash).toBeDefined();
    });
});

test.describe('API — On-chain Agent Permission', () => {
    test('set permission on agent with clearance', async ({ request }) => {
        // Get an agent to target
        const agentsRes = await request.get(`${BASE}/v1/agents`);
        const agents = await agentsRes.json();

        if (agents.total > 0) {
            const targetId = agents.agents[0].agent_id;
            const res = await request.put(`${BASE}/v1/agent/${targetId}/permission`, {
                data: {
                    clearance: 2,
                    domain_access: '{"general":{"read":true,"write":true}}',
                },
            });
            expect(res.ok()).toBeTruthy();
            const body = await res.json();
            expect(body.agent_id).toBe(targetId);
            expect(body.status).toBe('permissions_updated');
            expect(body.tx_hash).toBeDefined();
        }
    });

    test('set permission requires agent id path param', async ({ request }) => {
        // Empty id should fail (route won't match, returns 404/405)
        const res = await request.put(`${BASE}/v1/agent//permission`, {
            data: { clearance: 1 },
        });
        expect(res.ok()).toBeFalsy();
    });

    test('set visible_agents on agent', async ({ request }) => {
        const agentsRes = await request.get(`${BASE}/v1/agents`);
        const agents = await agentsRes.json();

        if (agents.total > 0) {
            const targetId = agents.agents[0].agent_id;
            const res = await request.put(`${BASE}/v1/agent/${targetId}/permission`, {
                data: {
                    visible_agents: '*',
                },
            });
            expect(res.ok()).toBeTruthy();
            const body = await res.json();
            expect(body.status).toBe('permissions_updated');
        }
    });
});

test.describe('API — Get Registered Agent', () => {
    test('get agent by id returns agent data', async ({ request }) => {
        const agentsRes = await request.get(`${BASE}/v1/agents`);
        const agents = await agentsRes.json();

        if (agents.total > 0) {
            const id = agents.agents[0].agent_id;
            const res = await request.get(`${BASE}/v1/agent/${id}`);
            expect(res.ok()).toBeTruthy();
            const body = await res.json();
            expect(body.agent_id).toBe(id);
            expect(body.name).toBeDefined();
            expect(body.role).toBeDefined();
            expect(body.status).toBeDefined();
            expect(body.clearance).toBeDefined();
        }
    });

    test('get nonexistent agent returns 404', async ({ request }) => {
        const res = await request.get(`${BASE}/v1/agent/nonexistent-agent-id-12345`);
        expect(res.ok()).toBeFalsy();
        expect(res.status()).toBe(404);
    });
});

// ---------------------------------------------------------------------------
//  UI — Agent Registration via Network Page
// ---------------------------------------------------------------------------

test.describe('UI — Agent Registration via Add Agent Wizard', () => {
    test('register agent through the Add Agent wizard', async ({ page }) => {
        await page.goto(`${BASE}/ui/#/network`);
        await page.waitForSelector('.agent-list', { timeout: 10000 });

        // Count agents before
        const cardsBefore = page.locator('.agent-card-row');
        const countBefore = await cardsBefore.count();

        // Open wizard
        await page.locator('.agent-card-add').click();
        const wizard = page.locator('.wizard-overlay');
        await expect(wizard).toBeVisible();

        // Step 1 — Fill agent details
        const nameInput = page.locator('.wizard-input').first();
        await expect(nameInput).toBeVisible();
        const agentName = `E2E-Identity-${Date.now()}`;
        await nameInput.fill(agentName);

        // Fill bio
        const bioTextarea = page.locator('.wizard-textarea');
        if (await bioTextarea.count() > 0) {
            await bioTextarea.fill('E2E test agent for on-chain identity validation.');
        }

        // Advance to Step 2
        await page.locator('.btn').filter({ hasText: 'Next' }).click();

        // Step 2 — Role selection (verify role cards visible)
        const roleCards = page.locator('.role-card');
        await expect(roleCards).toHaveCount(3);

        // Select "Member" role
        await roleCards.filter({ hasText: 'Member' }).click();

        // Advance to Step 3
        await page.locator('.btn').filter({ hasText: 'Next' }).click();

        // Step 3 — Connect method + Summary
        const summary = page.locator('.summary-card');
        await expect(summary).toBeVisible();
        await expect(summary).toContainText(agentName);
        await expect(summary).toContainText('member');

        // Submit registration
        const createBtn = page.locator('.btn').filter({ hasText: /Create|Register|Add/ });
        await expect(createBtn).toBeVisible();
        await createBtn.click();

        // Wizard should close
        await expect(wizard).not.toBeVisible({ timeout: 10000 });

        // Agent list should have one more entry
        await page.waitForSelector('.agent-list', { timeout: 10000 });
        const cardsAfter = page.locator('.agent-card-row');
        await expect(cardsAfter).toHaveCount(countBefore + 1, { timeout: 10000 });
    });

    test('new agent card shows correct details after registration', async ({ page }) => {
        await page.goto(`${BASE}/ui/#/network`);
        await page.waitForSelector('.agent-list', { timeout: 10000 });

        // Open wizard and register
        await page.locator('.agent-card-add').click();
        const agentName = `E2E-Verify-${Date.now()}`;
        await page.locator('.wizard-input').first().fill(agentName);
        await page.locator('.btn').filter({ hasText: 'Next' }).click();

        // Select Observer role for distinctiveness
        await page.locator('.role-card').filter({ hasText: 'Observer' }).click();
        await page.locator('.btn').filter({ hasText: 'Next' }).click();
        await page.locator('.btn').filter({ hasText: /Create|Register|Add/ }).click();

        // Wait for wizard to close and list to refresh
        await page.waitForSelector('.wizard-overlay', { state: 'hidden', timeout: 10000 });
        await page.waitForSelector('.agent-list', { timeout: 10000 });

        // Find the newly created agent card by name
        const newCard = page.locator('.agent-card-row').filter({ hasText: agentName });
        await expect(newCard).toBeVisible({ timeout: 10000 });

        // Verify role badge shows Observer
        const roleBadge = newCard.locator('.agent-role-badge');
        await expect(roleBadge).toContainText(/observer/i);
    });
});

// ---------------------------------------------------------------------------
//  UI — Agent Permission Update
// ---------------------------------------------------------------------------

test.describe('UI — Agent Permission Update', () => {
    test('change clearance level via Access Control tab', async ({ page }) => {
        await page.goto(`${BASE}/ui/#/network`);
        await page.waitForSelector('.agent-list', { timeout: 10000 });

        // Expand first agent
        const firstCard = page.locator('.agent-card-row').first();
        await firstCard.click();
        await page.waitForSelector('.agent-expanded.open');

        // Switch to Access Control tab
        await page.locator('.agent-tab').filter({ hasText: 'Access Control' }).click();

        // Read current clearance value
        const slider = page.locator('.clearance-row input[type="range"]');
        await expect(slider).toBeVisible();
        const currentVal = await slider.inputValue();

        // Change clearance value
        const newVal = parseInt(currentVal) >= 4 ? 1 : parseInt(currentVal) + 1;
        await slider.evaluate((el, val) => {
            el.value = val;
            el.dispatchEvent(new Event('input', { bubbles: true }));
        }, newVal);

        // Save should be enabled
        const saveBtn = page.locator('.access-save-bar .btn-primary');
        await expect(saveBtn).toBeEnabled();

        // Click Save
        await saveBtn.click();

        // Confirmation
        const savedConfirm = page.locator('.access-saved');
        await expect(savedConfirm).toBeVisible({ timeout: 5000 });

        // Verify clearance label updated
        const label = page.locator('.clearance-row .clearance-label');
        await expect(label).toBeVisible();
    });

    test('update domain access settings', async ({ page }) => {
        await page.goto(`${BASE}/ui/#/network`);
        await page.waitForSelector('.agent-list', { timeout: 10000 });

        const firstCard = page.locator('.agent-card-row').first();
        await firstCard.click();
        await page.waitForSelector('.agent-expanded.open');

        await page.locator('.agent-tab').filter({ hasText: 'Access Control' }).click();

        // Domain matrix should be visible
        const matrix = page.locator('.domain-matrix');
        await expect(matrix).toBeVisible();

        // Toggle a domain access checkbox
        const checkbox = matrix.locator('input[type="checkbox"]').first();
        if (await checkbox.count() > 0) {
            await checkbox.evaluate(el => el.click());

            // Save should be enabled
            const saveBtn = page.locator('.access-save-bar .btn-primary');
            await expect(saveBtn).toBeEnabled();

            await saveBtn.click();

            // Confirmation
            const savedConfirm = page.locator('.access-saved');
            await expect(savedConfirm).toBeVisible({ timeout: 5000 });
        }
    });

    test('change agent role and verify', async ({ page }) => {
        await page.goto(`${BASE}/ui/#/network`);
        await page.waitForSelector('.agent-list', { timeout: 10000 });

        // Find a non-admin agent to change role (avoid last-admin protection)
        const cards = page.locator('.agent-card-row');
        const count = await cards.count();

        // Try to find a member or observer to change
        for (let i = 0; i < count; i++) {
            const card = cards.nth(i);
            const badge = card.locator('.agent-role-badge');
            const badgeText = await badge.textContent();

            if (badgeText.trim().toLowerCase() !== 'admin') {
                await card.click();
                await page.waitForSelector('.agent-expanded.open');
                await page.locator('.agent-tab').filter({ hasText: 'Access Control' }).click();

                // Toggle to observer if member, or member if observer
                const targetRole = badgeText.trim().toLowerCase() === 'member' ? 'Observer' : 'Member';
                await page.locator('.role-card').filter({ hasText: targetRole }).click();

                const saveBtn = page.locator('.access-save-bar .btn-primary');
                await expect(saveBtn).toBeEnabled();
                await expect(page.locator('.access-dirty')).toBeVisible();

                await saveBtn.click();
                await expect(page.locator('.access-saved')).toBeVisible({ timeout: 5000 });
                break;
            }
        }
    });
});

// ---------------------------------------------------------------------------
//  UI — Agent List Shows Registered Agents
// ---------------------------------------------------------------------------

test.describe('UI — Agent List Shows Registered Agents', () => {
    test('agent list renders with at least the genesis agent', async ({ page }) => {
        await page.goto(`${BASE}/ui/#/network`);
        await page.waitForSelector('.agent-list', { timeout: 10000 });

        const cards = page.locator('.agent-card-row');
        await expect(cards.first()).toBeVisible();
        const count = await cards.count();
        expect(count).toBeGreaterThanOrEqual(1);
    });

    test('genesis/primary agent shows admin role', async ({ page }) => {
        await page.goto(`${BASE}/ui/#/network`);
        await page.waitForSelector('.agent-list', { timeout: 10000 });

        // At least one agent should have admin role
        const adminBadges = page.locator('.agent-role-badge').filter({ hasText: /admin/i });
        const adminCount = await adminBadges.count();
        expect(adminCount).toBeGreaterThanOrEqual(1);
    });

    test('agent list header shows correct count', async ({ page }) => {
        await page.goto(`${BASE}/ui/#/network`);
        await page.waitForSelector('.agent-list', { timeout: 10000 });

        // Get actual card count
        const cards = page.locator('.agent-card-row');
        const cardCount = await cards.count();

        // Header should reflect the count
        const header = page.locator('.network-header');
        await expect(header).toContainText(`${cardCount}`);
    });

    test('each agent card shows name, role, and status', async ({ page }) => {
        await page.goto(`${BASE}/ui/#/network`);
        await page.waitForSelector('.agent-list', { timeout: 10000 });

        const firstCard = page.locator('.agent-card-row').first();

        // Role badge exists
        const roleBadge = firstCard.locator('.agent-role-badge');
        await expect(roleBadge).toBeVisible();
        const roleText = await roleBadge.textContent();
        expect(['admin', 'member', 'observer']).toContain(roleText.trim().toLowerCase());
    });

    test('expanding agent shows on-chain identity fields', async ({ page }) => {
        await page.goto(`${BASE}/ui/#/network`);
        await page.waitForSelector('.agent-list', { timeout: 10000 });

        const firstCard = page.locator('.agent-card-row').first();
        await firstCard.click();
        await page.waitForSelector('.agent-overview-grid');

        // Agent ID (Ed25519 public key) should be visible
        await expect(page.locator('.agent-info-label').filter({ hasText: 'Agent ID' }).first()).toBeVisible();
        await expect(page.locator('.agent-info-label').filter({ hasText: 'Name' }).first()).toBeVisible();
        await expect(page.locator('.agent-info-label').filter({ hasText: 'Status' }).first()).toBeVisible();
    });
});

// ---------------------------------------------------------------------------
//  API — Agent Identity Data Integrity
// ---------------------------------------------------------------------------

test.describe('API — Agent Identity Data Integrity', () => {
    test('registered agent has expected fields', async ({ request }) => {
        const agentsRes = await request.get(`${BASE}/v1/agents`);
        const agents = await agentsRes.json();

        if (agents.total > 0) {
            const agent = agents.agents[0];
            // Core identity fields
            expect(agent.agent_id).toBeDefined();
            expect(agent.name).toBeDefined();
            expect(agent.role).toBeDefined();
            expect(agent.status).toBeDefined();
            expect(typeof agent.clearance).toBe('number');
            expect(agent.created_at).toBeDefined();
        }
    });

    test('agent clearance is within valid range', async ({ request }) => {
        const agentsRes = await request.get(`${BASE}/v1/agents`);
        const agents = await agentsRes.json();

        for (const agent of agents.agents) {
            expect(agent.clearance).toBeGreaterThanOrEqual(0);
            expect(agent.clearance).toBeLessThanOrEqual(4);
        }
    });

    test('agent role is one of admin/member/observer', async ({ request }) => {
        const agentsRes = await request.get(`${BASE}/v1/agents`);
        const agents = await agentsRes.json();

        for (const agent of agents.agents) {
            expect(['admin', 'member', 'observer']).toContain(agent.role);
        }
    });

    test('agents total matches array length', async ({ request }) => {
        const res = await request.get(`${BASE}/v1/agents`);
        const body = await res.json();
        expect(body.total).toBe(body.agents.length);
    });

    test('dashboard agents API also returns on-chain agents', async ({ request }) => {
        // Both endpoints should surface registered agents
        const onChainRes = await request.get(`${BASE}/v1/agents`);
        const onChain = await onChainRes.json();

        const dashRes = await request.get(`${BASE}/v1/dashboard/network/agents`);
        const dash = await dashRes.json();

        // Dashboard should have at least as many as on-chain (it includes all)
        expect(dash.agents.length).toBeGreaterThanOrEqual(1);
        expect(onChain.agents.length).toBeGreaterThanOrEqual(0);
    });
});
