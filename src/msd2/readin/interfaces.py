import dataframely as dy


class MSDSchema(dy.Schema):
    apartment_id = dy.String(nullable=False)
    site_id = dy.Int64(nullable=False)
    building_id = dy.Int64(nullable=False)
    plan_id = dy.Int64(nullable=False)
    floor_id = dy.Int64(nullable=False)
    unit_id = dy.Float64(nullable=False)
    area_id = dy.Float64(nullable=True)
    unit_usage = dy.String(nullable=False)
    entity_type = dy.String(nullable=False)
    entity_subtype = dy.String(nullable=False)
    geom = dy.String(nullable=False)
    elevation = dy.Float64(nullable=False)
    height = dy.Float64(nullable=False)
    zoning = dy.String(nullable=False)
    roomtype = dy.String(nullable=False)
