"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { EmptyState } from "../../components/EmptyState";
import { Recipe, mealPlanApi, recipesApi } from "../../lib/recipes";

const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
const MEALS = ["Breakfast", "Lunch", "Dinner"];

type PlanItem = {
  recipeId: number;
  recipeName: string;
};

type Plan = Record<string, PlanItem>;

type TrayFilter = "All" | "Breakfast" | "Lunch" | "Dinner" | "High-Protein" | "Vegetarian";

type DayTotals = {
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  hasMeals: boolean;
};

function inferMealCategories(recipe: Recipe): ("Breakfast" | "Lunch" | "Dinner")[] {
  const name = recipe.name.toLowerCase();
  const cats: ("Breakfast" | "Lunch" | "Dinner")[] = [];

  const isBreakfast =
    name.includes("oat") ||
    name.includes("toast") ||
    name.includes("pancake") ||
    name.includes("parfait") ||
    name.includes("omelette") ||
    name.includes("egg") ||
    name.includes("scramble") ||
    name.includes("pudding") ||
    name.includes("waffle") ||
    name.includes("smoothie") ||
    name.includes("cereal") ||
    name.includes("muffin") ||
    name.includes("granola") ||
    name.includes("shakshuka");

  const isLunch =
    name.includes("salad") ||
    name.includes("wrap") ||
    name.includes("sandwich") ||
    name.includes("panini") ||
    name.includes("bowl") ||
    name.includes("soup") ||
    name.includes("burger") ||
    name.includes("taco") ||
    name.includes("quesadilla") ||
    name.includes("risotto") ||
    name.includes("shawarma") ||
    name.includes("tuna") ||
    name.includes("snack");

  const isDinner =
    name.includes("curry") ||
    name.includes("salmon") ||
    name.includes("chicken") ||
    name.includes("steak") ||
    name.includes("cod") ||
    name.includes("meatball") ||
    name.includes("rice") ||
    name.includes("pasta") ||
    name.includes("spaghetti") ||
    name.includes("stir-fry") ||
    name.includes("roast") ||
    name.includes("stew") ||
    name.includes("bake") ||
    name.includes("palak") ||
    name.includes("paneer") ||
    name.includes("tofu");

  if (isBreakfast) cats.push("Breakfast");
  if (isLunch) cats.push("Lunch");
  if (isDinner) cats.push("Dinner");

  if (cats.length === 0) {
    cats.push("Lunch", "Dinner");
  }
  return cats;
}

