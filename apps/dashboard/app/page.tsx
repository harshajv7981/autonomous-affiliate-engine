'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';

const navItems = ['Overview', 'Offers', 'Audiences', 'Campaigns', 'Finance', 'System'];
const API = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

type Overview = {
  revenue: number;
  net_profit: number;
  roi: number;
  active_campaigns: number;
  clicks: number;
  conversions: number;
};

type CampaignRow = {
  campaign_id: string;
  name: string;
  clicks: number;
  conversions: number;
  revenue: number;
  net_contribution: number;
  action: string;
};

const money = (n: number) => `$${n.toFixed(2)}`;

export default function DashboardPage() {
  const [overview, setOverview] = useState<Overview | null>(null);
  const [campaigns, setCampaigns] = useState<CampaignRow[]>([]);
  const [live, setLive] = useState(false);

  useEffect(() => {
    // Live numbers from the engine; falls back to a placeholder if the API is down.
    Promise.all([
      fetch(`${API}/api/analytics/overview`).then((r) => r.json()),
      fetch(`${API}/api/analytics/campaigns`).then((r) => r.json()),
    ])
      .then(([o, c]) => {
        setOverview(o);
        setCampaigns(c.campaigns ?? []);
        setLive(true);
      })
      .catch(() => setLive(false));
  }, []);

  const metrics = overview
    ? [
        { label: 'Revenue', value: money(overview.revenue), tone: '#0f766e' },
        { label: 'Net Profit', value: money(overview.net_profit), tone: '#1d4ed8' },
        { label: 'Active Campaigns', value: String(overview.active_campaigns), tone: '#7c3aed' },
        { label: 'Clicks', value: String(overview.clicks), tone: '#ea580c' },
        { label: 'Conversions', value: String(overview.conversions), tone: '#16a34a' },
      ]
    : [{ label: 'Revenue', value: '—', tone: '#0f766e' }];

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#f5f7fb' }}>
      <aside style={{ width: 220, background: '#111827', color: '#f9fafb', padding: '1.5rem 1rem' }}>
        <h2 style={{ margin: '0 0 1.5rem' }}>Affiliate Engine</h2>
        <nav style={{ display: 'grid', gap: '0.5rem' }}>
          {navItems.map((item) => (
            <Link
              key={item}
              href={item === 'Campaigns' ? '/campaigns/growth-push' : item === 'Overview' ? '/' : '#'}
              style={{
                padding: '0.75rem 0.9rem',
                borderRadius: 8,
                background: item === 'Overview' ? '#1f2937' : 'transparent',
                fontWeight: item === 'Overview' ? 700 : 500,
              }}
            >
              {item}
            </Link>
          ))}
        </nav>
      </aside>

      <main style={{ flex: 1, padding: '2rem' }}>
        <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <div>
            <div style={{ color: '#6b7280', fontSize: 14 }}>
              Performance dashboard {live ? '· live simulation' : '· API offline'}
            </div>
            <h1 style={{ margin: '0.25rem 0 0', fontSize: '2rem' }}>Overview</h1>
          </div>
          <button
            style={{
              background: '#2563eb',
              color: '#fff',
              border: 'none',
              borderRadius: 8,
              padding: '0.75rem 1rem',
              fontWeight: 700,
              cursor: 'pointer',
            }}
          >
            New campaign
          </button>
        </header>

        <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
          {metrics.map((metric) => (
            <div key={metric.label} style={{ background: '#fff', borderRadius: 12, padding: '1rem 1.25rem', boxShadow: '0 1px 2px rgba(15, 23, 42, 0.06)' }}>
              <div style={{ color: '#6b7280', fontSize: 13, marginBottom: 10 }}>{metric.label}</div>
              <div style={{ fontSize: '1.8rem', fontWeight: 700, color: metric.tone }}>{metric.value}</div>
            </div>
          ))}
        </section>

        <section style={{ background: '#fff', borderRadius: 12, padding: '1.25rem', boxShadow: '0 1px 2px rgba(15, 23, 42, 0.06)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 style={{ margin: 0 }}>Campaign performance</h3>
            <span style={{ color: '#6b7280', fontSize: 13 }}>Current run</span>
          </div>

          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ textAlign: 'left', color: '#6b7280', fontSize: 13 }}>
                <th style={{ padding: '0.75rem 0.5rem' }}>Campaign</th>
                <th style={{ padding: '0.75rem 0.5rem' }}>Decision</th>
                <th style={{ padding: '0.75rem 0.5rem' }}>Clicks</th>
                <th style={{ padding: '0.75rem 0.5rem' }}>Conversions</th>
                <th style={{ padding: '0.75rem 0.5rem' }}>Revenue</th>
                <th style={{ padding: '0.75rem 0.5rem' }}>Net</th>
              </tr>
            </thead>
            <tbody>
              {campaigns.map((row) => (
                <tr key={row.campaign_id} style={{ borderTop: '1px solid #e5e7eb' }}>
                  <td style={{ padding: '0.8rem 0.5rem', fontWeight: 600 }}>
                    <Link href="/campaigns/growth-push">{row.name}</Link>
                  </td>
                  <td style={{ padding: '0.8rem 0.5rem' }}>
                    <span style={{ background: '#e0f2fe', color: '#075985', borderRadius: 999, padding: '0.3rem 0.6rem', fontSize: 12 }}>
                      {row.action}
                    </span>
                  </td>
                  <td style={{ padding: '0.8rem 0.5rem' }}>{row.clicks}</td>
                  <td style={{ padding: '0.8rem 0.5rem' }}>{row.conversions}</td>
                  <td style={{ padding: '0.8rem 0.5rem' }}>{money(row.revenue)}</td>
                  <td style={{ padding: '0.8rem 0.5rem' }}>{money(row.net_contribution)}</td>
                </tr>
              ))}
              {campaigns.length === 0 && (
                <tr>
                  <td colSpan={6} style={{ padding: '1rem 0.5rem', color: '#6b7280' }}>
                    No campaigns yet — start the API ({API}) to see the live simulation.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </section>
      </main>
    </div>
  );
}
