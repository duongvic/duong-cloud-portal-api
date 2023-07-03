#
# Copyright (c) 2020 FTI-CAS
#


class BaseType(object):
    @classmethod
    def is_valid(cls, value):
        return value in cls.all()


class UserType(BaseType):
    @staticmethod
    def all():
        return tuple()


class UserStatus(BaseType):
    ENABLED = 'ENABLED'
    DEACTIVATED = 'DEACTIVATED'
    BLOCKED = 'BLOCKED'
    DELETED = 'DELETED'

    @staticmethod
    def all():
        return 'ENABLED', 'DEACTIVATED', 'BLOCKED', 'DELETED'


class UserRole(BaseType):
    USER = 'USER'
    SALE = 'SALE'
    ADMIN_SALE = 'ADMIN_SALE'
    ADMIN_IT = 'ADMIN_IT'
    ADMIN = 'ADMIN'

    __role_values__ = {
        'USER': 1,
        'SALE': 10,
        'ADMIN_SALE': 20,
        'ADMIN_IT': 30,
        'ADMIN': 100,
    }

    @staticmethod
    def all():
        return 'USER', 'SALE', 'ADMIN_SALE', 'ADMIN_IT', 'ADMIN'

    @staticmethod
    def admin_all():
        return 'SALE', 'ADMIN_SALE', 'ADMIN_IT', 'ADMIN'

    @classmethod
    def is_admin(cls, role):
        all_admin = cls.admin_all()
        for r in role.split(','):
            if r.strip() in all_admin:
                return True
        return False

    @classmethod
    def is_valid(cls, role):
        all_roles = cls.all()
        for r in role.split(','):
            if r.strip() not in all_roles:
                return False
        return True

    @classmethod
    def compare(cls, role1, role2):
        if role1 == role2:
            return 0
        return cls.max_role_value(role1) - cls.max_role_value(role2)

    @classmethod
    def max_role_value(cls, role):
        roles = role.split(',')
        max_val = 0
        for r in roles:
            role_val = cls.__role_values__[r.strip()]
            if max_val < role_val:
                max_val = role_val
        return max_val

    @classmethod
    def admin_roles_of(cls, roles):
        result = []
        admin_all = cls.admin_all()
        for r in roles:
            if r in admin_all:
                result.append(r)
        return result


class ConfigurationType(BaseType):
    APP = 'APP'
    NETWORK_IP = 'NETWORK_IP'
    LAST_ID = 'LAST_ID'
    COMPUTE = 'COMPUTE'
    NETWORK = 'NETWORK'
    BACKEND = 'BACKEND'

    @staticmethod
    def all():
        return 'APP', 'NETWORK_IP', 'LAST_ID', 'COMPUTE', 'NETWORK', 'BACKEND'


class ConfigurationStatus(BaseType):
    ENABLED = 'ENABLED'
    DISABLED = 'DISABLED'

    @staticmethod
    def all():
        return 'ENABLED', 'DISABLED'


