from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.catalog.models import Ingredient, Recipe, RecipeIngredient


def seed_demo_data(session: Session) -> None:
    if session.scalar(select(func.count()).select_from(Recipe)):
        return

    ingredient_data = {
        "zabpehely": ("zabpehely", "gabona", 372, 13.5, 58.7, 7.0, 42, [], ["gluten"]),
        "tej": ("tej", "tejtermek", 60, 3.2, 4.8, 3.3, 48, [], ["milk"]),
        "gorog-joghurt": ("görög joghurt", "tejtermek", 97, 9.0, 3.9, 5.0, 120, [], ["milk"]),
        "alma": ("alma", "gyumolcs", 52, 0.3, 13.8, 0.2, 70, [8, 9, 10, 11], []),
        "banan": ("banán", "gyumolcs", 89, 1.1, 22.8, 0.3, 85, [], []),
        "tojas": ("tojás", "feherje", 143, 12.6, 0.7, 9.5, 105, [], ["egg"]),
        "paradicsom": ("paradicsom", "zoldseg", 18, 0.9, 3.9, 0.2, 95, [6, 7, 8, 9], []),
        "paprika": ("paprika", "zoldseg", 31, 1.0, 6.0, 0.3, 110, [7, 8, 9], []),
        "csirkemell": ("csirkemell", "hus", 120, 22.5, 0.0, 2.6, 255, [], []),
        "rizs": ("rizs", "gabona", 360, 7.0, 79.0, 0.7, 65, [], []),
        "voroshagyma": ("vöröshagyma", "zoldseg", 40, 1.1, 9.3, 0.1, 45, [7, 8, 9, 10], []),
        "tejfol": ("tejföl", "tejtermek", 198, 2.4, 3.5, 20.0, 95, [], ["milk"]),
        "teljes-kiorlesu-teszta": (
            "teljes kiőrlésű tészta",
            "gabona",
            350,
            13.0,
            68.0,
            3.0,
            82,
            [],
            ["gluten"],
        ),
        "passata": ("passata", "zoldseg", 30, 1.4, 5.0, 0.2, 78, [], []),
        "olivaolaj": ("olívaolaj", "zsiradek", 884, 0.0, 0.0, 100.0, 190, [], []),
        "voroslencse": ("vöröslencse", "huvelyes", 352, 25.8, 60.1, 1.1, 95, [], []),
        "sargarepa": ("sárgarépa", "zoldseg", 41, 0.9, 9.6, 0.2, 45, [7, 8, 9, 10, 11], []),
        "burgonya": ("burgonya", "zoldseg", 77, 2.0, 17.0, 0.1, 50, [6, 7, 8, 9, 10], []),
        "cukkini": ("cukkini", "zoldseg", 17, 1.2, 3.1, 0.3, 90, [6, 7, 8, 9], []),
        "kuszkusz": ("kuszkusz", "gabona", 376, 12.8, 77.4, 0.6, 88, [], ["gluten"]),
        "csicseriborso": ("csicseriborsó", "huvelyes", 164, 8.9, 27.4, 2.6, 72, [], []),
        "feta": ("feta", "tejtermek", 264, 14.2, 4.1, 21.3, 180, [], ["milk"]),
        "turo": ("sovány túró", "tejtermek", 98, 17.0, 3.4, 1.5, 110, [], ["milk"]),
        "tortilla": (
            "teljes kiőrlésű tortilla",
            "gabona",
            310,
            9.0,
            52.0,
            8.0,
            100,
            [],
            ["gluten"],
        ),
        "salata": ("salátakeverék", "zoldseg", 20, 1.5, 3.0, 0.2, 150, [4, 5, 6, 7, 8, 9, 10], []),
        "mozzarella": ("mozzarella", "tejtermek", 280, 22.0, 3.0, 21.0, 220, [], ["milk"]),
        "gomba": ("csiperkegomba", "zoldseg", 22, 3.1, 3.3, 0.3, 120, [9, 10, 11], []),
    }
    package_data: dict[str, tuple[float, int]] = {
        "zabpehely": (500, 210),
        "tej": (1000, 480),
        "gorog-joghurt": (400, 480),
        "alma": (1000, 700),
        "banan": (1000, 850),
        "tojas": (500, 525),
        "paradicsom": (1000, 950),
        "paprika": (1000, 1100),
        "csirkemell": (1000, 2550),
        "rizs": (1000, 650),
        "voroshagyma": (1000, 450),
        "tejfol": (330, 314),
        "teljes-kiorlesu-teszta": (500, 410),
        "passata": (500, 390),
        "olivaolaj": (500, 950),
        "voroslencse": (500, 475),
        "sargarepa": (1000, 450),
        "burgonya": (2500, 1250),
        "cukkini": (1000, 900),
        "kuszkusz": (500, 440),
        "csicseriborso": (400, 288),
        "feta": (200, 360),
        "turo": (250, 275),
        "tortilla": (320, 320),
        "salata": (150, 225),
        "mozzarella": (125, 275),
        "gomba": (500, 600),
    }
    ingredients: dict[str, Ingredient] = {}

    for slug, values in ingredient_data.items():
        (
            name,
            category,
            kcal,
            protein,
            carbs,
            fat,
            _legacy_price,
            months,
            allergens,
        ) = values

        package_size_grams, package_price_huf = package_data[slug]

        normalized_price_per_100g = (
            package_price_huf / package_size_grams * 100
        )

        ingredient = Ingredient(
            slug=slug,
            name=name,
            category=category,
            kcal_per_100g=kcal,
            protein_per_100g=protein,
            carbs_per_100g=carbs,
            fat_per_100g=fat,
            price_per_100g_huf=round(normalized_price_per_100g, 2),
            package_size_grams=package_size_grams,
            package_price_huf=package_price_huf,
            price_store="MVP demo",
            price_source="Kézi mintaadat, production előtt frissítendő",
            price_checked_at=None,
            seasonal_months=months,
            allergens=allergens,
        )

        ingredients[slug] = ingredient
        session.add(ingredient)

    session.flush()

    recipes: list[dict[str, Any]] = [
        {
            "slug": "almas-zabkasa",
            "name": "Almás-fahéjas zabkása",
            "description": "Laktató, rostban gazdag reggeli szezonális almával.",
            "meal_type": "breakfast",
            "cuisine": "hungarian",
            "servings": 1,
            "prep": 3,
            "cook": 8,
            "tags": ["vegetarian", "light"],
            "ingredients": [
                ("zabpehely", 55, "55 g"),
                ("tej", 200, "2 dl"),
                ("alma", 140, "1 közepes"),
            ],
            "instructions": [
                "A zabpelyhet és a tejet melegítsd össze kis lángon.",
                "Keverd krémesre 6-8 perc alatt.",
                "Reszeld rá az almát, majd ízesítsd fahéjjal.",
            ],
        },
        {
            "slug": "joghurtos-bananos-pohar",
            "name": "Joghurtos-banános reggeli pohár",
            "description": "Gyors, magas fehérjetartalmú reggeli főzés nélkül.",
            "meal_type": "breakfast",
            "cuisine": "mediterranean",
            "servings": 1,
            "prep": 5,
            "cook": 0,
            "tags": ["vegetarian", "high_protein"],
            "ingredients": [
                ("gorog-joghurt", 250, "250 g"),
                ("banan", 120, "1 darab"),
                ("zabpehely", 35, "35 g"),
            ],
            "instructions": [
                "Tedd a joghurt felét egy pohárba.",
                "Rétegezd rá a felszeletelt banánt és a zabpelyhet.",
                "Fedd be a maradék joghurttal.",
            ],
        },
        {
            "slug": "zoldseges-omlett",
            "name": "Zöldséges omlett",
            "description": "Fehérjedús, gyors reggeli friss zöldségekkel.",
            "meal_type": "breakfast",
            "cuisine": "mediterranean",
            "servings": 1,
            "prep": 5,
            "cook": 8,
            "tags": ["vegetarian", "gluten_free", "high_protein"],
            "ingredients": [
                ("tojas", 150, "3 darab"),
                ("paradicsom", 100, "1 darab"),
                ("paprika", 80, "fél darab"),
                ("olivaolaj", 5, "1 teáskanál"),
            ],
            "instructions": [
                "Verd fel a tojásokat.",
                "Párold meg röviden a felkockázott zöldségeket.",
                "Öntsd rá a tojást, majd süsd készre fedő alatt.",
            ],
        },
        {
            "slug": "konnyu-csirkepaprikas",
            "name": "Könnyű csirkepaprikás rizzsel",
            "description": "Magyaros ebéd csökkentett zsiradékkal és pontos adagokkal.",
            "meal_type": "lunch",
            "cuisine": "hungarian",
            "servings": 2,
            "prep": 12,
            "cook": 30,
            "tags": ["high_protein", "gluten_free", "light"],
            "ingredients": [
                ("csirkemell", 360, "360 g"),
                ("rizs", 130, "130 g szárazon"),
                ("voroshagyma", 100, "1 darab"),
                ("paprika", 120, "1 darab"),
                ("tejfol", 60, "3 evőkanál"),
            ],
            "instructions": [
                "A hagymát kevés vízen vagy olajspray-vel párold üvegesre.",
                "Add hozzá a felkockázott csirkét és a paprikát.",
                "Fűszerezd pirospaprikával, majd kevés vízzel főzd puhára.",
                "Húzd le a tűzről, keverd bele a tejfölt, és főtt rizzsel tálald.",
            ],
        },
        {
            "slug": "olaszos-paradicsomos-csirketeszta",
            "name": "Olaszos paradicsomos csirketészta",
            "description": "Gyors, családbarát tésztaétel sovány csirkével.",
            "meal_type": "lunch",
            "cuisine": "italian",
            "servings": 2,
            "prep": 10,
            "cook": 25,
            "tags": ["high_protein"],
            "ingredients": [
                ("csirkemell", 320, "320 g"),
                ("teljes-kiorlesu-teszta", 160, "160 g szárazon"),
                ("passata", 300, "3 dl"),
                ("voroshagyma", 80, "1 kisebb"),
                ("olivaolaj", 10, "1 evőkanál"),
            ],
            "instructions": [
                "Főzd meg a tésztát a csomagolás szerint.",
                "Pirítsd át a hagymát és a felkockázott csirkét.",
                "Öntsd fel passatával, majd fűszerezd bazsalikommal és oregánóval.",
                "Forgasd össze a tésztával.",
            ],
        },
        {
            "slug": "voroslencse-fozelek",
            "name": "Vöröslencse-főzelék tükörtojással",
            "description": "Olcsó, rostban gazdag magyaros ebéd.",
            "meal_type": "lunch",
            "cuisine": "hungarian",
            "servings": 2,
            "prep": 8,
            "cook": 25,
            "tags": ["vegetarian", "gluten_free", "high_protein"],
            "ingredients": [
                ("voroslencse", 180, "180 g"),
                ("sargarepa", 150, "2 darab"),
                ("voroshagyma", 80, "1 kisebb"),
                ("tojas", 100, "2 darab"),
            ],
            "instructions": [
                "Öblítsd át a lencsét.",
                "A hagymát és répát párold meg, majd add hozzá a lencsét.",
                "Öntsd fel vízzel és főzd krémesre.",
                "Készíts két tükörtojást, és ezzel tálald.",
            ],
        },
        {
            "slug": "mediterran-csicseriborsos-kuszkusz",
            "name": "Mediterrán csicseriborsós kuszkusz",
            "description": "Színes, gyors és jól csomagolható zöldséges ebéd.",
            "meal_type": "lunch",
            "cuisine": "mediterranean",
            "servings": 2,
            "prep": 10,
            "cook": 15,
            "tags": ["vegetarian"],
            "ingredients": [
                ("kuszkusz", 150, "150 g"),
                ("csicseriborso", 240, "240 g főtt"),
                ("cukkini", 200, "1 kisebb"),
                ("paradicsom", 180, "2 darab"),
                ("feta", 80, "80 g"),
            ],
            "instructions": [
                "Öntsd le a kuszkuszt azonos mennyiségű forró vízzel, majd fedd le.",
                "Pirítsd át a felkockázott cukkinit.",
                "Keverd össze a kuszkuszt, csicseriborsót, paradicsomot és cukkinit.",
                "Morzsold rá a fetát.",
            ],
        },
        {
            "slug": "turos-zoldseges-wrap",
            "name": "Túrós-zöldséges wrap",
            "description": "Hidegen is fogyasztható, fehérjedús vacsora.",
            "meal_type": "dinner",
            "cuisine": "hungarian",
            "servings": 1,
            "prep": 10,
            "cook": 0,
            "tags": ["vegetarian", "high_protein", "light"],
            "ingredients": [
                ("turo", 180, "180 g"),
                ("tortilla", 65, "1 darab"),
                ("paprika", 80, "fél darab"),
                ("paradicsom", 100, "1 darab"),
            ],
            "instructions": [
                "A túrót keverd össze sóval, borssal és zöldfűszerekkel.",
                "Kend a tortillára.",
                "Add hozzá a felcsíkozott zöldségeket, majd tekerd fel.",
            ],
        },
        {
            "slug": "csirkes-mediterran-salata",
            "name": "Csirkés mediterrán saláta",
            "description": "Könnyű, magas fehérjetartalmú vacsora.",
            "meal_type": "dinner",
            "cuisine": "mediterranean",
            "servings": 1,
            "prep": 10,
            "cook": 15,
            "tags": ["high_protein", "gluten_free", "lactose_free", "light"],
            "ingredients": [
                ("csirkemell", 180, "180 g"),
                ("salata", 120, "120 g"),
                ("paradicsom", 120, "1 nagy"),
                ("cukkini", 120, "fél kisebb"),
                ("olivaolaj", 8, "2 teáskanál"),
            ],
            "instructions": [
                "Fűszerezd és süsd át a csirkemellet.",
                "A cukkinit röviden grillezd vagy pirítsd meg.",
                "Forgasd össze a salátát és a paradicsomot.",
                "Szeleteld rá a csirkét, majd locsold meg olívaolajjal.",
            ],
        },
        {
            "slug": "gombas-mozzarellas-rizotto",
            "name": "Gombás-mozzarellás rizottó",
            "description": "Krémes olaszos vacsora mérsékelt adagban.",
            "meal_type": "dinner",
            "cuisine": "italian",
            "servings": 2,
            "prep": 10,
            "cook": 30,
            "tags": ["vegetarian", "gluten_free"],
            "ingredients": [
                ("rizs", 150, "150 g"),
                ("gomba", 250, "250 g"),
                ("voroshagyma", 70, "1 kisebb"),
                ("mozzarella", 100, "100 g"),
                ("olivaolaj", 10, "1 evőkanál"),
            ],
            "instructions": [
                "Párold meg a hagymát és a gombát.",
                "Add hozzá a rizst, majd fokozatosan adagolj forró vizet vagy alaplevet.",
                "Kevergesd, amíg a rizs krémes és puha lesz.",
                "A végén keverd bele a felkockázott mozzarellát.",
            ],
        },
    ]

    for item in recipes:
        recipe = Recipe(
            slug=item["slug"],
            name=item["name"],
            description=item["description"],
            meal_type=item["meal_type"],
            cuisine=item["cuisine"],
            default_servings=item["servings"],
            prep_minutes=item["prep"],
            cook_minutes=item["cook"],
            tags=item["tags"],
            instructions=item["instructions"],
        )
        session.add(recipe)
        session.flush()
        for ingredient_slug, quantity, display in item["ingredients"]:
            session.add(
                RecipeIngredient(
                    recipe_id=recipe.id,
                    ingredient_id=ingredients[ingredient_slug].id,
                    quantity_grams=quantity,
                    display_quantity=display,
                )
            )
    session.commit()
