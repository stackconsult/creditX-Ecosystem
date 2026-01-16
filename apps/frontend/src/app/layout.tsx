import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { CopilotKit } from "@copilotkit/react-core";
import "@copilotkit/react-ui/styles.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "CreditX Ecosystem",
  description: "Enterprise Credit Intelligence Platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <CopilotKit
          runtimeUrl="/api/copilotkit"
          publicApiKey={process.env.NEXT_PUBLIC_COPILOTKIT_API_KEY}
        >
          {children}
        </CopilotKit>
      </body>
    </html>
  );
}
