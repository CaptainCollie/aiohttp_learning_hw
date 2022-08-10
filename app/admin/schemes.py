from marshmallow import Schema, fields

from app.web.schemes import OkResponseSchema


class AdminSchema(Schema):
    email = fields.Str(required=True)
    password = fields.Str()


class AdminResponseSchema(Schema):
    id = fields.Integer()
    email = fields.Str()


class AdminOkResponseSchema(OkResponseSchema):
    data = fields.Nested(AdminResponseSchema)
