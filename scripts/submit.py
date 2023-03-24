def submit_dashboard(name, port, model, X_test, y_test):
    dashboard_name = "yeet"
    explainer = RegressionExplainer(model, X_test, y_test)

    DIRECTORY_TO_WATCH = "/home/sagemaker-user/dashboard-definitions"
    db = ExplainerDashboard(
        explainer,
        title=name,
        whatif=False,
        mode="dash",
        port=port,
        routes_pathname_prefix="/",
        requests_pathname_prefix=f"/jupyter/default/proxy/{PORT}/",
    )

    filename = name.replace(" ", "_").replace(".", "_")

    db.to_yaml(filepath=f"{DIRECTORY_TO_WATCH}/{filename}.yaml", explainerfile=f"{DIRECTORY_TO_WATCH}/{filename}.joblib", dump_explainer=True)
    print(f"<STUDIO_URL>/jupyter/default/proxy/{port}")
