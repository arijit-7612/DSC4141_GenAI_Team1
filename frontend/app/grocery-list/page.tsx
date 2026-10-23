"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { EmptyState } from "../../components/EmptyState";
import { GroceryListResponse, groceryApi } from "../../lib/recipes";

const CATEGORY_ICONS: Record<string, string> = {
  "Produce": "🥦",
  "Meat & Seafood": "🥩",
  "Dairy & Eggs": "🥛",
  "Bakery & Grains": "🌾",
  "Canned & Packaged": "🥫",
  "Spices & Seasonings": "🧂",
  "Other": "🛒",
};

export default function GroceryListPage() {
  const [data, setData] = useState<GroceryListResponse>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [checkedItems, setCheckedItems] = useState<Record<string, boolean>>({});

  function loadList() {
    setLoading(true);
    setError("");
    groceryApi
      .get()
      .then((res) => {
        setData(res);
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : "Failed to load grocery list.");
      })
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    loadList();
  }, []);

  function toggleCheck(itemKey: string) {
    setCheckedItems((current) => ({
      ...current,
      [itemKey]: !current[itemKey],
    }));
  }

  function clearChecked() {
    setCheckedItems({});
  }

  function checkAllStaples() {
    if (!data) return;
    const updated = { ...checkedItems };
    for (const item of data.items) {
      if (!item.show_quantity) {
        const itemKey = `${item.name}-${item.unit}`;
        updated[itemKey] = true;
      }
    }
    setCheckedItems(updated);
  }

  const items = data?.items ?? [];
  const categories = data?.categories ?? [];
  const checkedCount = Object.values(checkedItems).filter(Boolean).length;
  const stapleCount = items.filter((i) => !i.show_quantity).length;

  return (
    <section className="page narrow grocery-page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Shopping made simple</p>
          <h1>Grocery list</h1>
          <p className="page-description">
            {data && data.total_items > 0
              ? `Aisle-sorted checklist for ${data.planned_meals_count} planned meal${
                  data.planned_meals_count === 1 ? "" : "s"
                } across your week.`
              : "Everything you need for your planned meals, organized by category."}
          </p>
        </div>
        <div className="heading-actions">
          <Link href="/weekly-planner" className="button secondary">
            ← Edit weekly plan
          </Link>
        </div>
      </div>

      {error && (
        <div className="error-panel" role="alert">
          <strong>We couldn’t load your grocery list.</strong>
          <span>{error}</span>
          <button className="button secondary" onClick={loadList}>
            Try again
          </button>
        </div>
      )}

      {loading && (
        <div className="content-card loading-card">
          <span className="spinner" aria-hidden="true" />
          Organizing your grocery list by aisle…
        </div>
      )}

      {!loading && !error && items.length === 0 && (
        <EmptyState
          icon="✓"
          title="Your grocery list is empty"
          description="You haven’t planned any meals for this week yet. Select recipes in your weekly planner and your ingredients will automatically appear here."
          actionHref="/weekly-planner"
          actionLabel="Plan your week"
        />
      )}

      {!loading && !error && items.length > 0 && (
        <>
          <div className="grocery-summary">
            <div className="summary-stat">
              <span className="stat-label">Total Items</span>
              <strong className="stat-value">{data?.total_items}</strong>
            </div>
            <div className="summary-stat">
              <span className="stat-label">Planned Meals</span>
              <strong className="stat-value">{data?.planned_meals_count}</strong>
            </div>
            <div className="summary-stat">
              <span className="stat-label">Aisles / Categories</span>
              <strong className="stat-value">{categories.length}</strong>
            </div>
            <div className="summary-stat">
              <span className="stat-label">Items Checked</span>
              <strong className="stat-value">
                {checkedCount} / {items.length}
              </strong>
            </div>
          </div>

          <div className="grocery-toolbar">
            <p className="toolbar-info">
              Items are sorted by grocery aisle. Exact quantities are shown for groceries to buy, while spices & staples are kept clean.
            </p>
            <div className="toolbar-actions">
              {stapleCount > 0 && (
                <button
                  type="button"
                  className="button secondary sm-button"
                  onClick={checkAllStaples}
                >
                  ✓ Check all pantry staples
                </button>
              )}
              {checkedCount > 0 && (
                <button
                  type="button"
                  className="button secondary sm-button"
                  onClick={clearChecked}
                >
                  Uncheck all ({checkedCount})
                </button>
              )}
            </div>
          </div>

          <div className="category-groups-container">
            {categories.map((group) => {
              const icon = CATEGORY_ICONS[group.category] ?? "🛒";
              const groupCheckedCount = group.items.filter(
                (item) => checkedItems[`${item.name}-${item.unit}`]
              ).length;

              return (
                <section
                  key={group.category}
                  className="category-group-card content-card"
                >
                  <div className="category-group-header">
                    <div className="category-title-wrap">
                      <span className="category-icon" aria-hidden="true">
                        {icon}
                      </span>
                      <h2>{group.category}</h2>
                    </div>
                    <span className="category-badge">
                      {groupCheckedCount}/{group.items.length}
                    </span>
                  </div>

                  <ul className="grocery-items-list" aria-label={`${group.category} items`}>
                    {group.items.map((item) => {
                      const itemKey = `${item.name}-${item.unit}`;
                      const isChecked = Boolean(checkedItems[itemKey]);

                      return (
                        <li
                          key={itemKey}
                          className={`grocery-item-row${isChecked ? " checked" : ""}`}
                          onClick={() => toggleCheck(itemKey)}
                        >
                          <label
                            className="checkbox-wrapper"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <input
                              type="checkbox"
                              checked={isChecked}
                              onChange={() => toggleCheck(itemKey)}
                              aria-label={`Mark ${item.name} as purchased`}
                            />
                            <span className="custom-checkbox" />
                          </label>

                          <div className="grocery-item-main">
                            <div className="grocery-item-info">
                              <span className="grocery-item-name">{item.name}</span>
                              {item.recipes.length > 0 && (
                                <span className="grocery-recipe-tags">
                                  For: {item.recipes.join(", ")}
                                </span>
                              )}
                            </div>

                            {item.show_quantity ? (
                              <span className="grocery-item-qty">
                                <strong>{item.quantity}</strong> {item.unit}
                              </span>
                            ) : (
                              <span className="grocery-item-staple">
                                Pantry staple
                              </span>
                            )}
                          </div>
                        </li>
                      );
                    })}
                  </ul>
                </section>
              );
            })}
          </div>
        </>
      )}
    </section>
  );
}
