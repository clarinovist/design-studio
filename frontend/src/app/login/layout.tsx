import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Login | Smart Design Studio",
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
