from pydantic import BaseModel
from Features.LangChainAPI.LangChainFacade import LangChainFacade
from Features.LangChainAPI.LangTools import LangTools
from fastapi import APIRouter, Depends, FastAPI
from fastapi.responses import StreamingResponse
from SharedKernel.persistence.Decorators import Controller
from Features.LangChainAPI.LangChainDTO import ChatRequest

@Controller
class BaiTapController:
    def __init__(self, app: FastAPI) -> None:
        """
        Moi chuong tuong ung voi tuan hoc
        """
        
        self.app = app
        self.router = APIRouter(
            prefix="/api/v1/bai_tap",
            tags=["BTCNLTHD"]
        )
        self.tools = LangTools()

        self.check_models()
        self.game_awards_QA()
        self.create_blog_with_ai()
        self.format_youtube_video()
        self.take_note()
        self.search_multi_domain()
        self.app.include_router(self.router)

    def check_models(self):
        @self.router.post("/chat")
        async def check_models(
            langfacade: LangChainFacade = Depends()
        ):
            return StreamingResponse(
                await langfacade.prompt_service.hello(),
                media_type="text/event-stream"
            )

    def game_awards_QA(self):
        """
        Ung dung hoi dap game award
        """
        class ChatRequest(BaseModel):
            question: str="Game of the Year 2026 là gì?"
        @self.router.post("/game_awards_QA")
        async def game_awards_QA(
            req: ChatRequest, 
            langfacade: LangChainFacade = Depends()
        ):
            return StreamingResponse(
                await langfacade.prompt_service.GameAwardQA(req.question),
                media_type="text/event-stream"
            )
        ...

    def create_blog_with_ai(self):
        """
        Ung dung tao blog voi AI
        """

        class BlogRequest(BaseModel):
            title: str
        @self.router.post("/create_blog_with_ai")
        async def create_blog_with_ai(
            req: BlogRequest, 
            langfacade: LangChainFacade = Depends()
        ):
            response = await langfacade.prompt_service.create_blog_with_ai(req.title)

            return StreamingResponse(
                response,
                media_type="text/event-stream"
            )
        ...

    def format_youtube_video(self):
        """
        Ung dung format dinh dang thong tin video 
        """

        class DescriptionVideo(BaseModel):
            description: str = """Video 'LangChain Tutorial for Beginners' của kênh AI Academy, 120000 views, đăng ngày 2024-05-12. Đây không phải Shorts."""
        @self.router.post("/format_video")
        async def format_video(
            req: DescriptionVideo,
            langfacade: LangChainFacade = Depends() 
        ):
            return StreamingResponse(
                await langfacade.prompt_service.extract_youtube_video_info(req.description),
                media_type="text/event-stream"
            )
        ...

    def take_note(self):
        """
        Ung dung ghi chu 

        query: Ngày 12/6 tôi sẽ bay về quê để dự đám cưới
        """

        class TakeNoteRequest(BaseModel):
            query: str
            session_id: str = "user_1"

        @self.router.post("/take_note")
        async def take_note(
            req: TakeNoteRequest,
            langfacade: LangChainFacade = Depends()
        ):
            response = await langfacade.agent_service.take_note(req.session_id, req.query)
            return StreamingResponse(
                response,
                media_type="text/event-stream"
            )
        ...

    def search_multi_domain(self):
        """
        Ung dung tim kiem da linh vuc

        query: Danh sách oscar 2026
        """

        class MulitDomainRequest(BaseModel):
            query: str

        @self.router.post("/search_multi_domain")
        async def search_multi_domain(
            req: MulitDomainRequest,
            langfacade: LangChainFacade = Depends()
        ):
            response = langfacade.agent.search_multi_domain(req.query)
            return StreamingResponse(
                response,
                media_type="text/event-stream"
            )
        ...
    ...

