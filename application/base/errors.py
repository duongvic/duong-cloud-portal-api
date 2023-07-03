#
# Copyright (c) 2020 FTI-CAS
#

from flask_babel import lazy_gettext as _l

DB_COMMIT_FAILED = 'Failed to commit object in database'
_l('Failed to commit object in database')
DB_LOCK_ACQUIRE_FAILED = 'Failed to acquire lock in database'
_l('Failed to acquire lock in database')
DB_LOCK_RELEASE_FAILED = 'Failed to release lock in database'
_l('Failed to release lock in database')

OBJECT_LIST_CONDITION_INVALID = 'Object listing condition invalid'
_l('Object listing condition invalid')
REQUEST_PARAM_INVALID = 'Request param invalid'
_l('Request param invalid')

CONFIG_NOT_FOUND = 'Configuration not found'
_l('Configuration not found')
CONFIG_VALUE_NOT_FOUND = 'Configuration value not found'
_l('Configuration value not found')

USER_NOT_FOUND = 'User not found'
_l('User not found')
USER_NOT_AUTHORIZED = 'User not authorized'
_l('User not authorized')
USER_ACTION_NOT_ALLOWED = 'User action not allowed'
_l('User action not allowed')
USER_NOT_ACTIVATED = 'User not activated'
_l('User not activated')
USER_ALREADY_ACTIVATED = 'User already activated'
_l('User already activated')
USER_BLOCKED_OR_DELETED = 'User blocked or deleted'
_l('User blocked or deleted')
USER_ALREADY_EXISTS = 'User already exists'
_l('User already exists')
USER_TOKEN_INVALID = 'User token invalid'
_l('User token invalid')
USER_NAME_INVALID = 'User name invalid'
_l('User name invalid')
USER_EMAIL_INVALID = 'User e-mail invalid'
_l('User e-mail invalid')
USER_PASSWORD_INVALID = 'User password invalid'
_l('User password invalid')
USER_PASSWORD_REQUIREMENT_NOT_MET = 'User password does not meet requirement'
_l('User password does not meet requirement')
USER_ROLE_INVALID = 'User role invalid'
_l('User role invalid')
USER_STATUS_INVALID = 'User status invalid'
_l('User status invalid')
USER_CREATE_FAILED = 'Failed to create user'
_l('Failed to create user')
USER_UPDATE_FAILED = 'Failed to update user'
_l('Failed to update user')
USER_DELETE_FAILED = 'Failed to delete user'
_l('Failed to delete user')
USER_OS_INFO_NOT_FOUND = 'OpenStack user info not found'
_l('OpenStack user info not found')
USER_OS_PROJECT_NOT_FOUND = 'OpenStack user project not found'
_l('OpenStack user project not found')

USER_BALANCE_NOT_FOUND = 'User balance not found'
_l('User balance not found')

ORDER_GROUP_NOT_FOUND = 'Order group not found'
_l('Order group not found')

ORDER_NOT_FOUND = 'Order not found'
_l('Order not found')
ORDER_NOT_FINISHED = 'Order not finished'
_l('Order not finished')
ORDER_ALREADY_FINISHED = 'Order already finished'
_l('Order already finished')
ORDER_EXPIRED = 'Order expired'
_l('Order expired')
ORDER_TIME_INVALID = 'Order time invalid'
_l('Order time invalid')
ORDER_PRODUCT_TYPE_NOT_FOUND = 'Order product type not found'
_l('Order product type not found')
ORDER_TYPE_INVALID = 'Order type invalid'
_l('Order type invalid')
ORDER_STATUS_INVALID = 'Order status invalid'
_l('Order status invalid')
ORDER_AMOUNT_INVALID = 'Order amount invalid'
_l('Order amount invalid')
ORDER_DURATION_INVALID = 'Order duration invalid'
_l('Order duration invalid')
ORDER_PRICE_NOT_MATCH = 'Order price not match'
_l('Order price not match')
ORDER_VALIDATION_FAILED = 'Order validation failed'
_l('Order validation failed')
ORDER_CREATED_TOO_MANY = 'Too many orders created'
_l('Too many orders created')

