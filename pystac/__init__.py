"""
PySTAC is a library for working with SpatioTemporal Asset Catalogs (STACs)
"""

# flake8: noqa
from pystac.errors import (
    STACError,
    STACTypeError,
    ExtensionAlreadyExistsError,
    ExtensionNotImplemented,
    ExtensionTypeError,
    RequiredPropertyMissing,
    STACValidationError,
)

from typing import Any, Dict, Optional
from pystac.version import (
    __version__,
    get_stac_version,
    set_stac_version,
)
from pystac.media_type import MediaType
from pystac.rel_type import RelType
from pystac.stac_io import StacIO
from pystac.stac_object import STACObject, STACObjectType
from pystac.link import Link, HIERARCHICAL_LINKS
from pystac.catalog import Catalog, CatalogType
from pystac.collection import (
    Collection,
    Extent,
    SpatialExtent,
    TemporalExtent,
    Provider,
    Summaries,
)
from pystac.summaries import RangeSummary
from pystac.item import Item, Asset, CommonMetadata
from pystac.item_collection import ItemCollection

import pystac.validation

import pystac.extensions.hooks
import pystac.extensions.datacube
import pystac.extensions.eo
import pystac.extensions.file
import pystac.extensions.item_assets
import pystac.extensions.label
import pystac.extensions.pointcloud
import pystac.extensions.projection
import pystac.extensions.sar
import pystac.extensions.sat
import pystac.extensions.scientific
import pystac.extensions.timestamps
import pystac.extensions.version
import pystac.extensions.view

EXTENSION_HOOKS = pystac.extensions.hooks.RegisteredExtensionHooks(
    [
        pystac.extensions.datacube.DATACUBE_EXTENSION_HOOKS,
        pystac.extensions.eo.EO_EXTENSION_HOOKS,
        pystac.extensions.file.FILE_EXTENSION_HOOKS,
        pystac.extensions.item_assets.ITEM_ASSETS_EXTENSION_HOOKS,
        pystac.extensions.label.LABEL_EXTENSION_HOOKS,
        pystac.extensions.pointcloud.POINTCLOUD_EXTENSION_HOOKS,
        pystac.extensions.projection.PROJECTION_EXTENSION_HOOKS,
        pystac.extensions.sar.SAR_EXTENSION_HOOKS,
        pystac.extensions.sat.SAT_EXTENSION_HOOKS,
        pystac.extensions.scientific.SCIENTIFIC_EXTENSION_HOOKS,
        pystac.extensions.timestamps.TIMESTAMPS_EXTENSION_HOOKS,
        pystac.extensions.version.VERSION_EXTENSION_HOOKS,
        pystac.extensions.view.VIEW_EXTENSION_HOOKS,
    ]
)


def read_file(href: str) -> STACObject:
    """Reads a STAC object from a file.

    This method will return either a Catalog, a Collection, or an Item based on what the
    file contains.

    This is a convenience method for :meth:`STACObject.from_file <pystac.STACObject.from_file>`

    Args:
        href : The HREF to read the object from.

    Returns:
        The specific STACObject implementation class that is represented
        by the JSON read from the file located at HREF.

    Raises:
        STACTypeError : If the file at ``href`` does not represent a valid
            :class:`~pystac.STACObject`. Note that an :class:`~pystac.ItemCollection` is not
            a :class:`~pystac.STACObject` and must be read using
            :meth:`ItemCollection.from_file <pystac.ItemCollection.from_file>`
    """
    stac_io = StacIO.default()
    d = stac_io.read_json(href)
    typ = pystac.serialization.identify.identify_stac_object_type(d)

    if typ == STACObjectType.CATALOG:
        return Catalog.from_file(href)
    elif typ == STACObjectType.COLLECTION:
        return Collection.from_file(href)
    elif typ == STACObjectType.ITEM:
        return Item.from_file(href)
    else:
        raise STACTypeError(f"Cannot read file of type {typ}")


def write_file(
    obj: STACObject,
    include_self_link: bool = True,
    dest_href: Optional[str] = None,
) -> None:
    """Writes a STACObject to a file.

    This will write only the Catalog, Collection or Item ``obj``. It will not attempt
    to write any other objects that are linked to ``obj``; if you'd like functionality to
    save off catalogs recursively see :meth:`Catalog.save <pystac.Catalog.save>`.

    This method will write the JSON of the object to the object's assigned "self" link or
    to the dest_href if provided. To set the self link, see :meth:`STACObject.set_self_href
    <pystac.STACObject.set_self_href>`.

    Convenience method for :meth:`STACObject.from_file <pystac.STACObject.from_file>`

    Args:
        obj : The STACObject to save.
        include_self_link : If ``True``, include the ``"self"`` link with this object.
            Otherwise, leave out the self link.
        dest_href : Optional HREF to save the file to. If ``None``, the object will be
            saved to the object's ``"self"`` href.
    """
    obj.save_object(include_self_link=include_self_link, dest_href=dest_href)


def read_dict(
    d: Dict[str, Any],
    href: Optional[str] = None,
    root: Optional[Catalog] = None,
    stac_io: Optional[StacIO] = None,
) -> STACObject:
    """Reads a :class:`~STACObject` or :class:`~ItemCollection` from a JSON-like dict
    representing a serialized STAC object.

    This method will return either a :class:`~Catalog`, :class:`~Collection`,
    or :class`~Item` based on the contents of the dict.

    This is a convenience method for either
    :meth:`stac_io.stac_object_from_dict <stac_io.stac_object_from_dict>`.

    Args:
        d : The dict to parse.
        href : Optional href that is the file location of the object being
            parsed.
        root : Optional root of the catalog for this object.
            If provided, the root's resolved object cache can be used to search for
            previously resolved instances of the STAC object.
        stac_io: Optional :class:`~StacIO` instance to use for reading. If ``None``,
            the default instance will be used.

    Raises:
        STACTypeError : If the ``d`` dictionary does not represent a valid
            :class:`~pystac.STACObject`. Note that an :class:`~pystac.ItemCollection` is not
            a :class:`~pystac.STACObject` and must be read using
            :meth:`ItemCollection.from_dict <pystac.ItemCollection.from_dict>`
    """
    if stac_io is None:
        stac_io = StacIO.default()
    return stac_io.stac_object_from_dict(d, href, root)
