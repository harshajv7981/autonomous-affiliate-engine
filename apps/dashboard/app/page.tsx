import Link from 'next/link';

const navItems = ['Overview', 'Offers', 'Audiences', 'Campaigns', 'Finance', 'System'];

const metrics = [
  { label: 'Revenue', value: '$250.00', tone: '#0f766e' },
  { label: 'Net Profit', value: '$95.00', tone: '#1d4ed8' },
  { label: 'Active Campaigns', value: '4', tone: '#7c3aed' },
  { label: 'Clicks', value: '400', tone: '#ea580c' },
  { label: 'Conversions', value: '18', tone: '#16a34a' },
];

const campaigns = [
  { name: 'Growth Push', status: 'SENDING', clicks: 180, conversions: 8, roi: '18%' },
  { name: 'Retention Flow', status: 'RUNNING', clicks: 120, conversions: 5, roi: '11%' },
  { name: 'Offer Test #3', status: 'QA', clicks: 58, conversions: 2, roi: '9%' },
  { name: 'Audience Split', status: 'OPTIMIZING', clicks: 42, conversions: 3, roi: '14%' },
];

export default function DashboardPage() {
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
            <div style={{ color: '#6b7280', fontSize: 14 }}>Performance dashboard</div>
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
            <span style={{ color: '#6b7280', fontSize: 13 }}>Last 7 days</span>
          </div>

          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ textAlign: 'left', color: '#6b7280', fontSize: 13 }}>
                <th style={{ padding: '0.75rem 0.5rem' }}>Campaign</th>
                <th style={{ padding: '0.75rem 0.5rem' }}>Status</th>
                <th style={{ padding: '0.75rem 0.5rem' }}>Clicks</th>
                <th style={{ padding: '0.75rem 0.5rem' }}>Conversions</th>
                <th style={{ padding: '0.75rem 0.5rem' }}>ROI</th>
              </tr>
            </thead>
            <tbody>
              {campaigns.map((row) => (
                <tr key={row.name} style={{ borderTop: '1px solid #e5e7eb' }}>
                  <td style={{ padding: '0.8rem 0.5rem', fontWeight: 600 }}>
                    <Link href="/campaigns/growth-push">{row.name}</Link>
                  </td>
                  <td style={{ padding: '0.8rem 0.5rem' }}>
                    <span style={{ background: '#e0f2fe', color: '#075985', borderRadius: 999, padding: '0.3rem 0.6rem', fontSize: 12 }}>
                      {row.status}
                    </span>
                  </td>
                  <td style={{ padding: '0.8rem 0.5rem' }}>{row.clicks}</td>
                  <td style={{ padding: '0.8rem 0.5rem' }}>{row.conversions}</td>
                  <td style={{ padding: '0.8rem 0.5rem' }}>{row.roi}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      </main>
    </div>
  );
}