PAYMENT_NOT_FOUND = 'Payment not found'
_l('Payment not found')
PAYMENT_TYPE_NOT_SUPPORTED = 'Payment type not supported'
_l('Payment type not supported')
PAYMENT_TYPE_INVALID = 'Payment type invalid'
_l('Payment type invalid')
PAYMENT_CURRENCY_INVALID = 'Payment currency invalid'
_l('Payment currency invalid')
PAYMENT_CURRENCY_NOT_SUPPORTED = 'Payment currency not supported'
_l('Payment currency not supported')
PAYMENT_START_FAILED = 'Payment starts failed'
_l('Payment starts failed')
PAYMENT_FINISH_FAILED = 'Payment finishes failed'
_l('Payment finishes failed')
PAYMENT_SECURE_CODE_INVALID = 'Payment secure code invalid'
_l('Payment secure code invalid')

BILLING_NOT_FOUND = 'Billing not found'
_l('Billing not found')

REGION_NOT_FOUND = 'Region not found'
_l('Region not found')
REGION_NOT_SUPPORTED = 'Region not supported'
_l('Region not supported')

PROMOTION_NOT_FOUND = 'Promotion not found'
_l('Promotion not found')
PROMOTION_NOT_ENABLED = 'Promotion not enabled'
_l('Promotion not enabled')
PROMOTION_NOT_APPLIED = 'Promotion not applied'
_l('Promotion not applied')
PROMOTION_USE_EXCEEDED = 'Promotion use exceeded'
_l('Promotion use exceeded')
PROMOTION_PRODUCT_NOT_ACCEPTED = 'Product not accepted for promotion'
_l('Product not accepted for promotion')
PROMOTION_USER_NOT_ACCEPTED = 'User not accepted for promotion'
_l('User not accepted for promotion')
PROMOTION_RESOURCE_LIMIT = 'Promotion resource limit'
_l('Promotion resource limit')
PROMOTION_CONDITION_NOT_MET = 'Promotion condition not met'
_l('Promotion condition not met')

PRODUCT_NOT_FOUND = 'Product not found'
_l('Product not found')
PRODUCT_NOT_ENABLED = 'Product not enabled'
_l('Product not enabled')
PRODUCT_TYPE_INVALID = 'Product type invalid'
_l('Product type invalid')
PRODUCT_AMOUNT_INVALID = 'Product amount invalid'
_l('Product amount invalid')

PRODUCT_TYPE_NOT_FOUND = 'Product type not found'
_l('Product type not found')
PRODUCT_TYPE_NOT_SUPPORTED = 'Product type not supported'
_l('Product type not supported')

HISTORY_NOT_FOUND = 'History not found'
_l('History not found')

REPORT_NOT_FOUND = 'Report not found'
_l('Report not found')

TICKET_NOT_FOUND = 'Ticket not found'
_l('Ticket not found')

SUPPORT_NOT_FOUND = 'Support not found'
_l('Support not found')

TASK_NOT_FOUND = 'Task not found'
_l('Task not found')

COMPUTE_NOT_FOUND = 'Compute not found'
_l('Compute not found')
COMPUTE_NOT_ENABLED = 'Compute not enabled'
_l('Compute not enabled')
COMPUTE_NOT_AVAILABLE = 'Compute not available'
_l('Compute not available')
COMPUTE_LOCKED = 'Compute locked'
_l('Compute locked')
COMPUTE_DELETED = 'Compute deleted'
_l('Compute deleted')
COMPUTE_IS_RUNNING = 'Compute is running'
_l('Compute is running')
COMPUTE_STOPPED = 'Compute was stopped'
_l('Compute was stopped')
COMPUTE_NAME_INVALID = 'Compute name invalid'
_l('Compute name invalid')
COMPUTE_USERNAME_INVALID = 'Compute username invalid'
_l('Compute username invalid')
COMPUTE_PASSWORD_INVALID = 'Compute password invalid'
_l('Compute password invalid')
COMPUTE_PASSWORD_REQUIREMENT_NOT_MET = 'Compute password does not meet requirement'
_l('Compute password does not meet requirement')
COMPUTE_SSH_KEY_INVALID = 'Compute ssh key invalid'
_l('Compute ssh key invalid')
COMPUTE_INFO_MISSING = 'Compute info missing'
_l('Compute info missing')
COMPUTE_RESOURCE_EXHAUSTED = 'Compute resource exhausted'
_l('Compute resource exhausted')

