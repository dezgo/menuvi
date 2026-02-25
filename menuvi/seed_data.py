"""Seed data extracted from Jewel of India menu HTML.

Each category maps to a list of (name, description, price_cents|None) tuples.
"""

MENU: dict[str, list[tuple[str, str, int | None]]] = {
    "Side Dishes": [
        ("Raita", "Seasoned yoghurt with cucumber", 500),
        ("Banana in Coconut", "With a dash of lime juice & flakes of almonds", 500),
        ("Fresh Garden Salad", "", 700),
        ("Kachumber", "Tossed salad Indian style", 500),
        ("Pappadams", "", 400),
        ("Lime Pickle / Mango Chutney", "", 400),
        ("Tamarind Chutney", "", 400),
        ("Mint Chutney", "", 400),
    ],
    "Desserts": [
        ("Gulab Jamun", "Reduced milk dumplings soaked in cardamom flavoured sugar syrup", 1000),
    ],
    "Special Dinner Packs": [
        (
            "Dinner for 2",
            "2 Pcs Vegetable Samosas, 2 Pcs Chicken Tikka, Beef Vindaloo (1), "
            "Butter Chicken (1), Steamed Rice (1), 2 Pcs Naan, Raita (1). "
            "$1.00 extra if substituted with lamb dishes",
            5590,
        ),
        (
            "Dinner for 4",
            "4 Pcs Vegetable Samosa, 4 Pcs Tandoori Chicken, Beef Vindaloo (1), "
            "Butter Chicken (1), Saag Gosht (1), Nizami Handi (1), "
            "Steamed Rice (2), 4 Pcs Naan, Raita (1)",
            10490,
        ),
    ],
    "Entrée": [
        ("Vegetable Samosas (2 pcs)", "Savoury pastry triangles filled with spicy potatoes and green peas", 1290),
        ("Onion Bhaji (4 pcs)", "Spicy onion fritters served with mint and tamarind chutneys", 1290),
        ("Palak Papdi Chaat", "Crispy spinach fritters on a tangy potato salad", 1490),
        ("Tali Jhinga", "Batter-fried crispy prawns", 2390),
        ("Seekh Kebab (4 pcs)", "Lean lamb mince skewers, cooked in tandoor", 1590),
        ("Chicken Tikka (4 pcs)", "Boneless tandoori chicken", 1590),
        ("Tandoori Chicken", "Half spring chicken cooked in tandoor", 1690),
        ("Tandoori Lamb Cutlets (4 pcs)", "", 2490),
        ("Cauliflower 65 (4 pcs)", "Deep fried cauliflower florets in a spicy yoghurt and fresh curry leaf marinade", 1490),
    ],
    "Seafood Dishes": [
        ("Kadhai Prawns", "Wok fried prawns", 2490),
        ("Prawn Curry Goanese", "Prawns cooked in a spiced coconut curry sauce", 2490),
        ("Prawn Vindaloo", "A very hot prawn curry with potato", 2490),
        ("Fish Methi Masala", "Fish, mildly spiced in tomato, onion and fenugreek sauce", 2490),
        ("Goan Fish Curry", "Fish cooked in a spiced coconut curry sauce", 2490),
    ],
    "Chicken Dishes": [
        ("Butter Chicken", "Boneless tandoori chicken in a tomato & butter sauce", 2290),
        ("Chicken Chettinad", "A speciality from Southern India, pepper spiced curry", 2290),
        ("Saag Chicken", "Chicken with spinach", 2290),
        ("Chicken Korma", "Boneless chicken pieces in a curry sauce mildly flavoured with cardamom", 2290),
        ("Chicken Vindaloo", "Ever popular with Australians - very hot!", 2290),
        ("Dum Ka Murgh", "Succulent pieces of chicken napped with herbs and spices and simmered in a smooth gravy on a slow fire", 2290),
        ("Chicken Tikka Masala", "Shredded chicken tikka tossed with capsicum, onions & spices", 2290),
    ],
    "Vegetarian": [
        ("Malai Kofta Kashmiri", "Cottage cheese dumplings in cashew gravy", 2090),
        ("Palak Paneer", "Home made cottage cheese curried with spinach & spices", 2090),
        ("Aloo Palak", "Spinach & potato cooked with spices", 2090),
        ("Kadhai Paneer / Vegetables", "Wok fried cottage cheese / vegetables", 2090),
        ("Baingan Masala", "Eggplant and potatoes cooked in onion-tomato gravy, flavoured with fresh herbs", 2090),
        ("Nizami Handi", "A mélange of vegetables cooked in a cashew & tomato gravy, strongly flavoured with carom seeds", 2090),
        ("Vegetable Korma", "", 2090),
        ("Aloo Mutter", "A simple preparation of green peas & potato with spices", 2090),
        ("Aloo Gobhi", "Cauliflower and potatoes sautéed with mild spices", 2090),
        ("Dal Makhni (Black Lentils)", "Whole black lentils cooked to perfection with tomatoes, garlic, butter and cream — a Signature Dish!", 2090),
        ("Dal Masala (Yellow Lentils)", "Yellow lentils tempered with mustard seeds and curry leaves", 2090),
    ],
    "Tandoori Breads": [
        ("Plain Naan", "Leavened plain flour bread, served smeared with butter", 400),
        ("Garlic Naan", "Garlic flavoured naan", 450),
        ("Tandoori Roti", "Unleavened, round, whole wheat flour bread", 450),
        ("Tandoori Paratha", "Whole wheat flour bread with flaky layers, served buttered", 500),
        ("Cheese Kulcha", "Bread stuffed with cheese", 500),
        ("Aloo Paratha", "Whole meal bread stuffed with spicy potatoes", 500),
    ],
    "Lamb / Beef Dishes": [
        ("Saag Lamb", "Lamb with spinach", 2290),
        ("Saag Beef", "Beef with spinach", 2190),
        ("Lamb Vindaloo", "", 2290),
        ("Beef Vindaloo", "", 2190),
        ("Lamb Rogan Josh", "A delicacy from Northern India", 2190),
        ("Kadhai Lamb", "Spiced lamb tossed with capsicum, onion & spices", 2290),
        ("Kadhai Beef", "Spiced beef tossed with capsicum, onion & spices", 2190),
        ("Dum Ka Gosht (Lamb)", "Diced lamb napped with herbs and spices and simmered in a smooth gravy on a slow fire", 2290),
        ("Dum Ka Gosht (Beef)", "Diced beef napped with herbs and spices and simmered in a smooth gravy on a slow fire", 2190),
        ("Madras Beef", "Beef cooked with roasted coconut gravy", 2190),
    ],
    "Rice Dishes": [
        ("Lamb Biryani", "Oven cooked rice with spiced lamb", 2290),
        ("Chicken Biryani", "Oven cooked rice with spiced chicken", 2290),
        ("Vegetable Biryani", "Mix vegetables cooked with spices & basmati rice in a slow temperature oven", 2190),
        ("Basmati Pulao", "", 400),
        ("Plain Boiled Rice", "", 400),
    ],
}
