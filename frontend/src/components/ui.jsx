function Icon({ name, size = 18 }) {
  const shapes = {
    home: <><path d="m3 10 9-7 9 7"/><path d="M5 9v11h14V9M9 20v-7h6v7"/></>,
    layers: <><path d="m12 3 9 5-9 5-9-5 9-5Z"/><path d="m3 12 9 5 9-5M3 16l9 5 9-5"/></>,
    clipboard: <><rect x="5" y="4.5" width="14" height="17" rx="2"/><path d="M9 4.5v-1h6v1M8.5 10h7M8.5 14h7M8.5 18h4"/></>,
    grid: <><rect x="3.5" y="3.5" width="7" height="7" rx="1.5"/><rect x="13.5" y="3.5" width="7" height="7" rx="1.5"/><rect x="3.5" y="13.5" width="7" height="7" rx="1.5"/><rect x="13.5" y="13.5" width="7" height="7" rx="1.5"/></>,
    chart: <><path d="M4 19V5M4 19h17"/><path d="m7 15 4-4 3 2 6-7"/></>,
    spark: <><path d="m12 3 1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8L12 3Z"/><path d="m19 16 .9 2.1L22 19l-2.1.9L19 22l-.9-2.1L16 19l2.1-.9L19 16Z"/></>,
    arrow: <><path d="M5 12h14M13 6l6 6-6 6"/></>,
    chevron: <path d="m9 18 6-6-6-6"/>,
    moon: <path d="M20.5 14.1A8.5 8.5 0 0 1 9.9 3.5 8.5 8.5 0 1 0 20.5 14.1Z"/>,
    sun: <><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42"/></>,
    check: <path d="m5 12 4 4L19 6"/>,
    book: <><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v16H6.5A2.5 2.5 0 0 0 4 21V5.5Z"/><path d="M4 17.5A2.5 2.5 0 0 1 6.5 15H20M8 7h8M8 10h6"/></>,
    menu: <><path d="M4 7h16M4 12h16M4 17h16"/></>,
    close: <><path d="m6 6 12 12M18 6 6 18"/></>,
    warning: <><path d="M10.3 3.9 2.8 17a2 2 0 0 0 1.7 3h15a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z"/><path d="M12 9v4m0 4h.01"/></>,
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{shapes[name]}</svg>;
}

function Eyebrow({ children }) { return <p className="eyebrow"><span className="eyebrow-dot" />{children}</p>; }
function SectionTitle({ eyebrow, title, detail, action }) { return <div className="section-title-row"><div>{eyebrow && <p className="eyebrow">{eyebrow}</p>}<h2>{title}</h2>{detail && <p className="section-detail">{detail}</p>}</div>{action}</div>; }
function EmptyState({ icon = "chart", title, detail, action }) { return <div className="empty-state"><span className="empty-state-icon"><Icon name={icon} size={21} /></span><h3>{title}</h3><p>{detail}</p>{action}</div>; }
function Notice({ type = "info", message }) { return <div className={`notice notice-${type}`} role="status"><Icon name={type === "warning" ? "warning" : "check"} size={16} /><span>{message}</span></div>; }
function SkillApiStatus({ state }) {
  if (state === "loading") return <div className="notice" role="status">Loading official skills…</div>;
  if (state === "error") return <Notice type="warning" message="Could not load skills from FastAPI. Showing the canonical catalog for reference." />;
  if (state === "empty") return <div className="notice" role="status">FastAPI returned no skill records.</div>;
  return null;
}

export { EmptyState, Eyebrow, Icon, Notice, SectionTitle, SkillApiStatus };
