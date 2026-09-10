import Link from "next/link";

type Props = { icon?: string; title: string; description: string; actionHref?: string; actionLabel?: string };

export function EmptyState({ icon = "✦", title, description, actionHref, actionLabel }: Props) {
  return <section className="empty-state" aria-labelledby="empty-state-title">
    <span className="empty-icon" aria-hidden="true">{icon}</span>
    <h2 id="empty-state-title">{title}</h2>
    <p>{description}</p>
    {actionHref && actionLabel && <Link className="button" href={actionHref}>{actionLabel}</Link>}
  </section>;
}
