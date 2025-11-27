"use client"

import { LogoFramed } from "@/components/brand/LogoFramed"

export default function BrandAssets() {
  return (
    <main className="min-h-screen px-6 py-12 text-(--foreground)">
      <h1 className="text-3xl font-bold mb-6">Brand Assets</h1>
      <p className="text-(--muted) mb-8">High-resolution framed logo suitable for digital and print.</p>

      <div className="grid gap-12">
        <section>
          <h2 className="text-xl font-semibold mb-4">Preview (3000x3000)</h2>
          <div className="overflow-auto rounded-xl border border-(--border) p-4 bg-(--card)">
            <LogoFramed widthPx={1200} heightPx={1200} />
          </div>
        </section>

        <section className="grid gap-6">
          <h2 className="text-xl font-semibold">Export Sizes</h2>
          <ul className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <li className="p-4 rounded-lg border border-(--border) bg-(--card)">
              <div className="font-medium">Website Header</div>
              <div className="text-sm text-(--muted)">1920px width</div>
              <a className="text-(--primary) mt-2 inline-block" href="/brand/logo-framed-header.svg" download>
                Download SVG
              </a>
            </li>
            <li className="p-4 rounded-lg border border-(--border) bg-(--card)">
              <div className="font-medium">Office Wall</div>
              <div className="text-sm text-(--muted)">36x36 inches (10800px @300DPI)</div>
              <a className="text-(--primary) mt-2 inline-block" href="/brand/logo-framed-36in.svg" download>
                Download SVG
              </a>
            </li>
            <li className="p-4 rounded-lg border border-(--border) bg-(--card)">
              <div className="font-medium">Trade Show Banner</div>
              <div className="text-sm text-(--muted)">8ft width (14400px @150DPI)</div>
              <a className="text-(--primary) mt-2 inline-block" href="/brand/logo-framed-8ft.svg" download>
                Download SVG
              </a>
            </li>
          </ul>
        </section>
      </div>
    </main>
  )
}

