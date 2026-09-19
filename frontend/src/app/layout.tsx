import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { ServiceWorkerRegister } from "@/components/offline/ServiceWorkerRegister";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "SGEP — Groupe Scolaire Privé Fodeba Keita",
  description:
    "Plateforme de gestion scolaire maternelle et primaire — Conakry, Guinée",
  manifest: "/manifest.json",
  appleWebApp: {
    capable: true,
    title: "SGEP",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr" className={`${inter.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col bg-drafting-gray text-graphite-ink font-sans">
        <ServiceWorkerRegister />
        {children}
      </body>
    </html>
  );
}
