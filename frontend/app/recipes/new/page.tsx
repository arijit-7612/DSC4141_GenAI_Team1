"use client";

import { useRouter } from "next/navigation";
import { RecipeForm } from "../../../components/RecipeForm";
import { recipesApi } from "../../../lib/recipes";

export default function NewRecipePage() {
  const router = useRouter();
  return <section className="page narrow"><p className="eyebrow">New recipe</p><h1>Create a recipe</h1><RecipeForm submitLabel="Create recipe" onSubmit={async (recipe) => { const created = await recipesApi.create(recipe); router.push(`/recipes/${created.id}`); }} /></section>;
}
