'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';

const navItems = ['Overview', 'Offers', 'Audiences', 'Campaigns', 'Finance', 'System'];
const API = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

type Overview = {
  revenue: number;
  net_profit: number;
  active_campaigns: number;
  clicks: number;
  conversions: number;
  ctr: number;
  epc: number;
  net_contribution_per_1000: number;
  bounce_rate: number;
  unsubscribe_rate: number;
  complaint_rate: number;
  is_simulated: boolean;
  system_status: string;
  optimizer_mode: string;
};

type CampaignRow = {
  campaign_id: string;
  name: string;
  sent: number;
  clicks: number;
  conversions: number;
  ctr: number;
  epc: number;
  revenue: number;
  net_contribution: number;
  net_contribution_per_1000: number;
  action: string;
  action_reason: string;
};

type RealRow = {
  campaign_id: string;
  sent: number;
  clicks: number;
  unique_clickers: number;
  conversions: number;
  test_commission: number;
  unsubscribes: number;
  confirmed_earnings: number;
};

type Earnings = {
  currency: string;
  confirmed: number;
  pending: number;
  paid: number;
  reversed: number;
  attributed: number;
  unattributed: number;
};

type BlockedRow = {
  campaign_id: string;
  name: string;
  decision: string;
  reasons: string[];
};

const money = (n: number) => `$${n.toFixed(2)}`;
const pct = (n: number) => `${(n * 100).toFixed(2)}%`;
const cell = { padding: '0.75rem 0.5rem' };
const card = { background: '#fff', borderRadius: 12, padding: '1.25rem', boxShadow: '0 1px 2px rgba(15, 23, 42, 0.06)' };