class HistoryAction(BaseType):
    CREATE_USER = 'CREATE_USER'
    UPDATE_USER = 'UPDATE_USER'
    DELETE_USER = 'DELETE_USER'
    ACTIVATE_USER = 'ACTIVATE_USER'
    RESET_USER_PASSWORD = 'RESET_USER_PASSWORD'
    LOGIN = 'LOGIN'
    LOGOUT = 'LOGOUT'

    CREATE_BALANCE = 'CREATE_BALANCE'
    UPDATE_BALANCE = 'UPDATE_BALANCE'
    DELETE_BALANCE = 'DELETE_BALANCE'

    CREATE_CONFIG = 'CREATE_CONFIG'
    UPDATE_CONFIG = 'UPDATE_CONFIG'
    DELETE_CONFIG = 'DELETE_CONFIG'

    CREATE_REGION = 'CREATE_REGION'
    UPDATE_REGION = 'UPDATE_REGION'
    DELETE_REGION = 'DELETE_REGION'

    CREATE_PRODUCT = 'CREATE_PRODUCT'
    UPDATE_PRODUCT = 'UPDATE_PRODUCT'
    DELETE_PRODUCT = 'DELETE_PRODUCT'

    CREATE_PRODUCT_TYPE = 'CREATE_PRODUCT_TYPE'
    UPDATE_PRODUCT_TYPE = 'UPDATE_PRODUCT_TYPE'
    DELETE_PRODUCT_TYPE = 'DELETE_PRODUCT_TYPE'

    CREATE_PROMOTION = 'CREATE_PROMOTION'
    UPDATE_PROMOTION = 'UPDATE_PROMOTION'
    DELETE_PROMOTION = 'DELETE_PROMOTION'

    CREATE_REPORT = 'CREATE_REPORT'
    UPDATE_REPORT = 'UPDATE_REPORT'
    DELETE_REPORT = 'DELETE_REPORT'

    CREATE_PAYMENT = 'CREATE_PAYMENT'
    UPDATE_PAYMENT = 'UPDATE_PAYMENT'
    DELETE_PAYMENT = 'DELETE_PAYMENT'
    FINISH_PAYMENT = 'FINISH_PAYMENT'

    CREATE_ORDER = 'CREATE_ORDER'
    UPDATE_ORDER = 'UPDATE_ORDER'
    DELETE_ORDER = 'DELETE_ORDER'
    RENEW_ORDER = 'RENEW_ORDER'
    APPROVE_ORDER = 'APPROVE_ORDER'
    COMPLETE_ORDER = 'COMPLETE_ORDER'

    CREATE_BILLING = 'CREATE_BILLING'
    UPDATE_BILLING = 'UPDATE_BILLING'
    DELETE_BILLING = 'DELETE_BILLING'

    CREATE_TICKET = 'CREATE_TICKET'
    UPDATE_TICKET = 'UPDATE_TICKET'
    DELETE_TICKET = 'DELETE_TICKET'

    CREATE_SUPPORT = 'CREATE_SUPPORT'
    UPDATE_SUPPORT = 'UPDATE_SUPPORT'
    DELETE_SUPPORT = 'DELETE_SUPPORT'

    CREATE_IP = 'CREATE_IP'
    UPDATE_IP = 'UPDATE_IP'
    DELETE_IP = 'DELETE_IP'

    CREATE_CLUSTER = 'CREATE_CLUSTER'
    UPDATE_CLUSTER = 'UPDATE_CLUSTER'
    DELETE_CLUSTER = 'DELETE_CLUSTER'

    PERFORM_COMPUTE_ACTION = 'PERFORM_COMPUTE_ACTION'

    CREATE_COMPUTE = 'CREATE_COMPUTE'
    UPDATE_COMPUTE = 'UPDATE_COMPUTE'
    DELETE_COMPUTE = 'DELETE_COMPUTE'
    SYNCHRONIZE_COMPUTE = 'SYNCHRONIZE_COMPUTE'
    MANAGE_COMPUTE = 'MANAGE_COMPUTE'

    CREATE_SNAPSHOT = 'CREATE_SNAPSHOT'
    UPDATE_SNAPSHOT = 'UPDATE_SNAPSHOT'
    DELETE_SNAPSHOT = 'DELETE_SNAPSHOT'
    ROLLBACK_SNAPSHOT = 'ROLLBACK_SNAPSHOT'

    CREATE_BACKUP_JOB = 'CREATE_BACKUP'
    UPDATE_BACKUP_JOB = 'UPDATE_BACKUP'
    DELETE_BACKUP_JOB = 'DELETE_BACKUP'

    CREATE_BACKUP_FILE = 'CREATE_BACKUP_FILE'
    UPDATE_BACKUP_FILE = 'UPDATE_BACKUP_FILE'
    DELETE_BACKUP_FILE = 'DELETE_BACKUP_FILE'
    ROLLBACK_BACKUP_FILE = 'ROLLBACK_BACKUP_FILE'

    CREATE_SECGROUP = 'CREATE_SECGROUP'
    UPDATE_SECGROUP = 'UPDATE_SECGROUP'
    DELETE_SECGROUP = 'DELETE_SECGROUP'

    CREATE_SECGROUP_RULE = 'CREATE_SECGROUP_RULE'
    UPDATE_SECGROUP_RULE = 'UPDATE_SECGROUP_RULE'
    DELETE_SECGROUP_RULE = 'DELETE_SECGROUP_RULE'

    CREATE_OS_USER = 'CREATE_OS_USER'
    UPDATE_OS_USER = 'UPDATE_OS_USER'
    DELETE_OS_USER = 'DELETE_OS_USER'

    CREATE_OS_PROJECT = 'CREATE_OS_PROJECT'
    UPDATE_OS_PROJECT = 'UPDATE_OS_PROJECT'
    DELETE_OS_PROJECT = 'DELETE_OS_PROJECT'

    CREATE_NETWORK = 'CREATE_NETWORK'
    UPDATE_NETWORK = 'UPDATE_NETWORK'
    DELETE_NETWORK = 'DELETE_NETWORK'

    CREATE_SUBNET = 'CREATE_SUBNET'
    UPDATE_SUBNET = 'UPDATE_SUBNET'
    DELETE_SUBNET = 'DELETE_SUBNET'

    CREATE_KEYPAIR = 'CREATE_KEYPAIR'
    UPDATE_KEYPAIR = 'UPDATE_KEYPAIR'
    DELETE_KEYPAIR = 'DELETE_KEYPAIR'

    CREATE_ROUTER = 'CREATE_ROUTER'
    UPDATE_ROUTER = 'UPDATE_ROUTER'
    DELETE_ROUTER = 'DELETE_ROUTER'

    CREATE_ROUTER_INTERFACE = 'CREATE_ROUTER_INTERFACE'
    UPDATE_ROUTER_INTERFACE = 'UPDATE_ROUTER_INTERFACE'
    DELETE_ROUTER_INTERFACE = 'DELETE_ROUTER_INTERFACE'

    CREATE_LB = 'CREATE_LB'
    UPDATE_LB = 'UPDATE_LB'
    DELETE_LB = 'DELETE_LB'

    CREATE_LISTENER = 'CREATE_LISTENER'
    UPDATE_LISTENER = 'UPDATE_LISTENER'
    DELETE_LISTENER = 'DELETE_LISTENER'

    CREATE_POOL = 'CREATE_POOL'
    UPDATE_POOL = 'UPDATE_POOL'
    DELETE_POOL = 'DELETE_POOL'

    CREATE_POOL_MEMBER = 'CREATE_POOL_MEMBER'
    UPDATE_POOL_MEMBER = 'UPDATE_POOL_MEMBER'
    DELETE_POOL_MEMBER = 'DELETE_POOL_MEMBER'

    CREATE_MONITOR = 'CREATE_MONITOR'
    UPDATE_MONITOR = 'UPDATE_MONITOR'
    DELETE_MONITOR = 'DELETE_MONITOR'

    CREATE_L7POLICY = 'CREATE_L7POLICY'
    UPDATE_L7POLICY = 'UPDATE_L7POLICY'
    DELETE_L7POLICY = 'DELETE_L7POLICY'

    CREATE_L7POLICY_RULE = 'CREATE_L7POLICY_RULE'
    UPDATE_L7POLICY_RULE = 'UPDATE_L7POLICY_RULE'
    DELETE_L7POLICY_RULE = 'DELETE_L7POLICY_RULE'

    CREATE_MAGNUM_CLUSTER = 'CREATE_MAGNUM_CLUSTER'
    UPDATE_MAGNUM_CLUSTER = 'UPDATE_MAGNUM_CLUSTER'
    DELETE_MAGNUM_CLUSTER = 'DELETE_MAGNUM_CLUSTER'

    CREATE_MAGNUM_CLUSTER_TEMPLATE = 'CREATE_MAGNUM_CLUSTER_TEMPLATE'
    UPDATE_MAGNUM_CLUSTER_TEMPLATE = 'UPDATE_MAGNUM_CLUSTER_TEMPLATE'
    DELETE_MAGNUM_CLUSTER_TEMPLATE = 'DELETE_MAGNUM_CLUSTER_TEMPLATE'

    CREATE_DB_CLUSTER = 'CREATE_DB_CLUSTER'
    UPDATE_DB_CLUSTER = 'UPDATE_DB_CLUSTER'
    DELETE_DB_CLUSTER = 'DELETE_DB_CLUSTER'

    CREATE_DB_DATASTORE = 'CREATE_DB_DATASTORE'
    UPDATE_DB_DATASTORE = 'UPDATE_DB_DATASTORE'
    DELETE_DB_DATASTORE = 'DELETE_DB_DATASTORE'

    CREATE_DB_DATASTORE_VERSION = 'CREATE_DB_DATASTORE_VERSION'
    UPDATE_DB_DATASTORE_VERSION = 'UPDATE_DB_DATASTORE_VERSION'
    DELETE_DB_DATASTORE_VERSION = 'DELETE_DB_DATASTORE_VERSION'

    CREATE_DB_INSTANCE = 'CREATE_DB_INSTANCE'
    UPDATE_DB_INSTANCE = 'UPDATE_DB_INSTANCE'
    DELETE_DB_INSTANCE = 'DELETE_DB_INSTANCE'

    CREATE_DB_BACKUP = 'CREATE_DB_BACKUP'
    UPDATE_DB_BACKUP = 'UPDATE_DB_BACKUP'
    DELETE_DB_BACKUP = 'DELETE_DB_BACKUP'

    # ADMIN only
    GET_MODEL_OBJECT = 'GET_MODEL_OBJECT'
    GET_MODEL_OBJECTS = 'GET_MODEL_OBJECTS'
    CREATE_MODEL_OBJECT = 'CREATE_MODEL_OBJECT'
    UPDATE_MODEL_OBJECT = 'UPDATE_MODEL_OBJECT'
    DELETE_MODEL_OBJECT = 'DELETE_MODEL_OBJECT'
    EXECUTE_SQL = 'EXECUTE_SQL'
    PERFORM_SERVER_ACTION = 'PERFORM_SERVER_ACTION'

    @staticmethod
    def all():
        return ('CREATE_USER', 'UPDATE_USER', 'DELETE_USER', 'ACTIVATE_USER', 'RESET_USER_PASSWORD', 'LOGIN', 'LOGOUT',
                'CREATE_BALANCE', 'UPDATE_BALANCE', 'DELETE_BALANCE',
                'CREATE_CONFIG', 'UPDATE_CONFIG', 'DELETE_CONFIG',
                'CREATE_REGION', 'UPDATE_REGION', 'DELETE_REGION',
                'CREATE_PRODUCT', 'UPDATE_PRODUCT', 'DELETE_PRODUCT',
                'CREATE_PRODUCT_TYPE', 'UPDATE_PRODUCT_TYPE', 'DELETE_PRODUCT_TYPE',
                'CREATE_PROMOTION', 'UPDATE_PROMOTION', 'DELETE_PROMOTION',
                'CREATE_REPORT', 'UPDATE_REPORT', 'DELETE_REPORT',
                'CREATE_PAYMENT', 'UPDATE_PAYMENT', 'DELETE_PAYMENT', 'FINISH_PAYMENT',
                'CREATE_ORDER', 'UPDATE_ORDER', 'DELETE_ORDER', 'RENEW_ORDER', 'APPROVE_ORDER', 'COMPLETE_ORDER',
                'CREATE_BILLING', 'UPDATE_BILLING', 'DELETE_BILLING',
                'CREATE_TICKET', 'UPDATE_TICKET', 'DELETE_TICKET',
                'CREATE_SUPPORT', 'UPDATE_SUPPORT', 'DELETE_SUPPORT',
                'CREATE_IP', 'UPDATE_IP', 'DELETE_IP',
                'CREATE_CLUSTER', 'UPDATE_CLUSTER', 'DELETE_CLUSTER',
                'PERFORM_COMPUTE_ACTION',
                'CREATE_COMPUTE', 'UPDATE_COMPUTE', 'DELETE_COMPUTE', 'SYNCHRONIZE_COMPUTE', 'MANAGE_COMPUTE',
                'CREATE_SNAPSHOT', 'UPDATE_SNAPSHOT', 'DELETE_SNAPSHOT', 'ROLLBACK_SNAPSHOT',
                'CREATE_BACKUP', 'UPDATE_BACKUP', 'DELETE_BACKUP',
                'CREATE_BACKUP_FILE', 'UPDATE_BACKUP_FILE', 'DELETE_BACKUP_FILE', 'ROLLBACK_BACKUP_FILE',
                'CREATE_SECGROUP', 'UPDATE_SECGROUP', 'DELETE_SECGROUP',
                'CREATE_SECGROUP_RULE', 'UPDATE_SECGROUP_RULE', 'DELETE_SECGROUP_RULE',
                'GET_MODEL_OBJECT', 'GET_MODEL_OBJECTS',
                'CREATE_MODEL_OBJECT', 'UPDATE_MODEL_OBJECT', 'DELETE_MODEL_OBJECT', 'EXECUTE_SQL',
                'PERFORM_SERVER_ACTION',
                'CREATE_OS_USER', 'UPDATE_OS_USER', 'DELETE_OS_USER',
                'CREATE_OS_PROJECT', 'UPDATE_OS_PROJECT', 'DELETE_OS_PROJECT',
                'CREATE_NETWORK', 'UPDATE_NETWORK', 'DELETE_NETWORK',
                'CREATE_SUBNET', 'UPDATE_SUBNET', 'DELETE_SUBNET',
                'CREATE_KEYPAIR', 'UPDATE_KEYPAIR', 'DELETE_KEYPAIR')


