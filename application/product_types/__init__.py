#
# Copyright (c) 2020 FTI-CAS
#

from application import app
from application.base import errors
from application import models as md
from application.product_types.operating_system import OSType as OSTypeClass
from application.product_types.compute_os import OSCompute as ComputeTypeClass
from application.product_types.network_os import OSNetwork as NetworkTypeClass
from application.product_types.project_os import OSProject as ProjectTypeClass
from application.product_types.keypair_os import OSKeypair as KeypairTypeClass
from application.product_types.lbaas_os import OSLbaas as LbaasTypeClass
from application.product_types.magnum_os import OSMagnum as MagnumTypeClass
from application.product_types.database_os import OSDatabase as TroveTypeClass

LOG = app.logger


PRODUCT_TYPES = {
    # OS
    md.ProductType.OS: OSTypeClass(),
    # COMPUTE
    md.ProductType.COMPUTE: ComputeTypeClass(),
    # NETWORK
    md.ProductType.NETWORK: NetworkTypeClass(),
    # PROJECT
    md.ProductType.PROJECT: ProjectTypeClass(),
    # NETWORK
    md.ProductType.KEY_PAIR: KeypairTypeClass(),
    # LBAAS
    md.ProductType.LBAAS: LbaasTypeClass(),
    # Octavia
    md.ProductType.MAGNUM: MagnumTypeClass(),
    # Trove
    md.ProductType.DATABASE: TroveTypeClass(),
}


def get_product_type(ctx, product_type=None, check_support=True):
    """
    Get product type for the type.
    :param ctx:
    :param product_type: one of md.ProductType values
    :param check_support:
    :return:
    """
    data = ctx.data
    product_type = product_type or data['product_type']
    check_support = check_support if check_support is not None else data['check_support']

    prod_type = PRODUCT_TYPES.get(product_type)
    if not prod_type:
        ctx.set_error(errors.PRODUCT_TYPE_NOT_FOUND, status=404)
        return

    if check_support and not prod_type.supported:
        ctx.set_error(errors.PRODUCT_TYPE_NOT_SUPPORTED, status=406)
        return

    ctx.response = {
        'product_type': prod_type,
    }
    return prod_type


def get_product_types(ctx):
    """
    Get multiple product types.
    :param ctx:
    :return:
    """
    product_types = []
    for k, v in PRODUCT_TYPES.items():
        product_types.append({
            'type': k.lower(),
            'supported': v.supported,
        })
    ctx.response = {
        'data': product_types,
        'has_more': False,
    }
    return product_types


def create_product_type(ctx):
    """
    Create product type.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)


def update_product_type(ctx):
    """
    Update product type.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)


def delete_product_type(ctx):
    """
    Delete product type.
    :param ctx:
    :return:
    """
    ctx.set_error('Not Implemented Yet', status=500)
