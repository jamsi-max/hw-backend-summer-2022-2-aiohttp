from aiohttp_apispec import (docs,
                             request_schema,
                             response_schema)
from aiohttp.web_exceptions import (HTTPBadRequest,
                                    HTTPNotFound,
                                    HTTPConflict)

from app.quiz.schemes import (
    ListQuestionSchema,
    QuestionListSchemaResponseSchema,
    QuestionSchema,
    ThemeListSchemaResponseSchema,
    ThemeSchema,
)
from app.web.app import View
from app.web.schemes import OkResponseSchema
from app.web.utils import json_response, login_required


# TODO: добавить проверку авторизации для этого View
class ThemeAddView(View):
    # + TODO: добавить валидацию с помощью aiohttp-apispec и marshmallow-схем
    @login_required()
    @docs(
        tags=['VKBot'],
        summary='Adding a new theme',
        description='Add new theme in database'
    )
    @request_schema(ThemeSchema)
    @response_schema(OkResponseSchema, 200)
    async def post(self):
        # + TODO: заменить на self.data["title"] после внедрения валидации
        title = self.data.get("title")

        # + TODO: проверять, что не существует темы с таким же именем, отдавать 409 если существует
        if await self.request.app.store.quizzes.get_theme_by_title(title=title):
            raise HTTPConflict

        theme = await self.store.quizzes.create_theme(title=title)
        return json_response(data=ThemeSchema().dump(theme))


class ThemeListView(View):
    @login_required()
    @docs(
            tags=['VKBot'],
            summary='List all theme',
            description='List all theme from database'
        )
    @response_schema(ThemeListSchemaResponseSchema, 200)
    async def get(self):
        themes = await self.store.quizzes.list_themes()
        raw_themes = [ThemeSchema().dump(theme) for theme in themes]

        return json_response(data={'themes': raw_themes})


class QuestionAddView(View):
    @login_required()
    @docs(
        tags=['VKBot'],
        summary='Adding a new question',
        description='Add new question in database'
    )
    @request_schema(QuestionSchema)
    @response_schema(OkResponseSchema, 200)
    async def post(self):
        MIN_ANSWERS = 2
        answers = self.data.get('answers')
        count_correct_answers = 0

        if len(answers) < MIN_ANSWERS:
            raise HTTPBadRequest

        for answer in answers:
            if answer['is_correct'] == True:
                count_correct_answers += 1
        
        if count_correct_answers != 1:
            raise HTTPBadRequest
        
        if await self.store.quizzes.get_question_by_title(self.data.get('title')):
            raise HTTPConflict
         
        if not await self.store.quizzes.get_theme_by_id(self.data.get('theme_id')):
            raise HTTPNotFound
        
        question = await self.store.quizzes.create_question(**self.data)

        return json_response(data=QuestionSchema().dump(question))


class QuestionListView(View):
    @login_required()
    @docs(
            tags=['VKBot'],
            summary='List all questions',
            description='List all questions from database'
        )
    @response_schema(QuestionListSchemaResponseSchema, 200)
    async def get(self):
        theme_id = self.request.query.get('theme_id')

        if not theme_id:
            questions = self.request.app.database.questions
        else:
            questions = await (
                self.store.quizzes.list_questions(theme_id=int(theme_id))
            )
        
        raw_questions = [QuestionSchema().dump(question) for question in questions]

        return json_response(data={'questions': raw_questions})
