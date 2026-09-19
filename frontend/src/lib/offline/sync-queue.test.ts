import { describe, expect, it } from "vitest";
import { parseOfflineMutation } from "./sync-queue";

describe("parseOfflineMutation", () => {
  it("détecte la mise à jour de notes", () => {
    const result = parseOfflineMutation(
      "/api/v1/notes/evaluations/abc-123/notes",
      "PUT",
      JSON.stringify({ notes: [{ eleve_id: "e1", valeur: 14 }] }),
    );
    expect(result?.entityType).toBe("notes");
    expect(result?.payload.evaluation_id).toBe("abc-123");
  });

  it("détecte la sauvegarde de présences", () => {
    const result = parseOfflineMutation(
      "/api/v1/presences/classes/cl1/appels?date=2025-10-01",
      "PUT",
      JSON.stringify({ presences: [{ eleve_id: "e1", statut: "present" }] }),
    );
    expect(result?.entityType).toBe("presence");
    expect(result?.payload.appel_date).toBe("2025-10-01");
  });

  it("détecte la création de paiement", () => {
    const result = parseOfflineMutation(
      "/api/v1/paiements",
      "POST",
      JSON.stringify({ eleve_id: "e1", montant: 50000 }),
    );
    expect(result?.entityType).toBe("paiement");
  });

  it("ignore les GET", () => {
    expect(parseOfflineMutation("/api/v1/eleves", "GET", undefined)).toBeNull();
  });
});
