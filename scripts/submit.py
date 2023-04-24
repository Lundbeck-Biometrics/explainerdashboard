import inspect

def submit_dashboard(name, port, explainer):
    '''Packages dashboard information and exports it into two files (yaml and joblib pair).
    The sagemaker lifecycle script starts a listener process that spins up explainer dashboards
    on the sagemaker system terminal.

    name: title for dashboard, also used for naming exported files
    port: the port on which sagemaker studio should spin up the dashboard
          (nothing will happen if the port is already in use)
    model: the model object (random forrest or whatever)'''

    DIRECTORY_TO_WATCH = "/home/sagemaker-user/dashboard-definitions"

    inspection = inspect.getmodule(explainer.model)
    print(f'model origin {inspection = }')
    if inspection and '__file__' in dir(inspection) and inspection.__file__.startswith('/home/sagemaker-user/'):
        raise EnvironmentError(f'WARNING! Detected Custom Python model: {inspection}')

    db = ExplainerDashboard(
        explainer,
        title=name,
        whatif=True,
        mode='dash',
        port=port,
        routes_pathname_prefix='/',
        requests_pathname_prefix=f'/jupyter/default/proxy/{port}/'
    )

    # export dashboard files
    filename_prefix = name.replace(' ', '_').replace('.', '_')
    db.to_yaml(
        filepath=f"{DIRECTORY_TO_WATCH}/{filename_prefix}.yaml",
        explainerfile=f"{DIRECTORY_TO_WATCH}/{filename_prefix}.joblib",
        dump_explainer=True)
    print(f'<STUDIO_URL>/jupyter/default/proxy/{port}')
