from functions.abac_functions import BloomACCRunner

BACC = BloomACCRunner()

choice = int(input("Select: "))
if choice == 1:
    BACC.deploy_bloomacc()
else:
    BACC.connect_bloomacc()
    BACC.add_subject()
    BACC.add_object()
    BACC.add_policy()
    BACC.access_control()
