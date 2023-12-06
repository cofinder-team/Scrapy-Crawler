from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from scrapy.utils import project


def create_llm_chain(model_name: str, template_path: str, input_variables: list[str]):
    settings = project.get_project_settings()
    llm: ChatOpenAI = ChatOpenAI(
        temperature=0,
        openai_api_key=settings.get("OPENAI_API_KEY"),
        model_name=model_name,
    )
    with open(template_path, encoding="UTF-8") as file:
        template: PromptTemplate = PromptTemplate(
            input_variables=input_variables, template=file.read()
        )
        return LLMChain(llm=llm, prompt=template)


PREFIX = "scrapy_crawler/common/chatgpt/prompts/%s"
GPT4_MODEL_NAME = "gpt-4-0613"
GPT3_MODEL_NAME = "gpt-3.5-turbo-0613"
unused_chain: LLMChain = create_llm_chain(
    GPT3_MODEL_NAME, PREFIX % "unused.txt", ["title", "content"]
)
apple_care_plus_chain: LLMChain = create_llm_chain(
    GPT3_MODEL_NAME, PREFIX % "apple_care_plus.txt", ["title", "content"]
)
macbook_system_chain: LLMChain = create_llm_chain(
    GPT3_MODEL_NAME,
    PREFIX % "macbook_system.txt",
    ["title", "content", "default_ram", "default_ssd"],
)
macbook_chain: LLMChain = create_llm_chain(
    GPT3_MODEL_NAME, PREFIX % "macbook.txt", ["title", "content"]
)
macbook_air_13_chain: LLMChain = create_llm_chain(
    GPT3_MODEL_NAME, PREFIX % "macbook_air_13.txt", ["title", "content"]
)
macbook_pro_13_chain: LLMChain = create_llm_chain(
    GPT3_MODEL_NAME, PREFIX % "macbook_pro_13.txt", ["title", "content"]
)
macbook_pro_14_chain: LLMChain = create_llm_chain(
    GPT3_MODEL_NAME, PREFIX % "macbook_pro_14.txt", ["title", "content"]
)
macbook_pro_16_chain: LLMChain = create_llm_chain(
    GPT3_MODEL_NAME, PREFIX % "macbook_pro_16.txt", ["title", "content"]
)
macmini_chain: LLMChain = create_llm_chain(
    GPT3_MODEL_NAME, PREFIX % "macmini.txt", ["title", "content"]
)

category_chain: LLMChain = create_llm_chain(
    GPT3_MODEL_NAME, PREFIX % "category_prompt.txt", ["title"]
)
ipad_chain: LLMChain = create_llm_chain(
    GPT3_MODEL_NAME, PREFIX % "ipad.txt", ["title", "content"]
)
ipad_gen_chain: LLMChain = create_llm_chain(
    GPT3_MODEL_NAME, PREFIX % "ipad_gen.txt", ["title", "content"]
)
ipad_system_chain: LLMChain = create_llm_chain(
    GPT3_MODEL_NAME, PREFIX % "ipad_system.txt", ["title", "content", "default_ssd"]
)
ipad_cellular_chain: LLMChain = create_llm_chain(
    GPT3_MODEL_NAME, PREFIX % "ipad_cellular.txt", ["title", "content"]
)

iphone_generation_chain = create_llm_chain(
    GPT3_MODEL_NAME, PREFIX % "iphone_generation.txt", ["title"]
)

iphone_storage_chain = create_llm_chain(
    GPT3_MODEL_NAME,
    PREFIX % "iphone_storage.txt",
    ["title", "content", "default_storage"],
)

iphone_model_chain = create_llm_chain(
    GPT3_MODEL_NAME, PREFIX % "iphone_model.txt", ["title", "content"]
)
