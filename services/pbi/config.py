class BaseConfig(object):
    # Can be set to 'MasterUser' or 'ServicePrincipal'
    AUTHENTICATION_MODE = 'MasterUser'

    # Workspace Id in which the report is present
    # WORKSPACE_ID = 'af59799a-ca32-4d56-8b91-54ba5aa426e0'
    
    # Report Id for which Embed token needs to be generated
    # REPORT_ID = '26bca2ee-82fd-4236-b841-91fb76ab67a6'
    
    # Id of the Azure tenant in which AAD app and Power BI report is hosted. Required only for ServicePrincipal authentication mode.
    TENANT_ID = '5763fc71-bb17-4d84-b9da-9b81b8bd943d'
    
    # Client Id (Application Id) of the AAD app
    CLIENT_ID = '94cb70d5-7579-471d-a724-30c44f8d7cd1'
    
    # Client Secret (App Secret) of the AAD app. Required only for ServicePrincipal authentication mode.
    CLIENT_SECRET = 'OA2GWeaeS.6Ge.~7w-SxJlMwDfb_XqS10-'
    
    # Scope of AAD app. Use the below configuration to use all the permissions provided in the AAD app through Azure portal.
    SCOPE = ['https://analysis.windows.net/powerbi/api/.default']
    
    # URL used for initiating authorization request
    AUTHORITY = 'https://login.microsoftonline.com/organizations'
    
    # Master user email address. Required only for MasterUser authentication mode.
    POWER_BI_USER = 'pbiuser@onesqftpbi.onmicrosoft.com'
    
    # Master user email password. Required only for MasterUser authentication mode.
    POWER_BI_PASS = '{sam007}'
