from aiohttp.web_exceptions import HTTPUnauthorized, HTTPConflict, \
    HTTPBadRequest, HTTPNotFound
from aiohttp_apispec import request_schema, querystring_schema, response_schema

from app.quiz.models import Answer
from app.quiz.schemes import (
    ThemeSchema, ThemeRequestSchema, ThemeListSchema, QuestionSchema,
    ThemeIdSchema, ListQuestionSchema, ListQuestionOkResponseSchema,
)
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class ThemeAddView(AuthRequiredMixin, View):
    @request_schema(ThemeRequestSchema)
    async def post(self):
        title = self.data["title"]
        if await self.store.quizzes.get_theme_by_title(title):
            raise HTTPConflict
        theme = await self.store.quizzes.create_theme(title=title)
        return json_response(data=ThemeSchema().dump(theme))


class ThemeListView(AuthRequiredMixin, View):
    async def get(self):
        themes = await self.store.quizzes.list_themes()
        return json_response(
            data=ThemeListSchema().dump({"themes": themes})
        )


class QuestionAddView(AuthRequiredMixin, View):
    @request_schema(QuestionSchema)
    async def post(self):
        answers = [Answer(title=answer["title"],
                          is_correct=answer["is_correct"]) for answer in
                   self.data["answers"]]
        title = self.data["title"]
        theme_id = self.data["theme_id"]
        if len(answers) < 2 or len(
                [answer for answer in answers if answer.is_correct]) != 1:
            raise HTTPBadRequest

        if await self.store.quizzes.get_question_by_title(title):
            raise HTTPConflict

        if not await self.store.quizzes.get_theme_by_id(theme_id):
            raise HTTPNotFound

        question = await self.store.quizzes.create_question(title, theme_id, answers)
        return json_response(data=QuestionSchema().dump(question))


class QuestionListView(AuthRequiredMixin, View):
    @querystring_schema(ThemeIdSchema)
    @response_schema(ListQuestionOkResponseSchema)
    async def get(self):
        theme_id = int(self.request.query.get('theme_id', '-1'))
        questions = await self.store.quizzes.list_questions(theme_id)
        return json_response(
            data=ListQuestionSchema().dump({"questions": questions})
        )
