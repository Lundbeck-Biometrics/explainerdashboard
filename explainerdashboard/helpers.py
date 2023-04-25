import inspect
from pathlib import Path

def submit_dashboard(name, port, explainer):
    '''Packages dashboard information and exports it into two files (yaml and joblib pair).
    The sagemaker lifecycle script starts a listener process that spins up explainer dashboards
    on the sagemaker system terminal.

    name: title for dashboard, also used for naming exported files
    port: the port on which sagemaker studio should spin up the dashboard
          (nothing will happen if the port is already in use)
    explainer: contains model and validation data, must be of type `ClassifierExplainer` or `RegressionExplainer`'''

    DIRECTORY_TO_WATCH = "/home/sagemaker-user/dashboard-definitions"
    PYTHON_SITE_PACKAGES = '/opt/conda/envs/studio/lib/python3.9/site-packages'
    filename_prefix = name.replace(' ', '_').replace('.', '_')
    python_syspaths=Path(f"{DIRECTORY_TO_WATCH}/{filename_prefix}.syspaths")

    inspection = inspect.getmodule(explainer.model)
    print(f'model origin {inspection = }')
    if inspection and '__file__' in dir(inspection) and inspection.__file__.startswith('/home/sagemaker-user/'):
        module_path_parent = Path(inspection.__file__).parent
        if not module_path_parent.exists():
            raise EnvironmentError(f'{module_path_parent} does not exists')
        python_syspaths.write_text(module_path_parent)
        print(f'Detected Custom Python code detected\n\t{inspection = }\n\t{python_syspaths = }')

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
    db.to_yaml(
        filepath=f"{DIRECTORY_TO_WATCH}/{filename_prefix}.yaml",
        explainerfile=f"{DIRECTORY_TO_WATCH}/{filename_prefix}.joblib",
        dump_explainer=True)
    print(f'<STUDIO_URL>/jupyter/default/proxy/{port}')
