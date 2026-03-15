import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Generative Expand | Smart Design Studio",
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