export default function DashboardPage() {
  const [overview, setOverview] = useState<Overview | null>(null);
  const [campaigns, setCampaigns] = useState<CampaignRow[]>([]);
  const [blocked, setBlocked] = useState<BlockedRow[]>([]);
  const [real, setReal] = useState<RealRow[]>([]);
  const [earnings, setEarnings] = useState<Earnings[]>([]);
  const [live, setLive] = useState(false);

  useEffect(() => {
    Promise.all([
      fetch(`${API}/api/analytics/overview`).then((r) => r.json()),
      fetch(`${API}/api/analytics/campaigns`).then((r) => r.json()),
      fetch(`${API}/api/analytics/real`).then((r) => r.json()),
    ])
      .then(([o, c, r]) => {
        setOverview(o);
        setCampaigns(c.campaigns ?? []);
        setBlocked(c.blocked ?? []);
        setReal(r.campaigns ?? []);
        setEarnings(r.earnings ?? []);
        setLive(true);
      })
      .catch(() => setLive(false));
  }, []);

  const halted = overview?.system_status === 'halted';
  const metrics = overview
    ? [
        { label: 'Revenue', value: money(overview.revenue) },
        { label: 'Net Contribution', value: money(overview.net_profit) },
        { label: 'Net / 1,000 recipients', value: money(overview.net_contribution_per_1000) },
        { label: 'EPC', value: money(overview.epc) },
        { label: 'CTR', value: pct(overview.ctr) },
        { label: 'Conversions', value: String(overview.conversions) },
        { label: 'Bounce rate', value: pct(overview.bounce_rate) },
        { label: 'Unsubscribe rate', value: pct(overview.unsubscribe_rate) },
        { label: 'Complaint rate', value: pct(overview.complaint_rate) },
      ]
    : [];

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

      <main style={{ flex: 1, padding: '2rem', minWidth: 0 }}>
        <header style={{ marginBottom: '1rem' }}>
          <div style={{ color: '#6b7280', fontSize: 14 }}>Performance dashboard</div>
          <h1 style={{ margin: '0.25rem 0 0', fontSize: '2rem' }}>Overview</h1>
        </header>

        {!live && (
          <div role="status" style={{ ...card, marginBottom: '1rem', color: '#6b7280' }}>
            API offline — start the backend ({API}) to see engine data.
          </div>
        )}

        {overview && (
          <div role="status" style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '1.25rem' }}>
            {overview.is_simulated && (
              <span style={{ background: '#fef3c7', color: '#92400e', borderRadius: 999, padding: '0.35rem 0.8rem', fontWeight: 700, fontSize: 13 }}>
                SIMULATED DATA — not real earnings
              </span>
            )}
            <span
              style={{
                background: halted ? '#fee2e2' : '#dcfce7',
                color: halted ? '#991b1b' : '#166534',
                borderRadius: 999,
                padding: '0.35rem 0.8rem',
                fontWeight: 700,
                fontSize: 13,
              }}
            >
              {halted ? 'KILL SWITCH ON — system halted' : 'System active'}
            </span>
            <span style={{ background: '#e0e7ff', color: '#3730a3', borderRadius: 999, padding: '0.35rem 0.8rem', fontSize: 13 }}>
              Optimizer: {overview.optimizer_mode} only
            </span>
          </div>
        )}

        <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
          {metrics.map((metric) => (
            <div key={metric.label} style={{ ...card, padding: '1rem 1.25rem' }}>
              <div style={{ color: '#6b7280', fontSize: 13, marginBottom: 10 }}>{metric.label}</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#111827' }}>{metric.value}</div>
            </div>
          ))}
        </section>

        <section style={{ ...card, marginBottom: '2rem', overflowX: 'auto' }}>
          <h3 style={{ margin: '0 0 1rem' }}>Campaigns and optimizer recommendations</h3>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ textAlign: 'left', color: '#6b7280', fontSize: 13 }}>
                <th style={cell}>Campaign</th>
                <th style={cell}>Recommendation</th>
                <th style={cell}>Sent</th>
                <th style={cell}>CTR</th>
                <th style={cell}>Conv.</th>
                <th style={cell}>EPC</th>
                <th style={cell}>Revenue</th>
                <th style={cell}>Net</th>
                <th style={cell}>Net / 1k</th>
              </tr>
            </thead>
            <tbody>
              {campaigns.map((row) => (
                <tr key={row.campaign_id} style={{ borderTop: '1px solid #e5e7eb' }}>
                  <td style={{ ...cell, fontWeight: 600 }}>{row.name}</td>
                  <td style={cell} title={row.action_reason}>
                    <span style={{ background: '#e0f2fe', color: '#075985', borderRadius: 999, padding: '0.3rem 0.6rem', fontSize: 12 }}>
                      {row.action}
                    </span>
                  </td>
                  <td style={cell}>{row.sent}</td>
                  <td style={cell}>{pct(row.ctr)}</td>
                  <td style={cell}>{row.conversions}</td>
                  <td style={cell}>{money(row.epc)}</td>
                  <td style={cell}>{money(row.revenue)}</td>
                  <td style={cell}>{money(row.net_contribution)}</td>
                  <td style={cell}>{money(row.net_contribution_per_1000)}</td>
                </tr>
              ))}
              {campaigns.length === 0 && (
                <tr>
                  <td colSpan={9} style={{ ...cell, color: '#6b7280' }}>
                    {halted ? 'Kill switch is on — no campaigns run.' : 'No campaigns yet — run make migrate && make seed.'}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </section>

        <section style={{ ...card, marginBottom: '2rem', border: '2px solid #16a34a' }}>
          <h3 style={{ margin: '0 0 0.25rem' }}>Real earnings</h3>
          <p style={{ margin: '0 0 1rem', color: '#6b7280', fontSize: 13 }}>
            From your affiliate network&apos;s own reports (make import-commissions). Only approved and paid commissions count as earned.
          </p>
          {earnings.length === 0 && <p style={{ margin: 0, color: '#6b7280' }}>No commission reports imported yet.</p>}
          {earnings.map((e) => (
            <div
              key={e.currency}
              style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem' }}
            >
              {[
                ['Confirmed earnings', e.confirmed],
                ['Paid out', e.paid],
                ['Pending', e.pending],
                ['Reversed', e.reversed],
              ].map(([label, value]) => (
                <div key={label as string}>
                  <div style={{ color: '#6b7280', fontSize: 13 }}>{label}</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>
                    {(value as number).toFixed(2)} {e.currency}
                  </div>
                </div>
              ))}
              <div>
                <div style={{ color: '#6b7280', fontSize: 13 }}>Attributed / unattributed</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>
                  {e.attributed} / {e.unattributed}
                </div>
              </div>
            </div>
          ))}
        </section>

        <section style={{ ...card, marginBottom: '2rem', overflowX: 'auto' }}>
          <h3 style={{ margin: '0 0 0.25rem' }}>Real test sends (your own inboxes)</h3>
          <p style={{ margin: '0 0 1rem', color: '#6b7280', fontSize: 13 }}>
            Real emails and real clicks. &quot;Test&quot; columns come from the mock network (not money); &quot;Confirmed&quot; is real, from imported network reports.
          </p>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ textAlign: 'left', color: '#6b7280', fontSize: 13 }}>
                <th style={cell}>Campaign</th>
                <th style={cell}>Sent</th>
                <th style={cell}>Clicks</th>
                <th style={cell}>Unique clickers</th>
                <th style={cell}>Test conversions</th>
                <th style={cell}>Test commission</th>
                <th style={cell}>Unsubscribes</th>
                <th style={cell}>Confirmed earnings</th>
              </tr>
            </thead>
            <tbody>
              {real.map((row) => (
                <tr key={row.campaign_id} style={{ borderTop: '1px solid #e5e7eb' }}>
                  <td style={{ ...cell, fontWeight: 600 }}>{row.campaign_id}</td>
                  <td style={cell}>{row.sent}</td>
                  <td style={cell}>{row.clicks}</td>
                  <td style={cell}>{row.unique_clickers}</td>
                  <td style={cell}>{row.conversions}</td>
                  <td style={cell}>{money(row.test_commission)}</td>
                  <td style={cell}>{row.unsubscribes}</td>
                  <td style={cell}>{money(row.confirmed_earnings)}</td>
                </tr>
              ))}
              {real.length === 0 && (
                <tr>
                  <td colSpan={8} style={{ ...cell, color: '#6b7280' }}>No real test sends yet — run make send-test-live.</td>
                </tr>
              )}
            </tbody>
          </table>
        </section>

        <section style={{ ...card, overflowX: 'auto' }}>
          <h3 style={{ margin: '0 0 1rem' }}>Blocked by compliance gate</h3>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ textAlign: 'left', color: '#6b7280', fontSize: 13 }}>
                <th style={cell}>Campaign</th>
                <th style={cell}>Decision</th>
                <th style={cell}>Reasons</th>
              </tr>
            </thead>
            <tbody>
              {blocked.map((row) => (
                <tr key={row.campaign_id} style={{ borderTop: '1px solid #e5e7eb' }}>
                  <td style={{ ...cell, fontWeight: 600 }}>{row.name}</td>
                  <td style={cell}>{row.decision}</td>
                  <td style={{ ...cell, fontFamily: 'monospace', fontSize: 13 }}>{row.reasons.join(', ')}</td>
                </tr>
              ))}
              {blocked.length === 0 && (
                <tr>
                  <td colSpan={3} style={{ ...cell, color: '#6b7280' }}>Nothing blocked.</td>
                </tr>
              )}
            </tbody>
          </table>
        </section>
      </main>
    </div>
  );
}
