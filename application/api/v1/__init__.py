#
# Copyright (c) 2020 FTI-CAS
#


from flask import Blueprint, request
from flask_restful import Api

from application import app
from application.api.v1 import (base, api_docs, admin, compute, config, history, network, order,
                                os_cluster, payment, billing, product, product_type, promotion, region,
                                report, support, task, user, keypair, lbaas, magnum, database)

api_auth = base.auth
bp_v1 = Blueprint('api_v1', __name__)


def before_request():
    if base.maintenance and not request.path.endswith('/maintenance'):
        return 'Sorry, off for maintenance!', 503


bp_v1.before_request(before_request)

api_v1 = Api(bp_v1)
app.register_blueprint(bp_v1, url_prefix='/api/v1')

#
# API DOCS
#
api_v1.add_resource(api_docs.ApiDocs, '/docs', endpoint='api_docs')

#
# ADMIN
#
api_v1.add_resource(admin.Maintenance, '/maintenance', endpoint='admin_maintenance')
api_v1.add_resource(admin.ModelObjects, '/admin/models/<model_class>', endpoint='admin_model_objects')
api_v1.add_resource(admin.ModelObject, '/admin/model/<model_class>', endpoint='admin_model_object')
api_v1.add_resource(admin.ServerActions, '/admin/server', endpoint='server_actions')
api_v1.add_resource(admin.Utilities, '/admin/utils', endpoint='admin_utils')

#
# CONFIGS
#
api_v1.add_resource(config.Configs, '/configs', endpoint='configs')
api_v1.add_resource(config.Config, '/config/<int:config_id>', endpoint='config')

#
# HISTORIES
#
api_v1.add_resource(history.Histories, '/histories', endpoint='histories')
api_v1.add_resource(history.History, '/history/<int:history_id>', endpoint='history')

#
# REPORTS
#
api_v1.add_resource(report.Reports, '/reports', endpoint='reports')
api_v1.add_resource(report.Report, '/report/<int:report_id>', endpoint='report')

#
# SUPPORT
#
api_v1.add_resource(support.Tickets, '/support/tickets', endpoint='support_tickets')
api_v1.add_resource(support.Ticket, '/support/ticket/<int:ticket_id>', endpoint='support_ticket')
api_v1.add_resource(support.Supports, '/support/assignments', endpoint='support_assignments')
api_v1.add_resource(support.Support, '/support/assignments/<int:support_id>', endpoint='support_assignment')

#
# USERS
#
api_v1.add_resource(user.Users, '/users', endpoint='users')
api_v1.add_resource(user.User, '/user', endpoint='user_self')
api_v1.add_resource(user.User, '/user/<int:user_id>', endpoint='user')
api_v1.add_resource(user.Auth, '/auth', endpoint='auth')
api_v1.add_resource(user.RefreshToken, '/refresh_token', endpoint='refresh_token')
api_v1.add_resource(user.Activate, '/activate', endpoint='activate')
api_v1.add_resource(user.ForgotPassword, '/forgot_password', endpoint='forgot_password')
api_v1.add_resource(user.ResetPassword, '/reset_password', endpoint='reset_password')

#
# PRODUCTS
#
api_v1.add_resource(product.Products, '/products', endpoint='products')
api_v1.add_resource(product.Product, '/product/<int:product_id>', endpoint='product')
api_v1.add_resource(product.Price, '/product_price', endpoint='product_price')

#
# PRODUCT TYPES
#
api_v1.add_resource(product_type.ProductTypes, '/product_types', endpoint='product_types')
api_v1.add_resource(product_type.ProductType, '/product_type/<product_type>', endpoint='product_type')

#
# ORDERS
#
api_v1.add_resource(order.Orders, '/orders', endpoint='orders')
api_v1.add_resource(order.Orders, '/user/<int:user_id>/orders', endpoint='user_orders')
api_v1.add_resource(order.Order, '/order/<int:order_id>', endpoint='order')
api_v1.add_resource(order.OrderRenew, '/order/<int:order_id>/renew', endpoint='order_renew')

#
# PAYMENTS
#
api_v1.add_resource(payment.Payments, '/payments', endpoint='payments')
api_v1.add_resource(payment.Payment, '/payment/<payment_type>', endpoint='payment')
api_v1.add_resource(payment.VNPayIPN, '/payment/vnpay_ipn', endpoint='payment_vnpay_ipn')

