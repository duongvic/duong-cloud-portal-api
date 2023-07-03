#
# Copyright (c) 2020 FTI-CAS
#

from shade import exc

from application import app

LOG = app.logger


class OSImageMixin(object):

    def create_image(self, name, filename=None, container='images',
                     md5=None, sha256=None, disk_format=None,
                     container_format=None, disable_vendor_agent=True,
                     wait=False, timeout=3600, allow_duplicates=False, meta=None,
                     volume=None, **kwargs):
        """
        Upload an image.

        :param name:
        :param filename:
        :param container:
        :param md5:
        :param sha256:
        :param disk_format:
        :param container_format:
        :param disable_vendor_agent:
        :param wait:
        :param timeout:
        :param allow_duplicates:
        :param meta:
        :param volume:
        :param kwargs:
        :returns: Image id
        """
        try:
            image_id = self.client.get_image_id(name)
            if image_id is not None:
                return None, image_id
            else:
                LOG.info("Creating image '%s'", name)
                image = self.client.create_image(
                    name, filename=filename, container=container, md5=md5, sha256=sha256,
                    disk_format=disk_format, container_format=container_format,
                    disable_vendor_agent=disable_vendor_agent, wait=wait, timeout=timeout,
                    allow_duplicates=allow_duplicates, meta=meta, volume=volume, **kwargs)
                return None, image["id"]
        except exc.OpenStackCloudException as e:
            LOG.error("Error [create_image(%s)]: %s.", name, e.orig_message)
            return self.fail(e)

    def delete_image(self, image_id, wait=False, timeout=3600, delete_objects=True):
        """
        Delete Image

        :param image_id
        :param wait
        :param timeout
        :param delete_objects
        :return
        """
        try:
            image = self.client.delete_image(image_id, wait=wait, timeout=timeout,
                                             delete_objects=delete_objects)
            return self.parse(image)
        except exc.OpenStackCloudException as e:
            LOG.error("Error [delete_image(%s)]: %s.", image_id, e.orig_message)
            return self.fail(e)

    def list_images(self, listing={}):
        try:
            images = self.client.list_images()
            return self.parse(images, **listing)
        except exc.OpenStackCloudException as e:
            LOG.error("Error [list_images()]: %s.", e.orig_message)
            return self.fail(e)
