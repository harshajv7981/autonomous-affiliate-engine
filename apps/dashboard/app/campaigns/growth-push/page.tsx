import Link from 'next/link';

const metrics = [
  { label: 'Delivered', value: '4,820', detail: '98.7% delivery rate' },
  { label: 'Clicks', value: '180', detail: '3.7% click rate' },
  { label: 'Conversions', value: '8', detail: '4.4% click-to-conversion' },
  { label: 'Net profit', value: '$31.50', detail: '18% return on cost' },
];

const events = [
  ['09:42', 'Compliance gate passed', 'APPROVED'],
  ['09:45', 'Campaign entered sending', 'SENDING'],
  ['10:12', 'First conversion attributed', 'CONVERSION'],
  ['11:05', 'Optimization review scheduled', 'QUEUED'],
];

export default function CampaignDetailPage() {
  return (
    <main style={{ minHeight: '100vh', padding: '2rem', background: '#f5f7fb' }}>
      <div style={{ maxWidth: 1120, margin: '0 auto' }}>
        <Link href="/" style={{ color: '#2563eb', fontSize: 14 }}>← Back to overview</Link>
        <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', gap: 16, margin: '1.5rem 0 2rem' }}>
          <div>
            <div style={{ color: '#6b7280', fontSize: 13, textTransform: 'uppercase', letterSpacing: '0.08em' }}>Campaign detail</div>
            <h1 style={{ margin: '0.35rem 0', fontSize: '2.25rem' }}>Growth Push</h1>
            <p style={{ margin: 0, color: '#6b7280' }}>Finance audience · Mock Offer 24 · Updated today at 11:05</p>
          </div>
          <span style={{ background: '#dcfce7', color: '#166534', borderRadius: 999, padding: '0.45rem 0.8rem', fontSize: 12, fontWeight: 700 }}>SENDING</span>
        </header>

        <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
          {metrics.map((metric) => (
            <div key={metric.label} style={{ background: '#fff', borderRadius: 12, padding: '1.15rem', boxShadow: '0 1px 2px rgba(15, 23, 42, 0.06)' }}>
              <div style={{ color: '#6b7280', fontSize: 13 }}>{metric.label}</div>
              <div style={{ margin: '0.55rem 0 0.25rem', fontSize: '1.8rem', fontWeight: 700 }}>{metric.value}</div>
              <div style={{ color: '#6b7280', fontSize: 12 }}>{metric.detail}</div>
            </div>
          ))}
        </section>

        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.4fr) minmax(280px, 0.6fr)', gap: '1.5rem' }}>
          <section style={{ background: '#fff', borderRadius: 12, padding: '1.25rem', boxShadow: '0 1px 2px rgba(15, 23, 42, 0.06)' }}>
            <h2 style={{ margin: '0 0 1rem', fontSize: '1.1rem' }}>Activity timeline</h2>
            <div style={{ display: 'grid', gap: '0.9rem' }}>
              {events.map(([time, event, state]) => (
                <div key={time} style={{ display: 'grid', gridTemplateColumns: '56px 1fr auto', gap: 12, alignItems: 'center', borderTop: '1px solid #e5e7eb', paddingTop: '0.9rem' }}>
                  <span style={{ color: '#6b7280', fontSize: 13 }}>{time}</span>
                  <span style={{ fontWeight: 600 }}>{event}</span>
                  <span style={{ color: '#6b7280', fontSize: 12 }}>{state}</span>
                </div>
              ))}
            </div>
          </section>

          <section style={{ background: '#fff', borderRadius: 12, padding: '1.25rem', boxShadow: '0 1px 2px rgba(15, 23, 42, 0.06)' }}>
            <h2 style={{ margin: '0 0 1rem', fontSize: '1.1rem' }}>Compliance status</h2>
            <div style={{ display: 'grid', gap: '0.75rem' }}>
              {['Offer permits email', 'Audience permission verified', 'Unsubscribe present', 'Prohibited claims clear', 'Tracking validated'].map((check) => (
                <div key={check} style={{ display: 'flex', justifyContent: 'space-between', gap: 12, fontSize: 14 }}>
                  <span>{check}</span>
                  <strong style={{ color: '#15803d' }}>PASS</strong>
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}
