import json
import warnings
from textwrap import indent

import dotenv
from funcsession import *

import hvac

siteToMigrate = {'hrisy': 'SMB'}


# SETTINGS
warnings.filterwarnings("ignore", category=DeprecationWarning)
dotenv_path = ".env"
dotenv.load_dotenv(dotenv_path)
hashiToken = os.environ.get("VAULT_TOKEN")
hashiHost = os.environ.get("VAULT_HOST")
s, urlST = Authenticate("ST_NON_PROD")
s.verify = False
s.headers.update({'Accept':'application/json'})

# VARS
vault = 'SecureTransport'
tier = 'production'
# Hashi Authentication
client = hvac.Client(
    url=hashiHost,
    token=hashiToken,
    verify=False
)

# EXPORT FROM SOURCE ST

resource = "sites/"
params = {'account': list(siteToMigrate)[0], 'name': siteToMigrate[list(siteToMigrate)[0]]}
res = s.get(urlST + resource, params = params)
sites = res.json()['result'][0]
read_response = client.secrets.kv.v2.read_secret_version(mount_point=vault,
                                                                 path=f'accounts/{list(siteToMigrate)[0]}/sites/{tier}/{siteToMigrate[list(siteToMigrate)[0]]}')



sess, targetST = Authenticate("ST_PROD")
resource = 'sites/'

if sites:
    sites['smbUploadFolder'] = read_response['data']['metadata']['custom_metadata']['smbUploadFolder']
    sites['smbPassword'] = read_response['data']['data']['smbPassword']
    response = sess.post(targetST + resource, json=sites)
    logging.info(f"Site migration status {response.status_code}; Message: {response.text}")