export default function WeeklyPlannerPage() {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [plan, setPlan] = useState<Plan>({});
  const [activeCell, setActiveCell] = useState<string>();
  const [search, setSearch] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  // Recipe Tray states
  const [trayOpen, setTrayOpen] = useState(true);
  const [trayFilter, setTrayFilter] = useState<TrayFilter>("All");
  const [traySearch, setTraySearch] = useState("");
  const [stampingRecipe, setStampingRecipe] = useState<Recipe | null>(null);
  const [dragTarget, setDragTarget] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([recipesApi.list(), mealPlanApi.list()])
      .then(([recipeItems, planSlots]) => {
        const sorted = [...recipeItems].sort((a, b) => a.name.localeCompare(b.name));
        setRecipes(sorted);

        const loadedPlan: Plan = {};
        for (const slot of planSlots) {
          const matched = sorted.find(
            (r) => r.id === slot.recipe_id || r.name.toLowerCase() === slot.recipe_name.toLowerCase()
          );
          loadedPlan[`${slot.day}-${slot.meal}`] = {
            recipeId: matched ? matched.id : slot.recipe_id,
            recipeName: slot.recipe_name,
          };
        }
        setPlan(loadedPlan);
      })
      .catch((exception) =>
        setError(exception instanceof Error ? exception.message : "Unable to load planner data.")
      )
      .finally(() => setLoading(false));
  }, []);

  // Filtered recipes for the in-cell popover search fallback
  const filteredCellRecipes = useMemo(
    () =>
      recipes.filter((recipe) =>
        recipe.name.toLocaleLowerCase().includes(search.toLocaleLowerCase())
      ),
    [recipes, search]
  );

  // Filtered recipes for the Recipe Tray
  const displayedTrayRecipes = useMemo(() => {
    return recipes.filter((recipe) => {
      // 1. Search text filter
      if (traySearch.trim()) {
        const q = traySearch.toLowerCase();
        const matchName = recipe.name.toLowerCase().includes(q);
        const matchIng = recipe.ingredients.some((ing) => ing.name.toLowerCase().includes(q));
        if (!matchName && !matchIng) return false;
      }

      // 2. Category filter
      if (trayFilter === "All") return true;

      if (trayFilter === "High-Protein") {
        return (
          recipe.nutrition?.dietary_tags.includes("High-Protein") ||
          (recipe.nutrition?.per_serving?.protein ?? 0) >= 25
        );
      }

      if (trayFilter === "Vegetarian") {
        return (
          recipe.nutrition?.dietary_tags.includes("Vegetarian") ||
          recipe.nutrition?.dietary_tags.includes("Vegan")
        );
      }

      const categories = inferMealCategories(recipe);
      return categories.includes(trayFilter as "Breakfast" | "Lunch" | "Dinner");
    });
  }, [recipes, traySearch, trayFilter]);

  const plannedCount = Object.keys(plan).length;

  // Calculate day's complete nutritional totals (Breakfast + Lunch + Dinner)
  function getDayTotals(day: string): DayTotals {
    let calories = 0;
    let protein = 0;
    let carbs = 0;
    let fat = 0;
    let hasMeals = false;

    for (const meal of MEALS) {
      const item = plan[`${day}-${meal}`];
      if (item) {
        hasMeals = true;
        const r = recipes.find((x) => x.id === item.recipeId);
        if (r?.nutrition?.per_serving) {
          calories += r.nutrition.per_serving.calories || 0;
          protein += r.nutrition.per_serving.protein || 0;
          carbs += r.nutrition.per_serving.carbohydrates || 0;
          fat += r.nutrition.per_serving.fat || 0;
        }
      }
    }

    return {
      calories: Math.round(calories),
      protein: Math.round(protein),
      carbs: Math.round(carbs),
      fat: Math.round(fat),
      hasMeals,
    };
  }

  async function selectRecipe(day: string, meal: string, recipe: { id: number; name: string }) {
    const cellKey = `${day}-${meal}`;
    setPlan((current) => ({
      ...current,
      [cellKey]: { recipeId: recipe.id, recipeName: recipe.name },
    }));
    setActiveCell(undefined);
    setSearch("");
    try {
      await mealPlanApi.setSlot(day, meal, recipe.id);
    } catch (exception) {
      setError(exception instanceof Error ? exception.message : "Failed to save meal plan.");
    }
  }

  function handleCellClick(day: string, meal: string, cellKey: string) {
    if (stampingRecipe) {
      // In stamping mode: clicking any cell instantly assigns the armed recipe
      selectRecipe(day, meal, stampingRecipe);
      return;
    }

    // Normal click: toggle in-cell picker and sync tray filter tab
    setActiveCell((current) => (current === cellKey ? undefined : cellKey));
    setSearch("");
    if (MEALS.includes(meal)) {
      setTrayFilter(meal as TrayFilter);
    }
  }

  async function removeRecipe(day: string, meal: string) {
    const cellKey = `${day}-${meal}`;
    setPlan((current) => {
      const updated = { ...current };
      delete updated[cellKey];
      return updated;
    });
    try {
      await mealPlanApi.removeSlot(day, meal);
    } catch (exception) {
      setError(exception instanceof Error ? exception.message : "Failed to remove recipe.");
    }
  }

  async function clearAll() {
    if (window.confirm("Clear all planned meals for the week?")) {
      setPlan({});
      try {
        await mealPlanApi.clear();
      } catch (exception) {
        setError(exception instanceof Error ? exception.message : "Failed to clear meal plan.");
      }
    }
  }

  // --- Drag and Drop Handlers ---
  function handleTrayCardDragStart(event: React.DragEvent, recipe: Recipe) {
    event.dataTransfer.setData(
      "application/json",
      JSON.stringify({ recipeId: recipe.id, recipeName: recipe.name })
    );
    event.dataTransfer.effectAllowed = "copy";
  }

  function handleCellDragStart(event: React.DragEvent, item: PlanItem) {
    event.dataTransfer.setData(
      "application/json",
      JSON.stringify({ recipeId: item.recipeId, recipeName: item.recipeName })
    );
    event.dataTransfer.effectAllowed = "copy";
  }

  function handleDragOver(event: React.DragEvent, cellKey: string) {
    event.preventDefault();
    event.dataTransfer.dropEffect = "copy";
    if (dragTarget !== cellKey) {
      setDragTarget(cellKey);
    }
  }

  function handleDragLeave(event: React.DragEvent, cellKey: string) {
    if (event.currentTarget.contains(event.relatedTarget as Node)) return;
    if (dragTarget === cellKey) {
      setDragTarget(null);
    }
  }

  function handleDrop(event: React.DragEvent, day: string, meal: string) {
    event.preventDefault();
    setDragTarget(null);
    try {
      const rawData = event.dataTransfer.getData("application/json");
      if (!rawData) return;
      const { recipeId, recipeName } = JSON.parse(rawData);
      selectRecipe(day, meal, { id: recipeId, name: recipeName });
    } catch {
      // ignore invalid drag event data
    }
  }

  return (
    <section className="page planner-page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Your week</p>
          <h1>Weekly planner</h1>
          <p className="page-description">
            Drag recipes from the tray or click slots to quickly plan your weekly meals.
          </p>
        </div>
        <div className="heading-actions">
          {plannedCount > 0 && (
            <button type="button" className="button secondary danger-text" onClick={clearAll}>
              Clear plan
            </button>
          )}
          <Link href="/grocery-list" className="button">
            View grocery list {plannedCount > 0 ? `(${plannedCount})` : ""} →
          </Link>
          <Link href="/recipes/new" className="button secondary">
            + Add recipe
          </Link>
        </div>
      </div>

      {/* Stamping Mode Active Banner */}
      {stampingRecipe && (
        <div className="stamping-banner" role="status">
          <div className="stamping-info">
            <span className="stamping-badge">Stamping Mode</span>
            <span>
              Click any slot in the grid to place <strong>{stampingRecipe.name}</strong>
            </span>
          </div>
          <button
            type="button"
            className="button secondary sm-button"
            onClick={() => setStampingRecipe(null)}
          >
            Done
          </button>
        </div>
      )}

      {error && (
        <div className="error-panel" role="alert">
          <strong>We couldn’t update your planner.</strong>
          <span>{error}</span>
          <button className="button secondary" onClick={() => window.location.reload()}>
            Try again
          </button>
        </div>
      )}

      {!error && !loading && recipes.length === 0 && (
        <EmptyState
          icon="▦"
          title="Your week is waiting to be planned"
          description="Add a recipe first, then return here to place it into your weekly plan."
          actionHref="/recipes/new"
          actionLabel="Add a recipe"
        />
      )}

      {loading && (
        <div className="content-card loading-card">
          <span className="spinner" aria-hidden="true" />
          Loading your meal plan…
        </div>
      )}

      {!error && !loading && recipes.length > 0 && (
        <div className="planner-workspace">
          {/* Main 7-Day Grid */}
          <div className="planner-main">
            <div className="planner-shell">
              <div className="planner-grid" role="table" aria-label="Weekly meal planner">
                {/* Column Headers with Week Names */}
                <div className="planner-cell planner-corner" role="columnheader" />
                {DAYS.map((day) => (
                  <div className="planner-cell planner-header" role="columnheader" key={day}>
                    <div className="planner-header-day">{day}</div>
                  </div>
                ))}

                {/* Meal Rows: Breakfast, Lunch, Dinner */}
                {MEALS.map((meal) => (
                  <div className="planner-row" role="row" key={meal}>
                    <div className="planner-cell planner-day" role="rowheader">
                      {meal}
                    </div>
                    {DAYS.map((day) => {
                      const cellKey = `${day}-${meal}`;
                      const selectedItem = plan[cellKey];
                      const recipeDetails = selectedItem
                        ? recipes.find((r) => r.id === selectedItem.recipeId)
                        : null;
                      const isDragOver = dragTarget === cellKey;

                      return (
                        <div
                          className={`planner-cell planner-meal${isDragOver ? " drag-over" : ""}`}
                          role="cell"
                          key={cellKey}
                          onDragOver={(e) => handleDragOver(e, cellKey)}
                          onDragLeave={(e) => handleDragLeave(e, cellKey)}
                          onDrop={(e) => handleDrop(e, day, meal)}
                        >
                          <button
                            type="button"
                            className={`meal-picker-trigger${selectedItem ? " selected is-draggable" : ""}${
                              stampingRecipe ? " stamping-ready" : ""
                            }`}
                            onClick={() => handleCellClick(day, meal, cellKey)}
                            draggable={Boolean(selectedItem)}
                            onDragStart={(e) =>
                              selectedItem && handleCellDragStart(e, selectedItem)
                            }
                            title={
                              selectedItem
                                ? `${selectedItem.recipeName} (drag to copy to another day)`
                                : stampingRecipe
                                ? `Click to place ${stampingRecipe.name}`
                                : "Click to select or drop a recipe"
                            }
                          >
                            {selectedItem ? (
                              <div className="slot-card-body">
                                <span className="slot-recipe-name">{selectedItem.recipeName}</span>
                                {recipeDetails?.nutrition?.per_serving && (
                                  <span className="slot-cals-pill">
                                    {recipeDetails.nutrition.per_serving.calories} kcal
                                  </span>
                                )}
                              </div>
                            ) : (
                              <span className="slot-placeholder">{isDragOver ? "Drop here" : "Select recipe"}</span>
                            )}
                          </button>
                          {selectedItem && (
                            <button
                              type="button"
                              className="meal-remove"
                              aria-label={`Remove recipe from ${day} ${meal}`}
                              onClick={() => removeRecipe(day, meal)}
                            >
                              ×
                            </button>
                          )}
                          {!stampingRecipe && activeCell === cellKey && (
                            <div className="recipe-picker">
                              <input
                                aria-label={`Search recipes for ${day} ${meal}`}
                                autoFocus
                                placeholder="Search recipes"
                                value={search}
                                onChange={(event) => setSearch(event.target.value)}
                              />
                              <div className="recipe-picker-options">
                                {filteredCellRecipes.map((recipe) => (
                                  <button
                                    type="button"
                                    key={recipe.id}
                                    onClick={() => selectRecipe(day, meal, recipe)}
                                  >
                                    {recipe.name}
                                  </button>
                                ))}
                                {filteredCellRecipes.length === 0 && <p>No matching recipes.</p>}
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                ))}

                {/* Daily Nutritional Summary Totals Row at Bottom */}
                <div className="planner-row planner-summary-row" role="row">
                  <div className="planner-cell planner-summary-header" role="rowheader">
                    <span className="summary-title">Daily Total</span>
                    <span className="summary-subtitle">3 meals</span>
                  </div>
                  {DAYS.map((day) => {
                    const totals = getDayTotals(day);
                    return (
                      <div
                        className="planner-cell planner-summary-cell"
                        role="cell"
                        key={`summary-${day}`}
                      >
                        {totals.hasMeals && totals.calories > 0 ? (
                          <>
                            <span className="summary-cals">{totals.calories} kcal</span>
                            <div className="summary-macros">
                              <span><strong>{totals.protein}g</strong> P</span>
                              <span className="summary-macros-dot">·</span>
                              <span><strong>{totals.carbs}g</strong> C</span>
                              <span className="summary-macros-dot">·</span>
                              <span><strong>{totals.fat}g</strong> F</span>
                            </div>
                          </>
                        ) : totals.hasMeals ? (
                          <span className="summary-pending">Calculating…</span>
                        ) : (
                          <span className="summary-empty">—</span>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>

          {/* Interactive Recipe Tray Sidebar (Collapsible to right) */}
          {trayOpen ? (
            <aside className="recipe-tray-panel" aria-label="Recipe tray">
              <div className="tray-header">
                <div className="tray-title-wrap">
                  <h3>Recipe Tray</h3>
                  <span className="recipe-tray-count">{displayedTrayRecipes.length}</span>
                </div>
                <button
                  type="button"
                  className="tray-close-btn"
                  onClick={() => setTrayOpen(false)}
                  title="Collapse tray to right"
                  aria-label="Collapse recipe tray"
                >
                  Collapse ⇥
                </button>
              </div>

              <p className="tray-subtext">
                Drag cards into slots or use Stamp to click-place.
              </p>

              {/* Tray Search */}
              <div className="tray-search-box">
                <input
                  type="text"
                  placeholder="Search recipes or ingredients…"
                  value={traySearch}
                  onChange={(e) => setTraySearch(e.target.value)}
                  aria-label="Search recipe tray"
                />
                {traySearch && (
                  <button
                    type="button"
                    className="tray-search-clear"
                    onClick={() => setTraySearch("")}
                    aria-label="Clear search"
                  >
                    ✕
                  </button>
                )}
              </div>

              {/* Clean Wrapped Category Filter Tabs (No scrollbar clipping!) */}
              <div className="tray-filter-tabs" role="tablist" aria-label="Meal categories">
                {(["All", "Breakfast", "Lunch", "Dinner", "High-Protein", "Vegetarian"] as TrayFilter[]).map(
                  (tab) => (
                    <button
                      key={tab}
                      type="button"
                      className={`tray-filter-pill${trayFilter === tab ? " active" : ""}`}
                      onClick={() => setTrayFilter(tab)}
                    >
                      {tab}
                    </button>
                  )
                )}
              </div>

              {/* Draggable Recipe Cards */}
              <div className="tray-cards-list">
                {displayedTrayRecipes.map((recipe) => {
                  const isStamping = stampingRecipe?.id === recipe.id;
                  const cals = recipe.nutrition?.per_serving?.calories;
                  const protein = recipe.nutrition?.per_serving?.protein;

                  return (
                    <div
                      key={recipe.id}
                      className={`tray-card${isStamping ? " stamping-active" : ""}`}
                      draggable
                      onDragStart={(e) => handleTrayCardDragStart(e, recipe)}
                      title="Drag to any meal slot in the grid"
                    >
                      <div className="tray-card-top">
                        <div className="tray-card-name-wrap">
                          <span className="tray-card-icon" aria-hidden="true">
                            ◒
                          </span>
                          <span className="tray-card-title">{recipe.name}</span>
                        </div>
                        <span className="tray-drag-handle" title="Drag handle" aria-hidden="true">
                          ⋮⋮
                        </span>
                      </div>

                      <div className="tray-card-bottom">
                        <div className="tray-card-meta">
                          {cals ? (
                            <span>
                              <strong>{cals}</strong> kcal{protein ? ` · ${Math.round(protein)}g P` : ""}
                            </span>
                          ) : (
                            <span>{recipe.ingredients.length} items</span>
                          )}
                        </div>

                        <button
                          type="button"
                          className={`tray-stamp-btn${isStamping ? " active" : ""}`}
                          onClick={(e) => {
                            e.stopPropagation();
                            setStampingRecipe(isStamping ? null : recipe);
                          }}
                          title={
                            isStamping
                              ? "Stop stamping"
                              : "Click to stamp this recipe into multiple slots"
                          }
                        >
                          {isStamping ? "✓ Stamping" : "+ Stamp"}
                        </button>
                      </div>
                    </div>
                  );
                })}

                {displayedTrayRecipes.length === 0 && (
                  <div className="tray-empty-hint">
                    <p>No recipes match "{traySearch || trayFilter}".</p>
                  </div>
                )}
              </div>
            </aside>
          ) : (
            /* Collapsed Dock Tab on the Right Edge */
            <button
              type="button"
              className="recipe-tray-dock-tab"
              onClick={() => setTrayOpen(true)}
              title="Expand Recipe Tray"
              aria-label="Expand Recipe Tray"
            >
              <span className="dock-tab-icon" aria-hidden="true">◀</span>
              <span className="dock-tab-title">Recipe Tray</span>
              <span className="dock-tab-badge">{displayedTrayRecipes.length}</span>
            </button>
          )}
        </div>
      )}
    </section>
  );
}