COMPUTE_LOCK_FAILED = 'Failed to lock compute'
_l('Failed to lock compute')
COMPUTE_UNLOCK_FAILED = 'Failed to unlock compute'
_l('Failed to unlock compute')
COMPUTE_GET_STATUS_FAILED = 'Failed to get compute status'
_l('Failed to get compute status')
COMPUTE_CREATE_FAILED = 'Failed to create compute'
_l('Failed to create compute')
COMPUTE_RECREATE_FAILED = 'Failed to re-create compute'
_l('Failed to re-create compute')
COMPUTE_UPDATE_FAILED = 'Failed to update compute'
_l('Failed to update compute')
COMPUTE_DELETE_FAILED = 'Failed to delete compute'
_l('Failed to delete compute')

COMPUTE_ACTION_NOT_SUPPORTED = 'Compute action not supported'
_l('Compute action not supported')

COMPUTE_STATS_NOT_SUPPORTED = 'Compute stats not supported'
_l('Compute stats not supported')

COMPUTE_SNAPSHOT_NOT_SUPPORTED = 'Compute snapshot not supported'
_l('Compute snapshot not supported')
COMPUTE_SNAPSHOT_NOT_FOUND = 'Compute snapshot not found'
_l('Compute snapshot not found')
COMPUTE_SNAPSHOT_ALREADY_EXISTS = 'Compute snapshot already exists'
_l('Compute snapshot already exists')
COMPUTE_SNAPSHOT_GET_FAILED = 'Failed to get snapshot of compute'
_l('Failed to get snapshot of compute')
COMPUTE_SNAPSHOT_EXCEEDED = 'Compute snapshot exceeded'
_l('Compute snapshot exceeded')
COMPUTE_SNAPSHOT_NAME_INVALID = 'Compute snapshot name invalid'
_l('Compute snapshot name invalid')
COMPUTE_SNAPSHOT_CREATE_FAILED = 'Failed to create snapshot of compute'
_l('Failed to create snapshot of compute')
COMPUTE_SNAPSHOT_UPDATE_FAILED = 'Failed to update snapshot of compute'
_l('Failed to update snapshot of compute')
COMPUTE_SNAPSHOT_DELETE_FAILED = 'Failed to delete snapshot of compute'
_l('Failed to delete snapshot of compute')
COMPUTE_SNAPSHOT_ROLLBACK_FAILED = 'Failed to rollback snapshot of compute'
_l('Failed to rollback snapshot of compute')

COMPUTE_BACKUP_NOT_SUPPORTED = 'Compute backup not supported'
_l('Compute backup not supported')
COMPUTE_BACKUP_NOT_FOUND = 'Compute backup not found'
_l('Compute backup not found')
COMPUTE_BACKUP_EXCEEDED = 'Compute backup exceeded'
_l('Compute backup exceeded')
COMPUTE_BACKUP_GET_FAILED = 'Failed to get backup of compute'
_l('Failed to get backup of compute')
COMPUTE_BACKUP_CREATE_FAILED = 'Failed to create backup of compute'
_l('Failed to create backup of compute')
COMPUTE_BACKUP_UPDATE_FAILED = 'Failed to update backup of compute'
_l('Failed to update backup of compute')
COMPUTE_BACKUP_DELETE_FAILED = 'Failed to delete backup of compute'
_l('Failed to delete backup of compute')

COMPUTE_BACKUP_FILE_NOT_FOUND = 'Compute backup file not found'
_l('Compute backup file not found')
COMPUTE_BACKUP_FILE_EXCEEDED = 'Compute backup file exceeded'
_l('Compute backup file exceeded')
COMPUTE_BACKUP_FILE_GET_FAILED = 'Failed to get backup file of compute'
_l('Failed to get backup file of compute')
COMPUTE_BACKUP_FILE_CREATE_FAILED = 'Failed to create backup file of compute'
_l('Failed to create backup file of compute')
COMPUTE_BACKUP_FILE_UPDATE_FAILED = 'Failed to update backup file of compute'
_l('Failed to update backup file of compute')
COMPUTE_BACKUP_FILE_DELETE_FAILED = 'Failed to delete backup file of compute'
_l('Failed to delete backup file of compute')
COMPUTE_BACKUP_FILE_RESTORE_FAILED = 'Failed to restore backup file of compute'
_l('Failed to restore backup file of compute')

