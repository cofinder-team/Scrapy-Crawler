from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from scrapy.utils import project


def create_llm_chain(model_name: str, template_path: str, input_variables: list[str]):
    settings = project.get_project_settings()
    llm: ChatOpenAI = ChatOpenAI(temperature=0,
                                 openai_api_key=settings.get("OPENAI_API_KEY"),
                                 model_name=model_name)
    with open(template_path, "r", encoding="UTF-8") as file:
        template: PromptTemplate = PromptTemplate(
            input_variables=input_variables,
            template=file.read()
        )
        return LLMChain(llm=llm, prompt=template)


PREFIX = "scrapy_crawler/util/chatgpt/prompts/%s"

unused_chain: LLMChain = create_llm_chain("gpt-3.5-turbo-0613", PREFIX % "unused.txt",
                                          ["title", "content"])
apple_care_plus_chain: LLMChain = create_llm_chain("gpt-3.5-turbo-0613", PREFIX % "apple_care_plus.txt",
                                                 ["title", "content"])
macbook_system_chain: LLMChain = create_llm_chain("gpt-3.5-turbo-0613", PREFIX % "macbook_system.txt",
                                                  ["title", "content", "default_ram", "default_ssd"])
macbook_chain: LLMChain = create_llm_chain("gpt-3.5-turbo-0613", PREFIX % "macbook.txt", ["title", "content"])
macbook_air_13_chain: LLMChain = create_llm_chain("gpt-3.5-turbo-0613", PREFIX % "macbook_air_13.txt",
                                                  ["title", "content"])
macbook_pro_13_chain: LLMChain = create_llm_chain("gpt-3.5-turbo-0613", PREFIX % "macbook_pro_13.txt",
                                                  ["title", "content"])
macbook_pro_14_chain: LLMChain = create_llm_chain("gpt-3.5-turbo-0613", PREFIX % "macbook_pro_14.txt",
                                                  ["title", "content"])
macbook_pro_16_chain: LLMChain = create_llm_chain("gpt-3.5-turbo-0613", PREFIX % "macbook_pro_16.txt",
                                                  ["title", "content"])
macmini_chain: LLMChain = create_llm_chain("gpt-3.5-turbo-0613", PREFIX % "macmini.txt", ["title", "content"])
category_chain: LLMChain = create_llm_chain("gpt-3.5-turbo-0613", PREFIX % "category_prompt.txt", ["title"])
ipad_chain: LLMChain = create_llm_chain("gpt-3.5-turbo-0613", PREFIX % "ipad.txt", ["title", "content"])
ipad_gen_chain: LLMChain = create_llm_chain("gpt-3.5-turbo-0613", PREFIX % "ipad_gen.txt", ["title", "content"])
ipad_system_chain: LLMChain = create_llm_chain("gpt-3.5-turbo-0613", PREFIX % "ipad_system.txt", ["title", "content", "default_ssd"])
ipad_cellular_chain: LLMChain = create_llm_chain("gpt-3.5-turbo-0613", PREFIX % "ipad_cellular.txt", ["title", "content"])
