import { EmptyState } from "../../components/EmptyState";

export default function GroceryListPage() {
  return <section className="page narrow"><div className="page-intro"><p className="eyebrow">Shopping made simple</p><h1>Grocery list</h1><p className="page-description">Everything you need for your planned meals, in one practical list.</p></div><EmptyState icon="✓" title="Your grocery list is waiting" description="Grocery-list generation isn’t connected to the current backend yet. Once meal plans can be saved, your ingredients will appear here." actionHref="/weekly-planner" actionLabel="Plan your week" /></section>;
}
