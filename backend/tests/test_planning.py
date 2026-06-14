from math import ceil

from fastapi.testclient import TestClient


def default_request() -> dict[str, object]:
    return {
        "people_count": 2,
        "calorie_target_per_person": 1800,
        "daily_budget_huf": 6500,
        "goal": "weight_loss",
        "meal_types": ["breakfast", "lunch", "dinner"],
        "preferred_cuisines": ["mixed"],
        "dietary_preferences": [],
        "excluded_ingredients": [],
        "max_total_cooking_minutes_per_meal": 60,
    }


def test_generate_plan_returns_options_and_package_costs(client: TestClient) -> None:
    response = client.post("/api/v1/plans/generate", json=default_request())

    assert response.status_code == 201
    payload = response.json()
    assert payload["id"]
    assert len(payload["meals"]) == 3
    assert len(payload["meal_options"]) == 3
    assert all(len(group["options"]) == 3 for group in payload["meal_options"])
    assert payload["shopping_list"]

    summary = payload["summary"]
    assert summary["people_count"] == 2
    assert summary["proportional_total_cost_huf"] > 0
    assert summary["full_purchase_total_cost_huf"] >= summary["proportional_total_cost_huf"]
    assert summary["shopping_total_cost_huf"] == summary["full_purchase_total_cost_huf"]


def test_shopping_list_rounds_to_complete_packages(client: TestClient) -> None:
    response = client.post("/api/v1/plans/generate", json=default_request())

    assert response.status_code == 201
    for item in response.json()["shopping_list"]:
        expected_packages = ceil(item["required_quantity_grams"] / item["package_size_grams"])
        assert item["packages_to_buy"] == expected_packages
        assert item["purchase_quantity_grams"] == (
            item["packages_to_buy"] * item["package_size_grams"]
        )
        assert item["purchase_cost_huf"] == (
            item["packages_to_buy"] * item["package_price_huf"]
        )


def test_excluded_ingredient_is_not_used_in_any_option(client: TestClient) -> None:
    request = default_request()
    request.update(
        {
            "people_count": 1,
            "meal_types": ["dinner"],
            "excluded_ingredients": ["gomba"],
        }
    )
    response = client.post("/api/v1/plans/generate", json=request)

    assert response.status_code == 201
    ingredient_names = {
        ingredient["name"]
        for group in response.json()["meal_options"]
        for meal in group["options"]
        for ingredient in meal["ingredients"]
    }
    assert all("gomba" not in name.casefold() for name in ingredient_names)


def test_saved_plan_can_be_loaded(client: TestClient) -> None:
    request = default_request()
    request.update(
        {
            "people_count": 1,
            "calorie_target_per_person": 2000,
            "daily_budget_huf": 5500,
            "goal": "high_protein",
        }
    )
    created = client.post("/api/v1/plans/generate", json=request)
    plan_id = created.json()["id"]

    loaded = client.get(f"/api/v1/plans/{plan_id}")
    assert loaded.status_code == 200
    assert loaded.json()["id"] == plan_id
    assert loaded.json()["meal_options"]
