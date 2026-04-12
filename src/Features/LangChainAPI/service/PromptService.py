from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from Features.LangChainAPI.LangChainDTO import Callback, ChatRequest, ChatTechniqueRequest, ChatTemplateRequest, TechType, TemplateType
from SharedKernel.persistence.Decorators import Service
from SharedKernel.utils.yamlenv import load_env_yaml
from langchain_core.language_models.chat_models import BaseChatModel
from pydantic import BaseModel, Field, config
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser

from Features.LangChainAPI.prompt import System_Instruction

class YouTubeVideo(BaseModel):
    title: str = Field(description="Tiêu đề video")
    channel: str = Field(description="Tên kênh YouTube")
    views: int = Field(description="Số lượt xem")
    upload_date: str = Field(description="Ngày đăng video")
    is_short: bool = Field(description="Video có phải YouTube Shorts hay không")

class PromptService:
    def __init__(self):
        ...

    async def hello(self):
        provider = ChatOllama(
            model="hf.co/unsloth/Qwen3-4B-Instruct-2507-GGUF:Q4_K_M",
            base_url="http://localhost:11434"
        )

        response = provider.astream("Xin chào, bạn khỏe không?")

        async def gen():
            yield f"[MODEL] {provider.model}\n"
            async for chunk in response:
                if chunk.content:
                    yield chunk.content
        return gen()
    async def GameAwardQA(self, question: str):
        provider = ChatOllama(
            model="hf.co/unsloth/Qwen3-4B-Instruct-2507-GGUF:Q4_K_M",
            base_url="http://localhost:11434"
        )

        GAME_AWARDS_2026 = {
            "Game of the Year": "Clair Obscur: Expedition 33",
            "Best RPG": "Clair Obscur: Expedition 33",
            "Best Action Game": "Hades II",
            "Best Adventure Game": "Ghost of Yōtei",
            "Best Strategy / Simulation": "The Alters",
            "Best Racing Game": "Mario Kart World",
            "Best Online Game": "ARC Raiders",
            "Best Sports Game": "Rematch"
        }

        def build_context():
            context = "Game Awards 2026 winners:\n"

            for category, game in GAME_AWARDS_2026.items():
                context += f"{category}: {game}\n"

            return context
        print(build_context())

        messages = [SystemMessage(content=f"""
        Bạn là trợ lý hỏi đáp về Game Awards.

        Sử dụng dữ liệu sau để trả lời:

        {build_context()}

        Trả lời ngắn gọn.
        Nếu không có dữ liệu thì nói "Không có thông tin".
        """)]

        messages.append(HumanMessage(content=question))

        async def gen():
            async for chunk in provider.astream(messages):
                if chunk.content:
                    yield chunk.content
        return gen()
        ...

    async def create_blog_with_ai(self, title: str):
        provider = ChatOllama(
            model="hf.co/unsloth/Qwen3-4B-Instruct-2507-GGUF:Q4_K_M",
            base_url="http://localhost:11434"
        )


        template = "Viết một blog ngắn nói về {topic}" 
        prompt_template = PromptTemplate.from_template(template)
        query = prompt_template.format(topic=title)

        async def gen():
            async for chunk in provider.astream(query):
                if chunk.content:
                    yield chunk.content
        gen()

    async def extract_youtube_video_info(self, description: str):
        provider = ChatOllama(
            model="hf.co/unsloth/Qwen3-4B-Instruct-2507-GGUF:Q4_K_M",
            base_url="http://localhost:11434"
        )

        parser = PydanticOutputParser(pydantic_object=YouTubeVideo)

        template = PromptTemplate(
        template="""
        Trích xuất thông tin video YouTube từ đoạn sau.

        {format_instructions}

        Description:
        {description}
        """,
                input_variables=["description"],
                partial_variables={
                    "format_instructions": parser.get_format_instructions()
                },
            )

        prompt_text = template.format(description=description)

        response = await provider.ainvoke([
            HumanMessage(content=prompt_text)
        ])

        result = parser.parse(response.content)
        def gen():
            yield result.model_dump_json()
        return gen()

        