class HistoryType(BaseType):
    USER = 'USER'
    TASK = 'TASK'

    @staticmethod
    def all():
        return 'USER', 'TASK'


class HistoryStatus(BaseType):
    SUCCEEDED = 'SUCCEEDED'
    FAILED = 'FAILED'
    IN_PROGRESS = 'IN_PROGRESS'
    TIMED_OUT = 'TIMED_OUT'

    @staticmethod
    def all():
        return 'SUCCEEDED', 'FAILED', 'IN_PROGRESS', 'TIMED_OUT'


class TaskType(BaseType):
    BACKUP = 'BACKUP'
    CREATE = 'CREATE'
    SYNC = 'SYNC'

    @staticmethod
    def all():
        return 'BACKUP', 'CREATE', 'SYNC'


class TaskStatus(BaseType):
    ENABLED = 'ENABLED'
    DISABLED = 'DISABLED'
    COMPLETED = 'COMPLETED'
    CLOSED = 'CLOSED'

    @staticmethod
    def all():
        return 'ENABLED', 'DISABLED', 'COMPLETED', 'CLOSED'


class ReportType(BaseType):
    USER = 'USER'
    ORDER = 'ORDER'
    PRODUCT = 'PRODUCT'
    COMPUTE = 'COMPUTE'

    @staticmethod
    def all():
        return 'USER', 'ORDER', 'PRODUCT', 'COMPUTE'