COMPUTE_SG_RULE_NOT_FOUND = 'Compute security group rule not found'
_l('Compute security group rule not found')
COMPUTE_SG_RULE_INVALID = 'Compute security group rule invalid'
_l('Compute security group rule invalid')
COMPUTE_SG_RULE_GET_FAILED = 'Failed to get security group rule of compute'
_l('Failed to get security group rule of compute')
COMPUTE_SG_RULE_CREATE_FAILED = 'Failed to create security group rule of compute'
_l('Failed to create security group rule of compute')
COMPUTE_SG_RULE_UPDATE_FAILED = 'Failed to update security group rule of compute'
_l('Failed to update security group rule of compute')
COMPUTE_SG_RULE_DELETE_FAILED = 'Failed to delete security group rule of compute'
_l('Failed to delete security group rule of compute')

COMPUTE_SG_NOT_FOUND = 'Compute security group not found'
_l('Compute security group not found')
COMPUTE_SG_INVALID = 'Compute security group invalid'
_l('Compute security group invalid')
COMPUTE_SG_GET_FAILED = 'Failed to get security group of compute'
_l('Failed to get security group of compute')
COMPUTE_SG_CREATE_FAILED = 'Failed to create security group of compute'
_l('Failed to create security group of compute')
COMPUTE_SG_UPDATE_FAILED = 'Failed to update security group of compute'
_l('Failed to update security group of compute')
COMPUTE_SG_DELETE_FAILED = 'Failed to delete security group of compute'
_l('Failed to delete security group of compute')

SG_NOT_FOUND = 'Security group not found'
_l('Security group not found')
SG_INVALID = 'Security group invalid'
_l('Security group invalid')
SG_GET_FAILED = 'Failed to get security group'
_l('Failed to get security group')
SG_CREATE_FAILED = 'Failed to create security group'
_l('Failed to create security group')
SG_UPDATE_FAILED = 'Failed to update security group'
_l('Failed to update security group')
SG_DELETE_FAILED = 'Failed to delete security group'
_l('Failed to delete security group')

SG_RULE_NOT_FOUND = 'Security group rule not found'
_l('Security group rule not found')
SG_RULE_INVALID = 'Security group rule invalid'
_l('Security group rule invalid')
SG_RULE_GET_FAILED = 'Failed to get Security group rule'
_l('Failed to get Security group rule')
SG_RULE_CREATE_FAILED = 'Failed to create Security group rule'
_l('Failed to create Security group rule')
SG_RULE_UPDATE_FAILED = 'Failed to update Security group rule'
_l('Failed to update Security group rule')
SG_RULE_DELETE_FAILED = 'Failed to delete Security group rule'
_l('Failed to delete Security group rule')

COMPUTE_ROUTE_INTERFACE_NOT_FOUND = 'Compute router interface not found'
_l('Compute router interface not found')
COMPUTE_ROUTE_INTERFACE_INVALID = 'Compute router interface invalid'
_l('Compute router interface invalid')
COMPUTE_ROUTE_INTERFACE_GET_FAILED = 'Failed to get router interface of compute'
_l('Failed to get router interface of compute')
COMPUTE_ROUTE_INTERFACE_CREATE_FAILED = 'Failed to create router interface of compute'
_l('Failed to create router interface of compute')
COMPUTE_ROUTE_INTERFACE_UPDATE_FAILED = 'Failed to update router interface of compute'
_l('Failed to update router interface of compute')
COMPUTE_ROUTE_INTERFACE_DELETE_FAILED = 'Failed to delete router interface of compute'
_l('Failed to delete router interface of compute')

COMPUTE_TASK_NOT_FOUND = 'Compute task not found'
_l('Compute task not found')
COMPUTE_TASK_INVALID = 'Compute task invalid'
_l('Compute task invalid')
COMPUTE_SYNC_PARAM_INVALID = 'Compute sync params invalid'
_l('Compute sync params invalid')
COMPUTE_SYNC_FAILED = 'Compute sync failed'
_l('Compute sync failed')
COMPUTE_MGMT_ACTION_INVALID = 'Compute management action invalid'
_l('Compute management action invalid')

BACKEND_CLUSTER_NOT_FOUND = 'Backend cluster not found'
_l('Backend cluster not found')
BACKEND_NODE_NOT_FOUND = 'Backend node not found'
_l('Backend node not found')
BACKEND_RESOURCE_NOT_FOUND = 'Backend resource not found'
_l('Backend resource not found')
BACKEND_CONNECTION_LOST = 'Backend connection lost'
_l('Backend connection lost')
BACKEND_CONNECT_FAILED = 'Failed to connect to backend'
_l('Failed to connect to backend')
BACKEND_TASK_TIMEOUT = 'Timeout when executing backend task'
_l('Timeout when executing backend task')
BACKEND_ERROR = 'Backend error occurred'
_l('Backend error occurred')
BACKEND_ACTION_UNSUPPORTED = 'Backend action unsupported'
_l('Backend action unsupported')
BACKEND_BAD_REQUEST = 'Backend bad request'
_l('Backend bad request')
BACKEND_DEFAULT_NET_NOT_FOUND = 'Backend default network not found'
_l('Backend default network not found')

