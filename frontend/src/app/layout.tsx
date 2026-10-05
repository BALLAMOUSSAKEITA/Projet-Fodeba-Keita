import type { Metadata } from "next";
import { DM_Sans } from "next/font/google";
import { ServiceWorkerRegister } from "@/components/offline/ServiceWorkerRegister";
import "./globals.css";

const dmSans = DM_Sans({
  variable: "--font-dm-sans",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "GSP · Groupe scolaire privé Fodeba Keita",
  description: "Plateforme de gestion scolaire maternelle et primaire à Conakry, Guinée",
  manifest: "/manifest.json",
  appleWebApp: {
    capable: true,
    title: "GSP",
  },
};

export const viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr" className={`${dmSans.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col bg-slate-50 text-slate-900 font-sans">
        <ServiceWorkerRegister />
        {children}
      </body>
    </html>
  );
}
