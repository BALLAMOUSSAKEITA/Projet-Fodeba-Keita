import type { UserInfo } from "@/types/auth";

const TOKEN_KEY = "sgep_token";
const REFRESH_KEY = "sgep_refresh_token";
const USER_KEY = "sgep_user";

export function saveSession(
  accessToken: string,
  refreshToken: string,
  user: UserInfo,
): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(TOKEN_KEY, accessToken);
  localStorage.setItem(REFRESH_KEY, refreshToken);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
  document.cookie = `sgep_token=${accessToken}; path=/; max-age=3600; SameSite=Lax`;
}

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(REFRESH_KEY);
}

export function getUser(): UserInfo | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as UserInfo;
  } catch {
    return null;
  }
}

export function hasPermission(code: string): boolean {
  const user = getUser();
  if (!user) return false;
  if (user.permissions.includes(code)) return true;
  if (code === "settings.view" && user.permissions.includes("settings.manage")) return true;
  if (code === "students.view" && user.permissions.includes("students.enroll")) return true;
  if (code === "personnel.view" && user.permissions.includes("personnel.manage")) return true;
  if (code === "timetable.view" && user.permissions.includes("timetable.manage")) return true;
  if (code === "grades.modify" && user.permissions.includes("grades.validate_bulletins")) return true;
  if (code === "grades.validate_bulletins" && user.permissions.includes("grades.modify")) return true;
  if (code === "attendance.view" && user.permissions.includes("attendance.manage")) return true;
  if (code === "payments.view" && user.permissions.includes("payments.collect")) return true;
  if (code === "payroll.view" && user.permissions.includes("payroll.generate")) return true;
  if (code === "communication.view" && user.permissions.includes("communication.manage")) return true;
  if (code === "reports.view" && user.permissions.includes("reports.view_pedagogical")) return true;
  if (code === "reports.view_pedagogical" && user.permissions.includes("reports.view")) return true;
  if (user.role === "super_admin") return true;
  return false;
}

export function clearSession(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
  localStorage.removeItem(USER_KEY);
  document.cookie = "sgep_token=; path=/; max-age=0";
}

export const ROLE_LABELS: Record<string, string> = {
  super_admin: "Super administrateur",
  directeur: "Directeur",
  secretaire: "Secrétaire",
  econome: "Économe",
  enseignant: "Enseignant",
  surveillant: "Surveillant",
  parent: "Parent",
};