class ReportStatus(BaseType):
    SUCCEEDED = 'SUCCEEDED'
    FAILED = 'FAILED'

    @staticmethod
    def all():
        return 'SUCCEEDED', 'FAILED'


class ProductType(BaseType):
    COMPUTE = 'COMPUTE'
    OS = 'OS'
    NETWORK = 'NETWORK'
    PROJECT = 'PROJECT'
    KEY_PAIR = 'KEY_PAIR'
    LBAAS = 'LBAAS'
    MAGNUM = 'MAGNUM'
    DATABASE = 'DATABASE'

    @staticmethod
    def all():
        return 'COMPUTE', 'OS', 'NETWORK', 'PROJECT', 'KEY_PAIR', 'LBAAS', 'MAGNUM', 'DATABASE'


class ProductStatus(BaseType):
    ENABLED = 'ENABLED'
    DISABLED = 'DISABLED'

    @staticmethod
    def all():
        return 'ENABLED', 'DISABLED'


class RegionId(BaseType):
    VN_HN = 'VN_HN'
    VN_HCM = 'VN_HCM'
    VN_DN = 'VN_DN'

    @staticmethod
    def all():
        return 'VN_HN', 'VN_HCM', 'VN_DN'


class RegionStatus(BaseType):
    ENABLED = 'ENABLED'
    DISABLED = 'DISABLED'

    @staticmethod
    def all():
        return 'ENABLED', 'DISABLED'


