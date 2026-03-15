import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Watermark Placer | Smart Design Studio",
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
