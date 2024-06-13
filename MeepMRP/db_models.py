from datetime import datetime
from pony.orm import *


db = Database()


class User(db.Entity):
    id = PrimaryKey(int, auto=True)
    username = Optional(str)
    user_groups = Set('UserGroup')
    ecos = Set('Eco', reverse='author')
    eco_approvals = Set('Eco', reverse='approvals')
    posts = Set('Post')
    password_hash = Optional(str)


class BasePart(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    description = Optional(str)
    files = Set('File', reverse='base_parts')
    link = Optional(str)
    thumbnail = Required('File', reverse='base_part_thumbnails')
    units = Optional(str)


class File(db.Entity):
    id = PrimaryKey(int, auto=True)
    hash = Optional(str)
    base_parts = Set(BasePart, reverse='files')
    base_part_thumbnails = Set(BasePart, reverse='thumbnail')


class PartRevision(BasePart):
    part = Required('Part')
    bom_item = Optional('BomItem', reverse='part_revision')
    bom = Set('BomItem', reverse='part_revisions')
    revision = Optional(str)
    released = Optional(bool)
    eco_original = Set('EcoChange', reverse='current')
    eco = Optional('EcoChange', reverse='new')
    manufacturer_parts = Set('ManufacturerPart')
    stock_items = Set('StockItem')


class Part(db.Entity):
    id = PrimaryKey(int, auto=True)
    part_number = Optional(str)
    part_revisions = Set(PartRevision)
    tags = Set('Tag')
    reviewers = Set('UserGroup')


class Tag(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    parts = Set(Part)


class UserGroup(db.Entity):
    id = PrimaryKey(int, auto=True)
    users = Set(User)
    parts = Set(Part)


class BomItem(db.Entity):
    id = PrimaryKey(int, auto=True)
    part_revision = Required(PartRevision, reverse='bom_item')
    quantity = Optional(int)
    part_revisions = Set(PartRevision, reverse='bom')


class Eco(db.Entity):
    id = PrimaryKey(int, auto=True)
    eco_number = Optional(str)
    name = Optional(str)
    description = Optional(str)
    author = Required(User, reverse='ecos')
    draft = Optional(bool)
    approvals = Set(User, reverse='eco_approvals')
    changes = Set('EcoChange')
    posts = Set('Post')


class ManufacturerPart(BasePart):
    manufacturer = Required('ProVendor')
    mpn = Optional(str)
    vendor_parts = Set('VendorPart')
    part_revisions = Set(PartRevision)


class ProVendor(BasePart):
    phone = Optional(str)
    manufacturer_parts = Set(ManufacturerPart)
    vendor_parts = Set('VendorPart')


class VendorPart(BasePart):
    pro_vendor = Required(ProVendor)
    vpn = Optional(str)
    manufacturer_part = Required(ManufacturerPart)


class EcoChange(db.Entity):
    id = PrimaryKey(int, auto=True)
    current = Required(PartRevision, reverse='eco_original')
    new = Required(PartRevision, reverse='eco')
    eco = Required(Eco)


class Post(db.Entity):
    id = PrimaryKey(int, auto=True)
    date = Optional(datetime)
    contents = Optional(str)
    author = Required(User)
    eco = Required(Eco)


class StockItem(db.Entity):
    id = PrimaryKey(int, auto=True)
    quantity = Optional(str)
    part = Required(PartRevision)
    location = Required('StockLocation')


class StockLocation(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    parent = Required('StockLocation', reverse='children')
    children = Set('StockLocation', reverse='parent')
    stock_items = Set(StockItem)

set_sql_debug(True)

db.bind(provider="sqlite", filename="database.sqlite", create_db=True)

db.generate_mapping(create_tables=True)