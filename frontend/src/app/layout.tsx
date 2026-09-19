import type { Metadata } from "next";
import { DM_Mono, DM_Sans, Outfit } from "next/font/google";
import { ServiceWorkerRegister } from "@/components/offline/ServiceWorkerRegister";
import "./globals.css";

const dmSans = DM_Sans({
  variable: "--font-dm-sans",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

const dmMono = DM_Mono({
  variable: "--font-dm-mono",
  subsets: ["latin"],
  weight: ["400", "500"],
});

const outfit = Outfit({
  variable: "--font-outfit",
  subsets: ["latin"],
  weight: ["300", "400", "500"],
});

export const metadata: Metadata = {
  title: "SGEP · Groupe Scolaire Privé Fodeba Keita",
  description: "Plateforme de gestion scolaire maternelle et primaire à Conakry, Guinée",
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
    <html
      lang="fr"
      className={`${dmSans.variable} ${dmMono.variable} ${outfit.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-midnight-navy text-canvas-white font-sans">
        <ServiceWorkerRegister />
        {children}
      </body>
    </html>
  );
}