NETWORK_NAME_INVALID = 'Network name invalid'
_l('Network name invalid')

NET_IP_NOT_FOUND = 'Network IP not found'
_l('Network IP not found')
NET_IP_IN_USE = 'Network IP in use'
_l('Network IP in use')
NET_IP_ADDRESS_INVALID = 'Network IP address invalid'
_l('Network IP address invalid')
NET_IP_VERSION_INVALID = 'Network IP version invalid'
_l('Network IP version invalid')
NET_IP_STATUS_INVALID = 'Network IP status invalid'
_l('Network IP status invalid')
NET_IP_OUT_OF_POOL = 'Network IP is out of pools'
_l('Network IP is out of pools')
NET_IP_POOL_INVALID = 'Network IP pools invalid'
_l('Network IP pools invalid')
NET_IP_POOL_EXHAUSTED = 'Network IP pools exhausted'
_l('Network IP pools exhausted')
NET_IP_CREATE_FAILED = 'Failed to create IP in database'
_l('Failed to create IP in database')
NET_IP_UPDATE_FAILED = 'Failed to update IP in database'
_l('Failed to update IP in database')
NET_IP_DELETE_FAILED = 'Failed to delete IP in database'
_l('Failed to delete IP in database')

NET_NOT_FOUND = 'Network not found'
_l('Network not found')
NET_INVALID = 'Network invalid'
_l('Network invalid')
NET_GET_FAILED = 'Failed to get Network'
_l('Failed to get Network')
NET_CREATE_FAILED = 'Failed to create Network'
_l('Failed to create Network')
NET_UPDATE_FAILED = 'Failed to update Network'
_l('Failed to update Network')
NET_DELETE_FAILED = 'Failed to delete Network'
_l('Failed to delete Network')
NET_NAME_INVALID = 'Network name invalid'
_l('Network name invalid')

SUBNET_NOT_FOUND = 'Subnet not found'
_l('Subnet not found')
SUBNET_INVALID = 'Subnet invalid'
_l('Subnet invalid')
SUBNET_CIDR_INVALID = 'Subnet CIDR invalid'
_l('Subnet CIDR invalid')
SUBNET_POOL_INVALID = 'Subnet pools invalid'
_l('Subnet pools invalid')
SUBNET_GATEWAY_INVALID = 'Subnet gateway invalid'
_l('Subnet gateway invalid')
SUBNET_GET_FAILED = 'Failed to get Subnet'
_l('Failed to get Network')
SUBNET_CREATE_FAILED = 'Failed to create Subnet'
_l('Failed to create Subnet')
SUBNET_UPDATE_FAILED = 'Failed to update Subnet'
_l('Failed to update Network')
SUBNET_DELETE_FAILED = 'Failed to delete Subnet'
_l('Failed to delete Subnet')
SUBNET_NAME_INVALID = 'Subnet name invalid'
_l('Subnet name invalid')

ROUTER_NOT_FOUND = 'Router not found'
_l('Router not found')
ROUTER_INVALID = 'Router invalid'
_l('ROUTER invalid')
ROUTER_GATEWAY_INVALID = 'Router gateway invalid'
_l('Router gateway invalid')
ROUTER_GET_FAILED = 'Failed to get Router'
_l('Failed to get Network')
ROUTER_CREATE_FAILED = 'Failed to create Router'
_l('Failed to create Router')
ROUTER_UPDATE_FAILED = 'Failed to update Router'
_l('Failed to update Network')
ROUTER_DELETE_FAILED = 'Failed to delete Router'
_l('Failed to delete Router')
ROUTER_NAME_INVALID = 'Router name invalid'
_l('Router name invalid')