class PromotionType(BaseType):
    DISCOUNT = 'DISCOUNT'
    TRIAL = 'TRIAL'

    @staticmethod
    def all():
        return 'DISCOUNT', 'TRIAL'


class PromotionStatus(BaseType):
    ENABLED = 'ENABLED'
    DISABLED = 'DISABLED'

    @staticmethod
    def all():
        return 'ENABLED', 'DISABLED'


class DiscountType(BaseType):
    RATIO = 'RATIO'
    FIXED = 'FIXED'

    @staticmethod
    def all():
        return 'RATIO', 'FIXED'


class OrderType(BaseType):
    BUY = 'BUY'
    TRIAL = 'TRIAL'

    @staticmethod
    def all():
        return 'BUY', 'TRIAL'


class OrderStatus(BaseType):
    CREATED = 'CREATED'
    APPROVED = 'APPROVED'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'
    CANCELLED = 'CANCELLED'
    PENDING = 'PENDING'
    DELETED = 'DELETED'

    @staticmethod
    def all():
        return 'CREATED', 'APPROVED', 'COMPLETED', 'FAILED', 'CANCELLED', 'PENDING', 'DELETED'


class PaymentType(BaseType):
    CASH = 'CASH'
    BANK_TRANSFER = 'BANK_TRANSFER'
    CREDIT_CARD = 'CREDIT_CARD'
    GATE_VNPAY = 'GATE_VNPAY'

    @staticmethod
    def all():
        return 'CASH', 'BANK_TRANSFER', 'CREDIT_CARD', 'GATE_VNPAY'


