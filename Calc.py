import sympy as smp
from fuzzywuzzy import process
from decimal import Decimal


def find_closest_match(input_string, valid_strings, threshold=70):
    match, score = process.extractOne(input_string, valid_strings)
    if score >= threshold:
        return match
    return None

def main():
    type_options = ["permenant", "limited", "non-secret", "pass", "shop"]
    variant_options = ["normal", "shiny", "mythic", "shiny mythic"]

    while True:  # Main loop
        type_input = input("Is the pet permenant, limited, non-secret, pass or shop? ").lower()
        type_input = find_closest_match(type_input, type_options)

        if type_input in ["permenant", "limited"]:
            while True:
                try:
                    exist = int(input("Enter # of exist: "))
                    rarity = int(input("Enter rarity: "))
                    demand = int(input("Enter demand (1-10): "))
                except ValueError:
                    print("Please enter valid numbers.")
                    continue

                rarity_confirmation = input(f"Rarity = {rarity:,}. Is this correct? (Y/N): ").strip().lower()
                if rarity_confirmation != 'y':
                    print("Let's try again.")
                    continue

                variant_input = input("Is the pet normal, shiny, mythic or shiny mythic? ").lower()
                variant_input = find_closest_match(variant_input, variant_options)

                if not variant_input:
                    print("Could not recognize variant. Try again.")
                    continue

                x_sym = smp.Symbol('x')

                # Normal
                if variant_input == "normal":
                    i1 = smp.integrate(smp.sqrt(rarity / (exist + 1)), (x_sym, 0, exist + 1))
                    i2 = smp.integrate(smp.sqrt(rarity / (exist)), (x_sym, 0, exist))
                # Shiny
                elif variant_input == "shiny":
                    i1 = smp.integrate(smp.sqrt(rarity*40 / (exist + 1)), (x_sym, 0, exist + 1))
                    i2 = smp.integrate(smp.sqrt(rarity*40 / (exist)), (x_sym, 0, exist))
                # Mythic
                elif variant_input == "mythic":
                    i1 = smp.integrate(smp.sqrt(rarity*80 / (exist + 1)), (x_sym, 0, exist + 1))
                    i2 = smp.integrate(smp.sqrt(rarity*80 / (exist)), (x_sym, 0, exist))
                # Shiny Mythic
                elif variant_input == "shiny mythic":
                    i1 = smp.integrate(smp.sqrt(rarity*320 / (exist + 1)), (x_sym, 0, exist + 1))
                    i2 = smp.integrate(smp.sqrt(rarity*320 / exist), (x_sym, 0, exist))
                else:
                    print("Invalid variant.")
                    continue

                diff = (i1 - i2) * (1 + 0.05 * smp.exp(0.25 * demand))
                value = diff.evalf()
                print(f"Estimated Value: {value}")

                cont = input("Would you like to continue? Y/N: ").strip().lower()
                if cont != "y":
                    return
                else:
                    break  # Go back to top of main loop

        elif type_input in ["pass", "non secret"]:
            while True:
                try:
                    rarity = Decimal(input("Enter Rarity: "))
                    demand = int(input("Enter Demand: "))
                    c = Decimal(input("Enter c value: "))
                except ValueError:
                    print("Please enter valid numbers")
                    continue

                rarity_confirmation = input(f"Rarity = {rarity:,}. Is this correct? (Y/N): ").strip().lower()
                if rarity_confirmation != 'y':
                    print("Let's try again.")
                    continue

                variant_input = input("Is the pet normal, shiny, mythic or shiny mythic? ").lower()
                variant_input = find_closest_match(variant_input, variant_options)

                if not variant_input:
                    print("Could not recognize variant. Try again.")
                    continue

                x_sym = smp.Symbol('x')

                if variant_input == "normal":
                    i1 = smp.integrate((((1 - smp.exp(-c * x_sym)) / c) / rarity), (x_sym, 0, demand + 1))
                    i2 = smp.integrate((((1 - smp.exp(-c * x_sym)) / c) / rarity), (x_sym, 0, demand))
                    diff = (i1 - i2) ** 3
                    diff = smp.sqrt(diff) / 2
                else:
                    try:
                        variant_multi = int(input("Enter a variant multiplier: "))
                    except ValueError:
                        print("Enter a valid number")
                        continue
                    i1 = smp.integrate((((1 - smp.exp(-c * x_sym)) / c) / rarity), (x_sym, 0, demand + 1))
                    i2 = smp.integrate((((1 - smp.exp(-c * x_sym)) / c) / rarity), (x_sym, 0, demand))
                    diff = ((i1 - i2) ** 3) / (1 / (variant_multi / 10))
                    diff = 0.5 * smp.sqrt(diff)

                value = diff.evalf()
                print(f"Estimated Value: {value}")

                cont = input("Would you like to continue? Y/N: ").strip().lower()
                if cont != "y":
                    return
                else:
                    break

        elif type_input == "shop":
            while True:
                try:
                    price = int(input("Enter Price: "))
                    demand = int(input("Enter Demand: "))
                    c = Decimal(input("Enter c Value: "))
                except ValueError:
                    print("Please enter a valid number")
                    continue

                variant_input = input("Is the pet normal or shiny? ").lower()
                variant_input = find_closest_match(variant_input, variant_options)

                if not variant_input:
                    print("Could not recognize variant. Try again.")
                    continue

                x_sym = smp.Symbol('x')

                if variant_input == "normal":
                    i1 = smp.integrate((price * (1 - smp.exp(-c * x_sym))) / c, (x_sym, 0, demand + 1))
                    i2 = smp.integrate((price * (1 - smp.exp(-c * x_sym))) / c, (x_sym, 0, demand))
                    diff = (i1 - i2) ** 1.5
                    diff = 0.5 * smp.sqrt(diff)
                elif variant_input == "shiny":
                    m = int(input("Enter Variant Multiplier: "))
                    i1 = smp.integrate((price * (1 - smp.exp(-c * x_sym))) / c, (x_sym, 0, demand + 1))
                    i2 = smp.integrate((price * (1 - smp.exp(-c * x_sym))) / c, (x_sym, 0, demand))
                    diff = ((i1 - i2) ** 1.5) / (1 / (m / 10))
                    diff = 0.5 * smp.sqrt(diff)
                else:
                    print("Invalid variant.")
                    continue

                value = diff.evalf()
                print(f"Estimated Value: {value}")

                cont = input("Would you like to continue? Y/N: ").strip().lower()
                if cont != "y":
                    return
                else:
                    break

        else:
            print("Unrecognized pet type. Please try again.")

if __name__ == "__main__":
    main()