KEYPAIR_NOT_FOUND = 'Keypair not found'
_l('Keypair not found')
KEYPAIR_INVALID = 'Keypair invalid'
_l('Keypair invalid')
KEYPAIR_GET_FAILED = 'Failed to get Keypair'
_l('Failed to get Keypair')
KEYPAIR_CREATE_FAILED = 'Failed to create Keypair'
_l('Failed to create Keypair')
KEYPAIR_UPDATE_FAILED = 'Failed to update Keypair'
_l('Failed to update Keypair')
KEYPAIR_DELETE_FAILED = 'Failed to delete Keypair'
_l('Failed to delete Keypair')
KEYPAIR_NAME_INVALID = 'Keypair name invalid'
_l('Keypair name invalid')

LB_NOT_FOUND = 'LB not found'
_l('LB not found')
LB_INVALID = 'LB invalid'
_l('LB invalid')
LB_GET_FAILED = 'Failed to get LB'
_l('Failed to get LB')
LB_CREATE_FAILED = 'Failed to create LB'
_l('Failed to create LB')
LB_UPDATE_FAILED = 'Failed to update LB'
_l('Failed to update LB')
LB_DELETE_FAILED = 'Failed to delete LB'
_l('Failed to delete LB')
LB_NAME_INVALID = 'LB name invalid'
_l('LB name invalid')

LISTENER_NOT_FOUND = 'Listener not found'
_l('Listener not found')
LISTENER_INVALID = 'Listener invalid'
_l('Listener invalid')
LISTENER_GET_FAILED = 'Failed to get listener'
_l('Failed to get listener')
LISTENER_CREATE_FAILED = 'Failed to create listener'
_l('Failed to create listener')
LISTENER_UPDATE_FAILED = 'Failed to update listener'
_l('Failed to update listener')
LISTENER_DELETE_FAILED = 'Failed to delete listener'
_l('Failed to delete listener')
LISTENER_NAME_INVALID = 'Listener name invalid'
_l('Listener name invalid')

POOL_NOT_FOUND = 'Pool not found'
_l('Pool not found')
POOL_INVALID = 'Pool invalid'
_l('Pool invalid')
POOL_GET_FAILED = 'Failed to get pool'
_l('Failed to get pool')
POOL_CREATE_FAILED = 'Failed to create pool'
_l('Failed to create pool')
POOL_UPDATE_FAILED = 'Failed to update pool'
_l('Failed to update pool')
POOL_DELETE_FAILED = 'Failed to delete pool'
_l('Failed to delete pool')
POOL_NAME_INVALID = 'Pool name invalid'
_l('Pool name invalid')

POOL_MEMBER_NOT_FOUND = 'Pool member not found'
_l('Pool member not found')
POOL_MEMBER_INVALID = 'Pool member invalid'
_l('Pool member invalid')
POOL_MEMBER_GET_FAILED = 'Failed to get Pool member'
_l('Failed to get Pool member')
POOL_MEMBER_CREATE_FAILED = 'Failed to create Pool member'
_l('Failed to create Pool member')
POOL_MEMBER_UPDATE_FAILED = 'Failed to update Pool member'
_l('Failed to update Pool member')
POOL_MEMBER_DELETE_FAILED = 'Failed to delete Pool member'
_l('Failed to delete Pool member')
POOL_MEMBER_NAME_INVALID = 'Pool member name invalid'
_l('Pool member name invalid')

MONITOR_NOT_FOUND = 'Monitor not found'
_l('Monitor not found')
MONITOR_INVALID = 'Monitor invalid'
_l('Monitor invalid')
MONITOR_GET_FAILED = 'Failed to get Monitor'
_l('Failed to get Monitor')
MONITOR_CREATE_FAILED = 'Failed to create Monitor'
_l('Failed to create Monitor')
MONITOR_UPDATE_FAILED = 'Failed to update Monitor'
_l('Failed to update Monitor')
MONITOR_DELETE_FAILED = 'Failed to delete Monitor'
_l('Failed to delete Monitor')
MONITOR_NAME_INVALID = 'Monitor name invalid'
_l('Monitor name invalid')

L7POLICY_NOT_FOUND = 'L7policy not found'
_l('L7policy not found')
L7POLICY_INVALID = 'L7policy invalid'
_l('L7policy invalid')
L7POLICY_GET_FAILED = 'Failed to get L7policy'
_l('Failed to get L7policy')
L7POLICY_CREATE_FAILED = 'Failed to create L7policy'
_l('Failed to create L7policy')
L7POLICY_UPDATE_FAILED = 'Failed to update L7policy'
_l('Failed to update L7policy')
L7POLICY_DELETE_FAILED = 'Failed to delete L7policy'
_l('Failed to delete L7policy')
L7POLICY_NAME_INVALID = 'L7policy name invalid'
_l('L7policy name invalid')

