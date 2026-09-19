import { expect, test } from "@playwright/test";

const ADMIN_EMAIL = "admin@fodebakeita.gn";
const ADMIN_PASSWORD = "admin123";
const API_URL = process.env.PLAYWRIGHT_API_URL ?? "http://localhost:8000";

async function apiAvailable(): Promise<boolean> {
  try {
    const res = await fetch(`${API_URL}/api/v1/health`);
    return res.ok;
  } catch {
    return false;
  }
}

test.describe("Parcours E2E SGEP", () => {
  test.beforeEach(async () => {
    test.skip(!(await apiAvailable()), "API non disponible — lancer docker-compose ou uvicorn");
  });

  test("connexion admin et tableau de bord", async ({ page }) => {
    await page.goto("/login");
    await page.fill("#email", ADMIN_EMAIL);
    await page.fill("#password", ADMIN_PASSWORD);
    await page.getByRole("button", { name: /se connecter/i }).click();
    await expect(page).toHaveURL(/\/dashboard/);
    await expect(page.getByText("Tableau de bord")).toBeVisible();
  });

  test("navigation modules clés après connexion", async ({ page }) => {
    await page.goto("/login");
    await page.fill("#email", ADMIN_EMAIL);
    await page.fill("#password", ADMIN_PASSWORD);
    await page.getByRole("button", { name: /se connecter/i }).click();
    await expect(page).toHaveURL(/\/dashboard/);

    await page.goto("/dashboard/eleves");
    await expect(page.getByText(/élèves/i).first()).toBeVisible();

    await page.goto("/dashboard/notes");
    await expect(page.getByText(/notes/i).first()).toBeVisible();

    await page.goto("/dashboard/finance");
    await expect(page.getByText(/finance|paiement/i).first()).toBeVisible();
  });

  test("parcours API inscription → bulletin → paiement", async ({ request }) => {
    const login = await request.post(`${API_URL}/api/v1/auth/login`, {
      data: { email: ADMIN_EMAIL, password: ADMIN_PASSWORD },
    });
    expect(login.ok()).toBeTruthy();
    const token = (await login.json()).access_token;
    const headers = { Authorization: `Bearer ${token}` };

    const classes = (await (await request.get(`${API_URL}/api/v1/parametrage/classes`, { headers })).json());
    const classe = classes[0];
    const matieres = await (await request.get(`${API_URL}/api/v1/parametrage/matieres`, { headers })).json();
    const annee = await (
      await request.get(`${API_URL}/api/v1/parametrage/annees-scolaires/active`, { headers })
    ).json();
    const periodes = await (
      await request.get(`${API_URL}/api/v1/parametrage/periodes?annee_scolaire_id=${annee.id}`, { headers })
    ).json();
    const typesEval = await (await request.get(`${API_URL}/api/v1/notes/types-evaluation`, { headers })).json();
    const typesFrais = await (await request.get(`${API_URL}/api/v1/parametrage/types-frais`, { headers })).json();
    const scol = typesFrais.find((t: { code: string }) => t.code === "SCOLARITE");

    const eleveRes = await request.post(`${API_URL}/api/v1/eleves`, {
      headers,
      data: {
        nom: "E2E",
        prenoms: "Playwright",
        sexe: "M",
        date_naissance: "2015-02-01",
        niveau_id: classe.niveau_id,
        tuteurs: [{ type: "pere", nom: "E2E", prenoms: "Parent", telephone: "+224621666666" }],
      },
    });
    expect(eleveRes.ok()).toBeTruthy();
    const eleve = await eleveRes.json();

    await request.post(`${API_URL}/api/v1/eleves/${eleve.id}/affecter-classe`, {
      headers,
      data: { classe_id: classe.id },
    });

    const evRes = await request.post(`${API_URL}/api/v1/notes/evaluations`, {
      headers,
      data: {
        libelle: "E2E Eval",
        classe_id: classe.id,
        matiere_id: matieres[0].id,
        periode_id: periodes[0].id,
        type_evaluation_id: typesEval[0].id,
      },
    });
    const evaluation = await evRes.json();

    await request.put(`${API_URL}/api/v1/notes/evaluations/${evaluation.id}/notes`, {
      headers,
      data: { notes: [{ eleve_id: eleve.id, valeur: 13 }] },
    });

    const bulletin = await request.get(
      `${API_URL}/api/v1/bulletins/eleve/${eleve.id}/periodes/${periodes[0].id}/pdf`,
      { headers },
    );
    expect(bulletin.ok()).toBeTruthy();

    const paiement = await request.post(`${API_URL}/api/v1/paiements`, {
      headers,
      data: {
        eleve_id: eleve.id,
        type_frais_id: scol.id,
        montant: 30000,
        mode_paiement: "especes",
        annee_scolaire_id: annee.id,
      },
    });
    expect(paiement.ok()).toBeTruthy();
    expect((await paiement.json()).numero_recu).toBeTruthy();
  });
});