#
# BILLINGS
#
api_v1.add_resource(billing.Billings, '/billings', endpoint='billings')
api_v1.add_resource(billing.Billing, '/billing/<int:billing_id>', endpoint='billing')

#
# PROMOTIONS
#
api_v1.add_resource(promotion.Promotions, '/promotions', endpoint='promotions')
api_v1.add_resource(promotion.Promotion, '/promotion/<int:promotion_id>', endpoint='promotion')

#
# REGIONS
#
api_v1.add_resource(region.Regions, '/regions', endpoint='regions')
api_v1.add_resource(region.Region, '/region/<region_id>', endpoint='region')

#
# TASKS
#
api_v1.add_resource(task.Tasks, '/tasks', endpoint='tasks')
api_v1.add_resource(task.Task, '/task/<int:task_id>', endpoint='task')

#
# CLUSTERS
#
api_v1.add_resource(os_cluster.Clusters, '/os/clusters', endpoint='os_clusters')
api_v1.add_resource(os_cluster.Cluster, '/os/cluster/<cluster_id>', endpoint='os_cluster')

#
# NETWORKS
#
api_v1.add_resource(network.Networks, '/networks', endpoint='networks')
api_v1.add_resource(network.Network, '/network/<network_id>', endpoint='network')
api_v1.add_resource(network.Subnets, '/network/<network_id>/subnets', endpoint='subnets')
api_v1.add_resource(network.Subnet, '/network/<network_id>/subnet/<subnet_id>', endpoint='subnet')
api_v1.add_resource(network.Routers, '/routers', endpoint='routers')
api_v1.add_resource(network.Router, '/router/<router_id>', endpoint='router')
api_v1.add_resource(network.RouterInterfaces, '/router/<router_id>/interfaces', endpoint='interfaces')
api_v1.add_resource(network.RouterInterface, '/router/<router_id>/interface', endpoint='interface')
api_v1.add_resource(network.ComputeSecgroups, '/secgroups', endpoint='secgroups')
api_v1.add_resource(network.ComputeSecgroup, '/secgroup/<secgroup_id>', endpoint='secgroup')
api_v1.add_resource(network.ComputeSecgroupRules, '/secgroup/<secgroup_id>/rules', endpoint='secgroup_rules')
api_v1.add_resource(network.ComputeSecgroupRule, '/secgroup/<secgroup_id>/rule/<rule_id>', endpoint='secgroup_rule')

# LBAAS
api_v1.add_resource(lbaas.LBs, '/lbaas/lbs', endpoint='lbs')
api_v1.add_resource(lbaas.LB, '/lbaas/lb/<lb_id>', endpoint='lb')
api_v1.add_resource(lbaas.Listeners, '/lbaas/listeners', endpoint='listeners')
api_v1.add_resource(lbaas.Listener, '/lbaas/listener/<listener_id>', endpoint='listener')
api_v1.add_resource(lbaas.Pools, '/lbaas/pools', endpoint='pools')
api_v1.add_resource(lbaas.Pool, '/lbaas/pool/<pool_id>', endpoint='pool')
api_v1.add_resource(lbaas.PoolMembers, '/lbaas/pool/<pool_id>/members', endpoint='pool_memebers')
api_v1.add_resource(lbaas.PoolMember, '/lbaas/pool/<pool_id>/member/<member_id>', endpoint='pool_memeber')
api_v1.add_resource(lbaas.Monitors, '/lbaas/healthmonitors', endpoint='healthmonitors')
api_v1.add_resource(lbaas.Monitor, '/lbaas/healthmonitor/<monitor_id>', endpoint='healthmonitor')
api_v1.add_resource(lbaas.L7policies, '/lbaas/l7policies', endpoint='l7policies')
api_v1.add_resource(lbaas.L7policy, '/lbaas/l7policy/<l7policy_id>', endpoint='l7policy')
api_v1.add_resource(lbaas.L7Rules, '/lbaas/l7policy/<l7policy_id>/l7rules', endpoint='l7rules')
api_v1.add_resource(lbaas.L7Rule, '/lbaas/l7policy/<l7policy_id>/l7rule/<l7rule_id>', endpoint='l7rule')

