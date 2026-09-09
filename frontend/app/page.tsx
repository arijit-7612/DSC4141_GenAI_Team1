import Link from "next/link";

export default function Home() {
  return (
    <section className="home-page">
      <div className="home-intro">
        <p className="eyebrow">Smart Bite</p>
        <h1>What would you like to do?</h1>
        <p>Plan your meals and keep your kitchen organized.</p>
      </div>

      <div className="home-options">
        <Link href="/recipes" className="home-option">
          <svg className="option-icon" viewBox="0 0 96 96" aria-hidden="true">
            <path d="M17 40h62l-5 37H22l-5-37Z" />
            <path d="M12 40h72M28 40c0-11 8-20 20-20s20 9 20 20M32 51v15M48 51v15M64 51v15" />
            <circle cx="34" cy="31" r="5" />
            <circle cx="48" cy="25" r="5" />
            <circle cx="62" cy="31" r="5" />
          </svg>
          <span className="option-title">Recipes</span>
          <span className="option-description">Browse your saved recipe library.</span>
        </Link>

        <Link href="/recipes/new" className="home-option">
          <svg className="option-icon" viewBox="0 0 96 96" aria-hidden="true">
            <path d="M20 74h56M27 65V22h42v43M35 32h26M35 43h26M35 54h14" />
            <path d="M62 57v20M52 67h20" />
          </svg>
          <span className="option-title">Add recipe</span>
          <span className="option-description">Save a new recipe to your library.</span>
        </Link>

        <Link href="/weekly-planner" className="home-option">
          <svg className="option-icon" viewBox="0 0 96 96" aria-hidden="true">
            <rect x="17" y="22" width="62" height="59" rx="5" />
            <path d="M17 38h62M31 15v14M65 15v14M29 51h10M43 51h10M57 51h10M29 64h10M43 64h10" />
          </svg>
          <span className="option-title">Weekly planner</span>
          <span className="option-description">Build your personalized weekly meal plan.</span>
        </Link>

        <div className="home-option unavailable" aria-disabled="true">
          <svg className="option-icon" viewBox="0 0 96 96" aria-hidden="true">
            <path d="M24 22h48v58H24zM32 34h32M32 46h32M32 58h20" />
            <path d="m59 66 6 6 11-13" />
          </svg>
          <span className="option-title">Grocery list</span>
          <span className="option-description">Create a shopping list from your recipes.</span>
          <span className="coming-soon">Coming soon</span>
        </div>
      </div>
    </section>
  );
}
