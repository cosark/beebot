import logging
from typing import TYPE_CHECKING

from autopack.utils import functions_summary
from langchain.chat_models.base import BaseChatModel

from beebot.body.llm import call_llm
from beebot.models.database_models import Plan
from beebot.planner.planning_prompt import (
    planning_prompt_template,
)

if TYPE_CHECKING:
    from beebot.body import Body

logger = logging.getLogger(__name__)


class Planner:
    body: "Body"
    llm: BaseChatModel

    def __init__(self, body: "Body"):
        self.body = body

    async def plan(self) -> Plan:
        task = self.body.task
        history = await self.body.current_execution_path.compile_history()
        file_list = await self.body.file_manager.document_contents()
        functions = functions_summary(self.body.packs.values())
        prompt_variables = {
            "task": task,
            "history": history,
            "functions": functions,
            "file_list": file_list,
        }
        formatted_prompt = planning_prompt_template().format(**prompt_variables)

        logger.info("=== Plan Request ===")
        logger.info(formatted_prompt)

        response = await call_llm(
            self.body,
            message=formatted_prompt,
            function_call="none",
        )

        logger.info("=== Plan Created ===")
        logger.info(response.text)

        plan = Plan(
            prompt_variables=prompt_variables,
            plan_text=response.text,
            llm_response=response.text,
        )
        await plan.save()
        return plan
