from functions.abac_functions import BloomACCRunner


def main(babac):
    print(
        """===================================================================
          \rPlease select from the following options:
          \r1) Deploy ABAC system
          \r2) Connect to pre-existing deployed system
          \r3) Add subjects from file
          \r4) Add objects from file
          \r5) Add policies from file
          \r6) Request access
          \r7) Check balances
          \r==================================================================="""
    )
    choice = int(input("Please select from the above options [1-6] (exit = -1): "))

    if choice == 1:
        babac.deploy_bloomacc()
        main(babac)
    elif choice == 2:
        babac.connect_bloomacc()
        main(babac)
    elif choice == 3:
        babac.add_subject()
        main(babac)
    elif choice == 4:
        babac.add_object()
        main(babac)
    elif choice == 5:
        babac.add_policy()
        main(babac)
    elif choice == 6:
        babac.access_control()
        main(babac)
    elif choice == 7:
        print("Printing account balances...")
        babac.account_balances()
        main(babac)
    elif choice == -1:
        print("[EXIT] Closing program...")
        exit()
    else:
        main(babac)


if __name__ == "__main__":
    babac = BloomACCRunner()
    main(babac)
