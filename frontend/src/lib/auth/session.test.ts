import { beforeEach, describe, expect, it } from "vitest";
import { clearSession, getToken, getUser, hasPermission, saveSession } from "./session";
import type { UserInfo } from "@/types/auth";

const mockUser: UserInfo = {
  id: "u1",
  email: "admin@fodebakeita.gn",
  nom: "Admin",
  prenom: "SGEP",
  role: "super_admin",
  permissions: ["users.manage", "students.view"],
};

beforeEach(() => {
  clearSession();
});

describe("session", () => {
  it("saveSession et getToken/getUser", () => {
    saveSession("access-token", "refresh-token", mockUser);
    expect(getToken()).toBe("access-token");
    expect(getUser()?.email).toBe("admin@fodebakeita.gn");
  });

  it("clearSession efface les données", () => {
    saveSession("t1", "t2", mockUser);
    clearSession();
    expect(getToken()).toBeNull();
    expect(getUser()).toBeNull();
  });

  it("hasPermission direct et implicite", () => {
    const secretaire: UserInfo = {
      ...mockUser,
      role: "secretaire",
      permissions: ["students.view", "students.enroll"],
    };
    saveSession("t", "r", secretaire);
    expect(hasPermission("students.view")).toBe(true);
    expect(hasPermission("students.enroll")).toBe(true);
    expect(hasPermission("settings.view")).toBe(false);
  });

  it("super_admin a toutes les permissions", () => {
    saveSession("t", "r", mockUser);
    expect(hasPermission("any.permission")).toBe(true);
  });
});
