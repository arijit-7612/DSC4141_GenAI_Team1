"use client";

import Link from "next/link";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { RecipeForm } from "../../../components/RecipeForm";
import {
  Recipe,
  RecipeNutrition,
  UserProfile,
  nutritionApi,
  recipesApi,
  userProfileApi,
} from "../../../lib/recipes";

function RecipeDetailContent() {
  const { id } = useParams<{ id: string }>();
  const searchParams = useSearchParams();
  const router = useRouter();

  const [recipe, setRecipe] = useState<Recipe>();
  const [nutrition, setNutrition] = useState<RecipeNutrition | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [servings, setServings] = useState<number>(1);
  const [editing, setEditing] = useState(searchParams.get("edit") === "true");
  const [error, setError] = useState("");
  const [loadingNutrition, setLoadingNutrition] = useState(false);
  const [deleting, setDeleting] = useState(false);

  // Load recipe and user profile
  useEffect(() => {
    recipesApi
      .get(id)
      .then((rec) => {
        setRecipe(rec);
        if (rec.nutrition) {
          setNutrition(rec.nutrition);
        }
      })
      .catch((exception) => setError(exception.message));

    userProfileApi
      .get()
      .then(setProfile)
      .catch(() => {
        // Silently tolerate if profile fails
      });
  }, [id]);

  // Recalculate nutrition when servings change
  useEffect(() => {
    if (!recipe) return;
    setLoadingNutrition(true);
    nutritionApi
      .get(recipe.id, servings)
      .then(setNutrition)
      .catch(() => {
        // Fallback to local scale if network fails
      })
      .finally(() => setLoadingNutrition(false));
  }, [servings, recipe]);

  if (error) {
    return (
      <section className="page narrow">
        <div className="error-panel" role="alert">
          <strong>We couldn’t load this recipe.</strong>
          <span>{error}</span>
          <Link className="button secondary" href="/recipes">
            Back to recipes
          </Link>
        </div>
      </section>
    );
  }

  if (!recipe) {
    return (
      <section className="page narrow">
        <div className="content-card loading-card">
          <span className="spinner" aria-hidden="true" />
          Loading recipe…
        </div>
      </section>
    );
  }

  const currentRecipe = recipe;

  async function remove() {
    if (window.confirm(`Delete ${currentRecipe.name}? This can’t be undone.`)) {
      setDeleting(true);
      try {
        await recipesApi.remove(currentRecipe.id);
        router.push("/recipes");
      } catch (exception) {
        setError(exception instanceof Error ? exception.message : "Unable to delete recipe.");
        setDeleting(false);
      }
    }
  }

  // Detect allergen conflicts between user profile and recipe
  const conflictingAllergens =
    profile && nutrition
      ? nutrition.allergens.filter((allergen) =>
          profile.allergies.some(
            (userAllergy) =>
              allergen.toLowerCase().includes(userAllergy.toLowerCase()) ||
              userAllergy.toLowerCase().includes(allergen.toLowerCase())
          )
        )
      : [];

  return (
    <section className="page narrow">
      <Link className="back-link" href="/recipes">
        ← Back to recipes
      </Link>

      <div className="page-heading">
        <div>
          <p className="eyebrow">Recipe details</p>
          <h1>{currentRecipe.name}</h1>
          <p className="page-description">
            {currentRecipe.ingredients.length} ingredient
            {currentRecipe.ingredients.length === 1 ? "" : "s"} · Estimated per serving
          </p>
        </div>
        <div className="heading-actions">
          {!editing && (
            <button className="button secondary" onClick={() => setEditing(true)}>
              ✏️ Edit recipe
            </button>
          )}
          <button className="button danger" disabled={deleting} onClick={remove}>
            {deleting ? "Deleting…" : "Delete"}
          </button>
        </div>
      </div>

      {/* Allergen Conflict Alert Banner */}
      {conflictingAllergens.length > 0 && (
        <div className="allergen-warning-banner" role="alert">
          <span className="warning-icon">⚠️</span>
          <div>
            <strong>Allergen Warning for Your Profile</strong>
            <p>
              This recipe contains <strong>{conflictingAllergens.join(", ")}</strong>, which matches
              your saved profile allergy restrictions.
            </p>
          </div>
        </div>
      )}

      {editing ? (
        <RecipeForm
          initialValue={currentRecipe}
          submitLabel="Save changes"
          onSubmit={async (payload) => {
            const updated = await recipesApi.update(currentRecipe.id, payload);
            setRecipe(updated);
            if (updated.nutrition) {
              setNutrition(updated.nutrition);
            }
            setEditing(false);
          }}
        />
      ) : (
        <>
          {/* Nutrition & Serving Scaler Card */}
          <section className="nutrition-card content-card">
            <div className="nutrition-card-header">
              <div>
                <p className="eyebrow">Nutritional profile</p>
                <h2>Nutrition & Serving Size</h2>
              </div>

              {/* Serving Stepper */}
              <div className="serving-stepper-wrap">
                <span className="serving-label">Servings:</span>
                <div className="serving-stepper">
                  <button
                    type="button"
                    className="stepper-btn"
                    onClick={() => setServings((s) => Math.max(1, s - 1))}
                    disabled={servings <= 1}
                    aria-label="Decrease servings"
                  >
                    −
                  </button>
                  <span className="stepper-count">{servings}</span>
                  <button
                    type="button"
                    className="stepper-btn"
                    onClick={() => setServings((s) => Math.min(20, s + 1))}
                    disabled={servings >= 20}
                    aria-label="Increase servings"
                  >
                    +
                  </button>
                </div>
              </div>
            </div>

            {nutrition && (
              <>
                {/* Confidence / Estimation Warning */}
                {nutrition.is_estimate && (
                  <div className="estimate-notice">
                    <span className="estimate-icon">ℹ️</span>
                    <span>
                      <strong>Estimated calculation:</strong> Some ingredients (
                      {nutrition.unmatched_ingredients.join(", ")}) could not be fully matched with
                      the standard food database.
                    </span>
                  </div>
                )}

                {/* Macro Cards Grid */}
                <div className={`macro-grid ${loadingNutrition ? "updating" : ""}`}>
                  <div className="macro-card calories-card">
                    <span className="macro-label">Calories</span>
                    <strong className="macro-num">
                      {servings === 1 ? nutrition.per_serving.calories : nutrition.total.calories}
                    </strong>
                    <span className="macro-unit">
                      kcal {servings > 1 ? `(${nutrition.per_serving.calories} / serv)` : ""}
                    </span>
                  </div>
                  <div className="macro-card protein-card">
                    <span className="macro-label">Protein</span>
                    <strong className="macro-num">
                      {servings === 1 ? nutrition.per_serving.protein : nutrition.total.protein}g
                    </strong>
                    <span className="macro-unit">
                      {servings > 1 ? `(${nutrition.per_serving.protein}g / serv)` : "grams"}
                    </span>
                  </div>
                  <div className="macro-card carbs-card">
                    <span className="macro-label">Carbs</span>
                    <strong className="macro-num">
                      {servings === 1
                        ? nutrition.per_serving.carbohydrates
                        : nutrition.total.carbohydrates}
                      g
                    </strong>
                    <span className="macro-unit">
                      {servings > 1 ? `(${nutrition.per_serving.carbohydrates}g / serv)` : "grams"}
                    </span>
                  </div>
                  <div className="macro-card fat-card">
                    <span className="macro-label">Total Fat</span>
                    <strong className="macro-num">
                      {servings === 1 ? nutrition.per_serving.fat : nutrition.total.fat}g
                    </strong>
                    <span className="macro-unit">
                      {servings > 1 ? `(${nutrition.per_serving.fat}g / serv)` : "grams"}
                    </span>
                  </div>
                </div>

                {/* Additional Micronutrients */}
                <div className="micronutrients-section">
                  <h3 className="sub-heading">Detailed Breakdown ({servings} serving{servings === 1 ? "" : "s"})</h3>
                  <div className="micro-pills-row">
                    <div className="micro-pill">
                      <span>Dietary Fiber:</span>
                      <strong>
                        {servings === 1 ? nutrition.per_serving.fiber : nutrition.total.fiber}g
                      </strong>
                    </div>
                    <div className="micro-pill">
                      <span>Sugars:</span>
                      <strong>
                        {servings === 1 ? nutrition.per_serving.sugar : nutrition.total.sugar}g
                      </strong>
                    </div>
                    <div className="micro-pill">
                      <span>Saturated Fat:</span>
                      <strong>
                        {servings === 1
                          ? nutrition.per_serving.saturated_fat
                          : nutrition.total.saturated_fat}
                        g
                      </strong>
                    </div>
                    <div className="micro-pill">
                      <span>Sodium:</span>
                      <strong>
                        {servings === 1 ? nutrition.per_serving.sodium : nutrition.total.sodium}mg
                      </strong>
                    </div>
                  </div>
                </div>

                {/* Dietary Tags & Allergen Info */}
                <div className="dietary-allergen-row">
                  {/* Dietary Badges */}
                  <div className="dietary-tags-block">
                    <h3 className="sub-heading">Dietary Labels</h3>
                    {nutrition.dietary_tags.length > 0 ? (
                      <div className="dietary-badges-list">
                        {nutrition.dietary_tags.map((tag) => (
                          <span key={tag} className="dietary-badge-chip">
                            ✓ {tag}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <p className="sub-muted">No specific dietary labels identified.</p>
                    )}
                  </div>

                  {/* Allergen Info */}
                  <div className="allergen-block">
                    <h3 className="sub-heading">Detected Allergens</h3>
                    {nutrition.allergens.length > 0 ? (
                      <div className="allergen-badges-list">
                        {nutrition.allergens.map((allergen) => (
                          <span key={allergen} className="allergen-chip">
                            ⚠️ {allergen}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <p className="allergen-none-text">✓ No common allergens detected.</p>
                    )}
                  </div>
                </div>
              </>
            )}
          </section>

          {/* Ingredients List */}
          <section className="ingredients-list content-card">
            <div className="section-heading">
              <div>
                <p className="eyebrow">What you need</p>
                <h2>Ingredients ({servings} serving{servings === 1 ? "" : "s"})</h2>
              </div>
              <span className="count-badge">{currentRecipe.ingredients.length}</span>
            </div>
            <ul>
              {currentRecipe.ingredients.map((ingredient) => {
                const scaledQty =
                  Math.round(ingredient.quantity * servings * 100) / 100;
                return (
                  <li key={ingredient.id}>
                    <span className="ingredient-name">{ingredient.name}</span>
                    <span>
                      {scaledQty} {ingredient.unit}
                    </span>
                  </li>
                );
              })}
            </ul>
          </section>
        </>
      )}
    </section>
  );
}

export default function RecipeDetailPage() {
  return (
    <Suspense
      fallback={
        <section className="page narrow">
          <div className="content-card loading-card">
            <span className="spinner" aria-hidden="true" />
            Loading recipe…
          </div>
        </section>
      }
    >
      <RecipeDetailContent />
    </Suspense>
  );
}
