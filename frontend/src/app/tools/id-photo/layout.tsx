import { Metadata } from "next";

export const metadata: Metadata = {
  title: "ID Photo Generator | Smart Design Studio",
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