# Magnum
api_v1.add_resource(magnum.Clusters, '/magnum/clusters', endpoint='clusters')
api_v1.add_resource(magnum.Cluster, '/magnum/cluster/<cluster_id>', endpoint='cluster')
api_v1.add_resource(magnum.ClusterTemplates, '/magnum/clustertemplates', endpoint='clustertemplates')
api_v1.add_resource(magnum.ClusterTemplate, '/magnum/clustertemplate/<template_id>', endpoint='clustertemplate')

# Trove
api_v1.add_resource(database.Datastores, '/database/datastores', endpoint='datastores')
api_v1.add_resource(database.Datastore, '/database/datastore/<datastore_id>', endpoint='datastore')
api_v1.add_resource(database.DatastoreVersions, '/database/datastore/<datastore_id>/versions', endpoint='db_versions')
api_v1.add_resource(database.DatastoreVersion, '/database/datastore/<datastore_id>/version/<version_id>', endpoint='db_version')
api_v1.add_resource(database.DBClusters, '/database/clusters', endpoint='db_clusters')
api_v1.add_resource(database.DBCluster, '/database/cluster/<db_cluster_id>', endpoint='db_cluster')
api_v1.add_resource(database.DBInstances, '/database/instances', endpoint='db_instances')
api_v1.add_resource(database.DBInstance, '/database/instance/<db_instance_id>', endpoint='db_instance')
api_v1.add_resource(database.DBBackups, '/database/instance/<db_instance_id>/backups', endpoint='db_backups')
api_v1.add_resource(database.DBBackup, '/database/instance/<db_instance_id>/backup/<db_backup_id>', endpoint='db_backup')
#
# COMPUTES
#

api_v1.add_resource(compute.Computes, '/computes', endpoint='computes')
api_v1.add_resource(compute.Compute, '/compute/<int:compute_id>', endpoint='compute')
api_v1.add_resource(compute.ComputeStatus, '/compute/<int:compute_id>/status', endpoint='compute_status')
api_v1.add_resource(compute.ComputeActions, '/compute/<int:compute_id>/actions', endpoint='compute_actions')
api_v1.add_resource(compute.ComputeAction, '/compute/<int:compute_id>/action', endpoint='compute_action')
api_v1.add_resource(compute.ComputeSnapshots, '/compute/<int:compute_id>/snapshots', endpoint='compute_snapshots')
api_v1.add_resource(compute.ComputeSnapshot, '/compute/<int:compute_id>/snapshot/<snapshot_id>', endpoint='compute_snapshot')
api_v1.add_resource(compute.ComputeBackupJobs, '/compute/<int:compute_id>/backup/jobs', endpoint='compute_backup_jobs')
api_v1.add_resource(compute.ComputeBackupJob, '/compute/<int:compute_id>/backup/job', endpoint='compute_backup_job')
api_v1.add_resource(compute.ComputeBackupFiles, '/compute/<int:compute_id>/backup/files', endpoint='compute_backup_files')
api_v1.add_resource(compute.ComputeBackupFile, '/compute/<int:compute_id>/backup/file/<backup_id>', endpoint='compute_backup_file')
api_v1.add_resource(compute.ComputeSecgroups, '/compute/<int:compute_id>/secgroups', endpoint='compute_secgroups')
api_v1.add_resource(compute.ComputeSecgroup, '/compute/<int:compute_id>/secgroup/<secgroup_id>', endpoint='compute_secgroup')
# api_v1.add_resource(compute.ComputeSecgroupRules, '/compute/<int:compute_id>/secgroup/<secgroup_id>/rules', endpoint='compute_secgroup_rules')
# api_v1.add_resource(compute.ComputeSecgroupRule, '/compute/<int:compute_id>/secgroup/<secgroup_id>/rule/<rule_id>', endpoint='compute_secgroup_rule')
api_v1.add_resource(compute.ComputeSSHKey, '/compute/ssh_key', endpoint='compute_ssh_key')

# KEYPAIR
api_v1.add_resource(keypair.KeyPairs, '/keypairs', endpoint='keypairs')
api_v1.add_resource(keypair.KeyPair, '/keypair/<keypair_id>', endpoint='keypair')

#
# TESTS
#
if app.config['DEBUG']:
    from application.api.v1 import test
    api_v1.add_resource(test.Test, '/test/<test_id>', endpoint='test')
