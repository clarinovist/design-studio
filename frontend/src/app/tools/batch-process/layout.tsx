import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Batch Process | Smart Design Studio",
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
