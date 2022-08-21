from app.web.schemes import OkResponseSchema
from marshmallow import Schema, fields


class ThemeSchema(Schema):
    id = fields.Int(required=False)
    title = fields.Str(required=True)

class AnswerSchema(Schema):
    title = fields.Str(required=True)
    is_correct = fields.Bool(required=True)


class QuestionSchema(Schema):
    id = fields.Int(required=False)
    title = fields.Str(required=True)
    theme_id = fields.Int(required=True)
    answers = fields.Nested(AnswerSchema, many=True)


class ThemeListSchema(Schema):
    themes = fields.Nested(ThemeSchema, many=True)


class ThemeListSchemaResponseSchema(OkResponseSchema):
    data = fields.Nested(ThemeListSchema)


class ThemeIdSchema(Schema):
    pass


class ListQuestionSchema(QuestionSchema):
    questions = fields.Nested(QuestionSchema, many=True)

class QuestionListSchemaResponseSchema(OkResponseSchema):
    data = fields.Nested(ListQuestionSchema)