L7POLICY_RULE_NOT_FOUND = 'L7policy rule not found'
_l('L7policy rule not found')
L7POLICY_RULE_INVALID = 'L7policy rule invalid'
_l('L7policy rule invalid')
L7POLICY_RULE_GET_FAILED = 'Failed to get L7policy rule'
_l('Failed to get L7policy rule')
L7POLICY_RULE_CREATE_FAILED = 'Failed to create L7policy rule'
_l('Failed to create L7policy rule')
L7POLICY_RULE_UPDATE_FAILED = 'Failed to update L7policy rule'
_l('Failed to update L7policy rule')
L7POLICY_RULE_DELETE_FAILED = 'Failed to delete L7policy rule'
_l('Failed to delete L7policy rule')
L7POLICY_RULE_NAME_INVALID = 'L7policy rule name invalid'
_l('L7policy rule name invalid')

MAGNUM_CLUSTER_NOT_FOUND = 'Magnum cluster not found'
_l('Magnum cluster not found')
MAGNUM_CLUSTER_INVALID = 'Magnum cluster invalid'
_l('Magnum cluster invalid')
MAGNUM_CLUSTER_GET_FAILED = 'Failed to get Magnum cluster'
_l('Failed to get MAGNUM cluster')
MAGNUM_CLUSTER_CREATE_FAILED = 'Failed to create Magnum cluster'
_l('Failed to create Magnum cluster')
MAGNUM_CLUSTER_UPDATE_FAILED = 'Failed to update Magnum cluster'
_l('Failed to update Magnum cluster')
MAGNUM_CLUSTER_DELETE_FAILED = 'Failed to delete Magnum cluster'
_l('Failed to delete MAGNUM cluster')
MAGNUM_CLUSTER_NAME_INVALID = 'Magnum cluster name invalid'
_l('Magnum clusterr name invalid')

MAGNUM_CLUSTER_TEMPLATE_NOT_FOUND = 'Magnum cluster template not found'
_l('Magnum cluster template not found')
MAGNUM_CLUSTER_TEMPLATE_INVALID = 'Magnum cluster template invalid'
_l('Magnum cluster template invalid')
MAGNUM_CLUSTER_TEMPLATE_GET_FAILED = 'Failed to get Magnum cluster template'
_l('Failed to get Magnum cluster template')
MAGNUM_CLUSTER_TEMPLATE_CREATE_FAILED = 'Failed to create Magnum cluster template'
_l('Failed to create Magnum cluster template')
MAGNUM_CLUSTER_TEMPLATE_UPDATE_FAILED = 'Failed to update Magnum cluster template'
_l('Failed to update Magnum CLUSTEcluster cluster template')
MAGNUM_CLUSTER_TEMPLATE_DELETE_FAILED = 'Failed to delete Magnum cluster template'
_l('Failed to delete Magnum cluster template')
MAGNUM_CLUSTER_TEMPLATE_NAME_INVALID = 'Magnum cluster template name invalid'
_l('Magnum cluster template name invalid')

DATASTORE_NOT_FOUND = 'Datastore not found'
_l('Datastore not found')
DATASTORE_INVALID = 'Datastore invalid'
_l('Datastore invalid')
DATASTORE_GET_FAILED = 'Failed to get Datastore'
_l('Failed to get Datastore')
DATASTORE_CREATE_FAILED = 'Failed to create Datastore'
_l('Failed to create Datastore')
DATASTORE_UPDATE_FAILED = 'Failed to update Datastore'
_l('Failed to update Datastore')
DATASTORE_DELETE_FAILED = 'Failed to delete Datastore'
_l('Failed to delete Datastore')
DATASTORE_NAME_INVALID = 'Datastore name invalid'
_l('Datastore name invalid')

DATASTORE_VERSION_NOT_FOUND = 'Datastore version not found'
_l('Datastore version not found')
DATASTORE_VERSION_INVALID = 'Datastore version invalid'
_l('Datastore version invalid')
DATASTORE_VERSION_GET_FAILED = 'Failed to get Datastore version'
_l('Failed to get Datastore version')
DATASTORE_VERSION_CREATE_FAILED = 'Failed to create Datastore version'
_l('Failed to create Datastore version')
DATASTORE_VERSION_UPDATE_FAILED = 'Failed to update Datastore version'
_l('Failed to update Datastore version')
DATASTORE_VERSION_DELETE_FAILED = 'Failed to delete Datastore version'
_l('Failed to delete Datastore version')
DATASTORE_VERSION_NAME_INVALID = 'Datastore version name invalid'
_l('Datastore version name invalid')