class PaymentStatus(BaseType):
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'
    CLOSED = 'CLOSED'

    @staticmethod
    def all():
        return 'COMPLETED', 'FAILED', 'CLOSED'


class BalanceType(BaseType):
    @staticmethod
    def all():
        return tuple()


class BalanceStatus(BaseType):
    ENABLED = 'ENABLED'
    BLOCKED = 'BLOCKED'
    DISABLED = 'DISABLED'

    @staticmethod
    def all():
        return 'ENABLED', 'BLOCKED', 'DISABLED'


class TicketType(BaseType):
    PRODUCT = 'PRODUCT'
    ORDER = 'ORDER'
    COMPUTE = 'COMPUTE'

    @staticmethod
    def all():
        return 'PRODUCT', 'ORDER', 'COMPUTE'


class TicketStatus(BaseType):
    CREATED = 'CREATED'
    PENDING = 'PENDING'
    COMPLETED = 'COMPLETED'
    CLOSED = 'CLOSED'

    @staticmethod
    def all():
        return 'CREATED', 'PENDING', 'COMPLETED', 'CLOSED'


class SupportType(BaseType):
    TICKET = 'TICKET'
    ORDER = 'ORDER'

    @staticmethod
    def all():
        return 'TICKET', 'ORDER'


class SupportStatus(BaseType):
    CREATED = 'CREATED'
    ACTIVE = 'ACTIVE'
    PENDING = 'PENDING'
    COMPLETED = 'COMPLETED'
    CLOSED = 'CLOSED'

    @staticmethod
    def all():
        return 'CREATED', 'ACTIVE', 'PENDING', 'COMPLETED', 'CLOSED'


class ComputeType(BaseType):
    VM = 'VM'
    CONTAINER = 'CONTAINER'
    BAREMETAL = 'BAREMETAL'

    @staticmethod
    def all():
        return 'VM', 'CONTAINER', 'BAREMETAL'


class ComputeStatus(BaseType):
    ENABLED = 'ENABLED'
    DISABLED = 'DISABLED'
    LOCKED = 'LOCKED'
    FAILED = 'FAILED'
    DELETED = 'DELETED'

    @staticmethod
    def all():
        return 'ENABLED', 'DISABLED', 'LOCKED', 'FAILED', 'DELETED'


class OSType(BaseType):
    LINUX = 'LINUX'
    WINDOWS = 'WINDOWS'
    UNIX = 'UNIX'

    @staticmethod
    def all():
        return 'LINUX', 'WINDOWS', 'UNIX'


class IPType(BaseType):
    @staticmethod
    def all():
        return tuple()


class IPVersion(BaseType):
    V4 = 4
    V6 = 6

    @staticmethod
    def all():
        return 4, 6


class IPStatus(BaseType):
    ASSIGNED = 'ASSIGNED'
    ASSIGNING = 'ASSIGNING'
    UNUSED = 'UNUSED'

    @staticmethod
    def all():
        return 'ASSIGNED', 'ASSIGNING', 'UNUSED'