DB_CLUSTER_NOT_FOUND = 'Trove cluster not found'
_l('Trove cluster not found')
DB_CLUSTER_INVALID = 'Trove cluster invalid'
_l('Trove cluster invalid')
DB_CLUSTER_GET_FAILED = 'Failed to get Trove cluster'
_l('Failed to get Trove cluster')
DB_CLUSTER_CREATE_FAILED = 'Failed to create Trove cluster'
_l('Failed to create Trove cluster')
DB_CLUSTER_UPDATE_FAILED = 'Failed to update Trove cluster'
_l('Failed to update Trove cluster')
DB_CLUSTER_DELETE_FAILED = 'Failed to delete Trove cluster'
_l('Failed to delete Trove cluster')
DB_CLUSTER_NAME_INVALID = 'Trove cluster name invalid'
_l('Trove cluster name invalid')

DB_INSTANCE_NOT_FOUND = 'Trove instance not found'
_l('Trove instance not found')
DB_INSTANCE_INVALID = 'Trove instance invalid'
_l('Trove instance invalid')
DB_INSTANCE_GET_FAILED = 'Failed to get Trove instance'
_l('Failed to get Trove instance')
DB_INSTANCE_CREATE_FAILED = 'Failed to create Trove instance'
_l('Failed to create Trove instance')
DB_INSTANCE_UPDATE_FAILED = 'Failed to update Trove instance'
_l('Failed to update Trove instance')
DB_INSTANCE_DELETE_FAILED = 'Failed to delete Trove instance'
_l('Failed to delete Trove instance')
DB_INSTANCE_NAME_INVALID = 'Trove instance name invalid'
_l('Trove instance name invalid')

DB_BACKUP_NOT_FOUND = 'Db backup not found'
_l('Db backup not found')
DB_BACKUP_INVALID = 'Db backup invalid'
_l('Db backup invalid')
DB_BACKUP_GET_FAILED = 'Failed to get Db backup'
_l('Failed to get Db backup')
DB_BACKUP_CREATE_FAILED = 'Failed to create Db backup'
_l('Failed to create Db backup')
DB_BACKUP_UPDATE_FAILED = 'Failed to update Db backup'
_l('Failed to update Db backup')
DB_BACKUP_DELETE_FAILED = 'Failed to delete Db backup'
_l('Failed to delete Db backup')
DB_BACKUP_NAME_INVALID = 'Db backup name invalid'
_l('Db backupr name invalid')


IP_INVALID = 'IP invalid'
_l('IP invalid')

NETBOX_IP_CREATE_FAILED = 'Failed to create IP in Netbox'
_l('Failed to create IP in Netbox')
NETBOX_IP_DELETE_FAILED = 'Failed to delete IP in Netbox'
_l('Failed to delete IP in Netbox')

MAIL_ACTIVATION_SEND_FAILED = 'Failed to send activation e-mail'
_l('Failed to send activation e-mail')
MAIL_RESET_PASSWORD_SEND_FAILED = 'Failed to send reset password e-mail'
_l('Failed to send reset password e-mail')
MAIL_ORDER_COMPLETE_SEND_FAILED = 'Failed to send order complete e-mail'
_l('Failed to send order complete e-mail')

UNKNOWN_ERROR = 'Unknown error'
_l('Unknown error')

METHOD_NOT_SUPPORTED = 'Method is not supported'
_l('Method is not supported')

class Error(Exception):
    def __init__(self, code=None, message=None, cause=None):
        super().__init__()
        self.code = code
        self.message = message
        self.cause = cause

    def get_message(self, localized=True, with_cause=True):
        msg = _l(self.message) if localized else self.message
        if self.code is not None:
            msg = msg + '. Code ' + str(self.code)
        if with_cause and self.cause is not None:
            msg = msg + '. Reason: ' + str(self.cause)
        return msg

    def __str__(self):
        return self.get_message(localized=False)

    def __repr__(self):
        return self.get_message(localized=False)

    def to_json(self):
        result = {
            'message': _l(self.message),
            'code': str(self.code) if self.code else self.message,
        }
        if self.cause:
            result['cause'] = str(self.cause)
        return result
